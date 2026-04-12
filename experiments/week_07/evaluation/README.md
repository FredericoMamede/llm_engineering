# Week 7 — Evaluation

Week 7 reuses **Week 6 evaluation** so base and QLoRA fine-tuned models are compared on the same test set and metrics (MAE, MSE, R²).

- **Harness:** `evaluate(predictor, data, size)` — same interface; predictor(item) returns price; post_process to float.
- **Metrics:** MAE, MSE, R² from `experiments.week_06.evaluation.metrics`.

This package re-exports Week 6 evaluation. Open-source predictor (base or base+PEFT) plugs in like any Week 6 predictor.
