## Day 5 – Advanced & Production RAG Patterns

### Goal of the Day

Explore **advanced ingest, retrieval, and evaluation** techniques that move the system toward **production‑grade RAG**:

- Use an LLM to create semantically meaningful chunks.
- Enrich chunks with summaries and headlines.
- Store richer representations in a vector database.
- Introduce pro‑level ideas like re‑ranking, query rewriting, and production patterns.

### RAG Concepts Explored

#### Implemented in notebooks

- **RAG without LangChain**:
  - Native Python ingest using the OpenAI client and Chroma directly.
- **Semantic chunking with LLMs**:
  - LLM‑driven creation of `Chunk`, `Chunks`, and `Result` objects.
  - Chunks with headline + summary + original text for better retrieval.
- **Advanced preprocessing**:
  - Document‑level transformations before embedding/indexing.

#### Conceptual / instructional (video-only)

- **Re-ranking strategies**:
  - Re‑ordering retrieved chunks using secondary scoring (e.g. LLM or heuristic).
- **Query rewriting & query expansion**:
  - Transforming user questions into alternative phrasings / related queries to improve recall.
- **GraphRAG concepts**:
  - Using graph structures (entities, relationships) to complement vector search.
- **Production RAG patterns**:
  - Clear separation between ingest and query services.
  - Monitoring, logging, and safe deployment patterns.
- **Multiprocessing ingestion**:
  - Scaling ingest to large corpora via parallel processing.
- **Advanced evaluation improvements**:
  - Combining Day 4 metrics with new signals (e.g. re‑ranker scores, LLM‑judge outputs).
- **RAG challenge & benchmarking mindset**:
  - Treating RAG as an ongoing optimization and benchmarking problem.

#### Partially explored / future extension

- Implementing **re‑ranking, query rewriting, and query expansion** on top of the existing ingest pipeline.
- Experimenting with **GraphRAG‑style** indices for the InsureLLM knowledge base.
- Hardening the current prototypes into **production‑like services** with proper ingest pipelines and monitoring.

### Relationship to Course Materials

- **Primary source notebook:** `week5/day5.ipynb`
- Uses:
  - `knowledge-base/` as input.
  - Native Python + OpenAI client (no LangChain) for maximum control.
  - Chroma as the target vector store for enriched chunks.
  - `week5/pro_implementation/ingest.py` for the concrete semantic chunking + multiprocessing ingest implementation.
  - `week5/pro_implementation/answer.py` for the concrete query-rewrite + re-ranking pipeline.
- This README documents the broader **advanced RAG and production patterns** that are taught in the videos, beyond what is fully implemented in the notebook.

### Why This Day Exists

This day shows how to:

- Push beyond “good enough” RAG into more **task‑aligned knowledge representations**.
- Introduce **pro‑level techniques** that build directly on:
  - Foundations from Day 1.
  - Chunking and embeddings from Day 2.
  - Pipelines and memory from Day 3.
  - Evaluation and iteration from Day 4.

It sets the stage for future weeks where:

- Productionization.
- Scaling.
- Multi‑tenant or multi‑KB setups.

become central concerns.

### Notebook Placement

- The **authoritative notebook** for this day lives at: `week5/day5.ipynb`.
- This folder provides a **home** for any advanced ingest scripts or experiments derived from that notebook, plus future work on re‑ranking, query rewriting, GraphRAG, and production patterns.

