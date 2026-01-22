## Day 1 – RAG Foundations & Brute‑Force Assistant

### Implementation Observations

The Day 1 notebook delivers a very direct, dictionary‑style RAG assistant: it loads files from the InsureLLM knowledge base, performs simple keyword or path‑based lookup, and hands whatever it finds to an LLM. On narrow, factual questions that line up cleanly with filenames or obvious keywords, this feels “good enough” and creates the illusion that retrieval is solved. As soon as questions become slightly more natural (“Who won the internal innovation award last year?” instead of “IIOTY winner 2023”), the limitations show up: relevant context may exist in the KB, but the lookup logic never finds it.

The key takeaway is that **“having the data” is not the same as “retrieving the right slice of it.”** Retrieval quality is tightly coupled to how close the user’s phrasing is to the raw text or filenames. This is consistent with the video framing: Day 1 is intentionally naïve so the need for embeddings and vector stores is felt empirically, not just explained theoretically.

### Knowledge Base Coverage

The InsureLLM knowledge base mixes company pages, product descriptions, contracts, and employee profiles. In the brute‑force prototype, all of these are treated essentially the same. Short, well‑named pages (e.g., product overviews) tend to work acceptably with basic search, while long contracts and dense employee lists expose the lack of structure. Either you retrieve too much text (entire documents) or you miss the relevant passage entirely.

This uneven coverage highlights why **KB structure matters**. Without chunking or indexing, the assistant cannot distinguish between “this file is generally relevant” and “this paragraph is exactly what we need.” The videos emphasize that RAG accuracy is as much about preparing the knowledge base as it is about choosing the right model.

### Failure Cases & Early Hallucinations

Two recurring failure modes:

- **No useful context retrieved** – The lookup misses the relevant file, so the LLM answers from prior knowledge or patterns, often hallucinating specifics (names, dates, policy details) that never appear in the KB.
- **Loosely related context retrieved** – The system finds something “in the right ballpark” (e.g., a general contracts summary) but not the precise answer. The LLM then blends that context with its own priors, producing plausible but unfounded statements.

In both cases, the user has almost no visibility into why the answer is wrong. There is no ranked list of candidates, no notion of retrieval confidence, and no clear signal that the KB was not actually consulted successfully. This opacity is exactly what later days (especially Day 3 UI and Day 4 evaluation) are designed to fix.

### Why Brute‑Force Lookup Fails Semantically

From the Day 1 videos: dictionary lookup gives, at best, **lexical overlap**, not **semantic similarity**. If the user asks about “our flagship auto insurance product,” but the KB uses the internal product name “Carllm,” a pure string‑based system may never connect the two. Similarly, questions that rely on paraphrase, aggregation, or implied context are especially brittle.

This semantic gap shows up most clearly when:

- The question uses synonyms instead of the exact words in the KB.
- The answer spans multiple documents or sections that are never retrieved together.
- The question is high‑level (“How do we reward top performers?”) and the relevant detail is buried in a specific HR policy document.

In each case, the system fails not because the KB lacks the answer, but because the retrieval layer cannot recognize that the question and the relevant passages “mean the same thing.”

### Embeddings & Vector Stores – Intuition from the Videos

The videos introduce embeddings as a way to encode meaning into geometry: semantically similar texts map to nearby points in a high‑dimensional space. Encoder models (OpenAI, BERT, HF encoders) are trained so that “Maxine Thompson won the IIOTY award in 2023” and “Who won the prestigious IIOTY award last year?” are close, even though their surface forms differ.

Vector stores (Chroma, FAISS) then act as **semantic search engines**: instead of matching substrings, they retrieve the nearest neighbors in embedding space. Day 1 does not implement this yet, but the failures of brute‑force lookup make the motivation concrete: we need a retrieval mechanism that understands meaning, not just text overlap.

### Motivation for Day 2 and Beyond

Day 1 establishes the baseline and its shortcomings:

- Retrieval is brittle and opaque.
- Hallucinations are common when lookup fails.
- The KB is rich but not query‑friendly.

This naturally motivates:

- **Day 2** – Introduce chunking and embeddings so retrieval operates on semantically meaningful units, backed by a vector store.
- **Day 3** – Wrap retrieval + LLM into a well‑structured pipeline with UI hooks and, eventually, conversation history.
- **Day 4** – Quantify performance with an evaluation harness, turning “seems good” into measurable metrics.
- **Day 5** – Explore advanced ingest and production patterns (semantic chunking with LLMs, re‑ranking, query rewriting) to close the remaining gaps.

In short, Day 1 proves that a simple assistant is possible, but also that **brute‑force retrieval caps accuracy and trustworthiness**, which the rest of the week is designed to address.

