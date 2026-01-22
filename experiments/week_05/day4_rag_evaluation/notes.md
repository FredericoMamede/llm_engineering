## Day 4 – RAG Evaluation & Iteration

### Test Suite Overview

The Day 4 evaluator is built around a JSONL test set (`evaluation/tests.jsonl`) with labeled questions, reference answers, and categories such as `direct_fact`. This mirrors the video’s guidance on **golden datasets**: a curated set of representative queries that encode what “good” looks like for the InsureLLM assistant. Each row is effectively a unit test for the RAG system, combining input, expected behavior, and some notion of difficulty or type.

The structure intentionally focuses on **answerable questions within the knowledge base** rather than open‑ended chat. This keeps the evaluation grounded: failures are almost always traceable to retrieval, context construction, or prompt behavior, not to the absence of training data. It also provides a stable baseline for comparing different chunking, embedding, and pipeline configurations.

### Performance by Category

Even without computing formal metrics in the notebook, it is clear that performance varies by category:

- **Direct factual lookups** (e.g., “Who won IIOTY in 2023?”) tend to do well once the vector store is correctly populated; they map cleanly to short, well‑defined KB snippets.
-
- **Multi‑hop or synthesis questions** (e.g., combining product and policy info) expose weaknesses in both retrieval and answer composition. The system may retrieve only one of the necessary documents, leading to partially correct answers.
- **Ambiguous or underspecified questions** highlight the system’s tendency to guess rather than abstain, a design choice that later evaluation work is meant to challenge.

The videos push for tracking performance **per category** because different failure patterns suggest different fixes (chunking vs embeddings vs prompting), and lumped averages can hide those signals.

### Why Accuracy Alone Is Insufficient

Raw “accuracy” (e.g., proportion of questions answered exactly as in the reference) is a blunt tool for RAG. It does not tell you whether failures are due to retrieval misses, bad prompts, or model hallucinations. The videos argue for **richer retrieval metrics** and qualitative analysis:

- A system might get many answers technically “wrong” but still be retrieving highly relevant context—indicating that prompt or model behavior is the main issue.
- Conversely, a system might occasionally hit the correct answer by chance while mostly retrieving noise, giving a misleading impression of robustness.

This is why metrics like **MRR** and **nDCG** are introduced conceptually: they focus on the **rank and quality of retrieved items**, independent of the LLM’s final wording.

### Rank-Based Metrics – MRR and nDCG (Video Concepts)

The evaluator as implemented does not compute MRR or nDCG, but the videos provide intuition for how they would apply:

- **MRR (Mean Reciprocal Rank)** – Looks at the position of the first relevant document in the ranked list. High MRR means relevant chunks tend to appear near the top, which is critical given the limited context window.
- **nDCG (Normalized Discounted Cumulative Gain)** – Considers **all** relevant items and discounts them by rank, capturing whether the system consistently ranks useful chunks higher than junk.

Thinking in these terms helps dissect failures: is the right chunk never retrieved (low recall), or is it retrieved but buried under less relevant content (ranking issue)? Even if the notebook only approximates this informally, the mental model is important when interpreting test runs.

### LLM-as-a-Judge – Pros and Cons

The videos also introduce **LLM-as-a-judge** as a complementary evaluation technique: instead of string‑matching answers against references, an LLM scores the quality, faithfulness, and completeness of a response given the question and context. Pros:

- Much more tolerant of superficial phrasing differences.
- Can capture partial credit and nuanced correctness.
- Can surface explanations or rationales for scores.

Cons:

- Introduces another model into the loop, which may have its own biases and failure modes.
- Requires careful prompt design to avoid the judge “cheating” by using prior knowledge instead of the provided context.
- Adds cost and latency to evaluation pipelines.

Day 4’s evaluator is a simpler, test‑driven harness, but the LLM‑judge framing is important for future iterations, especially when exact matching is too brittle.

### Notable Failure Cases

Common patterns that show up when running the tests include:

- Answers that are **almost** correct but miss a key detail (year, amount, or name), often due to retrieving a related but not exact snippet.
- Cases where the system retrieves the right document but the LLM fails to extract or emphasize the relevant portion, leading to vague or incomplete answers.
- Questions that require more context than the current top‑k retrieval provides; the right answer is present somewhere in the KB but never appears in the selected chunks.

Each of these failure types points back to different levers: chunk size, retrieval parameters, embedding choice, or prompt design.

### Ideas for New Tests and Design Feedback Loop

The videos frame evaluation as an **iterative design tool**, not a one‑time report card. Useful follow‑ups include:

- Adding more tests for **edge cases** observed during manual UI usage (from Day 3), so real failures become part of the golden set.
- Designing tests that specifically stress different components:
  - Retrieval stress tests (synonyms, paraphrases, multi‑hop queries).
  - Prompt robustness tests (long questions, ambiguous wording).
  - Domain boundary tests (questions just outside the KB’s scope).
- Using evaluation results to **reshape earlier decisions**:
  - If certain categories consistently underperform, revisit Day 2 chunking or embeddings for those documents.
  - If many failures involve partial answers, adjust prompts or consider adding LLM‑as‑judge checks before surfacing responses.

In this sense, Day 4 closes the loop: it turns the earlier days’ architectural choices into measurable hypotheses, and it creates a framework where new RAG ideas (from Day 5 and beyond) can be judged rigorously rather than anecdotally.

