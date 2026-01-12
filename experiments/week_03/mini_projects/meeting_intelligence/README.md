# 📝 Week 3 Mini-Project — Meeting Intelligence Extractor

> **Status:** 🚧 In Progress
> **Scope:** Focused, single-use system
> **Model:** `meta-llama/Llama-3.2-3B-Instruct` (local, quantized)

---

## 🎯 Project Goal

Build a **focused system** that transforms **raw meeting transcripts** into **actionable business intelligence**, including:

* concise summaries
* decisions made
* action items with owners
* risks and open questions

This project is intentionally **narrow and opinionated**.
It is **not** a framework, a UI app, or a multi-model comparison.

---

## 🧠 Why This Project Exists

Meeting transcripts are:

* long
* messy
* unstructured
* hard to act on

Yet businesses make critical decisions in meetings every day.

This project demonstrates how an LLM can be used as a **reasoning and structuring engine**, not just a text generator.

---

## 🧱 Design Principles (Non-Negotiable)

This project deliberately emphasizes:

* **Single model, deeply understood**
* **Prompt design over model hopping**
* **Token awareness and budgeting**
* **Explicit tradeoffs**
* **Readable, maintainable code**
* **Understanding over feature count**

---

## 🚫 Explicit Non-Goals

This mini-project intentionally does **NOT**:

* train or fine-tune models
* support multiple providers
* expose a UI
* implement batching or async processing
* build a reusable library
* optimize for throughput or latency
* include evaluation frameworks

If something feels “missing” — it probably is **on purpose**.

---

## 🤖 Model Choice

### Selected Model

**`meta-llama/Llama-3.2-3B-Instruct`**

**Why this model:**

* Small enough to run locally
* Strong instruction-following
* Requires correct chat templates
* Forces token awareness
* Supports quantization
* Matches Week 3 Transformers content

### Inference Strategy

* HuggingFace `transformers`
* `AutoModelForCausalLM`
* 4-bit quantization (BitsAndBytes)
* GPU if available, CPU fallback acceptable

---

## 📂 Project Structure

```
meeting_intelligence/
├── README.md                 # This file
├── prompts/
│   └── meeting_analysis.md   # Core system + user prompt
├── schemas.py                # Output schema definitions
├── extractor.py              # Core extraction logic
├── run.py                    # Entry point
├── sample_inputs/
│   └── meeting.txt           # Raw transcript example
└── sample_outputs/
    └── meeting.json          # Example structured output
```

---

## 📥 Input

* Plain text meeting transcript
* Source can be:

  * ASR output (Whisper, Zoom, etc.)
  * copied meeting notes
  * public transcripts (e.g. city council)

No preprocessing assumptions are made beyond **raw text**.

---

## 📤 Output

A **single structured JSON object**:

```json
{
  "summary": "...",
  "decisions": [...],
  "action_items": [
    {
      "owner": "...",
      "task": "...",
      "due_date": "optional"
    }
  ],
  "risks": [...],
  "open_questions": [...]
}
```

Structure matters more than perfect wording.

---

## 🔄 High-Level Flow

1. Load transcript from file
2. Build prompt using schema + instructions
3. Apply chat template correctly
4. Run inference with token limits
5. Decode and clean output
6. Parse JSON safely
7. Save structured result to disk

---

## 🧩 Key Engineering Challenges

This project intentionally surfaces:

### 1. Token Budgeting

* Transcripts can be long
* Input length vs output length tradeoffs
* `max_new_tokens` must be chosen carefully

### 2. Prompt Design

* System vs user roles
* Generation prompts
* Enforcing JSON structure

### 3. Robust Parsing

* LLM output is not guaranteed to be valid JSON
* Must handle:

  * markdown fences
  * trailing text
  * missing fields

### 4. Model Behavior Understanding

* Instruction models continue text unless prompted correctly
* Chat templates are mandatory
* Quantization tradeoffs are visible

---

## 🧪 What “Success” Looks Like

This project is complete when:

* A transcript file can be processed end-to-end
* Output JSON matches the schema
* Code is readable and explainable
* Tradeoffs are documented in comments or README
* You can explain **why** each design choice was made

Not when it has “more features”.

---

## ⚙️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```bash
# .env
HF_TOKEN=your_huggingface_token_here
```

**Get your HuggingFace token:**
- Visit https://huggingface.co/settings/tokens
- Create a token with "Read" permissions
- Required for accessing gated models like `meta-llama/Llama-3.2-3B-Instruct`

**Note:** The `.env` file is automatically loaded by `python-dotenv`. Never commit this file to git.

---

## ▶️ Running the Project

```bash
python run.py \
  --input sample_inputs/meeting.txt \
  --output sample_outputs/meeting.json
```

CLI simplicity is intentional.

---

## 🧠 Relationship to Week 3 Challenge

| Challenge      | Mini-Project      |
| -------------- | ----------------- |
| Broad          | Narrow            |
| Multi-model    | Single model      |
| Framework      | Product           |
| Exploration    | Decision-making   |
| System breadth | Depth and clarity |

This mini-project demonstrates **focus**, not scale.

---

## 🚀 Future Extensions (Not Implemented)

Ideas deliberately **out of scope** for now:

* transcript chunking + aggregation
* multi-pass summarization
* speaker attribution
* UI or API layer
* vector storage or retrieval
* evaluation metrics

These belong in **later weeks or separate projects**.

---

## 🧾 Final Note

> **Clarity beats cleverness.**
> **Understanding beats output.**
> **Focus beats scope creep.**

This project is about building **engineering judgment**, not a demo.

---


