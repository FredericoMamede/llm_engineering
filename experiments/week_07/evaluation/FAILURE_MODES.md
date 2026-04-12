# Week 7 — Failure Modes and Tradeoffs

## Base vs fine-tuned

- **Base (4-bit) only:** Often high error (e.g. course ~110 MAE for Llama 3.2 4-bit) because the model was not trained for price prediction.
- **Fine-tuned (base + PEFT):** Can greatly reduce error (e.g. course fine-tuned full ~40 MAE) but is not guaranteed to improve over every baseline; document results on the same test set.

## Overfitting

- Small train set or many epochs can overfit; validation loss should be monitored.
- Use same test set for final comparison; avoid tuning on test.

## Regression vs base

- In some setups (e.g. wrong hyperparameters, too few examples), fine-tuned model can be **worse** than base. Always report both base and fine-tuned on the same test set.

## Resource and cost

- **QLoRA** reduces memory but 8B models still need substantial GPU (e.g. A100 or high-end consumer); 3B fits on T4.
- **LITE vs full dataset:** Full (e.g. 400K) gives better results but longer training and more GPU time.

## Human baseline

- Course uses human (e.g. "Ed") as a reference; models can beat or underperform. Report human baseline when available.
