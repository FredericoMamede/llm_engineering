## Day 1 – RAG Foundations & Simple Knowledge Assistant

### Goal of the Day

Establish a **baseline RAG implementation** for the “Expert Knowledge Worker” assistant used by InsureLLM employees, and introduce the **core ideas of RAG**:

- Simple, understandable retrieval logic.
- Clear connection to the business context (internal insurance knowledge).
- End‑to‑end question‑answering loop, even if naïve.
- Mental model for how retrieval and generation interact.

### RAG Concepts Explored

#### Implemented in notebooks

- Building a **simple RAG knowledge assistant**:
  - Load documents from the InsureLLM knowledge base.
  - Retrieve relevant context (dictionary / file lookup) for a given question.
  - Call an LLM to answer using the retrieved context.
- **Dictionary lookup & context retrieval**:
  - Direct string / keyword style retrieval over the knowledge base.
  - No vector search yet – intentionally brute‑force.

#### Conceptual / instructional (video-only)

- **Introduction to RAG**:
  - What “Retrieval‑Augmented Generation” means.
  - Why we separate retrieval from generation.
- **Vector embeddings and encoder LLMs**:
  - How modern RAG systems use encoder models to map text to vectors.
- **How embeddings represent meaning**:
  - From word2vec intuitions to sentence / document embeddings.
- **Big picture: Why RAG + vector stores matter**:
  - Accuracy: grounding answers in your own data.
  - Cost: avoiding long prompts and repeated explanations.
  - Control: constraining what the model can say to known facts.

#### Partially explored / future extension

- Transition from dictionary‑style retrieval to **vector‑based retrieval**.
- Evolving the simple assistant into a fully vector‑backed RAG system (Days 2–3).

### Relationship to Course Materials

- **Primary source notebook:** `week5/day1.ipynb`
- Connects to the shared assets in `week5/`:
  - `knowledge-base/` (company, products, employees, contracts).
  - Early implementation files (e.g. `app.py`, `implementation/`).
- This README adds **video-only** concepts that are not fully implemented in the notebook but are essential to understanding Day 1.

### Why This Day Exists

This day gives you:

- A concrete, end‑to‑end **mental model** for RAG.
- A reference “minimum viable” system that later days will refine:
  - Day 2 improves **how we chunk and embed**.
  - Day 3 improves **how we orchestrate the pipeline** (and later, memory).
  - Day 4 improves **how we evaluate** the system.
  - Day 5 improves **how we ingest and preprocess knowledge**.

### Notebook Placement

- The **authoritative notebook** for this day lives at: `week5/day1.ipynb`.
- This folder is a **documentation and scaffold** layer for code‑first or refactored implementations that mirror the notebook’s intent and **include all video concepts**.

