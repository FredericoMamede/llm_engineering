"""
Meeting Intelligence Extractor

Extracts structured information from meeting transcripts using Llama 3.2 3B Instruct.

Uses 4-bit quantization for memory efficiency and applies chat templates
for proper instruction formatting. Handles JSON extraction with fallback
parsing for markdown-wrapped or malformed outputs.
"""

import os
import json
import re
import torch
import gc
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TextIteratorStreamer,
)
from threading import Thread
from huggingface_hub import login

from schemas import validate_meeting_dict

# Load environment variables from .env file
load_dotenv()


class MeetingExtractor:
    """
    Extracts structured information from meeting transcripts.
    
    Uses HuggingFace transformers with Llama 3.2 3B Instruct.
    Applies chat templates correctly and handles JSON extraction robustly.
    """
    
    def __init__(
        self,
        model_name: str = "meta-llama/Llama-3.2-3B-Instruct",
        use_quantization: bool = True,
        device: Optional[str] = None,
        hf_token: Optional[str] = None,
        temperature: float = 0.3,
        max_new_tokens: int = 1500
    ):
        """
        Initializes the extractor with model configuration.
        
        Model is lazy-loaded on first extraction call. Quantization reduces
        VRAM usage from ~6.4GB to ~1.5-2GB at the cost of slight quality degradation.
        """
        self.model_name = model_name
        self.use_quantization = use_quantization
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        
        if self.hf_token:
            login(token=self.hf_token, add_to_git_credential=False)
        
        self._tokenizer = None
        self._model = None
    
    def _get_quantization_config(self) -> Optional[BitsAndBytesConfig]:
        """Returns 4-bit quantization config if enabled and CUDA is available."""
        if not self.use_quantization or not torch.cuda.is_available():
            return None
        
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_quant_type="nf4"
        )
    
    def _load_model(self):
        """Lazy loads model and tokenizer on first use."""
        if self._model is not None:
            return
        
        try:
            token_kwargs = {}
            if self.hf_token:
                token_kwargs["token"] = self.hf_token
            
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                **token_kwargs
            )
            
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
            
            quant_config = self._get_quantization_config()
            
            if quant_config:
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    device_map="auto",
                    quantization_config=quant_config,
                    trust_remote_code=True,
                    **token_kwargs
                )
            else:
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    device_map="auto" if self.device == "cuda" else None,
                    trust_remote_code=True,
                    **token_kwargs
                )
                if self.device != "cuda":
                    self._model = self._model.to(self.device)
            
        except Exception as e:
            raise RuntimeError(
                f"Failed to load model '{self.model_name}': {str(e)}\n"
                f"Check: 1) Model name is correct, 2) You have access (for gated models), "
                f"3) HF token is set (for gated models)"
            ) from e
    
    def _load_prompt_template(self) -> str:
        """Loads prompt template from prompts/meeting_analysis.md."""
        prompt_path = Path(__file__).parent / "prompts" / "meeting_analysis.md"
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Prompt template not found: {prompt_path}\n"
                f"Please ensure prompts/meeting_analysis.md exists"
            )
    
    def _build_prompt(self, transcript: str) -> str:
        """Builds prompt from template, replacing {transcript} placeholder."""
        template = self._load_prompt_template()
        
        if "{transcript}" in template:
            return template.replace("{transcript}", transcript)
        else:
            return f"{template}\n\nMeeting transcript:\n{transcript}"
    
    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extracts JSON from model output with fallback parsing strategies.
        
        Attempts extraction in order: markdown code blocks, direct JSON objects,
        then full text parsing.
        """
        json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        match = re.search(json_block_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        json_object_pattern = r'\{.*\}'
        match = re.search(json_object_pattern, text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        return None
    
    def extract(self, transcript_path: str) -> Dict[str, Any]:
        """
        Extracts structured meeting intelligence from transcript file.
        
        Returns validated dictionary matching MeetingIntelligence schema.
        Raises FileNotFoundError, RuntimeError, or ValueError on failure.
        """
        transcript_file = Path(transcript_path)
        if not transcript_file.exists():
            raise FileNotFoundError(f"Transcript file not found: {transcript_path}")
        
        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript = f.read()
        
        self._load_model()
        user_content = self._build_prompt(transcript)
        
        messages = [{"role": "user", "content": user_content}]
        
        try:
            formatted_prompt = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to apply chat template: {e}\n"
                f"This model requires proper chat template formatting"
            ) from e
        
        inputs = self._tokenizer(
            formatted_prompt,
            return_tensors="pt"
        ).to(self.device)
        
        generation_kwargs = {
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "do_sample": self.temperature > 0,
            "pad_token_id": self._tokenizer.pad_token_id,
            "eos_token_id": self._tokenizer.eos_token_id,
        }
        
        try:
            with torch.no_grad():
                outputs = self._model.generate(**inputs, **generation_kwargs)
        except Exception as e:
            raise RuntimeError(f"Generation failed: {e}") from e
        
        generated_text = self._tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )
        
        if formatted_prompt in generated_text:
            generated_text = generated_text[len(formatted_prompt):].strip()
        else:
            input_length = inputs.input_ids.shape[1]
            output_tokens = outputs[0][input_length:]
            generated_text = self._tokenizer.decode(output_tokens, skip_special_tokens=True)
        
        result = self._extract_json_from_text(generated_text)
        
        if result is None:
            raise ValueError(
                f"Failed to extract valid JSON from model output.\n"
                f"Output (first 500 chars): {generated_text[:500]}"
            )
        
        if not validate_meeting_dict(result):
            raise ValueError(
                f"Extracted JSON does not match expected schema.\n"
                f"Got: {list(result.keys())}"
            )
        
        return result
    
    def extract_with_streaming(
        self,
        transcript: str,
        stream_callback=None
    ) -> Dict[str, Any]:
        """
        Extracts meeting intelligence with token-by-token streaming.
        
        Uses TextIteratorStreamer to yield tokens as they're generated.
        Callback receives each token chunk for real-time UI updates.
        Final output is parsed and validated identically to extract().
        """
        self._load_model()
        user_content = self._build_prompt(transcript)
        
        messages = [{"role": "user", "content": user_content}]
        
        try:
            formatted_prompt = self._tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to apply chat template: {e}\n"
                f"This model requires proper chat template formatting"
            ) from e
        
        inputs = self._tokenizer(
            formatted_prompt,
            return_tensors="pt"
        ).to(self.device)
        
        streamer = TextIteratorStreamer(
            self._tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )
        
        generation_kwargs = {
            "max_new_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "do_sample": self.temperature > 0,
            "pad_token_id": self._tokenizer.pad_token_id,
            "eos_token_id": self._tokenizer.eos_token_id,
            "streamer": streamer,
        }
        
        def generate_with_streamer():
            with torch.no_grad():
                self._model.generate(**inputs, **generation_kwargs)
        
        generation_thread = Thread(target=generate_with_streamer)
        generation_thread.start()
        
        generated_text = ""
        for new_text in streamer:
            generated_text += new_text
            if stream_callback:
                stream_callback(new_text)
        
        generation_thread.join()
        
        result = self._extract_json_from_text(generated_text)
        
        if result is None:
            raise ValueError(
                f"Failed to extract valid JSON from model output.\n"
                f"Output (first 500 chars): {generated_text[:500]}"
            )
        
        if not validate_meeting_dict(result):
            raise ValueError(
                f"Extracted JSON does not match expected schema.\n"
                f"Got: {list(result.keys())}"
            )
        
        return result
    
    def extract_to_file(
        self,
        transcript_path: str,
        output_path: Optional[str] = None
    ) -> str:
        """
        Extracts meeting intelligence and persists to JSON file.
        
        Auto-generates timestamped filename if output_path not provided.
        Returns absolute path to saved file.
        """
        result = self.extract(transcript_path)
        
        if output_path is None:
            import datetime
            base_name = Path(transcript_path).stem
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(__file__).parent / "sample_outputs"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{base_name}_{timestamp}.json"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return str(output_path)
    
    def unload(self):
        """Releases model and tokenizer from memory and clears CUDA cache."""
        if self._model is not None:
            del self._model
            self._model = None
        
        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
    
    def __del__(self):
        """Releases resources on object destruction."""
        self.unload()
