# Week 3 Learning Notes

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

**Package Installation:**
```bash
!pip install -q --upgrade transformers==4.56.2
```

**Key Points:**
- Pinning versions avoids surprises
- Dependency warnings can usually be ignored
- No installs later in course ≠ no installs ever — this is foundational
- Must reinstall every session (Colab doesn't persist packages)

**Pattern:** Always start sessions with required package installations

---

### GPU Verification (Tesla T4)

**Problem:** Need to verify GPU type before running heavy models

**Solution:** Use `nvidia-smi` to check GPU availability and type

**Verification Code:**
```python
gpu_info = !nvidia-smi
gpu_info = '\n'.join(gpu_info)
if gpu_info.find('failed') >= 0:
  print('Not connected to a GPU')
else:
  print(gpu_info)
  if gpu_info.find('Tesla T4') >= 0:
    print("Success - Connected to a T4")
  else:
    print("NOT CONNECTED TO A T4")
```

**Key Learning:**
- Always verify GPU *before* running heavy models
- Not all GPUs are equal (T4 vs A100 matters a lot)
- GPU can silently downgrade to CPU

**Pattern:** Verify GPU type → Check memory → Then run models

---

### Hugging Face Authentication

**Problem:** Need to access HuggingFace Hub models and avoid rate limits

**Solution:** Create HF token with WRITE permissions and store as Colab secret

**Why This Matters:**
- Avoids rate limits
- Enables model downloads
- Required for later weeks
- Mirrors real production secret management

**Setup Steps:**
1. Create HuggingFace account at https://huggingface.co
2. Navigate to Settings → Access Tokens
3. Create new token with **WRITE** permissions (not fine-grained)
4. Copy token (starts with `hf_...`)
5. In Colab: Press key icon → Add secret:
   - Name: `HF_TOKEN`
   - Value: Your token
   - Ensure notebook access switch is ON

**Code Used:**
```python
from huggingface_hub import login
from google.colab import userdata

hf_token = userdata.get('HF_TOKEN')
login(hf_token, add_to_git_credential=True)
```

**Key Learning:**
- Secrets management matters even in notebooks
- This pattern mirrors real production environments
- Never hardcode tokens

**Pattern:** Store secrets in Colab secrets → Access via `userdata.get()` → Never commit tokens

---

### Text-to-Image Generation (Diffusers)

**Problem:** Want to understand what's possible with GPU-accelerated image generation

**Solution:** Explore multiple diffusers models with different speed/quality tradeoffs

#### First Demo: SDXL Turbo (Fast)

```python
from diffusers import AutoPipelineForText2Image
pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16")
pipe.to("cuda")
image = pipe(prompt=prompt, num_inference_steps=4, guidance_scale=0.0).images[0]
```

**Characteristics:**
- Very fast (4 inference steps)
- Lower quality but instant feedback
- Good for rapid iteration

#### Second Demo: SDXL Base (Higher Quality)

```python
from diffusers import DiffusionPipeline
pipe = DiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, variant="fp16")
pipe.to("cuda")
image = pipe(prompt=prompt, num_inference_steps=30).images[0]
```

**Characteristics:**
- More steps (30 vs 4)
- Better quality
- Slower

#### Third Demo: Base + Refiner (Advanced)

```python
# Split inference: 80% base model, 20% refiner
n_steps = 40
high_noise_frac = 0.8

image = base(prompt=prompt, num_inference_steps=n_steps, denoising_end=high_noise_frac, output_type="latent").images
image = refiner(prompt=prompt, num_inference_steps=n_steps, denoising_start=high_noise_frac, image=image).images[0]
```

**Characteristics:**
- Two-stage pipeline (base + refiner)
- Produces noticeably better images
- More complex setup

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

**Code:**
```python
from transformers import pipeline
from datasets import load_dataset
import soundfile as sf
import torch
from IPython.display import Audio

synthesiser = pipeline("text-to-speech", "microsoft/speecht5_tts", device='cuda')
embeddings_dataset = load_dataset("matthijs/cmu-arctic-xvectors", split="validation", trust_remote_code=True)
speaker_embedding = torch.tensor(embeddings_dataset[7306]["xvector"]).unsqueeze(0)
speech = synthesiser("Hi to an artificial intelligence engineer, on the way to mastery!", forward_params={"speaker_embeddings": speaker_embedding})

Audio(speech["audio"], rate=speech["sampling_rate"])
```

**Key Learning:**
- HuggingFace isn't just text models
- Audio workloads are GPU-accelerated
- Pipelines abstract a *lot* of complexity
- Speaker embeddings enable voice consistency

**Pattern:** Use `device='cuda'` for GPU acceleration in pipelines

---

### Paid GPU Demonstration (A100)

**Problem:** Want to understand what's possible with higher-tier GPUs

**Solution:** Demonstrate A100 capabilities (explicitly optional, educational)

**Purpose:**
- Show what's possible with **small paid budget**
- Demonstrate scale difference between T4 and A100
- Understand cloud GPU pricing

**Model Used:**
```python
from diffusers import FluxPipeline
pipe = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-schnell", torch_dtype=torch.bfloat16).to("cuda")
```

**Cost Estimation:**
- A100 = 5.37 compute units per hour (as of Oct 2025)
- $9.99 = 100 compute units
- Example: ~$0.003 for a single generation
- **Critical:** You pay for **kernel uptime**, not just inference time

**Key Learning:**
- Cloud GPU pricing is approachable
- Performance scales non-linearly with hardware
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
> 🚧 To be completed after Day 2 experiments

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

## References

- Course material: Week 3 Day 1-5 notebooks
- HuggingFace Transformers: https://huggingface.co/docs/transformers
- HuggingFace Hub: https://huggingface.co/models
- Google Colab: https://colab.research.google.com
- Transformers Library: https://github.com/huggingface/transformers
- Tokenizers Library: https://github.com/huggingface/tokenizers
