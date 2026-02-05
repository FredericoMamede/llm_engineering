# Week 6 — Regression Capstone: "The Price Is Right"

## Status: **Complete**

Week 6 is **fully implemented**. All components (curation, preprocess, baselines, DNN, LLM zero-shot and fine-tuned, evaluation harness, baseline comparison) are in place and runnable.

---

## Theme and goals

Week 6 builds a **regression system** that predicts product price from description, using the same **evaluation-first** rigor as Week 5 but applied to a **different task**: numeric prediction from text, not retrieval or QA.

**Goals (all implemented):**

- **Data curation** — Parse and scrub Amazon-style product data; canonical `Item` schema; train/val/test splits; load from Hub, local JSONL, or synthetic.
- **LLM-based pre-processing** — Rewrite raw product text to a standard format via fixed system prompt; cost/token tracking; toggle ON/OFF.
- **Evaluation-first** — Single harness: same metrics and test set for all predictors (random, constant, traditional ML, DNN, zero-shot LLM, fine-tuned).
- **Baseline comparison** — Compare all models on MAE, MSE, R²; table printed and saved to `evaluation/runs/comparison_latest.json`.
- **Fine-tuning** — JSONL generation, fine-tuned inference (OpenAI); documented when fine-tuning **regresses** vs base (see `evaluation/FAILURE_MODES.md`).

---

## How this differs from Week 5

| Aspect | Week 5 | Week 6 |
|--------|--------|--------|
| Task | RAG: retrieve chunks, generate answer | Regression: predict price from description |
| Data | Documents, chunks, embeddings | Product records, Item schema, train/val/test |
| Models | Retriever + generator | Traditional ML, DNN, LLM zero-shot, fine-tuned |
| Evaluation | MRR, nDCG, recall, concept coverage | MAE, MSE, R²; baseline comparison |
| New ideas | Chunking, embeddings, ranking | Curation, LLM pre-processing, fine-tuning API |

Week 6 reuses **conceptual patterns** (evaluation harness, baselines, metrics) but **no code** from Week 5; the domain and stack are different.

---

## What is implemented

- **curation/** — Item (Pydantic), parser (parse, scrub, get_weight), loaders (Hub, local JSONL, synthetic), save_train_val_test.
- **preprocess/** — SYSTEM_PROMPT, Preprocessor (LLM rewrite, cost tracking, use_preprocessing), process_items.
- **models/** — baselines (random, constant, length heuristic, linear regression, NLP+LR, Random Forest), DNNRegressor / dnn_predictor, zero_shot_predictor, fine_tuned_predictor, make_jsonl_for_finetuning.
- **evaluation/** — metrics (MAE, MSE, R²), harness (evaluate, post_process), FAILURE_MODES.md.
- **experiments/run_baseline_comparison.py** — Load data, run all predictors through harness, print comparison table, save JSON.

See [docs/STATUS.md](docs/STATUS.md) for the full checklist.

---

## How to run

### Baseline comparison (default: synthetic data, no API)

From **repo root**:

```bash
python -m experiments.week_06.experiments.run_baseline_comparison
```

- Uses synthetic data (300 train, 80 val, 100 test) so no external data or API is required.
- Runs: Random, Constant, Length heuristic, Linear regression, NLP+LR, Random Forest.
- Output: table to stdout; `experiments/week_06/evaluation/runs/comparison_latest.json`.

### Optional: real data

- **HuggingFace Hub:** `W6_DATA_SOURCE=hub W6_HUB_DATASET=username/items_lite` (requires `datasets` and hub auth).
- **Local JSONL:** Put `train.jsonl`, `val.jsonl`, `test.jsonl` in `experiments/week_06/data/processed/`, then `W6_DATA_SOURCE=local`.

### Optional: DNN and LLM

- **DNN:** `W6_RUN_DNN=1` (slower; trains a small DNN).
- **Zero-shot LLM:** `W6_RUN_LLM=1` (requires API; uses gpt-4o-mini by default).
- **Fine-tuned:** `W6_FINE_TUNED_MODEL=ft:...` to add fine-tuned model to comparison.

### Eval size

- `W6_EVAL_SIZE=200` to evaluate on more test items (default 100).

---

## What is being evaluated

- **Metrics:** Mean absolute error (MAE), mean squared error (MSE), R² on a held-out test set.
- **Baselines:** Random, constant (train mean), length heuristic, linear regression, NLP+LR, Random Forest, optionally DNN, zero-shot LLM, fine-tuned.
- **Failure modes:** Fine-tuning can regress vs base model; human baseline as reference. See `evaluation/FAILURE_MODES.md`.

All evaluation is **offline**, **deterministic** where possible (fixed seed, same test set), and **auditable** (same harness for every predictor).

---

## Outcomes and lessons

- **Evaluation-first:** One harness for every model; no special-case metrics. Comparison table and saved JSON make results inspectable and reproducible.
- **What worked:** Curation and preprocessing mirror the course; traditional ML and DNN plug in cleanly; LLM and fine-tuned use the same prompt format; synthetic data allows pipeline validation without external deps.
- **What didn’t:** Fine-tuning is not guaranteed to improve over base (course and FAILURE_MODES.md document regression). Synthetic metrics are for pipeline validation only; use real data for real baselines.
- **Portfolio-ready:** Clear structure, no RAG/retrieval, honest failure-mode notes, and a complete regression experimentation pipeline suitable for professional review.
