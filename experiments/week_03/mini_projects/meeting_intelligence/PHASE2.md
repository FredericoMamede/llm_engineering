# 🚀 Phase 2 — Meeting Intelligence Extractor (UI & UX Layer)

> **Phase:** 2 (Post-CLI, Pre-Production)  
> **Status:** ⏳ Planned (Not Implemented)  
> **Depends on:** Phase 1 — Core Extraction Engine  
> **Primary Goal:** Add a thin UI layer without modifying core logic

---

## 🎯 Phase 2 Objective

Extend the **Phase 1 Meeting Intelligence Extractor** with a **minimal, disciplined UI layer** that:

- accepts meeting transcripts via file upload or text input
- runs the **existing extraction logic unchanged**
- streams model output for transparency
- displays structured results clearly
- saves outputs to disk

> **Critical Rule:**  
> Phase 2 must **not change** prompt logic, schema definitions, parsing behavior, or extraction semantics.

The UI is a wrapper — not a brain.

---

## 🧠 Why Phase 2 Exists

Phase 1 proves:
- reasoning quality
- prompt correctness
- token budgeting
- robust parsing

Phase 2 proves:
- usability
- separation of concerns
- UI discipline
- production-style layering

This mirrors how **real internal tools** are built in professional environments.

---

## 🧱 Design Principles (Non-Negotiable)

Phase 2 adheres strictly to:

- UI is a **thin orchestration layer**
- No duplication of business logic
- No model switching (still a single model)
- No framework abstractions
- No “settings explosion”

If the UI requires complexity, the core logic is wrong.

---

## 📂 Updated Project Structure (Phase 2)

```text
meeting_intelligence/
├── README.md                  # Phase 1 + Phase 2 overview
├── extractor.py               # Core extraction logic (unchanged)
├── schemas.py                 # Output schema definitions (unchanged)
├── run.py                     # CLI entrypoint (unchanged)
│
├── ui/
│   ├── app.py                 # Gradio UI (new)
│   └── ui_utils.py            # UI-only helpers (optional)
│
├── prompts/
│   └── meeting_analysis.md    # Prompt templates (unchanged)
│
├── sample_inputs/
├── sample_outputs/
└── outputs/                   # Generated files
````

---

## 🖥️ UI Scope (Strictly Limited)

### Inputs

The UI supports **only**:

1. **Transcript Input**

   * File upload (`.txt`)
   * OR raw text input (textbox)

2. **Run Button**

   * Single action: *“Extract Meeting Intelligence”*

No model selector
No temperature slider
No token controls

These are intentionally excluded and belong in later weeks.

---

### Outputs

The UI displays **three sections**:

1. **Streaming Model Output**

   * Shows generation token-by-token
   * Enables transparency into model behavior

2. **Parsed Structured Result**

   * Pretty-printed JSON
   * Must match schema exactly

3. **Saved File Confirmation**

   * Displays output file path
   * Confirms persistence to disk

---

## 🔄 Phase 2 Execution Flow

```text
User uploads transcript
        ↓
UI reads file contents
        ↓
UI calls existing extractor.extract()
        ↓
Model runs (streaming enabled)
        ↓
Output parsed (existing logic)
        ↓
JSON rendered + saved
```

The UI **never**:

* builds prompts
* parses JSON
* touches token logic
* cleans or validates output

---

## 🧩 Required Technical Additions

### 1️⃣ Streaming Support

Enable streaming using HuggingFace primitives:

* Use `TextIteratorStreamer`
* Stream **raw generated text only**
* Parsing occurs **after generation completes**

Streaming is for **UX transparency**, not logic changes.

---

### 2️⃣ UI Entry Point

`ui/app.py` responsibilities:

* load environment variables
* initialize model once
* define Gradio layout
* call extractor functions
* handle errors gracefully

No business logic allowed inside the UI.

---

### 3️⃣ Error Handling Philosophy

Errors must be:

* visible
* readable
* non-technical

Examples:

* “Transcript too long for token limit”
* “Failed to parse structured output”
* “Model ran out of memory”

No stack traces or raw exceptions in the UI.

---

## 🎨 UI Layout (Intentional Simplicity)

**Left panel**

* transcript input (file or text)
* run button

**Right panel**

* streaming output (scrolling)
* final structured JSON
* save confirmation

Anything more is out of scope.

---

## 🚫 Explicit Non-Goals (Phase 2)

Phase 2 intentionally excludes:

* multiple models
* prompt editing
* schema switching
* batch processing
* async queues
* auth management
* persistence beyond local files
* evaluation frameworks

These belong to later projects or later weeks.

---

## 🧪 Phase 2 Completion Criteria

Phase 2 is complete when:

* CLI still works unchanged
* UI cleanly calls core logic
* streaming works correctly
* output JSON matches schema
* errors are human-readable
* every line of UI code can be explained

---

## 🧭 Relationship to Later Weeks

| Phase / Week | Focus                   |
| ------------ | ----------------------- |
| Phase 1      | Reasoning & structure   |
| Phase 2      | UX & layering           |
| Week 4       | Streaming & performance |
| Week 5       | Chunking & retrieval    |
| Week 6+      | Evaluation & scaling    |

This ensures learning **compounds**, not overlaps.

---

## 📝 Current Status

* Phase 1: 🚧 In progress / near completion
* Phase 2: ⏳ Designed, not implemented

Implementation will begin **only after Phase 1 is complete and committed**.

---

> **Clarity beats cleverness.**
> **Understanding beats output.**
> **Structure beats speed.**

```


