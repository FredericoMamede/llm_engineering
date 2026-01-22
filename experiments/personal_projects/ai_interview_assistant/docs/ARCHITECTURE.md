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
- Metadata-aware filtering
- Configurable top-K and final-K
- Strict context injection (no free generation)
- Refusal behavior when context insufficient
- Interview mode-specific configurations

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
- `evaluation/judge.py`: LLM-as-a-judge evaluation

**Key Features:**
- Structured feedback (strengths, gaps, missed concepts, follow-ups)
- Confidence scoring (1-5 scale)
- Grounded evaluation (only uses retrieved chunks)
- Robust parsing of LLM evaluation responses

### 5. UI Layer

**Components:**
- `ui/app.py`: Gradio interface
- `ui/drill_mode.py`: Drill mode conversation tracking
- `ui/weakness_tracker.py`: Weakness tracking with JSON persistence

**Key Features:**
- Mode selector
- Retrieved context viewer with badges and highlighting
- Answer + evaluation panel
- Debug visibility (similarity scores, retrieval metadata)
- Drill mode for iterative practice
- Weakness tracking with automatic persistence
- Confidence badges and visual indicators

## Data Flow

### Ingestion Flow

```
1. Requirement Enumeration (22 requirements + company context)
2. Source Discovery (web scraping, official docs)
3. Normalization (clean Markdown)
4. Semantic Chunking (LLM-based with structured outputs)
5. Embedding (all-MiniLM-L6-v2)
6. Vector Store (Chroma with metadata)
7. Coverage Verification (checklist per requirement)
```

### Query Flow

```
1. User Query + Mode Selection
2. Query Rewriting (original + rewritten)
3. Dual Retrieval (both queries, top-K each)
4. Merge Results
5. Re-ranking (LLM-based, structured output)
6. Context Validation (sufficient coverage check)
7. Mode-Specific Prompt Construction
8. Answer Generation (strict context injection)
9. Evaluation (LLM-as-a-judge)
10. Response (answer + evaluation + sources)
```

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

1. Create new mode file in `modes/`
2. Implement mode interface
3. Add mode to UI selector
4. System automatically supports new mode

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

Chroma stores:
- Document text (headline + summary + original_text)
- Embedding vector
- Metadata (all fields above)
- ID (unique identifier)

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

- **Retrieval Metrics**: Track retrieval success rates
- **Re-ranking Metrics**: Track re-ranking quality
- **Answer Quality**: Track evaluation scores
- **Source Freshness**: Monitor source age
- **Coverage**: Track requirement coverage completeness
