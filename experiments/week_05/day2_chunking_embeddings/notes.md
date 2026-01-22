## Day 2 – Chunking, Embeddings & Vector Stores

### Chunking Strategy – Recall vs Precision

Day 2 operationalizes a key idea from the videos: **chunking is a first‑class design decision**, not a detail. Larger chunks tend to have higher recall (they are more likely to contain the answer somewhere) but lower precision (they pull in a lot of irrelevant text, which can confuse the model). Smaller chunks increase precision but risk fragmenting context so much that no individual chunk is clearly relevant.

The recursive character splitter used in the notebook is a pragmatic default, but the videos make clear that “good” chunking is domain‑specific. For InsureLLM, contracts and policy docs might benefit from section‑ or clause‑aware splitting, while product and employee pages could use shorter, paragraph‑scale chunks. The important observation is that **chunking errors propagate directly into retrieval**: if the answer straddles two poorly chosen chunks, neither will be ranked highly and the system will appear to “miss” information it actually has.

### Encoder vs Vector Database Responsibilities

The videos draw a sharp line between **encoder models** and **vector databases**:

- Encoders (OpenAI embeddings, BERT, Hugging Face sentence encoders) are responsible for mapping text into a meaningful vector space.
- Vector DBs (Chroma, FAISS) are responsible purely for **indexing and similarity search** over those vectors.

In practice, this means that “bad retrieval” can be caused by either side:

- If the encoder produces poor embeddings (e.g., not tuned to the domain), semantically similar texts may not be near each other in vector space.
- If the vector DB is misconfigured (e.g., wrong distance metric, poor indexing parameters), even good embeddings won’t yield good neighbors.

The notebook primarily exercises one encoder + Chroma, but the conceptual model from the videos is broader: **encoders define the geometry; vector DBs search it**. Treating them as separate knobs is important when debugging retrieval quality later in the week.

### Chroma vs FAISS – Conceptual Comparison

Although the Day 2 notebook focuses on Chroma, the videos position FAISS as an alternative backend with a different tradeoff profile:

- **Chroma**: batteries‑included, developer‑friendly, with metadata filtering and persistence semantics that fit small‑to‑medium projects well.
- **FAISS**: lower‑level, optimized for large‑scale nearest‑neighbor search, often used as the engine inside custom retrieval systems.

From a conceptual standpoint, both implement the same idea—approximate nearest neighbors in vector space—but they differ in how much infrastructure they expect you to bring. For Week 05, Chroma is the right teaching tool; FAISS becomes more relevant when talking about scaling and productionization (foreshadowing some of the Day 5 topics).

### Embedding Model Comparisons (Video‑Level)

The videos highlight that embedding models differ along several axes:

- **Quality** – how well semantic similarity aligns with human judgment.
- **Latency / throughput** – how quickly embeddings can be generated.
- **Cost** – API pricing for hosted encoders vs local models.

In the notebook, the primary choice is between OpenAI embeddings and a Hugging Face encoder like `all-MiniLM-L6-v2`. The latter offers a good local baseline, while OpenAI’s models may offer higher quality at a cost. A key insight is that **embedding choice is as important as base LLM choice**: a strong generator paired with weak embeddings will still perform poorly in RAG.

### How Chunking Errors Propagate into Retrieval Failures

The most important cross‑day observation is that chunking is upstream of **everything**:

- Overly large chunks dilute the relevance signal: embeddings represent “the average” of a lot of content, so a small relevant section may be drowned out by surrounding text.
-
- Overly small chunks increase noise: many small pieces look similarly relevant, making it harder for the retriever to distinguish which ones actually answer the question.
- Boundary errors (e.g., splitting mid‑sentence or across logical sections) can make every chunk slightly off, so none of them passes a relevance threshold.

By Day 4, these decisions show up as lower retrieval metrics (MRR, nDCG) even if the base LLM and encoder are strong. Day 5’s semantic chunking with LLMs is essentially a response to this: use a model to design chunks that better match how questions will be asked, instead of relying purely on mechanical splitting rules.

### Questions to Revisit on Day 4 and Day 5

- How much do evaluation results (Day 4) change when:
  - Increasing/decreasing chunk size?
  - Switching encoders (OpenAI vs HF) while holding Chroma constant?
- Which documents or categories are consistently mis‑retrieved, and is that traceable to chunking decisions?
- For Day 5: which parts of the KB seem like good candidates for **LLM‑driven semantic chunking** rather than simple recursive splitting?

These questions turn Day 2 from a one‑off ingest script into a configurable component that can be tuned and revisited as evaluation data accumulates.

