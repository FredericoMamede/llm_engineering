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

---

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

Day 2 introduces the **High-Level Pipeline API** – the simplest way to use pre-trained models for common inference tasks without worrying about model internals.

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

### Goal of Day 3

Day 3 explores the world of Tokenizers - the crucial bridge between human-readable text and the numerical inputs that LLMs actually process. This day reveals the "missing piece" that connects high-level APIs to model internals.

### What I'm Testing

#### 1. Basic Tokenization Process
**What:** Understand how text is converted to tokens and token IDs

**Why:**
- Foundation for understanding how LLMs process input
- Essential for debugging model behavior
- Critical for understanding token limits

**What I learned:**
- Tokenization process: Text → Tokens → Token IDs
- Character count ≠ Word count ≠ Token count
- Tokens are fragments of words, not always whole words
- Different tokenizers produce different tokenizations for the same text
- **Pattern:** `tokenizer.encode(text)` → list of token IDs

#### 2. Vocabulary and Token Mapping
**What:** Explore tokenizer vocabularies and token-to-ID mappings

**Why:**
- Understand how tokens map to numerical IDs
- Learn about vocabulary size and special tokens
- Foundation for understanding model inputs

**What I learned:**
- Each tokenizer has a vocabulary (mapping of tokens to IDs)
- Vocabulary size varies by model
- Special tokens are added to vocabulary
- Can inspect vocabulary with `tokenizer.vocab` and `tokenizer.get_added_vocab()`

#### 3. Decoding Tokens
**What:** Convert token IDs back to text

**Why:**
- Verify tokenization round-trip
- Understand model outputs
- Debug tokenization issues

**What I learned:**
- `decode()` converts token IDs back to text
- `batch_decode()` can decode multiple sequences
- Round-trip: text → tokens → token IDs → text (should match original)

#### 4. Instruct Variants and Chat Templates
**What:** Understand how chat/conversation models format prompts

**Why:**
- Many models have Instruct variants for chat
- Need to format messages correctly for each model
- Foundation for building chat applications

**What I learned:**
- Instruct models are trained for chat/conversation
- `apply_chat_template()` converts messages format to model-specific prompts
- Different models have different chat template formats
- Chat templates add special tokens for system/user/assistant roles
- **Pattern:** Messages (list of dicts) → Chat template → Model-specific prompt

#### 5. The Crucial "Aha" Moment
**What:** Understand that LLMs take Token IDs as input, not Python objects

**Why:**
- This is the missing piece connecting high-level APIs to model internals
- Explains how messages format gets converted to model inputs
- Foundation for understanding model architecture

**What I learned:**
- **LLMs take Token IDs as input, not Python objects**
- Messages format (list of dicts) is converted to token IDs
- Process: Messages → Text with tags → Tokens → Token IDs
- Output is probability distribution of next Token ID
- **This is the missing piece** - LLMs are statistical models that predict next token

#### 6. Multiple Models Comparison
**What:** Compare tokenization across different models

**Why:**
- Different models use different tokenizers
- Understanding differences helps choose the right model
- See how tokenization affects model behavior

**What I learned:**
- **Llama 3.1:** Commonly used in industry (why it's in the course), requires Meta approval
- **Phi-4:** Microsoft's model
- **DeepSeek 3.1:** DeepSeek AI model
- **QwenCoder 2.5:** Alibaba Cloud's code-specific model
- Each has different tokenization behavior and chat templates
- Same text produces different token IDs across models

#### 7. Llama 3.1 Access (Meta)
**What:** Set up access to Llama 3.1 from Meta

**Why:**
- Requires special approval process (see Multiple Models Comparison section for industry relevance)
- Important for real-world applications

**What I learned:**
- Must sign Meta's terms of service
- Approval usually comes in a couple of minutes
- Approval applies to whole 3.1 family of models
- Troubleshooting steps if access is denied

#### 8. CPU vs GPU Requirements
**What:** Understand that tokenizers can run on CPU

**Why:**
- Tokenization doesn't require GPU
- Can run locally without GPU hardware
- More accessible for experimentation

**What I learned:**
- Can run tokenizers on CPU (no GPU needed)
- Tokenization is fast even on CPU
- GPU verification is still useful but not required
- **Pattern:** Tokenization = CPU-friendly, Model inference = GPU-accelerated

---

## Day 4: Transformers Library Models

### Goal of Day 4

Day 4 moves beyond pipelines to the lower-level Transformers API, directly interacting with model objects, understanding quantization, and exploring Transformer architecture.
This day marks the transition from high-level abstractions to explicit model execution and resource-aware inference.

### What I'm Testing

- Direct model access via `AutoModelForCausalLM` for customization beyond pipelines
- Quantization as a deployment strategy for memory-constrained environments
- Transformer architecture internals (embeddings, decoder layers, attention mechanisms)
- Streaming outputs for better user experience
- Generation prompts to ensure proper Instruct model behavior
- Memory management patterns for multi-model workflows
- Model selection tradeoffs across different architectures

### What I Learned

- Pipelines abstract away control; direct API access enables fine-tuning and customization
- Quantization is a necessary tradeoff for running large models on limited hardware
- Transformer architecture follows a consistent pattern: embeddings → decoder layers → LM head
- Streaming transforms user experience from "wait then see" to "see as it generates"
- Generation prompts are critical for Instruct models to respond rather than continue
- Memory management is a runtime concern, not just a setup step
- Model selection involves balancing quality, memory, speed, and access requirements

---

## Day 5: Meeting Minutes Creator

### Goal of Day 5

Day 5 builds an end-to-end AI workflow that combines audio transcription with LLM-powered text analysis to create structured meeting minutes from raw audio files.

### What I'm Testing

- Token prediction visualization: Understanding how models predict tokens one at a time with probability distributions
- Google Drive integration with Colab for persistent file storage
- Automatic speech recognition (ASR) using HuggingFace Whisper pipeline
- OpenAI transcription API as alternative transcription option
- End-to-end pipeline: Audio → Transcription → LLM Analysis → Structured Meeting Minutes
- System prompts for structured output generation
- Real-world application pattern for audio-to-text workflows

### What I Learned

- Model inference is token-by-token prediction: Each token is chosen from a probability distribution, with alternatives showing what the model "almost said"
- Visualizing token predictions reveals the probabilistic nature of LLMs and helps understand uncertainty in outputs
- Combining multiple AI capabilities (ASR + LLM) creates powerful end-to-end applications
- Transcription options involve tradeoffs: open-source (free, GPU-based) vs. API (paid, cloud-based, potentially higher quality)
- Google Drive mounting enables persistent file access in ephemeral Colab environments
- LLMs excel at transforming unstructured transcripts into structured formats (summaries, action items, takeaways)
- System prompts are critical for guiding LLM output format and structure
- This pattern generalizes to any audio-to-structured-text workflow (interviews, lectures, podcasts, customer calls)

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
