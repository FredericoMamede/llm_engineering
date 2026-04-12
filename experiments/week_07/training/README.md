# Week 7 — Training (QLoRA)

Build SFT dataset from Week 6 Items and run QLoRA training (4-bit + LoRA) with SFTTrainer.

## Dataset

- **dataset.py:** Build prompt/completion pairs from Items (same format as course: QUESTION + text + PREFIX / completion).
- **CLI:** `python -m experiments.week_07.training.dataset --data_source synthetic --out_dir data/prompts`
- Output: `train.jsonl`, `val.jsonl`, `test.jsonl` under `out_dir`.

## Config

- **config.py:** `QLoRAConfig` — base model, 4-bit settings, LoRA r/alpha/dropout/target_modules, SFT epochs/batch size/output dir.
- Override via env: `W7_BASE_MODEL`, `W7_OUTPUT_DIR`, `W7_HUB_MODEL_ID`.

## Train

- **train.py:** Load base model (4-bit), apply PEFT LoRA, run SFTTrainer. Requires GPU.
- Full run: use Colab (course Day 3–4) or `python -m experiments.week_07.experiments.run_qlora_train` after preparing dataset.
- Adapters saved to `training/outputs/` or pushed to Hub if `W7_HUB_MODEL_ID` is set.

## Dependencies

- torch, transformers, peft, bitsandbytes, trl, datasets
