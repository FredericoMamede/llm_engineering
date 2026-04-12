# Week 7 — Open-Source Fine-Tuning Capstone: "The Price Is Right" (QLoRA)

## Status: **Scaffold complete**

Week 7 extends the price-prediction task from Week 6 by **fine-tuning an open-source model** (e.g. Llama 3.2 3B / Llama 3.1 8B) with **QLoRA** (4-bit quantization + LoRA) for memory-efficient training. Same evaluation harness and metrics (MAE, MSE, R²) as Week 6; new pieces are prompt data prep, training pipeline, and open-source PEFT predictor.

---

## Theme and goals

- **Same task as Week 6:** Predict product price from description (regression).
- **Week 6:** API fine-tuning (OpenAI), traditional ML, DNN, zero-shot LLM.
- **Week 7:** Fine-tune an **open-source** causal LM (e.g. Llama) with **QLoRA**; load base + PEFT adapter; evaluate with the same harness.

**Goals:**

- **Prompt data** — Reuse Week 6 `Item` and prompt format (QUESTION + summary + PREFIX + completion); build SFT dataset for training.
- **QLoRA training** — 4-bit quantization (e.g. BitsAndBytes), LoRA config, SFTTrainer; train on GPU (Colab/A100 or local); save/push adapter to Hub.
- **Open-source predictor** — Load base model (4-bit) + PEFT adapter; predict price from test prompt; plug into Week 6 evaluation harness.
- **Evaluation** — Same MAE, MSE, R² and test set as Week 6; compare base vs fine-tuned open-source.

---

## How this relates to Week 6

| Aspect | Week 6 | Week 7 |
|--------|--------|--------|
| Task | Price from description | Same |
| Data | Item, train/val/test, Hub/local/synthetic | Same; plus SFT prompt/completion dataset |
| Fine-tuning | OpenAI API (closed) | QLoRA on open-source (Llama, etc.) |
| Eval | Harness, MAE, MSE, R² | Same harness and metrics |
| Output | comparison_latest.json | Same; add base vs QLoRA fine-tuned |

Week 7 **reuses** Week 6 curation (Item, loaders) and evaluation (harness, metrics). It adds `training/` (QLoRA config, dataset, train) and `models/open_source_pricer.py` (load base + PEFT, predict).

---

## What is in this repo

- **curation/** — Re-exports Week 6 curation (Item, loaders) so Week 7 can load train/val/test and build prompt data.
- **training/** — QLoRA config, SFT dataset from Items, train script (or Colab-oriented steps); adapter save/push.
- **models/** — Open-source pricer: load base (4-bit) + PEFT adapter, run inference, same interface as Week 6 predictors.
- **evaluation/** — Re-use Week 6 harness and metrics; optional thin wrapper.
- **experiments/** — `run_qlora_train.py` (training entry), `run_eval_opensource.py` (evaluate base + fine-tuned).
- **docs/** — ARCHITECTURE, NOTES, STATUS.

---

## How to run

### 1. Data (same as Week 6)

- **Synthetic:** No external data; use Week 6 synthetic generator.
- **Hub:** `W6_DATA_SOURCE=hub W6_HUB_DATASET=username/items_lite` (or items_full).
- **Local:** Put `train.jsonl`, `val.jsonl`, `test.jsonl` in Week 6 `data/processed/` and use `W6_DATA_SOURCE=local`.

### 2. Build SFT prompt dataset

From repo root, using Week 6 curation and Week 7 training helpers:

```bash
python -m experiments.week_07.training.dataset --data_source synthetic --out_dir experiments/week_07/data/prompts
```

(Implementation in `training/dataset.py` builds prompt/completion from Items.)

### 3. Train (QLoRA)

Training requires a GPU (e.g. Colab T4/A100). Use either:

- **Colab:** Follow course notebooks (Day 3–4); or run a script that mirrors them.
- **Local/script:**  
  `python -m experiments.week_07.experiments.run_qlora_train`  
  (Config: base model, LoRA r/alpha/dropout, max length, batch size, output dir / Hub name.)

Adapters are saved under `training/outputs/` or pushed to HuggingFace Hub.

### 4. Evaluate open-source (base vs fine-tuned)

From repo root:

```bash
python -m experiments.week_07.experiments.run_eval_opensource
```

- Loads base model (4-bit) and optional PEFT adapter.
- Runs both on the same test set through the Week 6 harness.
- Prints MAE, MSE, R² and optionally appends to comparison JSON.

Env (optional): `W7_BASE_MODEL=meta-llama/Llama-3.2-3B`, `W7_ADAPTER=username/run-name`, `W6_DATA_SOURCE=synthetic`, `W6_EVAL_SIZE=100`.

---

## Dependencies

- Week 6 deps (curation, evaluation).
- For training: `torch`, `transformers`, `peft`, `bitsandbytes`, `trl`, `datasets`.
- See `requirements.txt`.

---

## Outcomes and lessons

- **QLoRA** reduces memory so larger models (e.g. 8B) can be fine-tuned on a single GPU.
- **Same prompt format** as Week 6 (and course) keeps evaluation comparable.
- **Base vs fine-tuned:** Course results (e.g. base Llama 3.2 4-bit ~110 MAE, fine-tuned full ~40) show large gains from fine-tuning; document failure modes (overfitting, small data) in FAILURE_MODES.md.
- **Portfolio-ready:** Clear split between data (Week 6), training (Week 7), and evaluation (shared); reproducible and auditable.
