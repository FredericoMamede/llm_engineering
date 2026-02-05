# Week 6 — Status

## Explicit checklist

### Implemented

- [x] **Scaffold and docs** — Directory structure, README, ARCHITECTURE, STATUS, NOTES.
- [x] **Evaluation metrics** — Pure functions: MAE, MSE, R² (`evaluation/metrics.py`).
- [x] **Evaluation harness** — Single `evaluate(predictor, data, size)`; post-process to number; returns n, mae, mse, r2 (`evaluation/harness.py`).
- [x] **Failure mode notes** — Fine-tuning regression, human baseline, cost tradeoffs (`evaluation/FAILURE_MODES.md`).
- [x] **Curation** — `Item` schema (Pydantic), parser (parse, scrub, get_weight), loaders (Hub, local JSONL, synthetic), train/val/test split (`curation/`).
- [x] **Preprocess** — SYSTEM_PROMPT, Preprocessor (LLM rewrite, cost/token tracking, use_preprocessing toggle), process_items / process_items_with_progress (`preprocess/`).
- [x] **Baselines** — Random, constant (train mean), length heuristic, linear regression (numeric), NLP+LR (CountVectorizer), Random Forest (`models/baselines.py`).
- [x] **DNN** — DNNRegressor (HashingVectorizer, log-price target, L1 loss, CosineAnnealingLR), dnn_predictor (`models/dnn.py`).
- [x] **LLM zero-shot** — zero_shot_predictor (litellm completion); same prompt format as course (`models/llm_pricer.py`).
- [x] **Fine-tuning** — make_jsonl_for_finetuning, fine_tuned_predictor (OpenAI inference); notes on when fine-tuning regresses (`models/llm_pricer.py`, FAILURE_MODES.md).
- [x] **Baseline comparison** — run_baseline_comparison.py: load data (synthetic / local / Hub), run all predictors through harness, print table (MAE, MSE, R²), save JSON to `evaluation/runs/comparison_latest.json`.

### In progress

- [ ] None.

### Not yet started (optional)

- [ ] **Harness extensions** — Optional scatter and error trend chart; parallel workers (course Tester used ThreadPoolExecutor).
- [ ] **Batch API** — Groq-style batch for preprocess at scale (course batch.py); cost comments in place.

All core components are implemented. Evaluation-first: every predictor plugs into the same harness; comparison is reproducible and auditable.
