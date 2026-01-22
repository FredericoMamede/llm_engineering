## Week 5 – RAG: Cross‑Day Observations

> Use this file to collect insights that span multiple days.  
> Keep it **descriptive**, not prescriptive – no conclusions, just observations.

---

### 1. Knowledge Base & Business Context

The InsureLLM knowledge base mixes heterogeneous document types: short product pages, dense contracts, employee profiles, and company policy documents. Day 1's brute‑force approach treats all of these identically, which exposes the core problem: without structure, the system cannot distinguish between "this file is generally relevant" and "this paragraph is exactly what we need." Short, well‑named pages (e.g., product overviews) work acceptably with basic search, while long contracts and dense employee lists either return too much text (entire documents) or miss the relevant passage entirely.

This uneven coverage persists even after Day 2 introduces chunking and embeddings. The recursive character splitter is domain‑agnostic, so contracts and policy docs that would benefit from section‑aware splitting are still fragmented mechanically. Day 5's semantic chunking with LLMs addresses this by producing topic‑aligned segments (e.g., "Eligibility Criteria," "Coverage Details"), but introduces a new dependency: the quality of the ingest LLM's segmentation directly affects retrieval quality downstream.

The business context (internal employees, accuracy + low cost) constrains choices throughout the week. For example, the tradeoff between OpenAI embeddings (higher quality, API cost) and local Hugging Face encoders (lower cost, potentially lower quality) is evaluated not just technically but against the "low cost" requirement. Similarly, the evaluation harness in Day 4 focuses on answerable questions within the KB rather than open‑ended chat, keeping failures traceable to retrieval, context construction, or prompt behavior rather than training data gaps.

### 2. Retrieval Strategies

Day 1's dictionary lookup provides lexical overlap at best, not semantic similarity. Questions that use synonyms, paraphrases, or implied context fail even when the KB contains the answer, because the retrieval layer cannot recognize that the question and relevant passages "mean the same thing." This creates a clear empirical motivation for vector‑based retrieval: the system fails not because the KB lacks information, but because the retrieval mechanism doesn't understand meaning.

Day 2 and Day 3 show that vector search improves robustness, but not uniformly. Direct factual lookups (e.g., "Who won IIOTY in 2023?") map cleanly to short, well‑defined KB snippets and perform well once the vector store is populated. Multi‑hop or synthesis questions expose weaknesses: the system may retrieve only one of the necessary documents, leading to partially correct answers. The semantic gap between question phrasing and KB language remains, though it's narrower than with brute‑force lookup.

The videos introduce re‑ranking, query rewriting, and query expansion as techniques to improve recall and ranking without changing the underlying KB. These sit naturally on top of Day 5's semantic chunks, but their impact is hypothetical until measured against Day 4's evaluation harness. The observation is that retrieval strategy is not a one‑time choice but a stack of techniques that can be layered and tuned based on measured outcomes.

### 3. Chunking & Embeddings

Chunking is upstream of everything. Day 2 establishes that larger chunks tend to have higher recall but lower precision (they pull in irrelevant text that confuses the model), while smaller chunks increase precision but risk fragmenting context so much that no individual chunk is clearly relevant. Boundary errors—splitting mid‑sentence or across logical sections—can make every chunk slightly off, so none passes a relevance threshold. If an answer straddles two poorly chosen chunks, neither will be ranked highly, and the system appears to "miss" information it actually has.

These chunking decisions propagate directly into Day 4's evaluation results. Overly large chunks dilute the relevance signal: embeddings represent "the average" of a lot of content, so a small relevant section may be drowned out by surrounding text. Overly small chunks increase noise: many small pieces look similarly relevant, making it harder for the retriever to distinguish which ones actually answer the question. Even with strong base LLMs and encoders, poor chunking shows up as lower retrieval metrics (MRR, nDCG).

Day 5's LLM‑driven semantic chunking is essentially a response to this: use a model to design chunks that better match how questions will be asked, instead of relying purely on mechanical splitting rules. However, it introduces new risks. If the ingest LLM produces poor summaries or misleading headlines, the retriever learns a distorted view of the KB. Advanced ingest can amplify model errors if not paired with careful evaluation. The tradeoff is that semantic chunking adds another layer that must be tuned and evaluated, not just assumed to be better.

The videos draw a sharp line between encoder models and vector databases: encoders define the geometry (mapping text into meaningful vector space), while vector DBs search it (indexing and similarity search). In practice, "bad retrieval" can be caused by either side. If the encoder produces poor embeddings (e.g., not tuned to the domain), semantically similar texts may not be near each other in vector space. If the vector DB is misconfigured (wrong distance metric, poor indexing parameters), even good embeddings won't yield good neighbors. Treating them as separate knobs is important when debugging retrieval quality.

### 4. RAG Pipelines & Tooling

Day 1's ad‑hoc notebook code wires retrieval and LLM together directly, making it hard to reason about where failures occur. Day 3's LangChain pipeline formalizes this into a chain: retriever backed by Chroma, ChatOpenAI model, and a simple chain that plugs retrieved documents into a prompt. This structure makes responsibilities clearer (retrieval happens first, then the LLM reasons over context) and surfaces configurable parameters (top‑k, temperature, model choice) that were previously buried in notebook code.

The chain abstraction is strong at composability: the same retriever can be reused across chains, and the same LLM can be swapped in and out. Its main weakness is that if retrieval is wrong, the chain has no internal notion of "this looks suspicious." Evaluation (Day 4) and UI support (Day 3) are needed to close that loop. Even a minimal Gradio UI underscores that RAG is much easier to debug when you can see what was retrieved—distinguishing "retrieval failed" from "LLM mis‑used a good context" requires visibility into the pipeline's intermediate steps.

Day 5 returns to a native (no‑LangChain) approach for advanced ingest, using direct OpenAI client calls for maximum control over chunking and summarization. This suggests that different pipeline stages benefit from different levels of abstraction: ingest may need fine‑grained control, while the query‑time RAG chain benefits from LangChain's composability. The observation is that tooling choice is not uniform across the pipeline; it depends on which stage you're optimizing for.

### 5. Evaluation

Day 4's evaluation harness reveals gaps between "looks good in a single query" and "holds up across many test cases." Performance varies by category: direct factual lookups tend to do well once the vector store is populated, while multi‑hop or synthesis questions expose weaknesses in both retrieval and answer composition. Ambiguous or underspecified questions highlight the system's tendency to guess rather than abstain. Tracking performance per category is important because different failure patterns suggest different fixes (chunking vs embeddings vs prompting), and lumped averages can hide those signals.

Raw "accuracy" (proportion of questions answered exactly as in the reference) is a blunt tool. It doesn't tell you whether failures are due to retrieval misses, bad prompts, or model hallucinations. A system might get many answers technically "wrong" but still be retrieving highly relevant context—indicating that prompt or model behavior is the main issue. Conversely, a system might occasionally hit the correct answer by chance while mostly retrieving noise, giving a misleading impression of robustness. This is why metrics like MRR and nDCG are introduced conceptually: they focus on the rank and quality of retrieved items, independent of the LLM's final wording.

The evaluation harness turns earlier days' architectural choices into measurable hypotheses. If certain categories consistently underperform, you can revisit Day 2 chunking or embeddings for those documents. If many failures involve partial answers, you can adjust prompts or consider adding LLM‑as‑judge checks. The videos frame evaluation as an iterative design tool, not a one‑time report card. Changes to chunking, embeddings, or ingest (from Days 2 and 5) can be quickly reflected in test metrics and used to iterate on prompts or configurations.

### 6. Advanced Ingest & Preprocessing

Day 5's enriched chunk schema (headline, summary, original text) reflects the idea that the retriever should index something that already looks like a good answer surface, not just arbitrary slices of text. The headline and summary give the embedding model concentrated, high‑signal text that captures what the chunk is "about," while the original text preserves exact phrasing for cases where precise wording matters (e.g., contract clauses). This helps retrieval become more semantically focused: chunks tend to be topically coherent and directly answerable.

However, the behavior of the ingest LLM is itself a function of prompts and model choice. If the prompt is vague or the model underpowered, chunks may be too generic ("General policy information") or too noisy, reducing the benefits of the richer schema. Advanced ingest can amplify model errors if not paired with careful evaluation. The observation is that semantic chunking is powerful but not free: it adds another layer that must be tuned and evaluated, not just assumed to be better.

The videos introduce re‑ranking, query rewriting, and query expansion as techniques that sit naturally on top of semantic chunks. Re‑ranking could prioritize chunks that mention key entities (customer names, product IDs, policy numbers) present in the query. Query rewriting could transform conversational phrasing into more retrieval‑friendly forms. Query expansion could generate related queries and retrieve across all of them. All three aim to improve recall and ranking without changing the underlying KB, and evaluation from Day 4 would be used to validate whether they actually move metrics in the right direction.

### 7. Iteration Loop (Days 1–5)

Day 1 establishes a baseline and its shortcomings: retrieval is brittle and opaque, hallucinations are common when lookup fails, and the KB is rich but not query‑friendly. This naturally motivates Day 2 (chunking and embeddings), Day 3 (structured pipeline with UI), Day 4 (evaluation harness), and Day 5 (advanced ingest). Each day builds on the previous one: Day 2's chunking choices affect Day 3's retrieval quality, which is measured in Day 4, which informs Day 5's semantic chunking experiments.

The loop is not just forward‑looking; it also feeds back. Day 4's evaluation results can reshape earlier decisions: if certain categories consistently underperform, revisit Day 2 chunking or embeddings for those documents. If many failures involve partial answers, adjust Day 3 prompts or consider adding Day 5 re‑ranking. Day 5's advanced ingest techniques change the distribution of retrieved chunks, which should be reflected in Day 4 metrics. This tightens the feedback loop: changes to chunking or re‑ranking can be quickly reflected in test metrics and used to iterate on prompts or configurations.

The observation is that RAG is an evolving system whose ingest, retrieval, and evaluation components must be co‑designed and continuously refined. Day 5 is less about a single "advanced" architecture and more about adopting a mindset: treat RAG as a benchmarking and iteration loop, not a one‑off project. As new models, chunking strategies, or retrieval techniques appear, they are evaluated against the existing golden dataset and only promoted if they provide measurable benefits.

### 8. Common RAG Failure Modes Across the Week

Retrieval misses manifest in two ways. First, relevant documents are never retrieved (recall failures). This happens in Day 1 when lookup misses the relevant file, and persists in later days when chunking errors cause the answer to straddle two poorly chosen chunks, so neither is ranked highly. Second, wrong document segments are retrieved due to poor chunking. Overly large chunks dilute the relevance signal, while overly small chunks increase noise, making it harder to distinguish which chunks actually answer the question.

Answering failures occur even when retrieval succeeds. Hallucinations can happen despite correct context being retrieved: the LLM blends retrieved context with its own priors, producing plausible but unfounded statements. Over‑confident but incomplete answers appear when the system retrieves the right document but the LLM fails to extract or emphasize the relevant portion, leading to vague responses. Answers that are "almost" correct but miss a key detail (year, amount, or name) often result from retrieving a related but not exact snippet.

Conversational failures (introduced conceptually in Day 3 videos) include drift and context bloat. Drift occurs when the model over‑weights early context and continues answering based on stale assumptions, even when later turns imply a new focus. Context bloat happens as more turns are appended to history, making both prompts and retrieval queries more ambiguous. Naive approaches that simply stuff all prior turns into the query or context window tend to degrade performance over time.

The key observation is that these failure modes are not independent. Poor chunking (Day 2) leads to retrieval misses, which cause hallucinations (Day 1, Day 3), which are only visible through evaluation (Day 4) or UI inspection (Day 3). Advanced ingest (Day 5) can help with chunking but introduces new failure modes (poor summaries, misleading headlines) that must be caught by evaluation. The system is only as strong as its weakest link, and the links are tightly coupled.

### 9. Open Questions for Future Weeks

Production RAG is an engineering problem as much as a modeling problem. For the InsureLLM assistant, this implies designing a proper ingest pipeline that watches for new or updated documents, regenerates semantic chunks safely and idempotently, and writes embeddings and metadata into Chroma in a transactional way. Multiprocessing or distributed workers would scale ingest to large contract corpora without blocking the online system. Instrumentation with logging and monitoring would track retrieval quality, latency, and evaluation metrics over time.

GraphRAG, as presented in the videos, reframes retrieval around entities and relationships rather than just text similarity. For InsureLLM, this might involve nodes for employees, products, policies, and contracts, with edges representing relationships. Queries would become graph traversals plus text search, which could capture multi‑hop questions more naturally than pure vector search. The semantic chunks created in Day 5 are a stepping stone: they often contain structured summaries that identify key entities and roles. A future GraphRAG system could extract these entities and relationships from chunks and build a graph index alongside the vector store, using Day 4 evaluation to verify that it actually improves multi‑hop and relational queries.

The question of which advanced techniques (re‑ranking, query rewriting, GraphRAG) are most promising for the InsureLLM domain remains open. Re‑ranking and query rewriting seem like natural extensions of the current pipeline and could be validated quickly against Day 4's evaluation harness. GraphRAG would require more infrastructure but might be worth it if multi‑hop questions are a significant failure mode. The observation is that these techniques should be evaluated rigorously rather than adopted anecdotally—Day 4's golden dataset provides the framework for that evaluation.

