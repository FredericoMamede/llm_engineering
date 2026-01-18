# Week 4: Model Evaluation & Code Generation Engineering

> **Theme:** Choosing, evaluating, and operationalizing LLMs for code generation under real constraints (performance, cost, latency, benchmarks, and business tradeoffs)

---

## Week Structure

**Days 1-2: Theory & Judgment** (No code)
- Day 1: Model Selection Foundations
- Day 2: Commercial & Product Thinking

**Days 3-5: Experiments & Implementation**
- Day 3: Python → C++ Conversion (Frontier Models)
- Day 4: Multi-Model Comparison + Gradio UI
- Day 5: Rust Conversion + Advanced Benchmarking

---

## Learning Objectives

By the end of this week, you will:

1. **Understand model selection criteria** beyond benchmarks
2. **Apply Chinchilla Scaling Law** to evaluate model efficiency
3. **Critically assess benchmarks** and their limitations
4. **Recognize commercial LLM progression** (automate → augment → differentiate)
5. **Implement multi-provider code generation** systems
6. **Benchmark and compare models** on real-world code translation tasks
7. **Build interactive UIs** for model evaluation

---

## Key Concepts

### Model Evaluation
- Model properties vs operational properties
- Chinchilla Scaling Law implications
- Benchmark types and their limitations
- Human evaluation (LM Arena, ELO scoring)

### Code Generation Engineering
- System information gathering for optimization
- Multi-provider architecture (OpenAI, Anthropic, Google, Grok, Groq, Ollama, OpenRouter)
- Performance benchmarking (Python vs compiled languages)
- Compiler optimization flags
- Interactive evaluation interfaces

### Commercial Thinking
- Automate: Wrappers and copilots
- Augment: Specialized domain tools
- Differentiate: Agentic systems with tool use

---

## Folder Structure

```
week_04/
├── day1_model_selection/     # Theory: Model comparison foundations
├── day2_commercial_llms/     # Theory: Commercial progression
├── core/                     # Shared utilities
├── day3_python_to_cpp/       # Experiments: Basic C++ conversion
├── day4_multi_model_ui/      # Experiments: Multi-model + UI
├── day5_rust_conversion/     # Experiments: Rust + benchmarking
└── outputs/                  # Generated code and results
```

---

## Important Notes

- **Days 1-2 are theory-only** — no code, no notebooks, just understanding
- **Days 3-5 are experimental** — hands-on implementation and evaluation
- **Week 4 is evaluation-focused** — not about building products, but about choosing the right model
- **No mini-projects, agents, or RAG** — keep scope focused on code generation quality

---

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure API keys in `.env`:
   ```
   OPENAI_API_KEY=...
   ANTHROPIC_API_KEY=...
   GOOGLE_API_KEY=...
   GROK_API_KEY=...
   GROQ_API_KEY=...
   OPENROUTER_API_KEY=...
   ```

3. (Optional) Install C++ compiler and/or Rust toolchain for code execution

---

## Model Evaluation: Technical vs Business Metrics

By Day 5, we can meaningfully evaluate models along two dimensions:

### Model-Centric (Technical) Metrics
- Compilation success rate
- Correctness of translated code
- Runtime performance (execution time)
- Memory usage
- Benchmark comparisons across models

These metrics are:
- Easier to measure
- Easier to optimize
- Necessary but not sufficient

### Business-Centric (Outcome) Metrics
- Developer time saved
- Reliability of generated code
- Reduction in debugging effort
- Consistency across runs
- Practical usability in workflows

These metrics are:
- Harder to quantify
- More subjective
- Ultimately more important

**Engineering takeaway:**  
A model that wins benchmarks but produces brittle or unreadable code may be worse in practice than a slower, more reliable model.

This distinction explains why Day 5 focuses on *comparative evaluation*, not just performance optimization.

---

## Next Steps

1. Start with **Day 1** — read and understand model selection foundations
2. Continue to **Day 2** — internalize commercial LLM thinking
3. Begin **Day 3** — implement basic Python → C++ conversion
4. Extend to **Day 4** — add multi-model support and UI
5. Complete **Day 5** — add Rust support and advanced benchmarking
