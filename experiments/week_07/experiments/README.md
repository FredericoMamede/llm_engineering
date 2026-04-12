# Week 7 — Experiments

## run_qlora_train.py

Build SFT dataset from Week 6 data and run QLoRA training (4-bit + LoRA, SFTTrainer). Requires GPU.

- **From repo root:** `python -m experiments.week_07.experiments.run_qlora_train`
- **Env:** `W7_BASE_MODEL`, `W6_DATA_SOURCE`, `W6_HUB_DATASET`, `W7_OUTPUT_DIR`, `W7_HUB_MODEL_ID`
- Writes prompt/completion JSONL to `data/prompts/`; trains and saves adapters to `training/outputs/` (or env).

## run_eval_opensource.py

Evaluate base (4-bit) and optional PEFT adapter on the same test set using Week 6 harness (MAE, MSE, R²).

- **From repo root:** `python -m experiments.week_07.experiments.run_eval_opensource`
- **Env:** `W7_BASE_MODEL`, `W7_ADAPTER` (optional), `W6_DATA_SOURCE`, `W6_HUB_DATASET`, `W6_EVAL_SIZE`
- Loads data, sets test prompts, runs base and (if `W7_ADAPTER` set) fine-tuned predictor; prints metrics.

## Dependencies

- Week 6: curation, evaluation.
- Week 7 training/eval: torch, transformers, peft; for 4-bit: bitsandbytes; for training: trl, datasets.
