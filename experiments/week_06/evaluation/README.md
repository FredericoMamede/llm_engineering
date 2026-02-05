# Evaluation

**Role:** Single harness for all predictors; clear metrics; baseline comparison; failure-mode notes.

**Course reference:** `week6/pricer/evaluator.py`, `week6/day3.ipynb`–`day5.ipynb`, `week6/results.ipynb`.

**Requirements:**

- **Harness:** One entry point, e.g. `evaluate(predictor_fn, test_data, size=DEFAULT_SIZE, workers=WORKERS)`. Run predictor on each test item; post-process output (string → float); collect errors.
- **Metrics:** Mean absolute error (MAE), mean squared error (MSE), R² on the evaluated subset. Optional: scatter (truth vs guess), error trend chart with 95% CI.
- **Baseline comparison:** Run harness for random, constant, linear, RF, DNN, LLM zero-shot, fine-tuned; record MAE (and optionally MSE, R²); table or bar chart; same test set for all.
- **Failure mode notes:** Fine-tuned model can regress vs base model (e.g. overfitting, small data); human baseline as reference. Document in comparison report.

**Placeholder:** Implement `evaluate()` and a small runner that runs all baselines and writes a comparison artifact (e.g. JSON or markdown) under `evaluation/runs/` or `experiments/outputs/`.
