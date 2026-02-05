# Week 6 — System Architecture

## System diagram (described in text)

```
[Raw product data] → [Curation] → [Items: train/val/test]
        ↓
[Preprocess (optional)] → [LLM rewrite / batch] → [Updated summaries]
        ↓
[Models] ← traditional ML, DNN, LLM zero-shot, fine-tuned
        ↓
[Evaluation harness] → [Metrics: MAE, MSE, R²] → [Baseline comparison]
```

- **Curation:** Parse raw records (e.g. Amazon-style), scrub (min chars, price range, removals), produce `Item` objects; split into train/val/test; optionally push/load from HuggingFace Hub.
- **Preprocess:** Rewrite product text to a standard format (title, category, brand, description, details) via LLM; optionally batch API for scale; output updates `Item.summary` (or equivalent).
- **Models:** Predictors that take an `Item` (or summary) and return a price (or string parsed to number). Categories: random/constant, traditional ML (linear, RF), DNN (PyTorch), LLM zero-shot, fine-tuned (OpenAI API).
- **Evaluation:** Single harness: run predictor on test set, post-process output to number, compute MAE, MSE, R²; optionally scatter (truth vs guess), error trend chart; same test set and metrics for every baseline.

## Data flow

1. **Raw → Curation:** Raw product records (e.g. HuggingFace dataset) → parser + scrub → list of `Item` (title, category, price, full, weight, summary, …) with train/val/test split.
2. **Curation → Preprocess:** Items with `full` (raw text) → LLM rewrite → `summary` (standard format). Batch API used for large datasets.
3. **Preprocess → Models:** Items with `summary` (and optionally other features) → each model type (traditional ML, DNN, LLM, fine-tuned) produces a price prediction.
4. **Models → Evaluation:** Each predictor is run on the same test set; harness post-processes (e.g. string → float), aggregates errors, reports MAE, MSE, R²; baseline comparison table/chart.

## Where evaluation occurs

- **Offline, after curation and preprocess.** Test set is fixed (or regenerated with fixed seed). No evaluation inside training; validation used only for model selection / early stopping where applicable.
- **Harness:** One entry point (e.g. `evaluate(predictor_fn, test_data, size, workers)`). Same interface for random, constant, sklearn, PyTorch, LLM, fine-tuned.
- **Baseline comparison:** Run harness for each baseline; record metrics; compare (e.g. bar chart or table). Failure mode: fine-tuned model can regress vs base; document in comparison.

## Tradeoffs discussed in the course

| Tradeoff | Description |
|----------|-------------|
| **LITE vs full dataset** | LITE: smaller, cheaper pre-processing; full: more data, higher cost (e.g. ~$30 for pre-processing). |
| **Fine-tuning size** | 50–100 examples (OpenAI recommendation) vs 20k: cost vs performance; small examples can still improve with 1 epoch. |
| **Pre-processing cost** | LLM rewrite per item; batch API reduces latency but has fixed cost; skip and use raw text if budget is tight. |
| **Human baseline** | Human predictions on a subset establish an upper bar; models can beat or underperform. |
| **Fine-tuning regression** | Fine-tuned model can be worse than base (e.g. overfitting, wrong hyperparameters); always compare on same test set. |
