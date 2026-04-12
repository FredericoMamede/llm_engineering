"""
Week 7 — QLoRA and SFT training config.

Override via env or pass to train script.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class QLoRAConfig:
    """QLoRA + SFT training configuration."""

    # Base model (HuggingFace id)
    base_model_name: str = field(
        default_factory=lambda: os.environ.get("W7_BASE_MODEL", "meta-llama/Llama-3.2-3B")
    )
    # 4-bit quantization (BitsAndBytes)
    load_in_4bit: bool = True
    bnb_4bit_compute_dtype: str = "bfloat16"
    bnb_4bit_quant_type: str = "nf4"
    bnb_4bit_use_double_quant: bool = True

    # LoRA
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    lora_target_modules: list = field(default_factory=lambda: ["q_proj", "v_proj"])

    # SFT
    max_seq_length: int = 512
    num_train_epochs: int = 1
    per_device_train_batch_size: int = 2
    per_device_eval_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-5
    warmup_ratio: float = 0.03
    logging_steps: int = 10
    save_strategy: str = "steps"
    save_steps: int = 100
    save_total_limit: int = 2

    # Paths
    output_dir: str = field(
        default_factory=lambda: os.environ.get("W7_OUTPUT_DIR", "training/outputs")
    )
    hub_model_id: str = field(default_factory=lambda: os.environ.get("W7_HUB_MODEL_ID", ""))
