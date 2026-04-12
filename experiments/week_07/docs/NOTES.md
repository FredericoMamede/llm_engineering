# Week 7 — Analysis Notes

## Source materials analyzed

- **Notebooks:** `week7/day1.ipynb` … `day5.ipynb`, `results.ipynb` (Colab links in repo).
- **Course flow:** Day 1 QLoRA; Day 2 prompt data and base model; Day 3–4 train; Day 5 eval.
- **Code:** `week7/pricer/items.py`, `pricer/evaluator.py`, `util.py`.
- **Community:** Various QLoRA/SFT scripts (Llama 3.1 8B, Llama 3.2 3B, OPT-125M, Gemma; PEFT, trl SFTTrainer, BitsAndBytes 4-bit).

---

## What Week 7 is trying to solve

1. **Fine-tune an open-source model** for the same task as Week 6 (price from description), without using the OpenAI fine-tuning API.
2. **Memory-efficient training** — QLoRA (4-bit quantization + LoRA) so 3B–8B models fit on a single GPU (e.g. T4, A100).
3. **Same evaluation** — Reuse Week 6 harness and metrics so base vs fine-tuned is comparable.
4. **Prompt format** — Align with course: QUESTION + summary + PREFIX + completion (rounded price string).

---

## How Week 7 relates to Week 6

- **Week 6:** Curation, preprocess, baselines, DNN, zero-shot LLM, **OpenAI fine-tuned**; evaluation harness.
- **Week 7:** Same task and eval; **open-source** base model + **QLoRA fine-tuning**; load base + PEFT adapter; predictor plugs into same harness.

No retrieval, no RAG; same regression and comparison methodology.

---

## New capabilities (Week 7)

| Area | Content |
|------|---------|
| **Prompt data** | Build SFT dataset from Items: prompt = QUESTION + text + PREFIX; completion = price string; optional tokenizer truncation. |
| **QLoRA** | 4-bit quantization (BitsAndBytes), LoRA (PEFT); LoraConfig (r, alpha, dropout, target_modules). |
| **Training** | SFTTrainer (trl); train on prompt+completion; save adapter / push to Hub. |
| **Inference** | Load base (4-bit) + PeftModel.from_pretrained(adapter); generate short completion; post_process to float. |
| **Comparison** | Base (4-bit) vs fine-tuned on same test set; course: base Llama 3.2 4-bit ~110 MAE, fine-tuned full ~40. |

---

## Core technical themes

- QLoRA and 4-bit quantization (Day 1).
- Prompt data and base model choice (Day 2).
- SFT training with PEFT (Day 3–4).
- Evaluation of base vs fine-tuned (Day 5).
- Same Item and eval as Week 6; no new retrieval or RAG.

---

## Implications for experiments/week_07

- **Reuse:** Week 6 curation (Item, loaders), Week 6 evaluation (harness, metrics).
- **Add:** `training/` (config, dataset builder, train script), `models/open_source_pricer.py` (load base + PEFT, predict), experiments to run train and eval.
- **Optional:** Colab-oriented instructions or notebook stubs that point to course Colab links.
- **Document:** Failure modes (overfitting, small data, base vs fine-tuned regression) in FAILURE_MODES.md.
