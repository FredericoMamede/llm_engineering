# Day 1 Notes: Model Selection Foundations

## Model Comparison Framework

### Model Properties Table

| Property | Examples | Impact |
|----------|----------|--------|
| **Open vs Closed** | Llama (open) vs GPT-4 (closed) | Control, cost, customization |
| **Architecture** | Chat-only, reasoning, hybrid | Capability, latency, cost |
| **Parameters** | 3B, 7B, 70B, 175B+ | Capability, memory, cost |
| **Training Tokens** | 1T, 2T, 10T+ | Quality, knowledge depth |
| **Context Window** | 4K, 8K, 32K, 128K, 1M+ | Use case scope, cost |
| **Knowledge Cutoff** | 2023-04, 2024-01, 2024-12 | Recency, accuracy |

### Operational Properties Table

| Property | Examples | Impact |
|----------|----------|--------|
| **Inference Cost** | $0.01/1K tokens, $0.50/1K tokens | Budget, scalability |
| **Speed** | 10 tok/s, 100 tok/s, 1000 tok/s | UX, throughput |
| **Latency** | 50ms, 500ms, 5s | Real-time requirements |
| **Rate Limits** | 10 req/min, 1000 req/min | Throughput limits |
| **License** | Apache 2.0, MIT, Proprietary | Commercial use, restrictions |

---

## Chinchilla Scaling Law Explained

### The Law

> For a given compute budget, optimal performance is achieved when:
> 
> **Model Parameters ≈ Training Tokens / 20**

### Practical Implications

**Example 1: Under-trained Model**
- 70B parameter model trained on 1T tokens
- Chinchilla suggests: 70B needs ~1.4T tokens
- **Result:** Model underperforms for its size

**Example 2: Well-trained Model**
- 7B parameter model trained on 1.4T tokens
- Chinchilla suggests: 7B needs ~140B tokens
- **Result:** Model may outperform larger, under-trained models

**Example 3: Cost-Performance Tradeoff**
- Small model (3B) + large dataset (600B tokens) = efficient
- Large model (70B) + small dataset (1T tokens) = inefficient
- **Decision:** Choose based on compute budget and latency requirements

### Why This Matters for Engineers

1. **Don't assume bigger = better**
2. **Check training data volume** before selecting
3. **Small models can be competitive** if well-trained
4. **Frontier models are expensive** because they're optimally scaled
5. **Open-source models are catching up** as training improves

---

## Benchmarks: What They Measure

### Benchmark Categories

#### 1. General Knowledge
- **MMLU** (Massive Multitask Language Understanding)
  - 57 tasks across STEM, humanities, social sciences
  - **Limitation:** Academic focus, may not reflect real-world use

#### 2. Reasoning
- **GPQA** (Graduate-Level Google-Proof Q&A)
  - PhD-level science questions
  - **Limitation:** Very narrow domain

- **AIME** (American Invitational Mathematics Examination)
  - Competition-level math problems
  - **Limitation:** Math-specific, may not generalize

#### 3. Coding
- **LiveCodeBench**
  - Real-world coding tasks
  - **Limitation:** May not capture production code quality

#### 4. Long-Form Reasoning
- **MuSR** (Multi-step Reasoning)
  - Complex, multi-step problems
  - **Limitation:** Evaluation is subjective

#### 5. Extreme Evaluation
- **HLE** (Hard Long-form Evaluation)
  - Academic-level challenges
  - **Limitation:** May not reflect practical use

---

## Limitations of Benchmarks

### 1. Training Data Contamination

**Problem:** Models may have seen test data during training.

**Example:**
- Benchmark released in 2023
- Model trained on data up to 2024
- Model may have memorized answers

**Solution:** Use benchmarks released after model training cutoff.

---

### 2. Inconsistent Application

**Problem:** Different evaluators use different methods.

**Example:**
- Some use exact match
- Others use semantic similarity
- Results aren't comparable

**Solution:** Standardize evaluation methodology.

---

### 3. Narrow Scope

**Problem:** Benchmarks test specific skills, not real-world performance.

**Example:**
- Model scores 90% on MMLU
- Fails on domain-specific tasks
- Benchmark doesn't predict production performance

**Solution:** Test on your actual use case.

---

### 4. Saturation & Overfitting

**Problem:** Models optimize for benchmark performance.

**Example:**
- Model trained specifically for MMLU
- Scores high on MMLU
- Performs poorly on other tasks

**Solution:** Use diverse benchmarks, not just one.

---

### 5. Evaluation Awareness

**Problem:** Models may "know" they're being evaluated.

**Example:**
- Model performs better in benchmark setting
- Performance drops in production
- Different context affects behavior

**Solution:** Test in production-like conditions.

---

## How I Would Choose a Model in Production

### Step 1: Define Constraints

- **Budget:** $X per month
- **Latency:** <Y ms required
- **Throughput:** Z requests/second
- **Use case:** Specific domain/task

### Step 2: Filter by Constraints

- **Eliminate models** that don't meet hard constraints
- **Consider cost** at required throughput
- **Check rate limits** against needs

### Step 3: Evaluate on Real Tasks

- **Don't rely solely on benchmarks**
- **Test on your actual data**
- **Measure real-world performance**

### Step 4: Consider Tradeoffs

- **Open-source vs closed:** Control vs convenience
- **Size vs speed:** Capability vs latency
- **Cost vs quality:** Budget vs performance

### Step 5: Make Decision

- **Choose model** that best fits constraints
- **Plan for scaling** and alternatives
- **Monitor performance** in production

---

## Key Takeaways

1. **No single best model** — only best for your constraints
2. **Chinchilla Law matters** — check training data volume
3. **Benchmarks are guides** — not definitive answers
4. **Test on real tasks** — don't trust benchmarks alone
5. **Consider all axes** — model properties + operational properties

---

## Reflection Questions

1. If you needed a model for real-time chat, what properties matter most?
2. If you needed a model for batch processing, what changes?
3. How would you evaluate a model for code generation specifically?
4. What benchmarks would you trust for your use case?
5. How does Chinchilla Law affect your model selection?

---

**Next:** Move to Day 2 to understand commercial LLM progression and product thinking.
