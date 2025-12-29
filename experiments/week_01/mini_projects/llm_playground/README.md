# LLM Engineering Playground

**Production Patterns Demo (Week 1 Consolidation)**

## Overview

**LLM Engineering Playground** is a small but professional CLI / notebook tool built to consolidate and demonstrate **core LLM engineering patterns learned in Week 1** of the *Become an LLM Engineer in 8 Weeks* course.

This project intentionally stays within the scope of Week 1 concepts and avoids introducing advanced techniques prematurely.

It is **not a toy** and **not a product**.

It is a **learning artifact** designed to demonstrate:

- correct API usage
- clean prompt engineering
- multi-step LLM workflows
- model abstraction (local vs cloud)
- performance-aware, production-minded code structure

The focus is on **engineering judgment**, not novelty.

---

## What This Project Demonstrates

This project brings together multiple LLM engineering fundamentals into **one cohesive pipeline**:

- Input handling (text, URL scraping, or file input)
- Multi-step LLM workflows
- Prompt variation and model comparison
- Streaming vs non-streaming responses
- Cost and token awareness
- Clean, maintainable Python code

All concepts are **derived directly from Week 1 learning**.

---

## Core Features

### 1. Input Handling

The tool accepts:

- **Raw text input**
- **URLs**, which are scraped automatically
- **Text files** via CLI

Scraping strategy:

- `requests + BeautifulSoup` for static pages
- **Playwright fallback** for JavaScript-rendered sites

All inputs are validated early using a **fail-fast** approach to prevent wasted API calls and surface clear errors.

---

### 2. Multi-Step LLM Workflow (Agentic-Lite)

The pipeline follows a clear, explicit pattern:

```

Analyze → Transform → Output

```

**Step 1 – Analyze**

- Detect key topics
- Identify tone
- Measure length and structure

**Step 2 – Transform**

- Generate:
  - summary
  - key bullet points
  - rewritten version (configurable tone)

**Step 3 – Optional Extension**

- Translation (e.g. English → Dutch), implemented as an additional LLM call

This mirrors real-world LLM application design without introducing full agent frameworks prematurely.

---

### 3. Prompt Variation & Model Comparison

The same task can be executed using:

- Different **system prompts**
- Different **models**

Supported patterns:

- OpenAI models (via API)
- Local models (via Ollama)
- OpenAI-compatible endpoints

For each run, the tool can capture:

- Generated output
- Token usage
- Estimated cost (OpenAI)
- Latency (best effort)

This enables **side-by-side qualitative comparison** of models and prompts.

---

### 4. Streaming Support

The pipeline supports:

- Streaming **on or off** via CLI flags
- Efficient output assembly using `list + join` (O(n))
- Clean real-time display without blocking control flow

This demonstrates performance-aware handling of streaming responses.

---

### 5. Clean Engineering Practices

The project intentionally applies production-minded patterns:

- Full **type hints**
- Clear function boundaries
- Small, composable modules
- Explicit error handling
- Descriptive docstrings
- No hidden magic or global state

The goal is readability and correctness over cleverness.

---

## Project Structure

```text
llm_playground/
├─ README.md
├─ main.py            # CLI entry point
├─ pipeline.py        # analyze → transform → translate workflow
├─ prompts.py         # system and user prompt templates
├─ models.py          # OpenAI / Ollama client abstraction
├─ scraper.py         # static + JS-aware web scraping
├─ utils.py           # validation, token counting, output formatting
├─ logger.py          # centralized logging
├─ config.py          # constants and configuration
├─ test_all.py        # end-to-end CLI integration tests
└─ examples/
   └─ sample_run.md   # example execution and output
```

This structure mirrors how small but serious LLM utilities are typically organized in production codebases.

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

## Testing

This project includes a **comprehensive CLI integration test suite** (`test_all.py`) that validates:

* Argument validation and fail-fast errors
* URL scraping and file input handling
* OpenAI and Ollama execution paths
* JSON mode behavior
* Streaming vs non-streaming output
* Tone selection and translation
* File output and encoding handling

OpenAI tests are **automatically skipped** if `OPENAI_API_KEY` is not set, making the suite safe for local development and CI environments.

Run all tests locally with:

```bash
python test_all.py
```

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


