# Project Status

**Last Updated:** 2026-01-25

## Current Phase: ✅ **Phase 5** - Retrieval Intelligence (Finalized)

### Phase 5: Retrieval Intelligence (Finalized)

**Objective**: Introduce retrieval intelligence that improves performance through controlled, explainable, and testable mechanisms without losing determinism or measurability.

**Approach**: Three deterministic layers that adapt retrieval behavior based on structured signals (requirement_ids, tags, confidence scores).

**Layer 1: Requirement-Aware Score Boosting** ✅ (Finalized)
- **Change**: Chunks matching the question's requirement_id receive a 5% similarity score boost
- **Constant**: `REQUIREMENT_MATCH_BOOST = 1.05` (≤ 1.15 constraint)
- **Applied**: After merge & deduplication, before final sorting
- **Rationale**: Improve early ranking (MRR) by favoring chunks aligned with the question's requirement
- **Final Tuning**: Reduced from 1.10 to 1.05 to reduce ranking distortion while preserving gains

**Layer 2: Failure-Mode Sensitivity** ✅ (Finalized - Disabled)
- **Change**: When question is tagged with `failure_mode`, failure_mode chunks receive no boost
- **Constant**: `FAILURE_MODE_BOOST = 1.00` (disabled)
- **Applied**: After merge & deduplication, before final sorting
- **Rationale**: Surface diagnostic content when questions imply failure analysis
- **Final Tuning**: Disabled (set to 1.00) to stabilize answer confidence

**Layer 3: Weakness-Aware Retrieval Depth** ✅ (Finalized)
- **Change**: When retrieval confidence (avg top-3 similarity) < 0.60, increase final_k by +5
- **Constants**: `CONFIDENCE_THRESHOLD = 0.60`, `DEPTH_INCREASE = 5`
- **Applied**: Before final result truncation
- **Rationale**: Increase recall only when retrieval confidence is low
- **Final Tuning**: Reduced threshold from 0.65 to 0.60 to reduce unnecessary depth expansion

**Design Principles**:
- Deterministic logic only (no LLM decision-making)
- Score-based, explainable adjustments
- Explicit constants (easily adjustable)
- Logged behavior (all adaptations tracked in retrieval_metadata)
- Fully reversible changes

**Evaluation Requirements**:
- Run evaluation without changing data
- Compare against Phase 4.4 baseline
- Measure deltas for: Concept MRR, nDCG@10, Recall@10, Concept Coverage, Weakest requirements
- If ≥2 core metrics improve → KEEP
- If any major regression → REVERT that layer only

**Status**: Finalized - Tuned for stability and confidence preservation

**Final Tuning Summary:**
- Requirement boost reduced from 10% to 5% for stability
- Failure-mode boost disabled to stabilize answer confidence
- Confidence threshold lowered from 0.65 to 0.60 to reduce unnecessary depth expansion
- All gains in MRR, nDCG, Recall, and Coverage preserved
- System ready for long-term use and interview discussion

---

## 🛑 Project Freeze

**Status**: Intentionally Paused

This project has reached a stable, evaluated state suitable for:
- Interview preparation use
- Technical interview discussion
- RAG system experimentation and learning
- Long-term archival

**Completion Rationale:**
- Architecturally sound with clear separation of concerns
- Empirically evaluated with measurable improvements
- Explainable end-to-end with deterministic logic
- Fully documented with transparent design decisions
- Complete by design - no pending improvements

**No further changes are planned.** The system is frozen at this state to preserve stability and serve as a reference implementation.

---

---

## Previous Phase: ✅ **Phase 4.5** - Chunk Identity Fix (Complete)

### Phase 4.5: Chunk Identity Fix (Completed)

**Objective**: Fix chunk ID generation to be content-aware using deterministic hashing, enabling correct incremental ingestion.

**Problem Identified**: Phase 4.4 added high-quality sources and chunks were created, but evaluation metrics did not change. Root cause: chunk ID collisions caused new content to be skipped by the embedder. The old ID generation used source filename + chunk index + headline hash, which could produce the same ID for different content.

**Solution**: Implemented content-hash-based chunk IDs derived from:
- Normalized chunk text (content)
- Stable metadata (requirement_id, chunk_type, company_domain)
- SHA256 hashing for robustness

**Changes**:
- Modified `ingest/chunker.py` to generate content-hash-based IDs
- Added text normalization (lowercase, whitespace collapse)
- IDs are now deterministic: same content = same ID, different content = different ID
- Old chunk IDs can coexist with new ones (backward compatible)

**Impact**:
- New or modified chunks are now correctly embedded incrementally
- Unchanged chunks are skipped (no unnecessary re-embedding)
- Vector DB rebuilds are no longer required for correctness
- Phase 4.4 ingestion impact can now be measured correctly

**Status**: Complete - Ready for evaluation to measure Phase 4.4 impact

---

## Previous Phase: ✅ **Phase 4.4** - Data Quality & Coverage Audit (Complete)

### Phase 4.4: Data Quality & Coverage Audit (In Progress)

**Objective**: Improve RAG performance by improving the QUALITY and COVERAGE of knowledge, not by changing retrieval or ranking logic.

**Methodology**: Evaluation-driven diagnosis using test case expectations vs. actual chunk inventory.

**Target Requirements**: req_8 (AI/LLM APIs), req_9 (Product thinking), req_10 (Autonomous work) - weakest performers in evaluation.

**Status**: Diagnostic Complete - Planning Phase

**Key Findings**:
- All three requirements have insufficient depth and missing production patterns
- Failure modes are completely absent (0 chunks across all three requirements)
- Decision frameworks are missing or too generic
- Real-world constraints and startup context are under-represented

**Diagnostic Results**:
- **req_8**: 7 chunks total, missing production patterns (rate limiting, error handling, prompt engineering depth)
- **req_9**: 11 chunks total, missing decision frameworks (build vs buy, technical debt vs velocity)
- **req_10**: 3 chunks total, 2 empty source files, missing actionable strategies (task prioritization, burnout prevention)

**Documentation**: See `docs/DATA_QUALITY_AUDIT.md` for comprehensive analysis and source improvement plan.

**Next Steps**:
1. Execute planned ingestion actions (Priority 1: req_10, Priority 2: req_8, Priority 3: req_9)
2. Re-run evaluation after each priority to measure impact
3. Iterate based on evaluation results

---

## Previous Phase: ✅ **Complete** - System Functional

### Phase 4.3: Chunking & Retrieval Ranking Refinement (Completed - Reverted)

**Objective**: Improve retrieval ranking quality (MRR, nDCG) by refining chunking and retrieval signals, without changing embeddings, models, or evaluation logic.

**Baseline**: Phase 4.2 evaluation metrics (45 test cases, stable and trustworthy)

**Refinement 1: Dual-Retrieval Boost** ❌ (Reverted)
- **Change**: Chunks retrieved by both original and rewritten queries received a 15% similarity score boost
- **Rationale**: Dual retrieval as a signal of relevance - if both query variants retrieve the same chunk, it's likely highly relevant
- **Result**: Neutral retrieval impact - no measurable improvement in MRR or nDCG
- **Status**: Reverted - dual retrieval boost did not improve ranking quality

**Refinement 2: Chunk-Type-Aware Ranking Penalties** ❌ (Reverted)
- **Change**: Applied small multiplicative penalties to over-used chunk types during final ranking
  - `primary` chunks: 0.90 penalty (10% reduction)
  - `tradeoff` chunks: 0.88 penalty (12% reduction)
- **Motivation**: RAG Evaluation Dashboard evidence showed severe over-use:
  - `primary` chunks ≈ 6x expected usage
  - `tradeoff` chunks ≈ 8x expected usage
  - Generic chunks dominated rankings, hurting MRR for specific concepts
  - Weakest requirements (req_8, req_9, req_10) showed near-zero MRR and coverage
- **Result**: Mixed impact - some improvement in chunk type diversity but insufficient improvement in MRR and weakest-requirement coverage
- **Status**: Reverted - ranking heuristics were not the primary bottleneck

**Conclusion**:
Phase 4.3 tested two ranking refinement approaches:
1. Dual-retrieval boosting (neutral impact)
2. Chunk-type penalties (mixed impact, insufficient improvement)

**Key Findings**:
- Ranking heuristics alone did not address the core issue: weakest requirements show near-zero coverage and MRR
- The problem is not ranking noise but fundamental data quality and coverage gaps
- Simple similarity-based ranking (Phase 4.2 baseline) remains the most appropriate approach

**Decision**: All Phase 4.3 refinements have been reverted. Retrieval ranking is now restored to Phase 4.2 baseline behavior (pure similarity-based ranking, no heuristic adjustments).

**Next Phase**: Phase 4.4 will focus on data quality and coverage improvements rather than ranking heuristics.

---

## Previous Phase: ✅ **Complete** - System Functional

### Phase 4.1: Embedding Model Alignment Experiment (Completed - Reverted)

**Objective**: Evaluate the impact of embedding model choice on RAG retrieval quality.

**Experiment Design**:
- **Baseline**: `all-MiniLM-L6-v2` (sentence-transformers, local)
- **Experiment**: `text-embedding-3-small` (OpenAI, API-based)
- **Test Set**: "core" (same test cases as baseline)
- **Evaluation**: Offline evaluation harness (same metrics, same test cases)

**Results**:
- Evaluation completed on "core" test set with OpenAI embeddings
- **Outcome**: Regression observed in key retrieval metrics (MRR and nDCG decreased)
- **Decision**: Changes reverted to restore baseline MiniLM embeddings

**Conclusion**:
The OpenAI embedding model (`text-embedding-3-small`) did not improve retrieval quality compared to the baseline `all-MiniLM-L6-v2` model. Metrics showed regression, indicating that the local sentence-transformers model performs better for this use case. All Phase 4.1 code changes have been reverted, and the system now uses the original MiniLM embedding configuration.

**Note**: Evaluation artifacts from Phase 4.1 are preserved in `evaluation/runs/` for reference. The experiment demonstrates the importance of measuring changes rather than assuming improvements.

---

## Previous Phase: ✅ **Complete** - System Functional (Phase 4.0)

### Completed ✅

#### Data Ingestion
- ✅ Source discovery pipeline (`ingest/discoverer.py`)
- ✅ Browser-based fetching for bot-protected pages (`ingest/browser_fetcher.py`)
- ✅ Document normalization to Markdown
- ✅ LLM-based semantic chunking (`ingest/chunker.py`)
- ✅ Embedding generation (`ingest/embedder.py`)
- ✅ Vector database creation (local pickle-based storage)
- ✅ All 22 requirements have verified sources
- ✅ Company context (7 domains) verified from official sources

#### Core RAG Pipeline
- ✅ Vector store abstraction (`core/vector_store.py`)
- ✅ Knowledge retrieval with query rewriting (`core/retriever.py`)
- ✅ Strict answer generation with grounding (`core/answer_generator.py`)
- ✅ Interview mode orchestration (`core/modes.py`)

#### Interview Modes
- ✅ Explain Mode
- ✅ Interviewer Mode (with follow-up questions)
- ✅ Evaluation Mode
- ✅ Company-Aware Mode (Eventyr-specific)
- ✅ System Design Mode
- ✅ Rapid Fire Mode

#### Evaluation System
- ✅ LLM-as-a-judge evaluation (`evaluation/judge.py`) - Runtime answer evaluation
- ✅ Structured feedback (strengths, gaps, missed concepts, follow-ups)
- ✅ Confidence scoring (1-5 scale)

#### RAG Evaluation System (Offline)
- ✅ RAG evaluation orchestrator (`evaluation/rag_evaluator.py`)
- ✅ Pure metric calculation (`evaluation/metrics.py`) - MRR, nDCG, Recall, coverage
- ✅ Test case definitions (`evaluation/test_sets.py`) - Curated test sets
- ✅ Data contracts (`evaluation/data_contracts.py`) - Immutable evaluation structures
- ✅ Analysis layer (`evaluation/analysis.py`) - Weakest requirements, chunk types, mismatches, regression
- ✅ Offline evaluation runner (`evaluation/run_evaluation.py`)
- ✅ RAG Evaluation Dashboard (read-only UI tab)

#### Interview Simulator
- ✅ Interview Simulator (`core/interview_simulator.py`)
- ✅ Session lifecycle management
- ✅ Question generation from retrieved chunks
- ✅ Adaptive difficulty progression
- ✅ Answer evaluation integration
- ✅ Teaching on demand (4 types)
- ✅ Session persistence (JSON)
- ✅ Enhanced session summary generation with:
  - Strong/weak area identification
  - Difficulty progression analysis
  - Representative example questions
  - Export to JSON/Markdown
- ✅ Coverage visualization (requirement, topic, chunk type)
- ✅ Examiner personality tuning (strict/balanced/supportive)
- ✅ Multi-company/multi-role UI expansion (config-based dropdowns)

#### User Interface
- ✅ Gradio UI (`ui/app.py`) with multiple tabs
- ✅ Q&A Mode tab (traditional question-answer interface)
- ✅ Interview Simulator tab (system-driven questioning)
- ✅ RAG Evaluation Dashboard tab (read-only visualization)
- ✅ Mode selector
- ✅ Retrieved context viewer
- ✅ Answer and evaluation panels
- ✅ Debug mode with transparency
- ✅ Drill mode for conversation tracking (`ui/drill_mode.py`)
- ✅ Weakness tracking with persistence (`ui/weakness_tracker.py`)

#### Documentation
- ✅ README.md
- ✅ ARCHITECTURE.md
- ✅ STATUS.md
- ✅ USAGE.md
- ✅ SOURCE_PLAN.md
- ✅ DISCOVERY_STATUS.md

## Coverage Status

### Requirements (1-22)
- **Core Requirements (1-11):** Documented in `configs/requirements.yaml`
- **Plus Requirements (12-22):** Documented in `configs/requirements.yaml`
- **Coverage Verification:** Pending ingestion

### Company Context (Eventyr)
- **7 Domains:** Documented in `configs/company_context.yaml`
- **Source Discovery:** ✅ Complete - All domains verified from official job posting
  - Domain 1: ✅ CONFIRMED (Eventyr website: https://eventyr.pro/about-us)
  - Domain 2: ✅ CONFIRMED (Job posting: https://eventyr.pro/vacancy/ai-first-mern-fullstack-developer/)
  - Domain 3: ✅ CONFIRMED (Job posting)
  - Domain 4: ✅ CONFIRMED (Job posting)
  - Domain 5: ✅ CONFIRMED (Job posting)
  - Domain 6: ✅ CONFIRMED (Job posting)
  - Domain 7: ✅ CONFIRMED (Job posting)
- **Coverage Verification:** ✅ Complete - All information verified from official sources. Ready for ingestion.

## Implementation Details

### Data Ingestion Layer ✅
- ✅ Source discovery (`ingest/discoverer.py`) - HTTP + Playwright fallback
- ✅ Document normalization - Integrated in discoverer
- ✅ Semantic chunking (`ingest/chunker.py`) - LLM-based with structured outputs
- ✅ Embedding generation (`ingest/embedder.py`) - `all-MiniLM-L6-v2` (sentence-transformers)
- ✅ Vector store (`core/vector_store.py`) - Local pickle-based implementation

### RAG Pipeline Layer ✅
- ✅ Query rewriting - Integrated in `core/retriever.py`
- ✅ Retriever (`core/retriever.py`) - Dual retrieval with metadata filtering
- ✅ Answer generation (`core/answer_generator.py`) - Strict grounding, refusal support
- ✅ Mode orchestration (`core/modes.py`) - 6 interview modes

### Mode Layer ✅
- ✅ All 6 modes implemented in `core/modes.py`:
  - Explain, Interviewer, Evaluation, Company-Aware, System Design, Rapid Fire

### Evaluation Layer ✅
- ✅ LLM-as-a-judge (`evaluation/judge.py`) - Structured feedback generation

### Interview Simulator Layer ✅
- ✅ Interview Simulator (`core/interview_simulator.py`) - System-driven questioning
- ✅ Session management - Start, progress tracking, end with summary
- ✅ Question generation - Grounded in retrieved chunks
- ✅ Adaptive difficulty - Escalates/descalates based on performance
- ✅ Teaching integration - Uses existing AnswerGenerator for explanations
- ✅ Session persistence - JSON files in `data/interview_sessions/`

### UI Layer ✅
- ✅ Gradio interface (`ui/app.py`) - Full-featured with multiple tabs
- ✅ Q&A Mode tab - Traditional question-answer interface
- ✅ Interview Simulator tab - System-driven interview interface with:
  - Config-based company/requirement set dropdowns
  - Examiner personality selector
  - Coverage visualization panel
  - Enhanced session summary with export
- ✅ Drill mode (`ui/drill_mode.py`) - Conversation tracking
- ✅ Weakness tracker (`ui/weakness_tracker.py`) - JSON persistence

### Configuration & Extensibility ✅
- ✅ Config loader (`core/config_loader.py`) - Reads requirement sets and companies from YAML
- ✅ Multi-company support via company domain metadata
- ✅ Multi-role support via requirement set metadata
- ✅ UI dropdowns populated from configs (backwards compatible)

## Project Completion Status

**All core systems are complete and functional.**

The system is ready for use with:
- Full RAG pipeline (ingestion → retrieval → generation)
- 6 interview modes for Q&A
- Interview Simulator for system-driven practice
- Runtime answer evaluation and teaching capabilities
- RAG Evaluation System (offline evaluation harness)
- Drill Mode and Weakness Tracking
- Complete documentation

**RAG Evaluation**: The system includes a complete offline evaluation harness for measuring RAG quality. Evaluations are run explicitly via `evaluation/run_evaluation.py` and generate immutable artifacts. The UI provides read-only visualization of evaluation results. Metrics are baseline measurements used to track improvements through measured deltas between runs.

**Extensibility**: The architecture supports multiple requirement sets and companies through configuration and metadata. UI-level selection for multiple sets is designed for extensibility but not yet implemented.

## Notes

- Project follows Week 5 RAG patterns from `week5/pro_implementation/`
- Evaluation patterns from `week5/evaluation/`
- All requirements must pass coverage checklist before ingestion is considered complete
- Interview Simulator questions are generated from retrieved chunks (grounded, not synthetic)
- Teaching is strictly opt-in - system behaves as interviewer first