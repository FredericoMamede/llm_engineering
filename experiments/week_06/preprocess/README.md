# Preprocess (Day 2)

**Role:** Rewrite product text to a standard format (title, category, brand, description, details) via LLM; optional batch API for scale.

**Course reference:** `week6/day2.ipynb`, `week6/pricer/batch.py`, `week6/pricer/preprocessor.py`.

**Concepts:**

- System prompt: fixed format (Title, Category, Brand, Description, Details); no part numbers.
- User message: `Item.full` (or raw text).
- Single-call preprocess: one completion per item; track tokens/cost.
- Batch: write JSONL (custom_id, body with model/messages), upload, submit batch, poll, fetch output, apply to items (update `summary`).
- LITE vs full: smaller vs larger dataset for cost control.

**Output:** Items with `summary` (rewritten) populated; optionally saved back to `data/processed/` or Hub.
