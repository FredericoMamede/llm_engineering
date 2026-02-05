# Curation (Day 1)

**Role:** Parse raw product data, scrub (min chars, price range, removals), produce `Item` objects; train/val/test split; optional Hub push/load.

**Course reference:** `week6/day1.ipynb`, `week6/pricer/parser.py`, `week6/pricer/items.py`.

**Concepts:**

- Load dataset (e.g. HuggingFace Amazon-Reviews-2023).
- Parse each record: price in range (e.g. $0.50–$999.49), min text length, scrub details (remove part numbers, best sellers rank, etc.), extract weight.
- Emit `Item`: title, category, price, full (scrubbed text), weight, summary (filled later by preprocess).
- Split into train/val/test (fixed seed for reproducibility).
- Optionally push/load from HuggingFace Hub.

**Output:** Lists of `Item` (train, val, test) or files under `data/processed/` / `data/eval_sets/`.
