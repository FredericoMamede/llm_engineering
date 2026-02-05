# Models (Days 3–5)

**Role:** Predictors that take an `Item` (or summary) and return a price (or string parsed to number). All use the same evaluation harness.

**Course reference:** `week6/day3.ipynb`, `day4.ipynb`, `day5.ipynb`, `week6/pricer/evaluator.py`, `week6/pricer/deep_neural_network.py`.

**Categories:**

1. **Baselines (Day 3)** — Random, constant (train mean), linear regression (numeric features: weight, text_length), NLP + linear regression (CountVectorizer), Random Forest.
2. **Deep learning (Day 4)** — Vanilla NN (notebook) or DNN (PyTorch: residual blocks, LayerNorm, log-price, L1 loss); HashingVectorizer; train/val loop, MAE.
3. **LLM zero-shot (Day 4)** — Frontier model (e.g. GPT-4.1-nano, Claude) with fixed user prompt: “Estimate the price… Respond with the price, no explanation”; response post-processed to number.
4. **Fine-tuned (Day 5)** — OpenAI (or equivalent) fine-tuning: JSONL (user + assistant messages per item), train/validation files, job create/retrieve, inference with fine-tuned model name; same prompt format at inference.

**Interface:** Each predictor is a function `(item) -> number or string`; evaluator post-processes string to number (e.g. regex for first number).
