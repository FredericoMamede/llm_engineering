# Week 3 Learning Notes

> This file accumulates learning notes incrementally.  
> Each section reflects understanding at the end of that day.

> **Note:** Early days include more procedural detail as learning scaffolding.  
> From Day 4 onward, notes focus on **mental models, abstractions, and tradeoffs**.

## Overview

Bullet-point insights from Week 3 experiments. Focus on **why** things work, not just **what** works.

---

## Day 1: Google Colab Setup

### Goal of Day 1

Day 1 is **not about theory**. It's about **environment, hardware, and intuition**:
> *"What can I do when I have real GPU compute, even on a small budget?"*

This day deliberately:
- Shows off **capabilities** (image generation, TTS)
- Builds **confidence** with GPU workflows
- Sets expectations for **Colab realities** (resets, package reinstalls)
- Motivates the rest of Week 3

---

### What Google Colab Is

**Problem:** Need GPU access for model inference without local GPU hardware

**Solution:** Use Google Colab - a remote Jupyter notebook running on Google's machines

**What Colab Provides:**
- Remote Jupyter notebook interface
- Code runs "locally" *on that machine*, not your laptop
- Free access to **real GPUs** (Tesla T4)

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

**Key Learning:**
Colab is amazing for **experiments and demos**, not for long-running production workloads.

**Pattern:** Use Colab for experimentation, local for production

**Tradeoff:**
- **Colab:** Free GPU access, but limited hours, data leaves machine, state is fragile
- **Local:** Full control, but requires GPU hardware, setup complexity

---

### Colab Survival Guide (Operational Knowledge)

**Problem:** Colab failures are common and can be confusing

**Solution:** Develop required habits for runtime management

**Required Habits:**
- Always:
  - Click **Connect → Connect to a hosted runtime: T4**
  - Check **View Resources** to confirm GPU + memory
- If things break:
  - `Runtime → Disconnect and Delete Runtime`
  - Reconnect
  - Run cells **from the top**

**Restart Types (Critical Distinction):**
- **Restart session** → Kernel resets, packages remain installed, disk persists
- **Disconnect & delete runtime** → Everything wiped, start completely fresh

**Key Learning:**
Colab failures are normal. Recovery speed matters more than perfection.

**Pattern:** When in doubt → Disconnect and Delete Runtime → Reconnect → Run from top

---

### Environment Setup

**Problem:** Need consistent package versions across sessions

**Solution:** Pin package versions and reinstall each session

**Key Points:**
- Pinning versions avoids surprises
- Dependency warnings can usually be ignored
- Must reinstall every session (Colab doesn't persist packages)
- Package management is foundational, not optional

**Pattern:** Always start sessions with required package installations

**Tradeoff:**
- **Pinned versions:** Reproducible, but may miss updates
- **Latest versions:** New features, but potential breaking changes

---

### GPU Verification (Tesla T4)

**Problem:** Need to verify GPU type before running heavy models

**Solution:** Verify GPU availability and type before model execution

**Key Learning:**
- Always verify GPU *before* running heavy models
- Not all GPUs are equal (T4 vs A100 matters a lot)
- GPU can silently downgrade to CPU without warning

**Pattern:** Verify GPU type → Check memory → Then run models

**Tradeoff:**
- **Verification:** Adds step, but prevents wasted time on wrong hardware
- **Skip verification:** Faster, but risk running on CPU unknowingly

---

### Hugging Face Authentication

**Problem:** Need to access HuggingFace Hub models and avoid rate limits

**Solution:** Create HF token with WRITE permissions and store as Colab secret

**Why This Matters:**
- Avoids rate limits
- Enables model downloads
- Required for later weeks
- Mirrors real production secret management

**Key Learning:**
- Secrets management matters even in notebooks
- This pattern mirrors real production environments
- Never hardcode tokens
- WRITE permissions required (not fine-grained)

**Pattern:** Store secrets in Colab secrets → Access via `userdata.get()` → Never commit tokens

**Tradeoff:**
- **Secrets management:** More setup, but secure and production-ready
- **Hardcoded tokens:** Faster, but security risk and not scalable

---

### Text-to-Image Generation (Diffusers)

**Problem:** Want to understand what's possible with GPU-accelerated image generation

**Solution:** Explore multiple diffusers models with different speed/quality tradeoffs

**Model Variants:**
- **SDXL Turbo:** Very fast (4 inference steps), lower quality, instant feedback
- **SDXL Base:** More steps (30), better quality, slower
- **Base + Refiner:** Two-stage pipeline (80% base, 20% refiner), best quality, most complex

**Key Learning:**
- Same task → multiple architectures
- Tradeoffs: **speed vs quality**
- GPU memory & inference steps matter
- Diffusers library abstracts complexity

**Pattern:** Start with fast models for prototyping → Use quality models for final output

**Tradeoff:**
- **Fast models (Turbo):** Quick iteration, but lower quality
- **Quality models (Base + Refiner):** Better output, but slower and more memory

---

### Text-to-Speech on GPU

**Problem:** Want to understand GPU-accelerated audio generation

**Solution:** Use HuggingFace pipeline for text-to-speech with GPU acceleration

**Key Learning:**
- HuggingFace isn't just text models
- Audio workloads are GPU-accelerated
- Pipelines abstract a *lot* of complexity
- Speaker embeddings enable voice consistency

**Pattern:** Use `device='cuda'` for GPU acceleration in pipelines

**Tradeoff:**
- **GPU acceleration:** Faster inference, but requires GPU
- **CPU:** Works everywhere, but slower

---

### Paid GPU Demonstration (A100)

**Problem:** Want to understand what's possible with higher-tier GPUs

**Solution:** Demonstrate A100 capabilities (explicitly optional, educational)

**Purpose:**
- Show what's possible with **small paid budget**
- Demonstrate scale difference between T4 and A100
- Understand cloud GPU pricing model

**Key Learning:**
- Cloud GPU pricing is approachable (e.g., ~$0.003 per generation)
- Performance scales non-linearly with hardware
- **Critical:** You pay for **kernel uptime**, not just inference time
- Always shut down paid runtimes when done
- A100 is dramatically faster than T4

**Pattern:** Use T4 for experimentation → Use A100 for production workloads or time-sensitive tasks

**Tradeoff:**
- **T4 (Free):** Limited hours, slower, but free
- **A100 (Paid):** Much faster, longer sessions, but costs money

---

### Kernel Restarts (Repeated on Purpose)

**Problem:** Need to understand that Colab state is fragile

**Solution:** Notebook intentionally restarts kernel multiple times

**Why This Matters:**
- Reinforces that state is fragile
- Order of execution matters
- You must be comfortable restarting
- This is a **lesson**, not inconvenience

**Key Learning:**
- Always be prepared to restart
- Run cells from top when reconnecting
- Don't assume state persists

**Pattern:** When reconnecting → Always run from top → Don't skip setup cells

---

## Day 2: HuggingFace Pipelines

### Goal of Day 2

Day 2 introduces the **High-Level Pipeline API** - the simplest way to use pre-trained models for common inference tasks without worrying about model internals.

---

### High-Level Pipeline API

**Problem:** Want to use pre-trained models without understanding internals

**Solution:** Use HuggingFace `pipeline()` function

**How It Works:**
- Create a pipeline function for a specific task
- Call it repeatedly with different inputs
- Pipelines handle all the plumbing (tokenization, model loading, inference, decoding)

**Key Points:**
- If you don't specify a model, HuggingFace picks a default for the task
- Specify `device="cuda"` for NVIDIA GPU, `device="mps"` on Mac
- Pipelines abstract away all implementation details

**Pattern:** Create once → Call many times

**Tradeoff:**
- **Pipelines:** Easy to use, but less control
- **Manual inference:** More control, but more code

---

### Training vs Inference Distinction

**Problem:** Need to understand when to use pipelines vs lower-level APIs

**Solution:** Understand the fundamental difference between training and inference

**Training:**
- Model learns from data
- Updates internal settings (parameters/weights)
- Makes model better at task in the future
- **Fine-tuning:** Training a model that's already been trained

**Inference:**
- Using a model that has already been trained
- Producing new outputs on new inputs
- Taking advantage of what model learned during training
- Also called "Execution" or "Running a model"

**Key Learning:**
- Pipelines API is **only for inference** (using pre-trained models)
- All API usage (GPT, Claude, Gemini) from previous weeks = inference
- Week 7 will cover training - need lower-level APIs then
- "P" in GPT = "Pre-trained" (already trained with lots of data)

**Pattern:** Pipelines = Inference only, Lower-level APIs = Training + Inference

---

### Pipeline Tasks Explored

**Problem:** Want to understand what tasks pipelines can handle

**Solution:** Explore multiple pipeline tasks to see breadth of capabilities

**Tasks Covered:**
1. **Sentiment Analysis:** Analyze emotional tone, returns label and confidence
2. **Named Entity Recognition (NER):** Extract entities (people, places, organizations)
3. **Question Answering:** Answer questions from provided context
4. **Text Summarization:** Condense long text, controllable length
5. **Translation:** Translate between language pairs
6. **Zero-shot Classification:** Classify without training examples, provide labels at inference
7. **Text Generation:** Generate text continuations
8. **Image Generation (Diffusers):** Create images from text prompts
9. **Audio Generation (Text-to-Speech):** Convert text to speech with voice consistency

**Key Insight:** Same simple API pattern works across all tasks - just change the task name

**Pattern:** `pipeline(task_name, model=optional, device="cuda")` → `pipeline(input)`

**Tradeoff:**
- **Unified API:** Easy to learn, but less task-specific control
- **Task-specific APIs:** More control, but more to learn

---

### Model Selection in Pipelines

**Problem:** Default models may not be best for your use case

**Solution:** Specify custom models or use defaults

**Default Behavior:**
- If no model specified, HuggingFace picks default for the task
- Defaults are usually good starting points
- May not be optimal for specific use cases

**Key Learning:**
- Different models have different strengths
- Multilingual models for international text
- Larger models often better quality but slower
- **Pattern:** Start with default → Try specific models if needed

**Tradeoff:**
- **Default models:** Easy, but may not be optimal
- **Custom models:** Better results, but need to know which to choose

---

### Colab Pro-Tips (Day 2 Specific)

**Problem:** Colab has quirks that can be confusing

**Solution:** Learn specific troubleshooting patterns

**Pro-Tip 1: Warnings Can Be Ignored**
- Data Science code often gives warnings and messages
- Can mostly be safely ignored
- Glance over them, but don't worry unless something breaks
- If something goes wrong later, warnings might give clues

**Pro-Tip 2: Misleading CUDA Errors**
- Error: "CUDA is required but not available for bitsandbytes"
- This is **super-misleading** - don't try changing package versions
- **Real issue:** Google switched out your Colab runtime (too busy), runtime downgraded from GPU to CPU
- **Solution:** Full reset (Disconnect and delete runtime → Clear outputs → Reconnect → Verify GPU → Run from top)

**Key Learning:**
- CUDA errors often mean runtime switch, not package issue
- Full reset is usually the solution
- Always verify GPU after reconnecting

**Pattern:** CUDA error → Full reset → Verify GPU → Run from top

---

## Day 3: Tokenizers

### Goal of Day 3

Day 3 explores the world of Tokenizers - the crucial bridge between human-readable text and the numerical inputs that LLMs actually process. This day reveals the "missing piece" that connects high-level APIs to model internals.

---

### Basic Tokenization Process

**Problem:** Need to convert human-readable text into numerical inputs for LLMs

**Solution:** Use tokenizers to convert text → tokens → token IDs

**How It Works:**
1. **Text:** Human-readable string
2. **Tokens:** Fragments of words (not always whole words)
3. **Token IDs:** Numerical IDs that map to tokens in vocabulary

**Key Learning:**
- Character count ≠ Word count ≠ Token count
- Tokens are fragments of words, not always whole words
- Different tokenizers produce different tokenizations for the same text
- **Pattern:** Text → Tokens → Token IDs

**Example:**
- Text: "I am excited to show Tokenizers in action to my LLM engineers"
- Characters: ~70
- Words: ~12
- Tokens: ~15-20 (varies by tokenizer)

---

### Vocabulary and Token Mapping

**Problem:** Understand how tokens map to numerical IDs

**Solution:** Explore tokenizer vocabularies

**What's Shown:**
- Each tokenizer has a vocabulary (mapping of tokens to IDs)
- Vocabulary size varies by model
- Special tokens are added to vocabulary

**Key Learning:**
- Vocabulary is the mapping between tokens and their numerical IDs
- Special tokens (like `<|system|>`, `<|user|>`, `<|assistant|>`) are added to vocabulary
- Vocabulary size is a model hyperparameter

---

### Decoding Tokens

**Problem:** Convert token IDs back to text for verification

**Solution:** Use decode methods to reverse tokenization

**Key Learning:**
- Decode converts token IDs back to text
- Batch decode can handle multiple sequences
- Round-trip: text → tokens → token IDs → text (should match original)
- Useful for debugging and verification

**Pattern:** Token IDs → Decode → Original text (verification)

---

### Instruct Variants and Chat Templates

**Problem:** Many models have Instruct variants that expect specific prompt formats

**Solution:** Use chat templates to convert messages format to model-specific prompts

**What's Shown:**
- Instruct models are trained for chat/conversation
- They expect prompts with system, user, and assistant roles
- Each model has its own chat template format

**Key Learning:**
- Chat templates convert messages format to model-specific prompts
- Different models have different chat template formats
- Chat templates add special tokens for system/user/assistant roles
- Generation prompts ensure models respond rather than continue
- **Pattern:** Messages (list of dicts) → Chat template → Model-specific prompt

**Tradeoff:**
- **Messages format:** Easy to use, but model-specific
- **Chat templates:** Handles conversion automatically

---

### The Crucial "Aha" Moment

**Problem:** Understanding how high-level APIs (messages format) connect to model internals

**Solution:** Realize that LLMs take Token IDs as input, not Python objects

**The Revelation:**
For 2.5 weeks, we've been using messages format (list of Python dictionaries), but an LLM is just a Data Science model that takes a sequence of numbers and predicts the probability of the next number! You can't pass a bunch of Python objects into a statistical model!

**The Missing Piece:**
1. The messages in OpenAI format get converted:
   - ...into a sequence of words with special tags to separate the System, User, Assistant prompt
2. Then the words are broken down into fragments - "tokens"
3. Then the tokens are replaced with Token IDs - and this is the input sequence

**The Input to an LLM is a sequence of Token IDs. The output is the probability distribution of the next Token ID to follow this input.**

**Key Learning:**
- **LLMs take Token IDs as input, not Python objects**
- Messages format (list of dicts) is converted to token IDs
- Process: Messages → Text with tags → Tokens → Token IDs
- Output is probability distribution of next Token ID
- This is the missing piece connecting high-level APIs to model internals

**Pattern:** High-level API (messages) → Tokenization → Token IDs → Model → Probability distribution → Next token

---

### Multiple Models Comparison

**Problem:** Different models use different tokenizers with different behaviors

**Solution:** Compare tokenization across multiple models (Llama 3.1, Phi-4, DeepSeek, QwenCoder)

**What's Shown:**
- **Llama 3.1** (industry-common; see access notes below)
- **Phi-4** from Microsoft
- **DeepSeek 3.1** from DeepSeek AI
- **QwenCoder 2.5** from Alibaba Cloud (code-specific)

**Key Learning:**
- Same text produces different token IDs across models
- Each model has different tokenization behavior and chat template formats
- Code-specific models optimize tokenization for code

**Pattern:** Same text → Different tokenizers → Different token IDs → Different model behavior

**Tradeoff:**
- **Model-specific tokenizers:** Optimized for that model, but can't assume consistency
- **Universal tokenizer:** Would be convenient, but models are trained with specific tokenizers

---

### Llama 3.1 Access (Meta)

**Problem:** Some models require approval before use (e.g., Llama 3.1)

**Solution:** Follow Meta's terms of service agreement process

**Key Requirements:**
- Agree to terms of service (use same email as HF account if possible)
- Approval usually takes a few minutes
- Approval applies to the whole 3.1 family of models

**Key Learning:**
- Llama 3.1 is commonly used in industry, which is why it's included in this course
- Requires explicit approval from Meta
- Access restrictions exist for legal/licensing reasons

---

### CPU vs GPU Requirements

**Problem:** Understanding hardware requirements for tokenization vs. model inference

**Solution:** Recognize that tokenization is CPU-friendly, while inference is GPU-accelerated

**Key Insight:**
- **Tokenization = CPU-friendly** (can run locally without GPU)
- **Model inference = GPU-accelerated** (needs GPU for speed)

**Pattern:** Tokenization (CPU) → Model inference (GPU)

**Tradeoff:**
- **CPU:** Accessible, no GPU needed, slower for model inference
- **GPU:** Faster for model inference, but requires GPU access

---

## Day 4: Transformers Library Models

### Goal of Day 4

Day 4 moves beyond pipelines to the lower-level Transformers API, directly interacting with model objects, understanding quantization, and exploring Transformer architecture.
> This day marks the intentional shift from procedural learning to abstraction-first reasoning.


---

### Pipelines vs Direct Model Access

**Problem:** Pipelines abstract away control needed for customization

**Solution:** Use `AutoModelForCausalLM` for direct model access

**Key Learning:**
- Pipelines are convenient but limit customization
- Direct API enables fine-tuning, custom generation parameters, and architecture inspection
- Tradeoff: More code and complexity for greater control

**Pattern:** Pipelines for quick tasks → Direct API for production customization

---

### Quantization as Deployment Strategy

**Problem:** Full precision models exceed available GPU memory

**Solution:** Quantization reduces memory footprint at minimal quality cost

**Key Learning:**
- 4-bit quantization reduces model size by ~75%
- Essential for running large models on limited hardware (T4, consumer GPUs)
- Quality loss is usually minimal for most use cases
- Tradeoff: Slight quality reduction for massive memory savings

**Pattern:** Memory-constrained → Quantize → Run larger models

---

### Transformer Architecture Mental Model

**Problem:** Understanding how models process inputs internally

**Solution:** Recognize the consistent architecture pattern across models

**Key Learning:**
- Architecture flow: Input tokens → Embeddings → Decoder layers → LM Head → Output probabilities
- Decoder layers contain attention and MLP components
- Model depth (number of layers) directly affects capacity and performance
- Tradeoff: Deeper models = better performance but more memory and slower inference

**Pattern:** Architecture understanding enables better debugging and customization

---

### Streaming as UX Choice

**Problem:** Long generations create poor user experience (wait then see)

**Solution:** Stream outputs incrementally as tokens are generated

**Key Learning:**
- Streaming transforms perception from "waiting" to "watching progress"
- Standard pattern in production applications
- Tradeoff: Slightly slower but dramatically better UX

**Pattern:** Long generations → Stream → Better UX

---

### Generation Prompts for Instruct Models

**Problem:** Instruct models need explicit signals to generate responses vs. continuing prompts

**Solution:** Use generation prompts in chat templates

**Key Learning:**
- Without generation prompt, models predict continuation of user message
- With generation prompt, models understand they should respond
- Critical distinction for chat/conversation applications
- Tradeoff: Adds tokens but ensures proper behavior

**Pattern:** Instruct models → Generation prompts → Proper responses

---

### Memory Management as Runtime Concern

**Problem:** GPU memory is limited and must be managed when switching models

**Solution:** Systematic cleanup process (delete references, garbage collect, clear cache)

**Key Learning:**
- Memory management is not optional when running multiple models
- Three-step cleanup ensures memory is actually freed
- Memory may not show as freed immediately in UI but is available
- Tradeoff: More code but prevents out-of-memory errors

**Pattern:** Switch models → Cleanup → Load next model

---

### Model Selection Tradeoffs

**Problem:** Different models have different strengths, sizes, and access requirements

**Solution:** Understand model characteristics to make informed choices

**Key Learning:**
- Model selection involves balancing quality, memory, speed, and access requirements
- Some models require quantization, others don't (size-dependent)
- Access restrictions exist for legal/licensing reasons
- Tradeoff: Restricted models often better quality but require approval; open models more accessible but may have limitations

**Pattern:** Task requirements → Model characteristics → Selection decision

---

## Day 5: Meeting Minutes Creator
> 🚧 To be completed after Day 5 experiments

---

## References

- Course material: Week 3 Day 1-5 notebooks
- HuggingFace Transformers: https://huggingface.co/docs/transformers
- HuggingFace Hub: https://huggingface.co/models
- Google Colab: https://colab.research.google.com
- Transformers Library: https://github.com/huggingface/transformers
- Tokenizers Library: https://github.com/huggingface/tokenizers
