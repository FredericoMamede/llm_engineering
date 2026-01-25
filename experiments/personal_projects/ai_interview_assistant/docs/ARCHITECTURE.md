# Architecture Documentation

## System Overview

The AI Interview Preparation Assistant is a production-grade RAG system designed to help candidates prepare for technical interviews. The system is architected for extensibility, allowing new roles, companies, and tech stacks to be added without code restructuring.

## Core Principles

1. **No Hallucinations**: All answers must be grounded in retrieved documents
2. **Explicit Labeling**: Clearly distinguish implemented vs conceptual vs future features
3. **RAG as a System**: Not a demo - production-ready patterns throughout
4. **Source Attribution**: Preserve source information and freshness metadata
5. **Correctness Over Brevity**: Prefer depth and accuracy over short answers
6. **Refuse When Uncertain**: If insufficient context is retrieved, refuse to answer

## Architecture Layers

### 1. Data Ingestion Layer

**Components:**
- `ingest/discoverer.py`: Source discovery and normalization from web
- `ingest/browser_fetcher.py`: Playwright-based fetching for bot-protected pages
- `ingest/chunker.py`: LLM-based semantic chunking
- `ingest/embedder.py`: Embedding generation and vector DB creation

**Flow:**
```
Source Discovery → Normalization → Semantic Chunking → Embedding → Vector Store
```

**Key Features:**
- LLM-based semantic chunking with structured outputs (headline, summary, original_text)
- **Content-hash-based chunk IDs** (Phase 4.5): Chunk IDs are derived from normalized chunk content and stable metadata (requirement_id, chunk_type, company_domain) using SHA256 hashing. This ensures any content change produces a new ID, enabling correct incremental ingestion without vector DB rebuilds.
- Metadata preservation (source, freshness, requirement_id, chunk_type)
- Source freshness validation (prefer < 24 months)
- Browser fallback for bot-protected pages
- Local pickle-based vector storage (Chroma-compatible interface available)

### 2. RAG Pipeline Layer

**Components:**
- `core/vector_store.py`: Vector store abstraction (local/Chroma)
- `core/retriever.py`: Knowledge retrieval with query rewriting
- `core/answer_generator.py`: Strict answer generation with grounding
- `core/modes.py`: Interview mode orchestration

**Flow:**
```
Query → Rewrite → Dual Retrieval → Merge & Deduplicate → Filter → Answer Generation
```

**Key Features:**
- Query rewriting for better retrieval (optional)
- Dual retrieval (original + rewritten queries)
- Merge and deduplication by chunk_id
- **Simple similarity-based ranking**: Results are ranked purely by cosine similarity scores (no heuristic adjustments)
- Metadata-aware filtering
- Configurable top-K and final-K
- Strict context injection (no free generation)
- Refusal behavior when context insufficient
- Interview mode-specific configurations

**Ranking Design Decision:**
Retrieval ranking is intentionally simple and similarity-based. Phase 4.3 tested heuristic ranking approaches (dual-retrieval boosting, chunk-type penalties) but evaluation showed these did not meaningfully improve MRR or nDCG. The current implementation prioritizes transparency and evaluation-driven iteration over complex ranking heuristics.

**Adaptive Retrieval (Deterministic) - Phase 5 (Final):**
The system includes deterministic retrieval intelligence that adapts behavior based on structured signals without LLM decision-making. This is the **final adaptive retrieval layer** - tuned for stability and confidence preservation:

- **Requirement-Aware Boosting**: Chunks matching the question's requirement_id receive a small score boost (1.05x) to improve early ranking for requirement-specific questions. Tuned to reduce ranking distortion while preserving gains.

- **Failure-Mode Sensitivity**: Disabled (1.00x) to stabilize answer confidence. Failure-mode chunks are still retrieved but do not receive special boosting.

- **Weakness-Aware Depth**: When retrieval confidence (average top-3 similarity) is low (< 0.60), the system increases retrieval depth by +5 chunks to improve recall. Threshold tuned to reduce unnecessary depth expansion.

**Why This Is Not Agentic:**
- All adaptations use explicit constants (no learned parameters)
- Logic is deterministic and explainable (no hidden heuristics)
- Behavior is logged and reversible (full transparency)
- No LLM-based decision making (no prompt-based magic)
- Changes are measurable through offline evaluation

**Rigor Preservation:**
- All adaptations are logged in `retrieval_metadata['phase5_adaptive']`
- Constants are defined at module level (easily adjustable)
- Each layer is independently ablatable (can be disabled individually)
- Evaluation metrics remain unchanged (same test sets, same metrics)
- Changes are fully reversible (no permanent state)

### 3. Mode Layer

**Components:**
- `core/modes.py`: All 6 interview modes in single orchestration module

**Modes:**
- **Explain Mode**: Detailed explanations with clarity focus
- **Interviewer Mode**: Simulates senior interviewer with follow-up questions
- **Evaluation Mode**: Evaluates candidate answers
- **Company-Aware Mode**: Eventyr-specific framing
- **System Design Mode**: Emphasizes tradeoffs and failure modes
- **Rapid Fire Mode**: Short, precise answers

**Key Features:**
- Configuration-driven modes (ModeConfig dataclass)
- Mode-specific retrieval parameters (K values, filters)
- Mode-specific prompt instructions
- Follow-up question generation (Interviewer Mode)
- No code duplication - shared retrieval and answer generation

### 4. Evaluation Layer

**Components:**
- `evaluation/judge.py`: LLM-as-a-judge evaluation (runtime answer evaluation)

**Key Features:**
- Structured feedback (strengths, gaps, missed concepts, follow-ups)
- Confidence scoring (1-5 scale)
- Grounded evaluation (only uses retrieved chunks)
- Robust parsing of LLM evaluation responses

### 4.5. RAG Evaluation Layer (Offline)

**Components:**
- `evaluation/rag_evaluator.py`: Orchestration for offline RAG evaluation
- `evaluation/metrics.py`: Pure metric calculation functions (MRR, nDCG, Recall, coverage)
- `evaluation/test_sets.py`: Curated test case definitions
- `evaluation/data_contracts.py`: Evaluation data structures
- `evaluation/analysis.py`: Analysis and diagnostic functions
- `evaluation/run_evaluation.py`: Offline evaluation runner script

**Key Features:**
- **Offline execution**: Evaluations run outside UI via `run_evaluation.py`
- **Concept-based test cases**: Test questions with expected concepts (no ground truth answers)
- **Retrieval metrics**: MRR, nDCG@K, Recall@K, concept coverage, chunk-type distribution
- **Answer quality metrics**: Confidence scores, missed concepts (reuses AnswerJudge)
- **Analysis functions**: Weakest requirements, chunk type usage, retrieval-answer mismatches
- **Regression detection**: Compare two evaluation runs to detect improvements/regressions
- **Immutable artifacts**: Each run saved as JSON snapshot in `evaluation/runs/`
- **Read-only UI**: RAG Evaluation Dashboard visualizes existing runs, never executes evaluations

**Architecture:**
- Reuses existing components: `KnowledgeRetriever`, `AnswerGenerator`, `AnswerJudge`
- No modifications to runtime components
- Pure analysis functions (no LLM calls in analysis layer)
- Complete separation: evaluation execution vs visualization

### 5. Interview Simulator Layer

**Components:**
- `core/interview_simulator.py`: Interview Simulator with session management

**Key Features:**
- Autonomous question generation from retrieved chunks
- Session lifecycle management (start, progress, end)
- Adaptive difficulty progression
- Answer evaluation using existing AnswerJudge
- Teaching on demand (opt-in only)
- Session persistence (JSON files)
- Weakness tracking integration

**Architecture:**
- Reuses existing components: `KnowledgeRetriever`, `AnswerGenerator`, `AnswerJudge`, `WeaknessTracker`
- No duplicated logic - leverages shared RAG pipeline
- Questions are generated from retrieved chunks (grounded, not synthetic)
- Teaching is strictly opt-in - system behaves as interviewer first

**Session Lifecycle:**
1. **Start Session**: Configure company, requirement set, difficulty, focus areas
2. **Question Generation**: System retrieves chunks and generates question using LLM
3. **User Answer**: User provides free-text answer
4. **Evaluation**: System evaluates using AnswerJudge (strict, no hints)
5. **Outcome Decision**: Correct/Partial/Incorrect based on confidence score
6. **User Actions**: User can request teaching, retry, follow-up, or move on
7. **Teaching (On Demand)**: Four types - full explanation, ideal answer, why weak, missed concepts
8. **Difficulty Progression**: Escalates after 2 consecutive correct, descalates after 2 consecutive incorrect
9. **Session Summary**: Generated on end with statistics, weaknesses, recommendations

### 6. UI Layer

**Components:**
- `ui/app.py`: Gradio interface with multiple tabs
- `ui/drill_mode.py`: Drill mode conversation tracking
- `ui/weakness_tracker.py`: Weakness tracking with JSON persistence

**Key Features:**
- **Q&A Mode Tab**: Traditional question-answer interface
  - Mode selector
  - Retrieved context viewer with badges and highlighting
  - Answer + evaluation panel
  - Debug visibility (similarity scores, retrieval metadata)
  - Drill mode for iterative practice
  - Weakness tracking with automatic persistence
- **Interview Simulator Tab**: System-driven interview interface
  - Session configuration
  - Question display with metadata
  - Answer input and submission
  - Evaluation panel
  - Teaching panel (on demand)
  - Progress tracking
  - Session controls
- **RAG Evaluation Dashboard Tab**: Read-only visualization of evaluation runs
  - Evaluation run selector (from `evaluation/runs/`)
  - Overall metrics summary
  - Weakest requirements table
  - Chunk type usage diagnostics
  - Retrieval-answer mismatch table
  - Regression comparison between runs
  - Export analysis reports
  - **Important**: UI never executes evaluations - only displays existing artifacts
- Confidence badges and visual indicators

## Data Flow

### Ingestion Flow

```
1. Requirement Enumeration (22 requirements + company context)
2. Source Discovery (web scraping, official docs)
3. Normalization (clean Markdown)
4. Semantic Chunking (LLM-based with structured outputs)
5. Embedding (all-MiniLM-L6-v2)
6. Vector Store (local pickle-based with JSON metadata)
7. Coverage Verification (checklist per requirement)
```

### Query Flow (Q&A Mode)

```
1. User Query + Mode Selection
2. Query Rewriting (original + rewritten)
3. Dual Retrieval (both queries, top-K each)
4. Merge Results
5. Re-ranking (LLM-based, structured output)
6. Context Validation (sufficient coverage check)
7. Mode-Specific Prompt Construction
8. Answer Generation (strict context injection)
9. Evaluation (LLM-as-a-judge, if candidate answer provided)
10. Response (answer + evaluation + sources)
```

### Interview Simulator Flow

```
1. Session Start (configuration)
2. Question Generation:
   - Retrieve chunks (considering weaknesses, focus areas, difficulty)
   - Generate question from chunks using LLM
   - Tag with requirement_id, company_domain, intent, difficulty
3. User Answer Submission
4. Evaluation:
   - Retrieve context for question
   - Evaluate using AnswerJudge
   - Determine outcome (Correct/Partial/Incorrect)
   - Update weakness tracker
   - Adjust difficulty progression
5. User Actions (optional):
   - Request teaching (full, ideal answer, why weak, missed concepts)
   - Retry question
   - Ask follow-up
   - Move to next question
6. Next Question Generation (repeat from step 2)
7. Session End:
   - Generate summary (statistics, weaknesses, recommendations)
   - Persist session to disk
```

### RAG Evaluation Flow (Offline)

```
1. Run evaluation runner: python evaluation/run_evaluation.py
2. Load test cases from test_sets.py
3. For each test case:
   a. Retrieve chunks (using KnowledgeRetriever)
   b. Generate answer (using AnswerGenerator)
   c. Evaluate answer (using AnswerJudge)
   d. Calculate retrieval metrics (MRR, nDCG, Recall, coverage)
   e. Calculate answer metrics (confidence, missed concepts)
4. Aggregate results across all test cases
5. Create EvaluationRun snapshot (immutable)
6. Persist to evaluation/runs/run_YYYYMMDD_HHMMSS.json
7. UI visualization (read-only):
   - Load existing run from JSON
   - Display metrics and analysis
   - Compare runs for regression detection
```

**Key Points:**
- Evaluations are **offline** - run explicitly via script, not from UI
- UI is **read-only** - only visualizes existing artifacts
- Metrics are **baseline** - not optimized, used to measure deltas
- Improvements are driven by **measured deltas** between runs

## Extensibility Design

### Adding New Roles

1. Create new `requirements.yaml` with role-specific requirements
2. Run ingestion pipeline with new requirements
3. System automatically handles new corpus

### Adding New Companies

1. Create new `company_context.yaml` with company-specific domains
2. Run ingestion pipeline with new company context
3. System automatically handles new context

### Adding New Modes

1. Add new mode configuration to `core/modes.py` (ModeConfig)
2. Add mode to ModeOrchestrator._get_mode_config()
3. Add mode to UI selector in `ui/app.py`
4. System automatically supports new mode

**Note**: All 6 interview modes are currently implemented in `core/modes.py`. The Interview Simulator is a separate system that uses these modes for teaching explanations.

## Metadata Schema

### Chunk Metadata

```python
{
    "source": "https://example.com/doc",
    "source_type": "official_docs" | "blog" | "tutorial",
    "freshness": "2024-01-15",
    "requirement_id": 1-22,
    "chunk_type": "primary" | "secondary" | "interview_question" | "tradeoff" | "failure_mode",
    "headline": "Brief heading",
    "summary": "Summary text",
    "original_text": "Full original text"
}
```

### Vector Store Metadata

Local pickle-based storage (Chroma-compatible interface available):
- Document text (headline + summary + original_text)
- Embedding vector (NumPy array)
- Metadata (all fields above, stored as JSON)
- ID (unique identifier)
- Stored in `data/vector_db/vector_db.pkl` (embeddings) and `data/vector_db/vector_db_metadata.json` (metadata)

## Performance Considerations

- **Retrieval**: Configurable top-K (default 20) before re-ranking
- **Re-ranking**: Final-K (default 10) after re-ranking
- **Embedding**: Local model (all-MiniLM-L6-v2) for fast inference
- **Generation**: Configurable model (default GPT-4o)
- **Caching**: Consider implementing retrieval result caching

## Security Considerations

- **Source Validation**: Verify source authenticity
- **Content Sanitization**: Clean and validate ingested content
- **API Key Management**: Secure environment variable handling
- **Rate Limiting**: Implement rate limiting for API calls

## Monitoring and Observability

- **Runtime Metrics**: 
  - Retrieval success rates (via debug mode)
  - Answer quality scores (confidence scores from AnswerJudge)
  - Source freshness (metadata in chunks)
  - Coverage (requirement coverage completeness)
- **Offline RAG Evaluation**:
  - Retrieval metrics (MRR, nDCG@K, Recall@K, concept coverage)
  - Answer quality metrics (confidence scores, missed concepts)
  - Weakest requirements analysis
  - Chunk type usage diagnostics
  - Regression detection between evaluation runs
  - All metrics are baseline measurements - improvements tracked via deltas
