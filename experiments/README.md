# 📋 Summary: Mini-Projects, Challenges & Personal Projects

## Overview

This document tracks all projects built under the `experiments/` folder, organized by:
- **Mini-Projects** (week-specific, focused implementations)
- **Challenges** (larger, multi-day projects)
- **Personal Projects** (independent, production-ready systems)

---

## 🎯 Personal Projects

### Master Prompt Generator
**Location:** `experiments/personal_projects/master_prompt_generator/`

**Status:** ✅ **Complete and Production-Ready**

**Description:**
A comprehensive prompt engineering platform that generates, evaluates, and refines prompts using AI-powered meta-prompting. This is a production-ready system designed for long-term use.

**Key Features:**
- ✅ **Intelligent Prompt Generation** - Meta-prompting using best-in-class LLMs
- ✅ **Comprehensive Coverage** - 8+ prompt techniques, 50+ use case categories, 4 complexity tiers
- ✅ **Quality Assurance** - Automatic evaluation (0-10 scale, 6 criteria), anti-pattern detection (12+ prompt smells)
- ✅ **Token Economics & Cost Analysis** - Token estimation, cost calculation, efficiency scoring
- ✅ **Prompt Lifecycle & Versioning** - Full lifecycle tracking (Draft → Generated → Evaluated → Refined → Approved → Archived), semantic versioning (MAJOR.MINOR.PATCH)
- ✅ **User-Friendly Interface** - Simple Gradio UI for inspection and control

**Technologies:**
- Python, Pydantic, LiteLLM
- Gradio UI
- YAML configuration
- SQLite (implied for persistence)

**Architecture:**
- Core modules: prompt generation, evaluation, refinement, approval logic
- Model manager: multi-provider support (OpenAI, Anthropic, Google, Ollama, etc.)
- Lifecycle guards: version integrity, regression detection
- Token economics: cost analysis and optimization

**Notable:**
- Analyzed 700+ prompts from repository
- Production-ready with defensive correctness
- Comprehensive documentation (architecture, integration, testing)

---

### AI Interview Preparation Assistant
**Location:** `experiments/personal_projects/ai_interview_assistant/`

**Status:** ✅ **Complete (Frozen – Evaluation-Driven RAG System)**

**Description:**
A production-grade RAG system that functions as an Expert Knowledge Worker for technical interview preparation. Built with evaluation-first development methodology, the system was intentionally frozen after rigorous evaluation and tuning (Phase 5 deterministic retrieval intelligence). Initially specialized for the "AI-First MERN Fullstack Developer" role at Eventyr, but architected to support future roles, companies, and tech stacks without restructuring. The project is complete and intentionally paused, not abandoned—serving as a reference implementation for evaluation-driven RAG systems.

**Key Features:**
- ✅ **No Hallucinations** - All answers grounded in retrieved documents
- ✅ **22 Requirement Coverage** - Complete knowledge domain mapping for all job requirements
- ✅ **Company Context Integration** - Eventyr-specific framing and constraints
- ✅ **Advanced RAG Pipeline** - Query rewriting, dual retrieval, deterministic score adjustments
- ✅ **6 Assistant Modes** - Explain, Interviewer, Evaluation, Company-Aware, System Design, Rapid Fire
- ✅ **LLM-as-a-Judge Evaluation** - Structured scoring (accuracy, depth, relevance, confidence)
- ✅ **Source Freshness Validation** - Prefer sources < 24 months, mark historical context
- ✅ **Strict Context Injection** - Refuse to answer if insufficient context retrieved
- ✅ **Interview Calibration** - Senior engineer/hiring manager level, emphasis on tradeoffs

**Evaluation & Retrieval Intelligence:**
- ✅ **Offline RAG Evaluation Harness** - Comprehensive metrics (MRR, nDCG@10, Recall@10, Concept Coverage)
- ✅ **Requirement-Level Weakness Analysis** - Identifies weakest requirements for targeted improvement
- ✅ **Deterministic Retrieval Intelligence (Phase 5)** - Score-based adjustments without LLM decision logic
- ✅ **Transparent, Logged Score Adjustments** - All adaptive behavior logged in retrieval metadata
- ✅ **Regression Detection & Comparison UI** - Read-only dashboard for comparing evaluation runs
- ✅ **Intentional System Freeze** - Frozen after metric convergence to prevent overfitting

**Technologies:**
- Python, Pydantic, ChromaDB
- LangChain, Sentence Transformers (all-MiniLM-L6-v2)
- OpenAI API, Anthropic API
- Gradio UI
- YAML configuration

**Architecture:**
- **Data Ingestion Layer**: Source discovery → Normalization → Semantic chunking → Embedding → Vector store
- **RAG Pipeline**: Query rewriting → Dual retrieval → Deterministic score adjustments → Context validation → Answer generation
- **Mode System**: Prompt-orchestrated modes with consistent interface
- **Offline Evaluation Layer**: Test case management, retrieval metrics, answer evaluation, aggregation
- **Read-only RAG Evaluation Dashboard**: UI for viewing evaluation runs, comparing baselines, analyzing weaknesses
- **Deterministic Retrieval Intelligence (Phase 5)**: Requirement-aware boosting, failure-mode sensitivity, confidence-based depth adjustment (all score-based, no LLM decision logic)
- **Runtime Evaluation**: LLM-as-a-judge with structured scoring and feedback

**Project Status & Rationale:**
The system reached metric convergence after Phase 5 deterministic retrieval intelligence tuning. Further tuning risked overfitting to the evaluation set without meaningful gains. The project was intentionally frozen to preserve stability and serve as a reference implementation for:
- **Evaluation-driven RAG development** - Systematic measurement and iteration
- **Deterministic retrieval refinement** - Score-based adaptations without black-box logic
- **Interview-grade AI systems** - Production-ready patterns for knowledge work

This decision reflects senior engineering judgment: stopping at the right time is as important as building the right features. The system is complete, evaluated, and ready for long-term use.

**Notable:**
- Production-grade RAG patterns from Week 5
- Extensible design (new roles/companies without code rewrites)
- Coverage guarantee: 5+ chunks per requirement with specific types
- Interview-focused calibration (senior engineer level, tradeoff emphasis)
- Content-hash-based chunk IDs for correct incremental ingestion
- Fully documented evaluation methodology and results

---

## 📚 Week 1 Mini-Projects

### LLM Playground
**Location:** `experiments/week_01/mini_projects/llm_playground/`

**Status:** ✅ **Complete**

**Description:**
A small but professional CLI/notebook tool built to consolidate and demonstrate core LLM engineering patterns learned in Week 1. Focuses on multi-step LLM workflows, model abstraction, and production-minded code structure.

**Key Features:**
- ✅ **Input Handling** - Text, URL scraping, file input
- ✅ **Multi-Step Workflow** - Analyze → Transform → Output
- ✅ **Prompt Variation & Model Comparison** - Compare different models and prompts
- ✅ **Streaming Support** - Streaming vs non-streaming responses
- ✅ **Cost & Token Awareness** - Track token usage and costs
- ✅ **Web Scraping** - requests + BeautifulSoup, Playwright fallback

**Technologies:**
- Python, OpenAI API, Ollama
- BeautifulSoup, Playwright
- CLI interface

**Use Cases:**
- Text analysis and transformation
- URL content summarization
- Multi-model comparison
- Translation workflows

---

## 📚 Week 2 Mini-Projects

### AI Knowledge Assistant
**Location:** `experiments/week_02/mini_projects/ai_knowledge_assistant/`

**Status:** ✅ **Complete and Production-Ready**

**Description:**
A configurable, prompt-orchestrated assistant for technical teams. It ingests code, errors, documents, URLs, and optionally voice, then responds with structured, explainable answers.

**Key Features:**
- ✅ **4 Core Use Cases:**
  1. Explain & diagnose errors (Python tracebacks, stack traces, logs)
  2. Review and improve code (quick vs deep review modes)
  3. Summarize & reason over technical documents (Markdown/TXT or scraped URLs)
  4. Voice-based technical questions (optional)
- ✅ **Prompt Strategy Comparator** - 3 profiles (Concise Expert, Teaching Mode, Reviewer Mode)
- ✅ **Multi-Provider Model Support** - GPT, Ollama, DeepSeek, Anthropic, Gemini, Groq, Together AI, Mistral
- ✅ **Security Features:**
  - Authentication (secure by default)
  - Prompt injection protection
  - Input validation (files, URLs, audio)
  - SSRF protection
  - SQL injection protection
- ✅ **Production Features:**
  - Rate limiting (requests, tokens, cost)
  - Context window management
  - Retry logic with exponential backoff
  - Structured logging with PII sanitization
  - Session persistence (SQLite)

**Technologies:**
- Python, Gradio UI
- SQLite for session storage
- Multi-provider LLM clients
- Whisper STT + TTS wrappers
- Playwright for JS-rendered sites

**Architecture:**
- Prompt-orchestrated design (code-driven, not LLM-driven)
- Tool registry pattern
- Model registry with capability flags
- Session management with isolation

---

## 📚 Week 3 Mini-Projects & Challenge

### Mini-Project: Meeting Intelligence Extractor
**Location:** `experiments/week_03/mini_projects/meeting_intelligence/`

**Status:** 🚧 **In Progress**

**Description:**
A focused system that transforms raw meeting transcripts into structured business intelligence. Intentionally narrow and opinionated - not a framework, UI app, or multi-model comparison.

**Key Features:**
- ✅ **Single Model** - `meta-llama/Llama-3.2-3B-Instruct` (local, quantized)
- ✅ **Structured Output** - Summaries, decisions, action items, risks, open questions
- ✅ **Token Budgeting** - Token awareness and budgeting
- ✅ **Robust Parsing** - Handles markdown fences, trailing text, missing fields
- ✅ **HuggingFace Transformers** - Direct model access

**Technologies:**
- Python, HuggingFace Transformers
- 4-bit quantization (BitsAndBytes)
- Pydantic for schemas

**Design Principles:**
- Single model, deeply understood
- Prompt design over model hopping
- Token awareness and budgeting
- Explicit tradeoffs

---

### Challenge: Synthetic Data Generation System
**Location:** `experiments/week_03/challenge/`

**Status:** ✅ **Implemented**

**Description:**
A synthetic data generation system that can generate structured datasets using LLMs, use multiple models and prompt strategies, produce diverse but controlled outputs, and expose functionality through a simple Gradio UI.

**Key Features:**
- ✅ **Multi-Provider Support:**
  - HuggingFace (open & gated models: Llama 3.1/3.2/3.3/4, Gemma 2, Phi-3/4, Qwen 2.5, Mistral, etc.)
  - OpenAI (GPT-4o, GPT-4o-mini, GPT-4-turbo)
  - Ollama (local models)
- ✅ **Multiple Schemas** - customer_record, incident_report, meeting_summary, business_event, product_review, employee_record, generic_json
- ✅ **Prompt Strategies** - default, formal, casual, detailed, concise, diverse
- ✅ **Smart Token Estimation** - Auto-updates `max_tokens` based on record count and schema complexity
- ✅ **Schema Filtering** - Removes schema definitions and placeholder values
- ✅ **Gradio UI** - Interactive generation interface
- ✅ **Lightweight Validation** - Structural validation ensures required fields

**Technologies:**
- Python, HuggingFace Transformers, OpenAI API, Ollama
- Gradio UI
- Pydantic for schemas
- JSON export

**Architecture:**
- BaseModel interface for model abstraction
- Adapter pattern for multi-provider support
- Lazy loading for models
- Optional 4-bit quantization for HF models

**Experiments:**
- `model_comparison.ipynb` - Compare outputs from different models
- `prompt_diversity.ipynb` - Explore how prompt strategies affect outputs

---

## 📚 Week 4 Experiments

### Day 3: Python → C++ Conversion
**Location:** `experiments/week_04/day3_python_to_cpp/`

**Status:** ✅ **Complete**

**Description:**
Converts Python code to optimized C++ using frontier models and benchmarks performance.

**Key Features:**
- ✅ **Models Tested** - GPT-5, Claude Sonnet 4.5, Grok 4, Gemini 2.5 Pro
- ✅ **System Information Gathering** - For compiler optimization
- ✅ **Performance Benchmarking** - Python vs C++ execution times
- ✅ **Model Comparison** - Code generation quality assessment

**Results (Expected):**
- 4th place: Claude Sonnet 4.5 (~184x speedup)
- 3rd place: GPT-5 (~233x speedup)
- 2nd place: Grok 4 (~1060x speedup)
- 1st place: Gemini 2.5 Pro (~1440x speedup)

**Technologies:**
- Python, OpenAI API, Anthropic API, Google API, Grok API
- C++ compiler for execution
- Benchmarking utilities

---

### Day 4: Multi-Model Comparison + Gradio UI
**Location:** `experiments/week_04/day4_multi_model_ui/`

**Status:** ✅ **Complete**

**Description:**
Extends Day 3 with open-source models, interactive Gradio UI, and model comparison.

**Key Features:**
- ✅ **Open-Source Models** - Qwen 2.5 Coder, DeepSeek Coder v2, GPT-OSS 20B, Qwen3 Coder 30B, OpenAI GPT-OSS 120B
- ✅ **Interactive Gradio UI** - Code conversion interface
- ✅ **Real-Time Conversion** - Execution testing
- ✅ **Performance Comparison** - Across providers

**Results (Expected):**
- 9th place: Qwen 2.5 Coder (Failed)
- 8th place: OpenAI GPT-OSS 120B (~14x speedup)
- 7th place: DeepSeek Coder v2 (~168x speedup)
- 6th place: Qwen3 Coder 30B (~168x speedup)
- 5th place: Claude Sonnet 4.5 (~184x speedup)
- 4th place: GPT-5 (~233x speedup)
- 3rd place: GPT-OSS 20B (~238x speedup)
- 2nd place: Grok 4 (~1060x speedup)
- 1st place: Gemini 2.5 Pro (~1440x speedup)

**Technologies:**
- Python, Gradio UI
- Multi-provider LLM clients (OpenAI, Anthropic, Google, Grok, Groq, OpenRouter, Ollama)
- C++ compiler

---

### Day 5: Rust Conversion + Advanced Benchmarking
**Location:** `experiments/week_04/day5_rust_conversion/`

**Status:** ✅ **Complete**

**Description:**
Extends code conversion to Rust, adds advanced benchmarking, and creates an enhanced UI with side-by-side execution.

**Key Features:**
- ✅ **Language Support** - C++ and Rust
- ✅ **Enhanced UI** - Side-by-side code editors, run buttons for Python/C++/Rust
- ✅ **Advanced Examples** - LCG (Linear Congruential Generator), Max Subarray Sum
- ✅ **Performance Metrics** - Display and comparison
- ✅ **Complex Algorithm Conversion** - Performance-critical code

**Results (Expected - Complex LCG Example):**
- Failed: Qwen 2.5 Coder, Gemini 2.5 Pro, DeepSeek Coder v2, Qwen3 Coder 30B, Claude Sonnet 4.5, GPT-5
- 3rd place: GPT-OSS 20B (~99,000x speedup)
- 2nd place: Grok 4 (~106,000x speedup)
- 1st place: OpenAI GPT-OSS 120B (~111,000x speedup)

**Technologies:**
- Python, Gradio UI
- Multi-provider LLM clients
- C++ and Rust compilers
- Advanced benchmarking utilities

---

## 📚 Week 6 — Regression Capstone

### Week 6: "The Price Is Right" scaffold
**Location:** `experiments/week_06/`

**Status:** 🚧 **Scaffold complete; implementation in progress**

**Description:**
Week 6 regression capstone scaffold: predict product price from description (Amazon-style data). Independent from Week 5 (RAG); reuses evaluation-first patterns: single harness, baselines, metrics (MAE, MSE, R²), baseline comparison, failure-mode notes.

**Key themes (from course):**
- **Data curation** — Parse, scrub, Item schema, train/val/test (Day 1)
- **LLM pre-processing** — Rewrite to standard format; batch API (Day 2)
- **Evaluation + baselines** — Random, constant, linear, NLP+LR, Random Forest (Day 3)
- **Deep learning** — PyTorch NN/DNN; frontier LLM zero-shot (Day 4)
- **Fine-tuning** — OpenAI API: JSONL, job lifecycle, inference (Day 5)

**Implemented in scaffold:**
- Directory structure: data/, curation/, preprocess/, models/, evaluation/, experiments/, docs/
- Evaluation metrics (MAE, MSE, R²) and harness (`evaluate(predictor, data, size)`)
- Failure mode notes (fine-tuning can regress; human baseline)
- Docs: ARCHITECTURE, STATUS, NOTES

**Not in Week 6 (no graph/retrieval/ranking):** GraphRAG, hybrid retrieval, query expansion, reranking — those are not in the Week 6 course content.

---

## 📊 Summary by Category

### Personal Projects (2)
1. **Master Prompt Generator** - Production-ready prompt engineering platform
2. **AI Interview Preparation Assistant** - Production-grade RAG system for technical interview prep (complete, frozen)

### Mini-Projects (3)
1. **Week 1: LLM Playground** - Multi-step LLM workflows and model comparison
2. **Week 2: AI Knowledge Assistant** - Production-ready technical assistant
3. **Week 3: Meeting Intelligence Extractor** - Meeting transcript analysis (in progress)

### Challenges (1)
1. **Week 3: Synthetic Data Generation System** - Multi-model data generation with Gradio UI

### Week Experiments (4)
1. **Week 4 Day 3: Python → C++ Conversion** - Code translation and benchmarking
2. **Week 4 Day 4: Multi-Model UI** - Extended conversion with UI
3. **Week 4 Day 5: Rust Conversion** - Advanced benchmarking and multi-language support
4. **Week 6: Regression Capstone** - "The Price Is Right" scaffold (evaluation harness, baselines, fine-tuning)

---

## 🔧 Common Technologies & Patterns

### Technologies
- **Python** (primary language)
- **Gradio** (UI framework)
- **HuggingFace Transformers** (model access)
- **OpenAI API, Anthropic API, Google API** (frontier models)
- **Ollama** (local models)
- **SQLite** (persistence)
- **Pydantic** (data validation)
- **LiteLLM** (multi-provider abstraction)

### Patterns
- **Model Registry Pattern** (multi-provider abstraction)
- **Tool Registry Pattern** (function routing)
- **Prompt Orchestration** (code-driven, not LLM-driven)
- **Session Management** (SQLite-backed)
- **Retry Logic** (exponential backoff)
- **Rate Limiting** (token bucket algorithm)
- **Context Window Management**
- **Structured Logging** (with PII sanitization)
- **Lifecycle Management** (versioning, approval gates)

---

## 📈 Project Statistics

- **Total Projects:** 9
- **Production-Ready:** 3 (Master Prompt Generator, AI Knowledge Assistant, AI Interview Preparation Assistant)
- **In Progress:** 1 (Meeting Intelligence Extractor)
- **Complete Experiments:** 5

All projects demonstrate practical LLM engineering patterns, from simple workflows to production-ready systems with security, monitoring, and scalability considerations.
