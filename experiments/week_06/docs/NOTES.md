# Week 6 — Analysis Notes (Step 1)

## Source materials analyzed

- **Notebooks:** `week6/day1.ipynb` … `day5.ipynb`, `redemption_train.ipynb`, `redemption_run.ipynb`, `results.ipynb`
- **Code:** `week6/pricer/` (parser, items, batch, preprocessor, evaluator, deep_neural_network, loaders)
- **Data:** Amazon-Reviews-2023 (HuggingFace), train/val/test splits, JSONL for fine-tuning

---

## What problems Week 6 is trying to solve

1. **Predicting a numeric outcome from text** — Estimate product price from description (regression), not retrieval or QA.
2. **Data quality as a lever** — Curation and pre-processing (including LLM rewriting) are framed as high-impact; “R&D with your dataset can often have a greater impact than hyper-parameter optimization.”
3. **Comparable baselines** — Need a single evaluation harness so random, constant, traditional ML, neural nets, zero-shot LLMs, and fine-tuned models can be compared on the same test set and metrics.
4. **Cost and scale** — Pre-processing and fine-tuning have real cost (LITE vs full dataset; 50–100 vs 20k examples); the course makes tradeoffs explicit.
5. **When fine-tuning helps (or doesn’t)** — Course results show fine-tuned GPT-4.1-nano can underperform base model (75.91 vs 62.51 in `results.ipynb`), illustrating a failure mode to document.

---

## Why Week 5 approaches are insufficient

- **Week 5** is RAG: retrieval, chunks, embeddings, ranking, answer generation, retrieval metrics (MRR, nDCG, recall). No regression, no fine-tuning, no traditional ML or DNN.
- **Week 6** is a **regression capstone**: same evaluation rigor (harness, metrics, baselines) but applied to a **different task** (price prediction), with **data curation**, **LLM-based pre-processing**, **traditional ML**, **deep learning**, **zero-shot LLMs**, and **API-based fine-tuning**. No retrieval, no graph, no hybrid search.

---

## New capabilities introduced in Week 6

| Area | Content |
|------|--------|
| **Data curation** | HuggingFace datasets, parsing raw product records, scrubbing (min chars, price range, removals), `Item` schema, train/val/test splits, push/load from Hub. |
| **Pre-processing with LLMs** | Rewriting product text to a standard format (title, category, brand, description, details) via system prompt + completion; batch API (Groq) for scale; LITE vs full. |
| **Evaluation harness** | Single `evaluate(pricer_fn, data, size, workers)`; post-process string → number; metrics: average absolute error, MSE, R²; scatter (truth vs guess), error trend chart with 95% CI; parallel execution. |
| **Baselines** | Random, constant (train average), linear regression (numeric features), NLP + linear regression (CountVectorizer), Random Forest. |
| **Deep learning** | Vanilla NN (notebook) and optional DNN (PyTorch: residual blocks, LayerNorm, log-price target, L1 loss, AdamW, CosineAnnealingLR); HashingVectorizer; train/val loss, MAE. |
| **LLM zero-shot** | “Frontier” models as pricers (GPT-4.1-nano, Claude, etc.) with a fixed user prompt; same `evaluate()` interface. |
| **Fine-tuning** | OpenAI fine-tuning API: JSONL format (messages: user + assistant), file upload, `fine_tuning.jobs.create`, validation set, seed/hyperparameters; retrieve job and fine-tuned model name; inference via same message format. |
| **Failure mode** | Fine-tuned model can regress vs base (documented in `results.ipynb`); human baseline as reference. |

---

## Core technical themes (explicit list)

- Data curation and quality (Day 1)
- LLM-based pre-processing and batch API (Day 2)
- Evaluation-first: harness + baselines before complex models (Day 3)
- Traditional ML: linear regression, bag-of-words, Random Forest (Day 3)
- Deep learning: PyTorch NN, optional DNN with residual blocks (Day 4)
- Frontier LLMs as zero-shot regressors (Day 4)
- API-based fine-tuning (OpenAI): JSONL, train/val, job lifecycle (Day 5)
- Baseline comparison and cost/size tradeoffs (LITE vs full, 100 vs 20k examples)

---

## What Week 6 does *not* cover

- GraphRAG, knowledge graphs, multi-hop reasoning
- Hybrid search, query expansion, reranking of retrieval results
- RAG retrieval or chunk ranking (Week 5 domain)
- Any UI beyond notebook charts (Plotly/Plotly express)

---

## Implications for experiments/week_06 scaffold

- **No** `graph/`, **no** `retrieval/`, **no** `ranking/` — not in Week 6.
- **Include:** `data/`, `curation/` (parse, scrub, Item), `preprocess/` (LLM rewrite, batch), `models/` (traditional ML, DNN, LLM zero-shot, fine-tuned), `evaluation/` (harness, metrics, baseline comparison), `experiments/`, `docs/`.
- **Evaluation is mandatory:** harness, clear metrics (e.g. MAE, MSE, R²), baseline comparison, failure-mode notes (e.g. fine-tuning regression).

---

## Final implementation notes (post full implementation)

### What worked

- **Single harness:** Every predictor (random, constant, heuristic, linear, NLP+LR, RF, DNN, LLM zero-shot, fine-tuned) uses the same `evaluate(predictor, data, size)` and post_process; metrics are comparable.
- **Data sources:** Synthetic data lets the pipeline run without HuggingFace or local files; Hub and local JSONL are supported for real data.
- **Curation:** Parser and scrub mirror course logic; Item is serializable for train/val/test and optional Hub push.
- **Preprocessing toggle:** `use_preprocessing=False` avoids LLM cost when not needed; cost/token tracking when ON.
- **Traditional ML:** Linear regression (numeric + text) and Random Forest (bag-of-words) match course Day 3; subset/size limits keep runs fast.
- **DNN:** Smaller config (num_layers, hidden_size) by default to reduce overfitting and training time; full course-style DNN available with larger params.
- **LLM and fine-tuning:** Same prompt format at inference; JSONL helper for fine-tuning; failure-mode doc (fine-tuning can regress) is explicit.

### What didn’t / tradeoffs

- **Fine-tuning:** Course showed fine-tuned model can be worse than base (results.ipynb); we document this and do not claim improvement without measured comparison.
- **Synthetic data:** Metrics on synthetic data are not meaningful for real performance; they validate the pipeline only. Use Hub or local data for real baselines.
- **DNN/LLM off by default:** Comparison script skips DNN and LLM unless `W6_RUN_DNN=1` / `W6_RUN_LLM=1` to avoid slow or API-dependent runs by default.
- **No UI:** No dashboards or charts in this repo; course used Plotly in notebooks. Harness returns truths/predictions for optional external plotting.

### Evaluation-first methodology

- Baselines are defined and evaluated before adding complex models.
- Same test set and metrics for every model; no cherry-picking.
- Failure modes (fine-tuning regression, cost) are documented, not hidden.
- Reproducibility: seed for synthetic/splits; deterministic metrics; comparison artifact (JSON) saved.
