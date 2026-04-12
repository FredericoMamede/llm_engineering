# Week 7 — System Architecture

## System diagram (described in text)

```
[Raw product data] → [Curation — Week 6] → [Items: train/val/test]
        ↓
[Prompt data builder] → [prompt + completion per Item] → [SFT dataset]
        ↓
[Base model 4-bit] + [QLoRA (LoRA + 4-bit quant)] → [SFTTrainer] → [Adapter]
        ↓
[Load base + PEFT adapter] → [Open-source predictor] → [Evaluation harness — Week 6]
        ↓
[Metrics: MAE, MSE, R²] → [Base vs fine-tuned comparison]
```

- **Curation:** Reuse Week 6: Item schema, loaders (Hub / local / synthetic), train/val/test.
- **Prompt data:** For each Item, build prompt = QUESTION + summary (or full) + PREFIX; completion = rounded price string. Same format as course (Week 7 Day 2).
- **Training:** Load base causal LM in 4-bit (BitsAndBytes); apply LoRA (PEFT); SFTTrainer on prompt+completion; save/push adapter.
- **Open-source predictor:** Load base (4-bit) + PEFT adapter; for each test item, run test_prompt → model.generate → post_process to float; same interface as Week 6 predictors.
- **Evaluation:** Reuse Week 6 harness and metrics; compare base vs fine-tuned on same test set.

## Data flow

1. **Data:** Same as Week 6 — Hub, local JSONL, or synthetic → train/val/test lists of Item.
2. **SFT dataset:** Items → prompt/completion pairs (QUESTION + text + PREFIX / completion); optional truncation by max_tokens; HuggingFace Dataset or JSONL.
3. **Train:** Base model (e.g. Llama 3.2 3B) 4-bit + LoRA → SFTTrainer → adapter on disk or Hub.
4. **Eval:** Load base and (optionally) adapter; run open_source_pricer on test set; harness returns MAE, MSE, R²; append to comparison.

## Where evaluation occurs

- **Offline,** after training. Same test set and metrics as Week 6.
- **Harness:** Week 6 `evaluate(predictor, data, size)`; predictor(item) returns price (number or string); post_process to float.
- **Comparison:** Base (4-bit) vs fine-tuned (base + PEFT); document regression/overfitting in FAILURE_MODES.md.

## Tradeoffs (course Week 7)

| Tradeoff | Description |
|----------|-------------|
| **LITE vs full** | Fewer vs more training examples; full (e.g. 400K) needs more GPU time and memory. |
| **4-bit vs fp16** | 4-bit (QLoRA) saves memory; slight quality tradeoff; required for 8B on single consumer GPU. |
| **LoRA r/alpha** | Larger r = more capacity, more memory; course uses r=8–32, alpha=16–64. |
| **Base model size** | 3B fits T4; 8B typically needs A100 or 4-bit + LoRA on high-end consumer GPU. |
