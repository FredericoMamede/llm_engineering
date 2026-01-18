# Day 2: Commercial & Product Thinking

> **Purpose:** Understand how LLMs are used in commercial products and why this matters for engineering decisions. This is a **theory-only day** — no code, no experiments.

---

## Core Concepts

### 1. Commercial Progression of LLM Products

Commercial LLM applications evolve through three distinct stages:

#### Stage 1: Automate
**What it is:**
- ChatGPT wrappers
- Copilots and assistants
- Thin UX layers over LLMs

**Characteristics:**
- Minimal customization
- Generic prompts
- Direct API integration
- Low differentiation

**Examples:**
- Early ChatGPT integrations
- Basic AI assistants
- Simple chatbots

**Why it matters:**
- Fast to market
- Low technical barrier
- **But:** Fragile business model (easily replicated)

---

#### Stage 2: Augment
**What it is:**
- Specialized domain tools
- Workflow-aware systems
- Constrained, focused applications

**Characteristics:**
- Domain-specific prompts
- Integration with existing tools
- Context-aware behavior
- Improved reliability

**Examples:**
- **Harvey** (legal AI)
- **Nebula.io** (healthcare)
- **Salesforce Health** (CRM + AI)

**Why it matters:**
- Higher value proposition
- Better user experience
- **But:** Requires domain expertise

---

#### Stage 3: Differentiate
**What it is:**
- Agentic systems
- Tool use and function calling
- Long-lived context
- Autonomous workflows

**Characteristics:**
- Multi-step reasoning
- External tool integration
- Persistent memory
- Complex orchestration

**Examples:**
- **Claude Code** (coding agent)
- **OpenAI Codex** (code generation)
- **OpenAI Agent** (autonomous agents)

**Why it matters:**
- Highest value creation
- Significant technical moat
- **But:** Complex to build and maintain

---

### 2. LM Arena & Human Evaluations

#### LM Arena (LMSYS)

**What it is:**
- Blind human head-to-head evaluation
- ELO-style scoring system
- Frontier + open-source models side-by-side

**How it works:**
1. Users compare two model outputs
2. Vote on which is better
3. ELO scores calculated from votes
4. Rankings updated continuously

**Why it matters:**
- **Human preference ≠ benchmark score**
- Reveals UX and reasoning quality
- Helps spot overfitting to benchmarks
- Real-world performance indicator

**Key insight:**
- Models that score well on benchmarks may rank lower in human preference
- Models that rank high in human preference may have lower benchmark scores
- **Both matter** — benchmarks for capability, human eval for UX

---

## What You Should Learn Today

After reading the notes, you should be able to:

1. **Recognize the three stages** of commercial LLM progression
2. **Understand why wrappers are fragile** businesses
3. **See why agentic systems matter** for differentiation
4. **Appreciate human evaluation** beyond benchmarks
5. **Make informed decisions** about product positioning

---

## Why This Matters for Week 4

Week 4 focuses on **code generation quality** because:

- Code generation is a **Stage 2/3** application (augment/differentiate)
- Quality matters more than chat capability
- Model selection directly impacts product quality
- Benchmarking code generation reveals real differences

This commercial context helps you:
- **Choose models** based on actual use case
- **Evaluate performance** beyond benchmarks
- **Understand tradeoffs** in production systems
- **Build systems** that create real value

---

## Next Steps

1. Read `notes.md` for detailed examples and analysis
2. Reflect on where your projects fit in the progression
3. Move to **Day 3** to begin experimental work

---

**Remember:** This is a judgment day. Internalize commercial thinking — code comes later.
