# Week 3 Experiments

**Learning Lab - Week 3 Concepts**

This directory contains experiments and explorations for Week 3 of the LLM Engineering course.

## Purpose

This is a **learning lab**, not a portfolio project. Experiments here are:
- Small, focused explorations
- Documentation of insights and tradeoffs
- Practice with Week 3 concepts (HuggingFace, Transformers, Tokenizers)
- Reusable patterns for future independent projects

## Structure

```
experiments/week_03/
├── notebooks/
│   ├── 01_colab_setup.ipynb              # Day 1: Google Colab introduction
│   ├── 02_huggingface_pipelines.ipynb   # Day 2: HuggingFace pipelines
│   ├── 03_tokenizers.ipynb               # Day 3: Tokenizers exploration
│   ├── 04_models_transformers.ipynb      # Day 4: Transformers library models
│   └── 05_meeting_minutes_creator.ipynb # Day 5: Meeting minutes creator
├── configs/
│   └── models.yaml                       # Model configurations (optional)
├── results/
│   └── week3_observations.md            # Findings and tradeoffs
├── mini_projects/
│   └── meeting_minutes_creator/         # Optional: Extracted project
├── README.md                             # This file
└── notes.md                              # Detailed patterns and code examples
```

## Day 1: Google Colab Setup

### Goal of Day 1

Day 1 is **not about theory**. It's about **environment, hardware, and intuition**:
> *"What can I do when I have real GPU compute, even on a small budget?"*

This day deliberately shows off capabilities, builds confidence, sets expectations for Colab realities, and motivates the rest of Week 3.

### What I'm Testing

#### 1. Colab Environment Setup
**What:** Set up Google Colab for GPU-accelerated model inference

**Why:**
- Local machines may not have GPUs
- Colab provides free/low-cost GPU access
- Learn cloud-based development workflow
- Understand runtime management
- Build confidence with GPU workflows

**What I learned:**
- Colab is a remote Jupyter notebook on Google's machines
- Free T4 GPU access, but runtime can reset at any time
- Must reinstall packages every session
- Sessions are ephemeral - state is fragile
- **Pattern:** Use Colab for experiments/demos, not long-running production

#### 2. Colab Survival Guide
**What:** Develop operational habits for runtime management

**Why:**
- Colab failures are common and can be confusing
- Need to know how to recover quickly
- Understanding restart types prevents data loss

**What I learned:**
- Always connect to T4 runtime and verify GPU via View Resources
- When things break: Disconnect and Delete Runtime → Reconnect → Run from top
- **Restart session** ≠ **Disconnect and delete runtime** (critical distinction)
- Recovery speed matters more than perfection

#### 3. GPU Verification
**What:** Verify GPU type before running heavy models

**Why:**
- GPU can silently downgrade to CPU
- Not all GPUs are equal (T4 vs A100 matters a lot)
- Need to confirm GPU availability before model loading

**What I learned:**
- Use `nvidia-smi` to check GPU type
- Always verify GPU *before* running heavy models
- Check for "Tesla T4" specifically (not just any GPU)

#### 4. HuggingFace Authentication
**What:** Set up HF token with WRITE permissions as Colab secret

**Why:**
- Avoids rate limits
- Enables model downloads
- Required for later weeks
- Mirrors real production secret management

**What I learned:**
- Token must have **WRITE** permissions (not fine-grained)
- Store in Colab secrets (key icon), not hardcoded
- Access via `userdata.get('HF_TOKEN')`
- **Pattern:** Secrets management matters even in notebooks

#### 5. Text-to-Image Generation (Diffusers)
**What:** Explore multiple diffusers models with different speed/quality tradeoffs

**Why:**
- Understand what's possible with GPU-accelerated image generation
- Learn speed vs quality tradeoffs
- See different architectures (Turbo, Base, Base+Refiner)

**What I learned:**
- **SDXL Turbo:** Very fast (4 steps), lower quality, good for iteration
- **SDXL Base:** Slower (30 steps), better quality
- **Base + Refiner:** Two-stage pipeline, best quality, more complex
- Diffusers library abstracts complexity
- **Pattern:** Fast models for prototyping → Quality models for final output

#### 6. Text-to-Speech on GPU
**What:** Use HuggingFace pipeline for GPU-accelerated TTS

**Why:**
- Understand that HuggingFace isn't just text models
- See GPU acceleration for audio workloads
- Learn about speaker embeddings

**What I learned:**
- Audio workloads are GPU-accelerated
- Pipelines abstract a lot of complexity
- Speaker embeddings enable voice consistency
- Use `device='cuda'` for GPU acceleration

#### 7. Paid GPU Demonstration (A100)
**What:** Understand what's possible with higher-tier GPUs (optional, educational)

**Why:**
- Show scale difference between T4 and A100
- Understand cloud GPU pricing
- See what's possible with small paid budget

**What I learned:**
- A100 is dramatically faster than T4
- Cost: ~$0.003 for single generation (example)
- **Critical:** Pay for kernel uptime, not just inference time
- Always shut down paid runtimes when done
- Cloud GPU pricing is approachable

#### 8. Kernel Restarts (Teaching Point)
**What:** Notebook intentionally restarts kernel multiple times

**Why:**
- Reinforce that state is fragile
- Teach that order of execution matters
- Build comfort with restarting

**What I learned:**
- This is a **lesson**, not inconvenience
- Always be prepared to restart
- Run cells from top when reconnecting
- Don't assume state persists

---

## Day 2: HuggingFace Pipelines

### Goal of Day 2

Day 2 introduces the **High-Level Pipeline API** - the simplest way to use pre-trained models for common inference tasks without worrying about model internals.

### What I'm Testing

#### 1. High-Level Pipeline API
**What:** Use HuggingFace `pipeline()` function for easy model access

**Why:**
- Simplest way to use pre-trained models
- No need to understand model internals
- Quick prototyping and experimentation
- Task-specific abstractions handle complexity

**What I learned:**
- Pipelines are a high-level API for inference only (not training)
- Two-step pattern: Create pipeline → Call pipeline
- Default models are automatically selected if not specified
- GPU acceleration via `device="cuda"` parameter
- **Pattern:** `my_pipeline = pipeline(task, model=xx, device=xx)` then `my_pipeline(input)`

#### 2. Training vs Inference Distinction
**What:** Understand the difference between training and inference

**Why:**
- Pipelines are for inference only (using pre-trained models)
- Important to understand when to use pipelines vs lower-level APIs
- Foundation for understanding when we'll need advanced APIs (Week 7)

**What I learned:**
- **Training:** Model learns from data, updates parameters/weights
- **Fine-tuning:** Training a model that's already been trained
- **Inference:** Using a trained model to produce outputs on new inputs
- Pipelines API is only for inference (Week 7 will cover training)
- All API usage (GPT, Claude, Gemini) from previous weeks = inference

#### 3. Multiple Pipeline Tasks
**What:** Explore different pipeline tasks available in HuggingFace

**Why:**
- Understand breadth of what pipelines can do
- Learn task-specific patterns
- See how same API works across different tasks

**What I learned:**
- **Sentiment Analysis:** Analyze emotional tone of text
- **Named Entity Recognition (NER):** Extract entities (people, places, organizations)
- **Question Answering:** Answer questions given context
- **Text Summarization:** Condense long text into summaries
- **Translation:** Translate between languages
- **Zero-shot Classification:** Classify text without training examples
- **Text Generation:** Generate new text from prompts
- **Image Generation:** Create images from text (Diffusers library)
- **Audio Generation (TTS):** Convert text to speech

**Key Learning:** Same simple API pattern works across all tasks - just change the task name

#### 4. Model Selection in Pipelines
**What:** Specify custom models vs using defaults

**Why:**
- Default models may not be best for your use case
- Different models have different strengths
- Learn to customize pipelines

**What I learned:**
- If no model specified, HuggingFace picks default for the task
- Can specify model: `pipeline("task", model="model-name")`
- Different models can improve results (e.g., multilingual sentiment model)
- **Pattern:** Start with default → Try specific models if needed

#### 5. Colab Pro-Tips (Day 2 Specific)
**What:** Additional Colab troubleshooting tips

**Why:**
- Some errors are misleading (CUDA errors when runtime switched)
- Need to know how to recover from runtime switches
- Build confidence with Colab workflows

**What I learned:**
- Data science warnings can mostly be ignored (glance, but don't worry)
- CUDA errors often mean runtime was switched (not a package issue)
- Recovery: Disconnect & delete runtime → Clear outputs → Reconnect → Run from top
- Always verify GPU after reconnecting (use View Resources)
- **Pattern:** When in doubt → Full reset → Run from top

---

## Day 3: Tokenizers
> 🚧 To be completed after Day 3 experiments

---

## Day 4: Transformers Library Models
> 🚧 To be completed after Day 4 experiments

---

## Day 5: Meeting Minutes Creator
> 🚧 To be completed after Day 5 experiments

---

## Setup

1. **HuggingFace Account and Token:**
   - Create account at https://huggingface.co
   - Generate token at https://huggingface.co/settings/tokens
   - In Colab: Add token as secret (Settings → Secrets)
   - Locally: Set environment variable `HF_TOKEN=xxxx`

2. **For Local Development:**
   ```bash
   pip install transformers torch huggingface_hub
   ```

3. **For Colab Notebooks:**
   - Follow setup instructions in each notebook
   - Select GPU runtime (Runtime → Change runtime type → GPU)
   - Free tier: T4 GPU available
   - Pro+: Better GPUs, longer sessions

4. **Google Drive (Day 5):**
   - Mount Drive in Colab: `from google.colab import drive; drive.mount('/content/drive')`
   - Access files at `/content/drive/MyDrive/...`

---

## Notes

See `notes.md` for:
- Key learnings from each day (Day 1-5)
- Detailed code patterns with explanations
- Tradeoffs observed (local vs Colab, pipelines vs manual)
- Ideas to extract for future projects
- HuggingFace-specific patterns and best practices

See `results/week3_observations.md` for:
- High-level findings from each day
- Summary of what worked and what didn't
- Business implications and recommendations

---

## Key Concepts Covered

- **Google Colab:** Cloud-based Jupyter environment with GPU access
- **HuggingFace Pipelines:** High-level API for easy model usage
- **Tokenizers:** Text-to-token conversion, vocabulary, token IDs
- **Transformers Library:** Direct model access, manual inference
- **Model Inference:** Tokenize → Forward Pass → Decode flow
- **Audio Processing:** Transcription and summarization
- **Token Visualization:** Understanding model predictions

---

## References

- Course material: Week 3 Day 1-5 notebooks
- HuggingFace Docs: https://huggingface.co/docs/transformers
- HuggingFace Hub: https://huggingface.co/models
- Google Colab: https://colab.research.google.com
- Transformers Library: https://github.com/huggingface/transformers

