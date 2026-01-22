## Day 3 – RAG Pipeline, Conversation & UI

### Pipeline Design

The Day 3 notebook formalizes RAG into a LangChain pipeline: a retriever backed by Chroma, a `ChatOpenAI` model, and a simple chain that plugs retrieved documents into a prompt. Compared to Day 1’s ad‑hoc wiring, this structure makes responsibilities clearer: retrieval happens first, then the LLM reasons over the retrieved context. The chain abstraction also surfaces configurable parameters—top‑k, temperature, model choice—that were previously buried in notebook code.

This design is strong at **composability**: the same retriever can be reused across chains, and the same LLM can be swapped in and out. Its main weakness, as the videos point out, is that if retrieval is wrong, the chain has no internal notion of “this looks suspicious.” Evaluation and UI support are needed to close that loop.

### Prompting Strategy

Prompting on Day 3 follows the now‑standard pattern: a system message defines the assistant as an “Expert Knowledge Worker,” and human messages include both the user’s question and the retrieved context. This works well when retrieval is reasonably accurate: the LLM can ground its answer in specific snippets and produce high‑quality, domain‑aligned responses.

However, the prompt is still **trusting**: it does not instruct the model to abstain when context is missing or contradictory, nor does it ask for citations or confidence estimates. The videos emphasize that conversational RAG benefits from more explicit instructions around uncertainty and context usage—something this notebook hints at but does not fully implement. This becomes particularly important once multi‑turn conversations are introduced.

### Conversation History & Memory (Video Concepts)

While the notebook itself is mostly single‑turn, the Day 3 videos extend the story to **RAG with conversation history**. Memory introduces two new families of failure modes:

- **Drift** – The model over‑weights early context and continues answering based on stale assumptions, even when later turns imply a new focus or corrected information.
- **Context bloat** – As more turns are appended to history, both prompts and retrieval queries become more ambiguous, making it harder to select the right chunks.

The key insight is that conversation history is itself “data” that can pollute retrieval: naive approaches that simply stuff all prior turns into the query or into the context window tend to degrade performance over time. A more careful design would use memory selectively (e.g., summarised conversation state) and tune the retriever to focus on the **current question plus relevant aspects of history**, not everything.

### UI & Debugging Retrieval

Even a minimal Gradio UI is enough to underscore a core point from the videos: **RAG is much easier to debug when you can see what was retrieved.** Right now, the pipeline can feel like a black box—questions go in, answers come out, and you have to infer whether the KB actually contributed.

The videos advocate for exposing at least:

- The list of retrieved chunks (with scores or ranks).
- Snippets of the underlying documents.
- Some simple metadata (source, document type).

This kind of UI turns failed answers into actionable diagnostics: you can distinguish “retrieval failed” from “LLM mis‑used a good context.” Although the current notebook’s UI is basic, it provides a natural anchor for these ideas and sets up the evaluation work in Day 4.

### Observed Strengths and Weaknesses vs Day 1

Compared to the Day 1 brute‑force assistant, the Day 3 pipeline:

- **Strengths**
  - Retrieves context that is semantically related rather than lexically identical, thanks to embeddings.
  - Structures the RAG process in a way that is easier to extend and instrument.
  - Produces more consistently grounded answers on questions that match the KB content.
- **Weaknesses**
  - Still lacks explicit handling of “no good context found” scenarios.
  - Does not yet incorporate conversation‑aware retrieval or more advanced prompt patterns for abstention and citation.

These weaknesses are by design—they are addressed in the evaluation focus of Day 4 and the advanced ingest patterns of Day 5.

### Ideas for Future Refactors (Toward Days 4–5)

- Integrate a **retrieval inspection panel** into the UI so that every answer is accompanied by its supporting chunks.
- Add a lightweight **memory component** that stores summarised conversation state and experiments with using it in both the query and the answer.
- Prepare the chain to log inputs/outputs systematically, so Day 4 evaluation can consume real interaction logs instead of only synthetic tests.
- Design prompts that encode clearer policies around uncertainty (“If the retrieved context does not contain the answer, say so explicitly…”), which will later align with LLM‑as‑judge evaluation criteria.

