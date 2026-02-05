# Experiments

**Role:** Runner scripts and comparison notebooks for baseline runs and ablations.

**Suggested use:**

- Script: load data (train/val/test), run each baseline through the evaluation harness, record metrics, write comparison report (e.g. `evaluation/runs/comparison_YYYYMMDD.json` or `.md`).
- Notebook: same flow for interactive runs; optional plots (bar chart of MAE by model).
- No demo-only code; no fake metrics. Prefer correctness over completeness.

**Outputs:** Prefer under `evaluation/runs/` or `experiments/outputs/` (gitignored).
