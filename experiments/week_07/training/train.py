"""
Week 7 — QLoRA training script (stub / Colab-oriented).

Full training requires GPU (e.g. Colab T4/A100). This module provides:
- Model loading (4-bit + PEFT config)
- Dataset loading from prompt/completion JSONL or HuggingFace Dataset
- SFTTrainer setup

Run end-to-end in Colab or with: python -m experiments.week_07.experiments.run_qlora_train
"""

import os
from pathlib import Path

# Training depends on torch, transformers, peft, bitsandbytes, trl
def get_model_and_tokenizer(config: "QLoRAConfig"):
    """
    Load base model in 4-bit and tokenizer.
    Returns (model, tokenizer) for use with PEFT and SFTTrainer.
    """
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from transformers import BitsAndBytesConfig
        from peft import prepare_model_for_kbit_training
        from peft import LoraConfig, get_peft_model
    except ImportError as e:
        raise ImportError(
            "QLoRA training requires: torch, transformers, peft, bitsandbytes. "
            "Install with: pip install torch transformers peft bitsandbytes trl"
        ) from e

    dtype_map = {"bfloat16": torch.bfloat16, "float16": torch.float16}
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=config.load_in_4bit,
        bnb_4bit_compute_dtype=dtype_map.get(config.bnb_4bit_compute_dtype, torch.bfloat16),
        bnb_4bit_quant_type=config.bnb_4bit_quant_type,
        bnb_4bit_use_double_quant=config.bnb_4bit_use_double_quant,
    )
    tokenizer = AutoTokenizer.from_pretrained(config.base_model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        config.base_model_name,
        quantization_config=bnb_config,
        device_map="auto",
    )
    model = prepare_model_for_kbit_training(model)
    lora_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.lora_target_modules,
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    return model, tokenizer


def run_train(
    config: "QLoRAConfig",
    train_dataset,
    eval_dataset=None,
    prompt_col: str = "prompt",
    completion_col: str = "completion",
) -> Path:
    """
    Run SFTTrainer. Requires trl.
    train_dataset: HuggingFace Dataset with prompt/completion or text column.
    Returns output_dir.
    """
    from .config import QLoRAConfig
    model, tokenizer = get_model_and_tokenizer(config)
    try:
        from trl import SFTTrainer
        from transformers import TrainingArguments
    except ImportError as e:
        raise ImportError("Training requires trl and transformers.TrainingArguments") from e

    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=config.num_train_epochs,
        per_device_train_batch_size=config.per_device_train_batch_size,
        per_device_eval_batch_size=config.per_device_eval_batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        logging_steps=config.logging_steps,
        save_strategy=config.save_strategy,
        save_steps=config.save_steps,
        save_total_limit=config.save_total_limit,
        bf16=True,
        remove_unused_columns=False,
    )
    # Dataset format: either "text" (concatenated prompt+completion) or dataset with prompt/completion
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        max_seq_length=config.max_seq_length,
        dataset_text_field="text",  # or use formatting_func
    )
    trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    return output_dir
