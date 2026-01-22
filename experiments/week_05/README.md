## Week 5: Retrieval-Augmented Generation (RAG) – Expert Knowledge Worker

> **Theme:** Building, evaluating, and iterating on an accurate, low‑cost RAG system for an internal “Expert Knowledge Worker” assistant.

---

## Week Structure (Derived from Course Notebooks + Video Curriculum)

This structure is **directly derived** from:

- The core Week 05 notebooks in `week5/`:
  - `week5/day1.ipynb`
  - `week5/day2.ipynb`
  - `week5/day3.ipynb`
  - `week5/day4.ipynb`
  - `week5/day5.ipynb`
- The **full Week 05 video curriculum**, which introduces additional conceptual topics that may be only lightly present or implicit in notebooks.

The `experiments/week_05/` folder mirrors those days and provides a **code-first, documentation-led scaffold**, similar to Week 4.  
Documentation here is meant to **complete the learning loop**: notebooks are necessary but **not sufficient** to cover all RAG concepts taught in Week 05.

---

## Day-by-Day Curriculum Mapping

Each day combines:

- **Implemented in notebooks** – concepts you can see directly in `week5/dayX.ipynb` and supporting code.
- **Conceptual / instructional (video-only)** – topics covered in lectures, even if not fully implemented.
- **Partially explored / future extension** – ideas that appear briefly or are natural next steps for experiments.

### Day 1 – RAG Foundations & Simple Knowledge Assistant

- **Source notebook:** `week5/day1.ipynb`
- **RAG Style:** Simplistic / brute‑force retrieval over the knowledge base.
- **Why this day exists:** Establishes the baseline RAG pipeline and business context (internal employees, accuracy + low cost).

**Implemented in notebooks**
- Building a simple **RAG knowledge assistant** for InsureLLM.
- Dictionary / file‑based **context retrieval** over the internal knowledge base.
- Initial integration of an LLM to answer questions given retrieved context.

**Conceptual / instructional (video-only)**
- **Introduction to RAG**: high‑level Retrieval‑Augmented Generation fundamentals.
- **Vector embeddings and encoder LLMs** as the backbone of modern RAG.
- **How embeddings represent meaning** (from word2vec intuition to modern encoders).
- **Big picture:** Why RAG + vector stores matter for accuracy, controllability, and cost.

**Partially explored / future extension**
- Transition path from dictionary / brute‑force lookup to vector‑based retrieval.
- System‑design tradeoffs when choosing between pure LLM vs RAG‑augmented answers.

### Day 2 – Chunking, Embeddings & Vector Stores

- **Source notebook:** `week5/day2.ipynb`
- **Focus:** Turning raw documents into chunks, embedding them, and storing them in a vector DB.

**Implemented in notebooks**
- Chunking documents with **LangChain text splitters** (recursive text splitting).
- Creating **vector stores with Chroma** from the InsureLLM knowledge base.
- Using **encoder models** (OpenAI / Hugging Face) to produce embeddings.
- **Visualizing embeddings with t‑SNE** to inspect structure in vector space.

**Conceptual / instructional (video-only)**
- **Vectors for RAG:** end‑to‑end picture of LangChain + vector DBs for retrieval.
- **Encoder models vs vector databases:** clear separation of concerns.
- Comparison between **OpenAI, BERT, Chroma, FAISS**:
  - Encoders (OpenAI, BERT) vs storage/search backends (Chroma, FAISS).

**Partially explored / future extension**
- Swapping Chroma for FAISS or other vector stores while keeping the same ingest pipeline.
- Systematic experiments comparing different encoder models and DB backends.

### Day 3 – RAG with Memory & UI

- **Source notebook:** `week5/day3.ipynb`
- **Focus:** LangChain‑based RAG pipeline that queries the vector store; early UI hooks.

**Implemented in notebooks**
- LangChain RAG pipeline combining:
  - **Retriever** (Chroma + embeddings).
  - **LLM** (e.g. `gpt-4.1-nano` via `ChatOpenAI`).
- Use of **HuggingFaceEmbeddings** consistent with Day 2.
- Minimal or prototype **Gradio UI** for an “Expert Question Answerer”.

**Conceptual / instructional (video-only)**
- **RAG with conversation history / memory**:
  - How prior turns influence retrieval and responses.
  - Why memory changes failure modes vs single‑turn RAG.
- **Building a robust Gradio UI for RAG**:
  - Inputs, outputs, and debugging aids for retrieval.
- **Debugging chunk retrieval**:
  - Inspecting which chunks were fetched.
  - Diagnosing “wrong context” vs “no context” failures.
- **Practical failure modes in conversational RAG**:
  - Drift in long conversations.
  - Over‑reliance on stale or irrelevant chunks.

**Partially explored / future extension**
- Adding explicit conversation memory components to the pipeline.
- UI affordances for showing retrieved context and ranking information.

### Day 4 – RAG Evaluation & Iteration

- **Source notebook:** `week5/day4.ipynb`
- **Focus:** Systematic evaluation of RAG quality using a test harness.

**Implemented in notebooks**
- Loading and running tests from `evaluation/` (e.g. `evaluation/tests.jsonl`).
- Using labeled examples and categories like `direct_fact` to assess performance.
- Driving the existing RAG pipeline (from Day 3) through the evaluator.

**Conceptual / instructional (video-only)**
- **Measuring RAG performance** with retrieval‑oriented metrics:
  - **MRR (Mean Reciprocal Rank)**.
  - **nDCG (Normalized Discounted Cumulative Gain)**.
- **Golden datasets & test data (JSONL)**:
  - How to curate and structure test cases.
- **LLM‑as‑a‑Judge (structured outputs)**:
  - Using an LLM to score answers and reasons.
- **Evaluation pipelines with Gradio**:
  - Interactive inspection of failures and scores.
- **Experimenting with chunking & embedding strategies**:
  - Running A/B trials on different ingest configs.
- **Measuring gains from improved embeddings**:
  - Connecting embedding/model choices to observable metric improvements.

**Partially explored / future extension**
- Adding explicit metric computations (MRR, nDCG) on top of the existing evaluator.
- Visual dashboards for tracking evaluation over time and configuration changes.

### Day 5 – Advanced & Production RAG

- **Source notebook:** `week5/day5.ipynb`
- **Focus:** More advanced ingest and preprocessing for RAG; pro‑level patterns.

**Implemented in notebooks**
- **RAG without LangChain**:
  - Native Python ingest using the OpenAI client and Chroma directly.
- **Semantic chunking with LLMs**:
  - LLM‑driven creation of `Chunk` / `Chunks` / `Result` objects.
- Storing enriched chunks (headline + summary + original text) in Chroma.

**Conceptual / instructional (video-only)**
- **Advanced preprocessing** for RAG knowledge bases.
- **Re-ranking strategies**:
  - Re‑ordering retrieved chunks using LLMs or secondary models.
- **Query rewriting and query expansion**:
  - Transforming user questions into more retrieval‑friendly forms.
- **GraphRAG concepts**:
  - Using graphs and relationships in addition to pure vector similarity.
- **Production RAG patterns**:
  - Separation of ingest vs query services.
  - Caching, monitoring, and observability.
- **Multiprocessing ingestion**:
  - Parallelizing ingest to handle larger corpora.
- **Advanced evaluation improvements**:
  - Combining retrieval metrics with LLM‑as‑judge.
- **RAG challenge & benchmarking mindset**:
  - Treating RAG as an ongoing optimization problem, not a one‑off feature.

**Partially explored / future extension**
- Implementing re‑ranking, query rewriting, query expansion, and GraphRAG variants on top of the existing ingest pipeline.
- Scaling the current prototypes toward production‑ready architectures.

---

## Folder Structure

```text
experiments/week_05/
├── README.md                      # This file – week overview and mapping to notebooks
├── week_05_observations.md        # Synthesized cross-day findings and patterns
├── day1_intro_bruteforce_rag/     # Day 1 – Baseline “brute-force” RAG assistant
├── day2_chunking_embeddings/      # Day 2 – Chunking + embeddings + Chroma
├── day3_langchain_rag_pipeline/   # Day 3 – LangChain RAG over existing vector DB
├── day4_rag_evaluation/           # Day 4 – RAG evaluation harness and tests
└── day5_advanced_rag_ingest/      # Day 5 – Advanced ingest and LLM-powered chunking
```

**Important:**
- The **authoritative implementations** remain under `week5/` (e.g. `week5/day3.ipynb`, `week5/implementation/`, `week5/pro_implementation/`, `week5/evaluation/`, `week5/app.py`).
- The `experiments/week_05/` subtree is a **structure + documentation mirror**, designed to support code‑first refactors or future extensions without changing the original course materials.
- The documentation here explicitly includes **all topics from the Week 05 videos**, even when a concept is:
  - Only lightly present in notebooks, or
  - Not implemented yet and better treated as a **future extension**.

---

## Usage Notes

- Start with each day’s `README.md` to understand:
  - The specific RAG concept being explored
  - How it builds on previous days
  - How it relates back to the “Expert Knowledge Worker” business context
- Read `week_05_observations.md` for synthesized cross-day findings:
  - Cross‑day design decisions and their consequences
  - Tradeoffs between brute‑force vs. vector‑DB vs. advanced ingest
  - How chunking and embedding choices propagate into evaluation results
  - How Day 5 techniques build on Days 1–4 to move toward production RAG
  - Open questions to explore in later weeks.

**Notebooks are necessary but not sufficient**:  
To fully learn Week 05, you should:

- Run and read the notebooks in `week5/`.
- Read the per‑day docs in `experiments/week_05/`.
- Use `notes.md` and `week_05_observations.md` to connect video concepts to concrete experiments.

