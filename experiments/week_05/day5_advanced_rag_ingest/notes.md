## Day 5 – Advanced & Production RAG

### Chunk Schema & Design Choices

The Day 5 notebook introduces a richer chunk schema (`Chunk`, `Chunks`, `Result`) that goes beyond raw text spans. Each chunk carries a **headline**, a **summary**, and the **original text**, which are then composed into a single `page_content` string for storage. This design reflects a core idea from the videos: the retriever should index something that already looks like a good answer surface, not just arbitrary slices of text.

This schema helps retrieval in two ways:

- The headline and summary give the embedding model concentrated, high‑signal text that captures what the chunk is “about.”
- The original text preserves exact phrasing for cases where precise wording matters (e.g., contract clauses).

However, it also introduces new risks: if the LLM produces poor summaries or misleading headlines, the retriever will learn a distorted view of the KB. In other words, **advanced ingest can amplify model errors** if not paired with careful evaluation (Day 4).

### LLM‑Driven Ingest Behavior

Compared to the mechanical recursive splitting in Day 2, LLM‑driven chunking is much more aligned with how humans would segment information: by topic, intent, or likely question type. For example, a long policy document might be segmented into chunks like “Eligibility Criteria,” “Coverage Details,” and “Exclusions,” each with its own summary. This makes it far easier for the retriever to surface a chunk that directly addresses a user query.

That said, the behavior of the ingest LLM is itself a function of prompts and model choice. If the prompt is vague or the model underpowered, chunks may be too generic (“General policy information”) or too noisy, reducing the benefits of the richer schema. The videos stress that **semantic chunking is powerful but not free**: it adds another layer that must be tuned and evaluated, not just assumed to be better.

### Re‑ranking, Query Rewriting & Expansion (Video Concepts)

The Day 5 curriculum introduces several advanced retrieval techniques that are not fully implemented in the notebook but are natural extensions of the current pipeline:

- **Re‑ranking** – After retrieving k candidates from the vector store, use an LLM or a smaller ranking model to reorder them based on how well they answer the specific question. In the InsureLLM setting, this could prioritize chunks that mention key entities (customer names, product IDs, policy numbers) present in the query.
- **Query rewriting** – Transform the user’s raw question into a more retrieval‑friendly form (e.g., expanding abbreviations, making implicit references explicit). This helps bridge the gap between conversational phrasing and formal KB language.
- **Query expansion** – Generate related queries (synonyms, alternative formulations) and retrieve across all of them, then merge and deduplicate the results.

All three techniques aim to **improve recall and ranking without changing the underlying KB**, and they sit naturally on top of the semantic chunks produced in Day 5. Evaluation from Day 4 would then be used to validate whether these techniques actually move metrics in the right direction.

### GraphRAG & Knowledge Structure

GraphRAG, as presented in the videos, reframes retrieval around **entities and relationships** rather than just text similarity. For InsureLLM, this might involve nodes for employees, products, policies, and contracts, with edges representing relationships (e.g., “Maxine Thompson → won → IIOTY 2023,” “Policy X → covers → Product Y”). Queries then become graph traversals plus text search, which can capture multi‑hop questions more naturally than pure vector search.

While the current implementation does not build an explicit graph, the semantic chunks created in Day 5 are a stepping stone: they often contain structured summaries that identify key entities and roles. A future GraphRAG system could extract these entities and relationships from chunks and build a graph index alongside the vector store, using Day 4 evaluation to verify that it actually improves multi‑hop and relational queries.

### Impact on Retrieval & Evaluation

Advanced ingest techniques change the distribution of retrieved chunks in subtle ways:

- Retrieval becomes more **semantically focused**: chunks tend to be topically coherent and directly answerable.
-
- Rank‑based metrics should improve if re‑ranking and semantic chunking succeed—relevant chunks move closer to the top of the list, improving both MRR and nDCG.
- Failure cases become more interpretable: when the system is wrong, it is often because the semantic chunk itself encoded an incomplete or misleading view of the underlying document.

This tightens the feedback loop between ingest (Day 5) and evaluation (Day 4): changes to chunking or re‑ranking can be quickly reflected in test metrics and used to iterate on prompts or configurations.

### Ideas for Future Productionization

The videos close by pointing out that **production RAG is an engineering problem as much as a modeling problem**. For the InsureLLM assistant, that implies:

- Designing a proper **ingest pipeline** that:
  - Watches for new or updated documents.
  - Regenerates semantic chunks safely and idempotently.
  - Writes embeddings and metadata into Chroma (or another store) in a transactional way.
- Using **multiprocessing or distributed workers** to scale ingest to large contract corpora without blocking the online system.
- Instrumenting the system with **logging and monitoring** so that retrieval quality, latency, and evaluation metrics are tracked over time.
- Treating RAG as a **benchmarking and iteration loop**, not a one‑off project: as new models, chunking strategies, or retrieval techniques appear, they are evaluated against the existing golden dataset and only promoted if they provide measurable benefits.

Day 5, therefore, is less about a single “advanced” architecture and more about adopting a **mindset**: RAG is an evolving system whose ingest, retrieval, and evaluation components must be co‑designed and continuously refined.

