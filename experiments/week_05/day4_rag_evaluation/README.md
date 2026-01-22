## Day 4 – RAG Evaluation & Iteration

### Goal of the Day

Build and use an **evaluation harness** to measure RAG quality and guide iteration:

- Run many questions through the system.
- Compare answers to reference (golden) answers.
- Categorize failure modes and track performance over time.
- Connect evaluation metrics back to chunking, embeddings, and pipeline design.

### RAG Concepts Explored

#### Implemented in notebooks

- **Evaluation harness** that:
  - Loads tests from `evaluation/tests.jsonl`.
  - Uses categories like `direct_fact` to organize question types.
- **RAG system under test**:
  - Uses the Day 3 pipeline (retriever + LLM) to produce answers.

#### Conceptual / instructional (video-only)

- **Measuring RAG performance**:
  - Retrieval‑oriented metrics such as **MRR (Mean Reciprocal Rank)** and **nDCG (Normalized Discounted Cumulative Gain)**.
- **Golden datasets & test data (JSONL)**:
  - How to design high‑quality test sets for your domain.
- **LLM‑as‑a‑Judge (structured outputs)**:
  - Using an LLM to score answers and produce structured evaluation outputs.
- **Evaluation pipelines with Gradio**:
  - Building UIs to visualize test runs, metrics, and failure cases.
- **Experimenting with chunking & embedding strategies**:
  - Running side‑by‑side experiments with different ingest settings.
- **Measuring gains from improved embeddings**:
  - Connecting embedding/model changes to measurable improvements in retrieval and answer quality.

#### Partially explored / future extension

- Adding explicit MRR/nDCG calculations on top of the existing evaluation harness.
- Building a small Gradio‑based evaluation console around the current test runner.
- Automating comparative runs for different chunking / embedding configurations.

### Relationship to Course Materials

- **Primary source notebook:** `week5/day4.ipynb`
- Uses:
  - `evaluation/` module (e.g. `evaluation/test.py`).
  - `evaluation/tests.jsonl` with labeled question/answer pairs.
  - `evaluation/eval.py` for the concrete implementation of MRR/nDCG and LLM-as-a-judge scoring.
  - The existing RAG pipeline (from Day 3) as the system under test.
- This README surfaces the **evaluation techniques and metrics** taught in the videos, including those not fully implemented yet.

### Why This Day Exists

This day reinforces that:

- A RAG system is only as good as its **measured behavior**.
- Evaluation is not an afterthought – it is a first‑class part of the architecture.

It sets up a feedback loop between:

- **Implementation choices** (chunking, prompts, retrieval parameters, embedding models).
- **Observed outcomes** (accuracy, rank‑based metrics, failure categories, robustness).

### Notebook Placement

- The **authoritative notebook** for this day lives at: `week5/day4.ipynb`.
- This folder is intended for:
  - Evaluation scripts or harnesses that mirror the notebook.
  - Documentation of evaluation strategies, metrics, and observed patterns from both notebooks and videos.

