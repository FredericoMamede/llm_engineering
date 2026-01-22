## Day 2 – Chunking, Embeddings & Vector Stores

### Goal of the Day

Design and build the **knowledge preparation** side of RAG:

- Break raw documents into useful **chunks**.
- Convert chunks into **vector embeddings**.
- Store them in a **vector database (Chroma)** for later querying.
- Connect concrete code to the broader landscape of encoder models and vector DBs.

### RAG Concepts Explored

#### Implemented in notebooks

- **Chunking documents with LangChain text splitters**:
  - Recursive character text splitter and related strategies.
  - Control over chunk size and overlap.
- **Creating vector stores with Chroma**:
  - Persisting embeddings for the InsureLLM knowledge base.
  - Querying by similarity against stored vectors.
- **Encoder models for embeddings**:
  - Using OpenAI or Hugging Face embedding models as encoders.
- **Visualizing embeddings with t‑SNE**:
  - Projecting high‑dimensional vectors into 2D for inspection.

#### Conceptual / instructional (video-only)

- **Vectors for RAG: LangChain + vector DBs**:
  - How retrievers, embeddings, and vector stores fit together.
- **Encoder models vs vector databases**:
  - Encoder models (OpenAI, BERT, HF) **produce vectors**.
  - Vector DBs (Chroma, FAISS, etc.) **store and search** those vectors.
- **OpenAI, BERT, Chroma, FAISS comparison**:
  - Tradeoffs between different encoders and backends:
    - Quality, latency, cost, and ecosystem maturity.

#### Partially explored / future extension

- Swapping **Chroma** for **FAISS** or other vector DBs with the same ingest pipeline.
- Systematic experiments that:
  - Compare different encoders (OpenAI vs BERT vs HF).
  - Compare Chroma vs FAISS on the same InsureLLM corpus.

### Relationship to Course Materials

- **Primary source notebook:** `week5/day2.ipynb`
- Uses:
  - `knowledge-base/` documents as input.
  - Chroma as the persistent vector store.
  - Optional visualizations (e.g. t‑SNE) to inspect embedding space.
- This README adds explicit references to **vector DB comparisons** and **encoder vs DB separation** that are emphasized in the videos.

### Why This Day Exists

This day introduces a **clean separation** between:

- **Ingest / indexing** (preparing knowledge into a vector DB).
- **Question answering** (which happens in later days using this DB).

It answers the question:  
*“How do we turn a messy knowledge base into something a RAG system can query effectively, and how do encoder + vector DB choices affect that?”*

### Notebook Placement

- The **authoritative notebook** for this day lives at: `week5/day2.ipynb`.
- This folder is a **scaffold** for code‑first re‑implementations or experiments around chunking, embeddings, and vector DB tradeoffs that are discussed in the videos.

