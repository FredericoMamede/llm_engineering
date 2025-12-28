---

# LLM Engineering Playground

**Production Patterns Demo (Week 1 Consolidation)**

## Overview

**LLM Engineering Playground** is a small but professional CLI/Notebook tool built to consolidate and demonstrate **core LLM engineering patterns learned in Week 1** of the *Become an LLM Engineer in 8 Weeks* course.

This project intentionally stays within the scope of Week 1 concepts and avoids introducing advanced techniques prematurely.

It is **not a toy** and **not a product**.

It is a **learning artifact** designed to show:

* correct API usage
* clean prompt engineering
* multi-step LLM workflows
* model abstraction (local vs cloud)
* performance-aware, production-minded code structure

The focus is on **engineering judgment**, not novelty.

---

## What This Project Demonstrates

This project brings together multiple LLM engineering fundamentals into **one cohesive pipeline**:

* Input handling (text or URL)
* Multi-step LLM workflows
* Prompt variation & model comparison
* Streaming vs non-streaming responses
* Cost & token awareness
* Clean, maintainable Python code

All concepts are **derived directly from Week 1 learning**.

---

## Core Features

### 1. Input Handling

The tool accepts:

* **Raw text input**
* **URLs**, which are scraped automatically

Scraping strategy:

* `requests + BeautifulSoup` for static pages
* **Playwright fallback** for JavaScript-rendered sites

Input is validated early using a **fail-fast** approach.

---

### 2. Multi-Step LLM Workflow (Agentic-Lite)

The pipeline follows a clear, explicit pattern:

```
Analyze → Transform → Output
```

**Step 1 – Analyze**

* Detect key topics
* Identify tone
* Measure length and structure

**Step 2 – Transform**

* Generate:

  * summary
  * bullet points
  * rewritten version (configurable tone)

**Step 3 – Optional Extension**

* Translation (e.g. English → Dutch), implemented as an additional LLM call

This mirrors real-world LLM application design without introducing full agent frameworks prematurely.

---

### 3. Prompt Variation & Model Comparison

The same task can be executed using:

* Different **system prompts**
* Different **models**

Supported patterns:

* OpenAI models (via API)
* Local models (via Ollama)
* OpenAI-compatible endpoints

For each run, the tool captures:

* Generated output
* Token usage
* Latency (best-effort)

This allows **side-by-side qualitative comparison**.

---

### 4. Streaming Support

The pipeline supports:

* Streaming **on or off** via configuration
* Efficient output assembly using `list + join` (O(n))
* Clean real-time display without blocking logic

This demonstrates performance-aware handling of streaming responses.

---

### 5. Clean Engineering Practices

The project intentionally applies production-minded patterns:

* Full **type hints**
* Clear function boundaries
* Small, composable modules
* Explicit error handling
* Descriptive docstrings
* No hidden magic or global state

The goal is readability and correctness over cleverness.

---

## Project Structure

```
llm_playground/
├─ README.md
├─ main.py            # CLI entry point
├─ pipeline.py        # analyze → transform → generate workflow
├─ prompts.py         # system and user prompt templates
├─ models.py          # model abstraction (OpenAI / Ollama)
├─ scraper.py         # static + JS-aware web scraping
├─ utils.py           # token counting, helpers, validation
└─ examples/
   └─ sample_run.md   # example execution and output
```

This structure mirrors how small LLM utilities are typically organized in production codebases.

---

## Example Usage

```bash
python main.py --url "https://example.com/article" --model openai --stream
```

or

```bash
python main.py --text "Paste any text here" --model ollama --tone professional
```

See `examples/sample_run.md` for a complete walkthrough.

---

## Why This Project Exists

This project exists to:

* Consolidate Week 1 learning
* Practice **realistic LLM application design**
* Reinforce good engineering habits early
* Create a reusable internal tool for experimentation

It intentionally avoids:

* Over-engineering
* Full agent frameworks
* Premature RAG or embeddings
* UI complexity

Those topics are covered later in the learning plan.

---

## What This Project Is *Not*

* ❌ A finished product
* ❌ A startup idea
* ❌ A portfolio centerpiece
* ❌ A framework replacement

It is a **learning-first engineering artifact**.

---

## Future Extensions (Optional)

This playground may later be extended with:

* Evaluation heuristics
* Embedding-based comparison
* RAG ingestion
* Lightweight UI

Or it may be deleted entirely.

Both outcomes are valid.

---

## Context

This mini-project was built as part of a structured transition into **LLM / AI Engineering**, following a documented learning plan and emphasizing:

* correctness
* clarity
* honest progression

---

## License

Educational use only.

---

