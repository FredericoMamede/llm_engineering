"""
Week 7 — Evaluate open-source base (4-bit) and optional PEFT adapter on Week 6 harness.

Loads train/val/test (same as Week 6), prepares test prompts (make_prompt for each item),
runs base and (if set) fine-tuned predictor through Week 6 evaluate(), prints MAE, MSE, R².

Usage (from repo root):
  python -m experiments.week_07.experiments.run_eval_opensource

Env: W7_BASE_MODEL, W7_ADAPTER (optional), W6_DATA_SOURCE, W6_HUB_DATASET, W6_EVAL_SIZE
"""

import os
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    _repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(_repo_root))

from experiments.week_06.curation import load_from_hf, load_from_local, generate_synthetic
from experiments.week_06.evaluation import evaluate
from experiments.week_07.models.open_source_pricer import open_source_pricer

DATA_SOURCE = os.environ.get("W6_DATA_SOURCE", "synthetic")
HUB_DATASET = os.environ.get("W6_HUB_DATASET", "")
LOCAL_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
EVAL_SIZE = int(os.environ.get("W6_EVAL_SIZE", "50"))  # Keep small for GPU memory
BASE_MODEL = os.environ.get("W7_BASE_MODEL", "meta-llama/Llama-3.2-3B")
ADAPTER = os.environ.get("W7_ADAPTER", "")  # Hub id or local path


def load_data():
    if DATA_SOURCE == "hub" and HUB_DATASET:
        return load_from_hf(HUB_DATASET)
    if DATA_SOURCE == "local" and LOCAL_DATA_DIR.exists():
        return load_from_local(LOCAL_DATA_DIR)
    return generate_synthetic(n_train=300, n_val=80, n_test=100, seed=42)


def main():
    print("Loading data...")
    train, val, test = load_data()
    print(f"Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
    test_subset = test[:EVAL_SIZE]

    # Ensure each item has prompt set for test_prompt() (question + text + PREFIX, no answer)
    for item in test_subset:
        item.make_prompt(item.text_for_model)

    print("Loading base model (4-bit)...")
    predictor_base = open_source_pricer(BASE_MODEL, adapter_path_or_id=None, load_in_4bit=True)
    r_base = evaluate(predictor_base, test_subset, size=EVAL_SIZE)
    print(f"Base (4-bit):  n={r_base['n']}  MAE={r_base['mae']:.2f}  MSE={r_base['mse']:.0f}  R2={r_base['r2']:.2f}")

    if ADAPTER:
        print("Loading fine-tuned adapter...")
        predictor_ft = open_source_pricer(BASE_MODEL, adapter_path_or_id=ADAPTER, load_in_4bit=True)
        r_ft = evaluate(predictor_ft, test_subset, size=EVAL_SIZE)
        print(f"Fine-tuned:   n={r_ft['n']}  MAE={r_ft['mae']:.2f}  MSE={r_ft['mse']:.0f}  R2={r_ft['r2']:.2f}")
    else:
        print("Set W7_ADAPTER to evaluate fine-tuned model.")

    print("Done.")


if __name__ == "__main__":
    main()
