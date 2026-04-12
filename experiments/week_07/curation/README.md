# Week 7 — Curation

Week 7 reuses **Week 6 curation** for the same price-prediction task: `Item` schema, loaders (Hub, local JSONL, synthetic), and train/val/test splits.

- **Item:** Same Pydantic model; `text_for_model` (summary or full), `make_prompt` / `test_prompt` for SFT and evaluation.
- **Loaders:** `load_from_hf`, `load_from_local`, `generate_synthetic`; optional `load_from_raw_dataset`, `save_train_val_test`.

This package re-exports Week 6 curation so Week 7 training and evaluation can load data without duplicating code. See `experiments.week_06.curation` for implementation.
