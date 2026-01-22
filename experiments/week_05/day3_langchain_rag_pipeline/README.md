## Day 3 – RAG with Memory, LangChain Pipeline & UI

### Goal of the Day

Build a **LangChain‑based RAG pipeline** that:

- Connects to the vector store created on Day 2.
- Uses an LLM (e.g. `gpt-4.1-nano`) to answer questions.
- Can be wired into a simple UI for interactive use.
- Sets up the foundation for **conversation history / memory** and debugging tools.

### RAG Concepts Explored

#### Implemented in notebooks

- **LangChain RAG pipeline**:
  - Retriever (`Chroma` + `HuggingFaceEmbeddings`).
  - Chat model (`ChatOpenAI`).
  - Prompt composition using system + human messages.
- **Integration with the Day 2 vector store**:
  - Reusing the same embeddings and Chroma DB.
- **Basic / prototype Gradio UI**:
  - An “Expert Question Answerer” that calls the RAG chain.

#### Conceptual / instructional (video-only)

- **RAG with conversation history**:
  - How memory components can feed prior turns into retrieval.
  - Why conversational context changes what should be retrieved.
- **Building a robust Gradio UI for RAG**:
  - Designing inputs, outputs, and panels to inspect retrieved chunks.
- **Debugging chunk retrieval**:
  - Surfacing which chunks were selected for each query.
  - Understanding when the system “looked in the wrong place”.
- **Practical failure modes in conversational RAG**:
  - Over‑reliance on early context.
  - Mixing old and new information incorrectly.

#### Partially explored / future extension

- Adding explicit **memory components** (conversation history) to the current chain.
- Extending the UI with:
  - Panels to show retrieved documents.
  - Toggles for retrieval parameters (k, score thresholds).

### Relationship to Course Materials

- **Primary source notebook:** `week5/day3.ipynb`
- Uses:
  - `Chroma` as the vector store.
  - `HuggingFaceEmbeddings` for consistency with Day 2.
  - `ChatOpenAI` for answer generation.
  - Optional Gradio UI for an “Expert Question Answerer”.
  - `week5/app.py` for the concrete Gradio chat app that wraps this RAG pipeline.
- This README documents additional **memory and debugging concepts** emphasized in the videos even if only lightly implemented.

### Why This Day Exists

This day shows how to move from:

- **Ad‑hoc notebook code** → to a more structured, chain‑based RAG pipeline.

It demonstrates how a well‑defined chain:

- Makes behavior easier to reason about.
- Makes evaluation (Day 4) and advanced ingest (Day 5) easier to plug in.
- Provides natural integration points for **memory and UI‑driven debugging**.

### Notebook Placement

- The **authoritative notebook** for this day lives at: `week5/day3.ipynb`.
- This folder provides a **landing zone** for any refactored LangChain RAG implementations, UI experiments, and memory/debugging extensions.

