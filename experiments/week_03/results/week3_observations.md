# Week 3 Observations

## Day 1: Google Colab Setup

### Goal of Day 1

Day 1 is **not about theory**. It's about **environment, hardware, and intuition**:
> *"What can I do when I have real GPU compute, even on a small budget?"*

This day deliberately shows off capabilities, builds confidence, sets expectations for Colab realities, and motivates the rest of Week 3.

---

### Colab Environment

**Finding:** Colab provides easy access to GPU resources for model inference
- Free tier offers T4 GPU (sufficient for most experiments)
- Pro+ offers better GPUs (A100) and longer sessions
- Jupyter-like interface (familiar workflow)
- Remote notebook running on Google's machines

**Benefits:**
- ✅ Free T4 GPU access
- ✅ No environment mismatch between students
- ✅ Easy sharing & reproducibility
- ✅ Fast experimentation with heavy models

**Downsides (Important Reality Check):**
- ❌ Runtime can reset at any time (especially if no code running)
- ❌ GPU can silently downgrade to CPU
- ❌ Must re-install packages every session
- ❌ Slight latency vs local machine
- ❌ Sessions are ephemeral

**Tradeoff:** 
- Colab: Free GPU, but limited hours, data leaves machine, state is fragile
- Local: Full control, but requires GPU hardware, setup complexity

**Recommendation:** Use Colab for experiments/demos, local for production

---

### Colab Survival Guide

**Finding:** Colab failures are normal and recovery speed matters
- Runtime management is a critical skill
- Understanding restart types prevents confusion and data loss

**Required Habits:**
- Always connect to T4 runtime and verify via View Resources
- When things break: Disconnect and Delete Runtime → Reconnect → Run from top

**Restart Types (Critical Distinction):**
- **Restart session:** Kernel resets, packages remain, disk persists
- **Disconnect & delete runtime:** Everything wiped, start fresh

**Key Insight:** This is a **lesson**, not inconvenience. Being comfortable with restarts is essential.

**Recommendation:** Develop these habits early - they save time later

---

### GPU Verification

**Finding:** Always verify GPU type before running heavy models
- GPU can silently downgrade to CPU
- Not all GPUs are equal (T4 vs A100 matters dramatically)

**Verification Pattern:**
- Use `nvidia-smi` to check GPU
- Verify "Tesla T4" specifically (not just any GPU)
- Check memory availability

**Recommendation:** Make GPU verification the first cell after connecting

---

### HuggingFace Authentication

**Finding:** Proper secret management matters even in notebooks
- Token must have WRITE permissions (not fine-grained)
- Colab secrets provide secure storage
- Pattern mirrors real production environments

**Key Requirements:**
- HF account + token with WRITE permissions
- Store as Colab secret (key icon), not hardcoded
- Access via `userdata.get('HF_TOKEN')`

**Recommendation:** Set this up once, reuse across all Colab notebooks

---

### Text-to-Image Generation (Diffusers)

**Finding:** Multiple architectures available with different speed/quality tradeoffs

**Models Explored:**
1. **SDXL Turbo:** Very fast (4 steps), lower quality, good for iteration
2. **SDXL Base:** Slower (30 steps), better quality
3. **Base + Refiner:** Two-stage pipeline, best quality, more complex

**Key Insights:**
- Same task → multiple architectures
- Tradeoffs: **speed vs quality**
- GPU memory & inference steps matter
- Diffusers library abstracts complexity

**Recommendation:** Start with fast models for prototyping → Use quality models for final output

---

### Text-to-Speech on GPU

**Finding:** HuggingFace isn't just text models - audio workloads are GPU-accelerated
- Pipelines abstract a lot of complexity
- Speaker embeddings enable voice consistency
- GPU acceleration makes TTS fast

**Key Insight:** HuggingFace ecosystem is broader than just transformers

**Recommendation:** Explore other pipeline types (audio, vision, etc.)

---

### Paid GPU Demonstration (A100)

**Finding:** Cloud GPU pricing is approachable with small budgets
- A100 is dramatically faster than T4
- Cost example: ~$0.003 for single generation
- **Critical:** Pay for kernel uptime, not just inference time

**Key Insights:**
- Performance scales non-linearly with hardware
- Always shut down paid runtimes when done
- Small paid budget opens up powerful models

**Recommendation:** Use T4 for experimentation → Use A100 for production or time-sensitive tasks

---

### Kernel Restarts (Teaching Point)

**Finding:** Notebook intentionally restarts kernel multiple times as a lesson
- Reinforces that state is fragile
- Teaches that order of execution matters
- Builds comfort with restarting

**Key Insight:** This is a **lesson**, not inconvenience. Being comfortable with restarts is essential for Colab workflows.

**Recommendation:** Always be prepared to restart - run cells from top when reconnecting

---

## Upcoming Days
> Observations for Days 2–5 will be added incrementally.
