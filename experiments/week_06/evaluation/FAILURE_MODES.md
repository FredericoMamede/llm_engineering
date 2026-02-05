# Failure mode notes (Week 6)

## Fine-tuning can regress vs base model

Course results (`week6/results.ipynb`) show **GPT 4.1 Nano (Fine-tuned)** with higher error (75.91) than **GPT 4.1 Nano** base (62.51). So fine-tuning is not guaranteed to improve; it can hurt.

**Possible causes:**

- Overfitting to small train set (e.g. 100 examples).
- Hyperparameters (epochs, batch size) not tuned for this task.
- Validation set too small or not representative.
- Task format (price-only response) may not benefit from fine-tuning vs zero-shot.

**What to do:**

- Always compare fine-tuned vs base on the **same test set** and report both.
- Document in baseline comparison; do not claim improvement without measured comparison.
- Consider human baseline as reference ceiling.

## Human baseline

Human predictions on a subset (e.g. 100 items) establish an upper bar. Models can beat or underperform. Use as reference only; not a “target” to optimize against.

## Data and cost

- **LITE vs full:** Smaller dataset is cheaper (pre-processing, fine-tuning) but may underrepresent distribution; full is costly.
- **Pre-processing cost:** LLM rewrite per item; batch API has fixed cost. Skipping preprocess and using raw text is a valid tradeoff if budget is tight.
