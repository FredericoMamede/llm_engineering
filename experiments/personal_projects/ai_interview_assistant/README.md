# AI Interview Preparation Assistant

> **Production-Grade RAG System for Technical Interview Preparation**

**Location:** `experiments/personal_projects/ai_interview_assistant/`

**Status:** ✅ **Functional** - Core system complete, in maintenance mode

---

## 🎯 Primary Goal

Build an AI Interview Preparation Assistant initially specialized for the **"AI-First MERN Fullstack Developer"** role at Eventyr, but architected to support future roles, companies, and tech stacks without restructuring.

---

## 🛡️ Non-Negotiable Principles

- ❌ **No hallucinations**: All answers must be grounded in retrieved documents
- ✅ **Explicitly label**: Implemented vs conceptual vs future
- 🏗️ **RAG is a system, not a demo**
- 📚 **Preserve source attribution and freshness**
- 🎯 **Prefer correctness and depth over brevity**
- 🚫 **Refuse to answer if insufficient context is retrieved**

---

## 🎤 Interview Calibration Rule

All generated answers must:
- Assume the listener is a **senior engineer or hiring manager**
- Emphasize **reasoning, tradeoffs, and decision criteria**
- Avoid tutorial-style explanations unless explicitly requested
- Prefer **real-world framing** over academic completeness

---

## 📚 Core Knowledge Domains

1. Every bullet point from the job requirements and "will be a plus" section (22 total)
2. Eventyr company context (mission, product, constraints, culture)
3. AI-first startup interview patterns
4. System design for high-throughput, AI-assisted platforms
5. Failure modes and real-world tradeoffs
6. Candidate's own project corpus (optional but supported)

---

## 📋 Canonical Requirement Scope

### CORE REQUIREMENTS (1-11)

1. 4+ years of commercial experience in fullstack TypeScript development
2. Strong experience with React 18 and modern React patterns (hooks, context, TanStack Query)
3. Production experience with Node.js and NestJS (or similar opinionated frameworks)
4. Solid knowledge of PostgreSQL — schema design, migrations, query optimization, JSONB
5. Experience with Redis for caching, pub/sub, or job queues
6. Understanding of REST API design and authentication (JWT, OAuth flows)
7. Experience integrating third-party APIs (payment gateways, external services)
8. Familiarity with AI/LLM APIs (OpenAI, Claude, or similar) — prompt engineering basics
9. Product thinking: understanding why you're building, not just how
10. Ability to work autonomously in a fast-paced startup environment
11. English: Upper-Intermediate+ (written communication with international team)

### PLUS (NICE TO HAVE) (12-22)

12. Experience with BullMQ or similar job queue systems (Agenda, Bull, AWS SQS)
13. Knowledge of TypeORM or Prisma ORM
14. Experience building SaaS products with multi-tenant architecture
15. Familiarity with Stripe API for subscription billing
16. Understanding of rate limiting, throttling, and anti-bot detection patterns
17. Experience with Tailwind CSS and component libraries (shadcn/ui, Radix)
18. Knowledge of WebSockets for real-time features
19. Experience with Testcontainers or similar for integration testing
20. CI/CD setup experience
21. Deployment experience on Railway, Render, or similar PaaS platforms
22. Startup experience or work in agile, fast-moving teams

### Coverage Guarantee

For each requirement item (1–22), the system MUST produce:
- ✅ At least one primary authoritative source
- ✅ At least one secondary explanatory source
- ✅ A minimum of 5 semantically distinct chunks
- ✅ At least one interview-question-oriented chunk
- ✅ At least one real-world tradeoff or failure-mode chunk

**If any requirement fails this checklist, ingestion is considered INCOMPLETE.**

---

## 🏢 Company Context Requirements (Eventyr)

The system must ingest and reason over:

1. Eventyr mission and positioning
2. Description of the autonomous recruiting platform
3. AI-powered agent workflows (sourcing, engagement, screening)
4. Performance constraints:
   - Sub-5-minute candidate response time
   - Hundreds of parallel conversations
5. Human-in-the-loop review and brand safety
6. Small, high-impact team dynamics (2–3 engineers)
7. AI-assisted development culture (Claude Code, Cursor)

---

## 🔄 Data Ingest Strategy

For each requirement bullet:
1. **Discover** authoritative, up-to-date web sources (official docs, respected engineering blogs)
2. **Normalize** to clean Markdown
3. **Perform LLM-based semantic chunking** with structured outputs:
   - `headline`: Brief heading likely to surface in queries
   - `summary`: Summary to answer common questions
   - `original_text`: Exact original text
   - `metadata`: Source, freshness, requirement_id, chunk_type
4. **Embed** using `all-MiniLM-L6-v2`
5. **Store** in persistent Chroma vector database with metadata filters

### Source Freshness Rule

- Prefer sources updated within the **last 24 months**
- If older sources are used, they MUST be marked as **historical context**
- Framework and API docs (React, Node, Stripe, Redis, etc.) must reflect **current major versions** in active production use

---

## 🔧 RAG Pipeline

- **Query rewriting** (original + rewritten)
- **Dual retrieval** (both queries)
- **LLM-based re-ranking** with structured outputs
- **Configurable top-K and final-K**
- **Conversation history awareness**
- **Strict context injection** (no free generation)

---

## 🎭 Assistant Modes

Implement prompt-orchestrated modes:

1. **Explain Mode** - Detailed explanations with reasoning
2. **Interviewer Mode** - Adaptive difficulty questions
3. **Evaluation Mode** - Scoring + feedback
4. **Company-Aware Mode** - Eventyr-specific framing
5. **System Design Mode** - Architecture and tradeoff discussions
6. **Rapid Fire Mode** - Quick Q&A format

---

## 📊 Evaluation

- **LLM-as-a-judge** with structured scoring:
  - Accuracy
  - Depth
  - Relevance
  - Confidence
- Identify missing concepts and weak framing
- Suggest follow-up questions

---

## 🖥️ UI Requirements

- **Gradio UI**
- Mode selector
- Retrieved context viewer
- Answer + evaluation panel
- Debug visibility into retrieval and re-ranking

---

## 🔌 Extensibility

- New roles = new corpus
- New companies = new context docs
- **No code rewrites required** to scale

---

## 📁 Project Structure

```
ai_interview_assistant/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
│
├── core/                        # Core RAG pipeline
│   ├── __init__.py
│   ├── vector_store.py         # Vector store abstraction (local/Chroma)
│   ├── retriever.py            # Knowledge retrieval with query rewriting
│   ├── answer_generator.py     # Strict answer generation
│   └── modes.py                # Interview mode orchestration
│
├── ingest/                      # Data ingestion pipeline
│   ├── __init__.py
│   ├── discoverer.py           # Source discovery and normalization
│   ├── browser_fetcher.py      # Playwright-based fetching for bot-protected pages
│   ├── chunker.py              # LLM-based semantic chunking
│   └── embedder.py             # Embedding generation and vector DB creation
│
├── evaluation/                 # Evaluation system
│   ├── __init__.py
│   └── judge.py                # LLM-as-a-judge evaluation
│
├── ui/                         # Gradio interface
│   ├── __init__.py
│   ├── app.py                  # Main UI
│   ├── drill_mode.py           # Drill mode conversation tracking
│   └── weakness_tracker.py    # Weakness tracking with JSON persistence
│
├── configs/                    # Configuration files
│   ├── requirements.yaml       # Canonical requirement list (22 requirements)
│   └── company_context.yaml    # Eventyr company context (7 domains)
│
├── data/                       # Data storage
│   ├── sources/                # Normalized source documents (Markdown)
│   ├── chunks/                 # Processed semantic chunks (JSON)
│   ├── vector_db/              # Vector database (pickle + JSON metadata)
│   ├── sessions/               # Drill mode session data (JSON)
│   └── weaknesses.json         # Tracked weaknesses (JSON)
│
└── docs/                       # Documentation
    ├── ARCHITECTURE.md         # System architecture
    ├── STATUS.md               # Project status
    ├── SOURCE_PLAN.md          # Source discovery plan
    └── DISCOVERY_STATUS.md     # Discovery implementation status
```

---

## 🚀 Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment (create .env file)
# Required: OPENAI_API_KEY (or other LLM provider keys)
```

### 2. Data Ingestion (if not already done)

```bash
# Discover and normalize sources
python ingest/discoverer.py

# Generate semantic chunks
python ingest/chunker.py

# Create embeddings and vector database
python ingest/embedder.py
```

### 3. Launch UI

```bash
python ui/app.py
```

Access at: `http://localhost:7860`

---

## 📝 Current Status

**Phase:** ✅ **Complete** - System fully functional

**Completed:**
- ✅ Source discovery and normalization
- ✅ LLM-based semantic chunking
- ✅ Vector database (local pickle-based storage)
- ✅ Retrieval pipeline with query rewriting
- ✅ Strict answer generation with grounding
- ✅ 6 interview modes (Explain, Interviewer, Evaluation, Company-Aware, System Design, Rapid Fire)
- ✅ LLM-as-a-judge evaluation
- ✅ Gradio UI with transparency features
- ✅ Drill mode for iterative practice
- ✅ Weakness tracking with persistence

---

## 🎯 Features

### Interview Modes

1. **Explain Mode** - Detailed explanations with clarity focus
2. **Interviewer Mode** - Simulates senior interviewer with follow-up questions
3. **Evaluation Mode** - Evaluates candidate answers against knowledge base
4. **Company-Aware Mode** - Frames answers in Eventyr's context
5. **System Design Mode** - Emphasizes tradeoffs and failure modes
6. **Rapid Fire Mode** - Short, precise answers (3-5 sentences)

### Key Capabilities

- **Strict Grounding**: All answers traceable to retrieved chunks
- **Refusal Behavior**: System refuses when context is insufficient
- **Transparency**: Full visibility into retrieval, citations, and confidence
- **Drill Mode**: Track conversation history for iterative practice
- **Weakness Tracking**: Automatically tracks missed concepts from evaluations
- **Debug Mode**: View similarity scores and retrieval metadata

### Usage Example

1. Enter an interview question (e.g., "How does TypeScript help with large-scale development?")
2. Select an interview mode
3. Optionally provide your answer for evaluation
4. Enable Drill Mode to track conversation history
5. View the grounded answer with citations
6. Review evaluation feedback (if candidate answer provided)
7. Check tracked weaknesses in the accordion panel

---

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: System architecture and design
- **[STATUS.md](docs/STATUS.md)**: Current implementation status
- **[USAGE.md](docs/USAGE.md)**: User guide and best practices
- **[SOURCE_PLAN.md](docs/SOURCE_PLAN.md)**: Source discovery plan
- **[DISCOVERY_STATUS.md](docs/DISCOVERY_STATUS.md)**: Discovery implementation details

## 📚 References

- Week 5 RAG implementation patterns
- Pro implementation: `week5/pro_implementation/`
- Evaluation harness: `week5/evaluation/`

---

**Build the best interview preparation system. Build it with production-grade RAG.** 🚀
