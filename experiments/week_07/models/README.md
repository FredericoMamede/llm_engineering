# Week 7 — Models

## Open-source pricer

- **open_source_pricer.py:** Load base causal LM (e.g. Llama 3.2 3B) in 4-bit and optional PEFT adapter; expose a callable `predictor(item)` that returns predicted price.
- **Interface:** Same as Week 6: predictor receives an object with `.test_prompt()` (or `.prompt` up to PREFIX) and `.price`; harness post_processes output to float.
- **Usage:** `predictor = open_source_pricer("meta-llama/Llama-3.2-3B", adapter_path_or_id="username/run-name")` then `evaluate(predictor, test_data, size=100)` (Week 6 harness).

## Dependencies

- torch, transformers, peft; for 4-bit: bitsandbytes
