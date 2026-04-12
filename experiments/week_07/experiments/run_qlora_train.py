"""
Week 7 — QLoRA training entry point.

Builds SFT dataset from Week 6 data (synthetic / Hub / local), then runs QLoRA training.
Requires GPU (e.g. Colab T4/A100). For full training, use course Colab (Day 3–4) or run
this after installing: torch, transformers, peft, bitsandbytes, trl, datasets.

Usage (from repo root):
  python -m experiments.week_07.experiments.run_qlora_train

Env: W7_BASE_MODEL, W6_DATA_SOURCE, W6_HUB_DATASET, W7_OUTPUT_DIR, W7_HUB_MODEL_ID
"""

import os
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    _repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(_repo_root))

from experiments.week_07.training.config import QLoRAConfig
from experiments.week_07.training.dataset import (
    load_data_for_prompts,
    items_to_prompt_completion_list,
    save_prompt_completion_jsonl,
)


def main():
    config = QLoRAConfig()
    data_source = os.environ.get("W6_DATA_SOURCE", "synthetic")
    hub_dataset = os.environ.get("W6_HUB_DATASET", "")
    local_dir = Path(__file__).resolve().parents[1] / "data" / "processed"
    if data_source == "local" and not local_dir.exists():
        local_dir = None

    print("Loading data...")
    train, val, test = load_data_for_prompts(
        data_source=data_source,
        hub_dataset=hub_dataset,
        local_dir=local_dir,
        seed=42,
    )
    print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")

    out_prompts = Path(__file__).resolve().parents[1] / "data" / "prompts"
    out_prompts.mkdir(parents=True, exist_ok=True)
    save_prompt_completion_jsonl(train, out_prompts / "train.jsonl")
    save_prompt_completion_jsonl(val, out_prompts / "val.jsonl")
    save_prompt_completion_jsonl(test, out_prompts / "test.jsonl")
    print(f"Wrote prompt/completion JSONL to {out_prompts}")

    try:
        from datasets import load_dataset
        from experiments.week_07.training.train import get_model_and_tokenizer, run_train
    except ImportError as e:
        print(
            "Skipping training (missing deps). Install: pip install torch transformers peft bitsandbytes trl datasets"
        )
        print(f"  {e}")
        return

    # Build HF Dataset with "text" = prompt + completion for SFT
    def to_text(row):
        return row["prompt"] + row["completion"]

    train_ds = load_dataset("json", data_files=str(out_prompts / "train.jsonl"), split="train")
    train_ds = train_ds.map(lambda x: {"text": x["prompt"] + x["completion"]}, remove_columns=["prompt", "completion"])
    val_ds = load_dataset("json", data_files=str(out_prompts / "val.jsonl"), split="train")
    val_ds = val_ds.map(lambda x: {"text": x["prompt"] + x["completion"]}, remove_columns=["prompt", "completion"])

    print("Starting QLoRA training (this requires GPU)...")
    output_dir = run_train(config, train_ds, eval_dataset=val_ds)
    print(f"Training done. Adapters saved to {output_dir}")


if __name__ == "__main__":
    main()
