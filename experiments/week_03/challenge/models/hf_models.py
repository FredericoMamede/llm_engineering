"""
HuggingFace Models Adapter

Supports both open and gated models from HuggingFace.
Handles authentication, quantization, and model loading.

Models included:
- Gated (requires access): Llama 3.x family, Gemma family
- Open: Phi-3, Qwen, Mistral, TinyLlama, Zephyr, and others
"""

import os
import torch
import gc
from typing import Optional, Dict
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from huggingface_hub import login

from .base import BaseModel, GenerationConfig, ModelResponse


# Comprehensive model list for synthetic data generation
# Organized by category for easy selection

HF_MODELS = {
    # Gated models (requires access approval and HF_TOKEN)
    "gated": {
        # Llama 3.1 models
        "llama_3_1_8b": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "llama_3_1_70b": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        # Llama 3.2 models
        "llama_3_2_1b": "meta-llama/Llama-3.2-1B-Instruct",
        "llama_3_2_3b": "meta-llama/Llama-3.2-3B-Instruct",
        # Llama 3.3 models
        "llama_3_3_8b": "meta-llama/Llama-3.3-8B-Instruct",
        # Llama 4 models (for use with transformers)
        "llama_4_scout_17b": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
        "llama_4_maverick_17b": "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
        "llama_4_maverick_17b_fp8": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        # Gemma 2 models
        "gemma_2_2b": "google/gemma-2-2b-it",
        "gemma_2_9b": "google/gemma-2-9b-it",
        "gemma_2_27b": "google/gemma-2-27b-it",
    },
    # Open models (no access required)
    "open": {
        # Microsoft models
        "phi_3_mini": "microsoft/Phi-3-mini-4k-instruct",
        "phi_3_medium": "microsoft/Phi-3-medium-4k-instruct",
        "phi_4_mini": "microsoft/Phi-4-mini-instruct",
        
        # Alibaba Qwen models
        "qwen_2_5_0_5b": "Qwen/Qwen2.5-0.5B-Instruct",
        "qwen_2_5_1_5b": "Qwen/Qwen2.5-1.5B-Instruct",
        "qwen_2_5_3b": "Qwen/Qwen2.5-3B-Instruct",
        "qwen_2_5_7b": "Qwen/Qwen2.5-7B-Instruct",
        "qwen_2_5_14b": "Qwen/Qwen2.5-14B-Instruct",
        
        # Mistral models
        "mistral_7b": "mistralai/Mistral-7B-Instruct-v0.2",
        "mistral_7b_v3": "mistralai/Mistral-7B-Instruct-v3",
        
        # TinyLlama (very small, fast)
        "tinyllama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        
        # Zephyr models (HuggingFace's instruction-tuned)
        "zephyr_7b": "HuggingFaceH4/zephyr-7b-beta",
        "zephyr_7b_v2": "HuggingFaceH4/zephyr-7b-alpha",
        
        # DeepSeek (open variants)
        "deepseek_coder_1_3b": "deepseek-ai/DeepSeek-Coder-1.3B-Instruct",
        "deepseek_coder_6_7b": "deepseek-ai/DeepSeek-Coder-6.7B-Instruct",
        
        # Other useful open models
        "falcon_7b": "tiiuae/falcon-7b-instruct",
        "openelm_1_1b": "apple/OpenELM-1_1B-Instruct",
    }
}


def get_all_hf_models() -> Dict[str, str]:
    """Get flat dictionary of all available HF models"""
    all_models = {}
    all_models.update(HF_MODELS["gated"])
    all_models.update(HF_MODELS["open"])
    return all_models


def get_model_by_key(key: str) -> Optional[str]:
    """Get model name by key (e.g., 'llama_3_2_3b')"""
    all_models = get_all_hf_models()
    return all_models.get(key)


class HuggingFaceModel(BaseModel):
    """
    HuggingFace model adapter.
    
    Handles:
    - Model loading with optional quantization
    - Chat template application
    - Tokenization and generation
    - Memory management
    
    Design decisions:
    - Lazy loading: Model only loaded when first generate() is called
    - Quantization: Optional 4-bit quantization to reduce memory
    - Chat templates: Automatically applied for instruct models
    """
    
    def __init__(
        self,
        model_name: str,
        use_quantization: bool = True,
        device: Optional[str] = None,
        hf_token: Optional[str] = None
    ):
        """
        Args:
            model_name: HuggingFace model identifier
            use_quantization: Whether to use 4-bit quantization (saves memory)
            device: Device to use ('cuda', 'cpu', 'mps', or None for auto)
            hf_token: HuggingFace token for gated models (or use env/login)
        """
        super().__init__(model_name, "huggingface")
        self.use_quantization = use_quantization
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        
        # Authenticate if token provided
        if self.hf_token:
            login(token=self.hf_token, add_to_git_credential=False)
        
        self._tokenizer = None
        self._model = None
    
    def _get_quantization_config(self) -> Optional[BitsAndBytesConfig]:
        """Create quantization config if enabled"""
        if not self.use_quantization:
            return None
        
        if not torch.cuda.is_available():
            # Quantization requires CUDA
            return None
        
        return BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_quant_type="nf4"
        )
    
    def _load_model(self):
        """Lazy load model and tokenizer"""
        if self._model is not None:
            return
        
        try:
            # Prepare token argument for gated models
            token_kwargs = {}
            if self.hf_token:
                token_kwargs["token"] = self.hf_token
            
            # Load tokenizer (pass token for gated models)
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                **token_kwargs
            )
            
            # Set pad token if not present
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
            
            # Load model with optional quantization (pass token for gated models)
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
                f"Failed to load HuggingFace model '{self.model_name}': {str(e)}\n"
                f"Check: 1) Model name is correct, 2) You have access (for gated models), "
                f"3) HF token is set (for gated models)"
            ) from e
    
    def is_loaded(self) -> bool:
        return self._model is not None
    
    def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> ModelResponse:
        """Generate text using HuggingFace model"""
        if config is None:
            config = GenerationConfig()
        
        # Lazy load if needed
        if not self.is_loaded():
            self._load_model()
        
        try:
            # Apply chat template if available (for instruct models)
            # Check if tokenizer has apply_chat_template method
            if hasattr(self._tokenizer, 'apply_chat_template'):
                try:
                    # Format as chat messages
                    messages = [{"role": "user", "content": prompt}]
                    formatted_prompt = self._tokenizer.apply_chat_template(
                        messages,
                        tokenize=False,
                        add_generation_prompt=True
                    )
                except Exception:
                    # Fallback to raw prompt if chat template fails
                    formatted_prompt = prompt
            else:
                formatted_prompt = prompt
            
            # Tokenize
            inputs = self._tokenizer(
                formatted_prompt,
                return_tensors="pt"
            ).to(self.device)
            
            # Generation parameters
            generation_kwargs = {
                "max_new_tokens": config.max_tokens,
                "temperature": config.temperature,
                "do_sample": config.temperature > 0,
            }
            
            if config.top_p is not None:
                generation_kwargs["top_p"] = config.top_p
            
            if config.seed is not None:
                generation_kwargs["seed"] = config.seed
            
            # Generate
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    **generation_kwargs
                )
            
            # Decode
            generated_text = self._tokenizer.decode(
                outputs[0],
                skip_special_tokens=True
            )
            
            # Remove input prompt from output
            if formatted_prompt in generated_text:
                generated_text = generated_text[len(formatted_prompt):].strip()
            
            return ModelResponse(
                text=generated_text,
                model_name=self.model_name,
                provider="huggingface",
                metadata={
                    "device": self.device,
                    "quantized": self.use_quantization and torch.cuda.is_available(),
                    "input_length": len(formatted_prompt),
                    "output_length": len(generated_text)
                }
            )
            
        except Exception as e:
            raise RuntimeError(
                f"Generation failed for '{self.model_name}': {str(e)}"
            ) from e
    
    def unload(self):
        """Unload model from memory (useful for memory management)"""
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
        """Cleanup on deletion"""
        self.unload()
