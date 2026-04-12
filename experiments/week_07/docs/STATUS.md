# Week 7 — Status

## Explicit checklist

### Implemented (scaffold)

- [x] **Scaffold and docs** — Directory structure, README, ARCHITECTURE, NOTES, STATUS.
- [x] **Curation** — Re-export Week 6 curation (Item, loaders) for train/val/test and prompt data.
- [x] **Training** — Config (QLoRA, base model, paths), dataset builder (prompt/completion from Items), train script stub / Colab instructions.
- [x] **Models** — Open-source pricer: load base (4-bit) + PEFT adapter, predict; interface compatible with Week 6 harness.
- [x] **Evaluation** — Re-use Week 6 harness and metrics; optional wrapper in week_07.evaluation.
- [x] **Experiments** — run_qlora_train.py, run_eval_opensource.py; README for how to run.

### In progress

- [ ] None (scaffold only).

### Not yet started (optional)

- [ ] **Full training pipeline** — End-to-end SFTTrainer run with real GPU (Colab or local); push adapter to Hub.
- [ ] **FAILURE_MODES.md** — Document overfitting, small-data regression, base vs fine-tuned.
- [ ] **Comparison JSON** — Append base vs QLoRA fine-tuned to same comparison artifact as Week 6.

Scaffold is complete; training and eval scripts are stubbed so that running with real data and GPU is a matter of filling config and executing.
