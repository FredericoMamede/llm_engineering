"""
Week 7 — Open-source price predictor: load base (4-bit) + PEFT adapter; predict from test prompt.

Same interface as Week 6 predictors: predictor(item) returns price (number or string);
evaluation harness post_processes to float.
"""

import os
import re
from pathlib import Path
from typing import Optional, Callable

# Week 6 Item has .price, .text_for_model, .test_prompt()
from experiments.week_06.curation import Item
from experiments.week_06.curation.items import PREFIX


def post_process(value: object) -> float:
    """Extract numeric price from model output (string or number)."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.replace("$", "").replace(",", "").strip()
        match = re.search(r"[-+]?\d*\.?\d+", s)
        return float(match.group()) if match else 0.0
    return 0.0


def open_source_pricer(
    base_model_name: str,
    adapter_path_or_id: Optional[str] = None,
    device_map: str = "auto",
    max_new_tokens: int = 10,
    load_in_4bit: bool = True,
) -> Callable[[object], object]:
    """
    Load base causal LM (optionally 4-bit) and optional PEFT adapter; return a predictor.

    predictor(item) expects item with .test_prompt() (or .prompt up to PREFIX) and .price (truth).
    Returns predicted price (string or float) for harness post_process.

    base_model_name: HuggingFace model id (e.g. meta-llama/Llama-3.2-3B).
    adapter_path_or_id: Local path or Hub id for PEFT adapter; if None, use base only.
    """
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel
    except ImportError as e:
        raise ImportError(
            "Open-source pricer requires: torch, transformers, peft. "
            "For 4-bit: pip install bitsandbytes"
        ) from e

    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if load_in_4bit:
        try:
            from transformers import BitsAndBytesConfig
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
            model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                quantization_config=bnb_config,
                device_map=device_map,
            )
        except Exception:
            model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                device_map=device_map,
                torch_dtype=torch.bfloat16,
            )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            device_map=device_map,
            torch_dtype=torch.bfloat16,
        )

    if adapter_path_or_id:
        model = PeftModel.from_pretrained(model, adapter_path_or_id)
        model.eval()

    def _predict(item: object) -> object:
        if hasattr(item, "test_prompt"):
            prompt = item.test_prompt()
        elif hasattr(item, "prompt"):
            # prompt may include completion; use only up to PREFIX
            p = getattr(item, "prompt", "") or ""
            prompt = p.split(PREFIX)[0] + PREFIX if PREFIX in p else p
        else:
            return 0.0
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )
        # Decode only the new tokens
        new_tokens = out[0][inputs["input_ids"].shape[1]:]
        completion = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        return post_process(completion)  # return float for harness

    return _predict
