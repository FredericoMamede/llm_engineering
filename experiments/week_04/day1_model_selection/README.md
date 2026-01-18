# Day 1: Model Selection Foundations

> **Purpose:** Understand how to compare, evaluate, and choose LLMs for production use. This is a **theory-only day** — no code, no experiments.

---

## Core Concepts

### 1. How to Compare LLMs

LLMs must be evaluated along multiple axes:

#### Model Properties
- **Open-source vs closed-source**
- **Chat vs reasoning vs hybrid** architectures
- **Release date & knowledge cutoff**
- **Parameter count** (3B, 7B, 70B, etc.)
- **Training tokens** (data volume)
- **Context window** (input/output limits)

#### Operational Properties
- **Inference cost** (API pricing vs compute)
- **Training cost** (one-time investment)
- **Build cost** (infrastructure)
- **Time to market** (availability)
- **Rate limits** (throughput constraints)
- **Speed** (tokens/second)
- **Latency** (response time)
- **License** (commercial use restrictions)

**Key Insight:** There is no single "best" model — only the *best model for your specific constraints*.

---

### 2. Chinchilla Scaling Law

> **Optimal performance occurs when model size is proportional to training tokens.**

#### Implications

- **Bigger model ≠ better** if under-trained
- **Doubling parameters** requires ~2× training data
- **Small, well-trained models** can outperform larger ones
- **Over-scaling without data** = diminishing returns

#### Why This Matters

- Explains why **3B–8B models** can be competitive
- Explains why **frontier models** are expensive
- Explains why **open-source models** are improving rapidly
- Guides **cost-performance tradeoffs** in production

---

### 3. Benchmarks You Must Know (and Their Limits)

#### Key Benchmarks

- **GPQA** — PhD-level science questions
- **MMLU-Pro** — advanced language understanding
- **AIME** — math competition problems
- **LiveCodeBench** — real-world coding tasks
- **MuSR** — long-form reasoning
- **HLE** — extreme academic evaluation

#### Why Benchmarks Are Flawed

1. **Training data contamination** — models may have seen test data
2. **Inconsistent application** — different evaluation methods
3. **Narrow scope** — don't capture nuanced reasoning
4. **Poor measurement** — miss real-world performance
5. **Saturation & overfitting** — models optimize for benchmarks
6. **Evaluation awareness** — models may "know" they're being tested

**Engineering Takeaway:** Benchmarks guide selection — they do **NOT** replace real testing.

---

## What You Should Learn Today

After reading the notes, you should be able to:

1. **Compare models** along multiple axes
2. **Apply Chinchilla Law** to evaluate efficiency
3. **Critically assess benchmarks** before trusting them
4. **Make informed decisions** about model selection for specific use cases

---

## Next Steps

1. Read `notes.md` for detailed explanations and examples
2. Reflect on how you would choose a model for a production system
3. Move to **Day 2** to understand commercial LLM thinking

---

**Remember:** This is a judgment day. Internalize the concepts — code comes later.
