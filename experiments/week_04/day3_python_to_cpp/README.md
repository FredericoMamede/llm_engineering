# Day 3: Python → C++ Conversion

> **Purpose:** Implement basic Python to C++ code conversion using frontier models and benchmark performance.

---

## Overview

Day 3 focuses on:
- Converting Python code to optimized C++ using frontier models
- System information gathering for compiler optimization
- Performance benchmarking (Python vs C++ execution times)
- Model comparison for code generation quality

---

## Models Tested

- **GPT-5** (OpenAI)
- **Claude Sonnet 4.5** (Anthropic)
- **Grok 4** (x.ai)
- **Gemini 2.5 Pro** (Google)

---

## Files

- `converter.py` - Core conversion logic
- `prompts.py` - Prompt templates for code generation
- `benchmark.py` - Performance benchmarking utilities
- `examples/` - Sample Python code to convert

---

## Usage

```python
from converter import convert_python_to_cpp
from benchmark import benchmark_code

# Convert Python to C++
python_code = """
def calculate(iterations, param1, param2):
    result = 1.0
    for i in range(1, iterations+1):
        j = i * param1 - param2
        result -= (1/j)
    return result
"""

cpp_code = convert_python_to_cpp(
    python_code=python_code,
    model="gpt-5"
)

# Benchmark performance
results = benchmark_code(python_code, cpp_code)
print(f"Speedup: {results['speedup']:.2f}x")
```

---

## Expected Results

Based on course experiments:
- **4th place:** Claude Sonnet 4.5 (~184x speedup)
- **3rd place:** GPT-5 (~233x speedup)
- **2nd place:** Grok 4 (~1060x speedup)
- **1st place:** Gemini 2.5 Pro (~1440x speedup)

*Note: Results vary based on code complexity and system configuration.*

---

## Next Steps

- Move to **Day 4** to add multi-model support and Gradio UI
- Extend to **Day 5** for Rust conversion and advanced benchmarking
