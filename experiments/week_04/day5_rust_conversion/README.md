# Day 5: Rust Conversion + Advanced Benchmarking

> **Purpose:** Extend code conversion to Rust, add advanced benchmarking, and create an enhanced UI with side-by-side execution.

---

## Overview

Day 5 extends Day 4 with:
- Rust code conversion (in addition to C++)
- Language selection (C++ or Rust)
- Enhanced UI with run buttons for both languages
- Advanced benchmarking and performance analysis
- Complex Python examples (LCG, max subarray sum)

---

## Features

### Language Support
- **C++** (from Day 3-4)
- **Rust** (new in Day 5)

### Enhanced UI
- Side-by-side code editors
- Run buttons for Python, C++, and Rust
- Real-time output comparison
- Performance metrics display

### Advanced Examples
- **LCG (Linear Congruential Generator)** - Random number generation
- **Max Subarray Sum** - Algorithm optimization
- **Complex nested loops** - Performance-critical code

---

## Files

- `converter.py` - Multi-language converter (C++/Rust)
- `ui.py` - Enhanced UI with language selection
- `benchmarks/` - Performance results and analysis

---

## Usage

### Command Line

```python
from converter import convert_python_to_language

# Convert to C++
cpp_code = convert_python_to_language(
    python_code=python_code,
    target_language="C++",
    model="gpt-5"
)

# Convert to Rust
rust_code = convert_python_to_language(
    python_code=python_code,
    target_language="Rust",
    model="gpt-5"
)
```

### Gradio UI

```bash
python ui.py
```

---

## Expected Results

Based on course experiments (complex LCG example):

- **Failed:** Qwen 2.5 Coder, Gemini 2.5 Pro, DeepSeek Coder v2, Qwen3 Coder 30B, Claude Sonnet 4.5, GPT-5
- **3rd place:** GPT-OSS 20B (~99,000x speedup)
- **2nd place:** Grok 4 (~106,000x speedup)
- **1st place:** OpenAI GPT-OSS 120B (~111,000x speedup)

*Note: Complex examples reveal significant differences in model capabilities.*

---

## Next Steps

- Extend to other languages (Go, TypeScript, etc.)
- Add more complex examples
- Build automated benchmarking suite
- Create model recommendation system
