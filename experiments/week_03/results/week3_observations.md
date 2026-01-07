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

## Day 2: HuggingFace Pipelines

### Goal of Day 2

Day 2 introduces the **High-Level Pipeline API** - the simplest way to use pre-trained models for common inference tasks without worrying about model internals.

---

### High-Level Pipeline API

**Finding:** Pipelines make model usage incredibly simple
- Two-step pattern: Create pipeline → Call pipeline
- One function call for complex tasks
- Automatic model selection if not specified
- GPU acceleration via `device="cuda"` parameter

**Key Pattern:**
```python
my_pipeline = pipeline(task, model=optional, device="cuda")
result = my_pipeline(input)
```

**Tradeoff:**
- **Pipelines:** Easy to use, but less control
- **Manual inference:** More control, but more code

**Recommendation:** Use pipelines for quick prototyping, manual for production

---

### Training vs Inference Distinction

**Finding:** Understanding this distinction is crucial for knowing when to use pipelines
- Pipelines are **only for inference** (using pre-trained models)
- Training requires lower-level APIs (Week 7)
- All API usage from previous weeks (GPT, Claude, Gemini) = inference

**Key Insight:** "P" in GPT = "Pre-trained" - already trained, we're just using it

**Recommendation:** Use pipelines for inference tasks, learn lower-level APIs for training

---

### Multiple Pipeline Tasks

**Finding:** Pipelines support many tasks with same simple API

**Tasks Explored:**
1. **Sentiment Analysis:** Analyze emotional tone
2. **Named Entity Recognition (NER):** Extract entities
3. **Question Answering:** Answer questions from context
4. **Text Summarization:** Condense long text
5. **Translation:** Translate between languages
6. **Zero-shot Classification:** Classify without training examples
7. **Text Generation:** Generate text continuations
8. **Image Generation:** Create images from text (Diffusers)
9. **Audio Generation (TTS):** Convert text to speech

**Key Insight:** Same simple API pattern works across all tasks - just change the task name

**Recommendation:** Explore different pipeline tasks to understand breadth of capabilities

---

### Model Selection in Pipelines

**Finding:** Can use defaults or specify custom models
- Default models are good starting points
- Custom models can improve results for specific use cases
- Different models have different strengths (multilingual, quality, speed)

**Key Insight:** Start with default → Try specific models if needed

**Recommendation:** Use defaults for prototyping, research specific models for production

---

### Colab Pro-Tips (Day 2 Specific)

**Finding:** Colab has specific quirks that can be confusing

**Pro-Tip 1: Warnings**
- Data science warnings can mostly be ignored
- Glance over them, but don't worry unless something breaks
- Warnings might give clues if something goes wrong later

**Pro-Tip 2: Misleading CUDA Errors**
- CUDA errors often mean runtime was switched (not package issue)
- Don't try changing package versions
- Solution: Full reset (Disconnect & delete → Reconnect → Run from top)

**Key Insight:** CUDA errors = runtime switch, not code problem

**Recommendation:** When CUDA errors appear → Full reset → Verify GPU → Run from top

---

---

## Day 3: Tokenizers

### Goal of Day 3

Day 3 explores the world of Tokenizers - the crucial bridge between human-readable text and the numerical inputs that LLMs actually process. This day reveals the "missing piece" that connects high-level APIs to model internals.

---

### Basic Tokenization Process

**Finding:** Tokenization converts text to numerical inputs that LLMs can process
- Process: Text → Tokens → Token IDs
- Character count ≠ Word count ≠ Token count
- Tokens are fragments of words, not always whole words
- Different tokenizers produce different tokenizations for the same text

**Key Insight:** Understanding tokenization is essential for debugging model behavior and understanding token limits

**Recommendation:** Always verify token counts, not character/word counts when working with token limits

---

### Vocabulary and Token Mapping

**Finding:** Each tokenizer has a vocabulary mapping tokens to numerical IDs
- Vocabulary size varies by model
- Special tokens are added to vocabulary
- Can inspect vocabulary to understand token structure

**Key Insight:** Vocabulary is the bridge between human-readable tokens and numerical IDs

**Recommendation:** Inspect vocabularies when debugging tokenization issues

---

### Decoding Tokens

**Finding:** Token IDs can be decoded back to text for verification
- `decode()` converts token IDs back to text
- Round-trip verification: text → tokens → token IDs → text
- Useful for debugging and understanding model outputs

**Key Insight:** Decoding is the reverse of encoding - allows verification of tokenization

**Recommendation:** Use decode() to verify tokenization round-trips correctly

---

### Instruct Variants and Chat Templates

**Finding:** Instruct models require specific prompt formats via chat templates
- `apply_chat_template()` converts messages format to model-specific prompts
- Different models have different chat template formats
- Chat templates add special tokens for system/user/assistant roles

**Key Insight:** Chat templates are model-specific - can't assume one format works for all models

**Recommendation:** Always use `apply_chat_template()` for Instruct models, don't manually format prompts

---

### The Crucial "Aha" Moment

**Finding:** LLMs take Token IDs as input, not Python objects
- Messages format (list of dicts) is converted to token IDs
- Process: Messages → Text with tags → Tokens → Token IDs
- Output is probability distribution of next Token ID
- This is the missing piece connecting high-level APIs to model internals

**Key Insight:** This revelation connects everything - explains how high-level APIs work under the hood

**Recommendation:** Internalize this understanding - it's foundational for working with LLMs

---

### Multiple Models Comparison

**Finding:** Different models use different tokenizers with different behaviors
- Same text produces different token IDs across models
- Each model has different tokenization behavior and chat templates

**Models Explored:**
- **Llama 3.1:** (industry-standard; see access notes below)
- **Phi-4:** Microsoft's model
- **DeepSeek 3.1:** DeepSeek AI model
- **QwenCoder 2.5:** Alibaba Cloud's code-specific model

**Key Insight:** Can't assume tokenization is consistent across models - each has its own behavior

**Recommendation:** Test tokenization with your specific model before production use

---

### Llama 3.1 Access (Meta)

**Finding:** Llama 3.1 requires Meta approval but is commonly used in industry
- Must sign Meta's terms of service
- Approval usually comes in a couple of minutes
- Approval applies to whole 3.1 family
- **Important:** Llama 3.1 is commonly used in industry, which is why it's included in the course

**Key Insight:** Industry relevance justifies the approval process

**Recommendation:** Complete Meta approval early - it's quick and unlocks industry-standard models

---

### CPU vs GPU Requirements

**Finding:** Tokenization can run on CPU, no GPU needed
- Tokenizers are CPU-friendly
- Tokenization is fast even on CPU
- GPU verification is useful but not required

**Key Insight:** Tokenization and model inference have different hardware requirements

**Recommendation:** Use CPU for tokenization, GPU for model inference

**Tradeoff:**
- **CPU:** Accessible, no GPU needed, sufficient for tokenization
- **GPU:** Required for fast model inference, but not needed for tokenization

---

## Upcoming Days
> Observations for Days 4–5 will be added incrementally.
