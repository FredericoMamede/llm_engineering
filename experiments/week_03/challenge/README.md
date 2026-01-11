# Week 3 Challenge — Synthetic Data Generation System

> **Status:** ✅ Implemented  
> **Scope:** Business-oriented experimentation  
> **Focus:** System design, model diversity, and data generation patterns

---

## 🎯 Challenge Objective

Design and implement a **synthetic data generation system** that can:

- Generate structured datasets using LLMs
- Use **multiple models** and **prompt strategies**
- Produce **diverse but controlled outputs**
- Expose functionality through a **simple Gradio UI**

This is a **business challenge**, not a research or training task.

---

## 🧠 Why This Matters

Synthetic data generation applies to:

- Data augmentation
- Testing pipelines
- Privacy-safe datasets
- Prototyping ML systems
- Prompt and model evaluation
- Business intelligence simulations

This pattern is reusable across **almost every industry**.

---

## 🧱 Design Principles

This challenge intentionally emphasizes:

- **System thinking**, not just model calls
- **Prompt design as a first-class tool**
- **Model diversity**, not “best model only”
- **Reproducibility and control**
- **UX clarity** over raw performance

This is **not** a portfolio artifact — it's a learning and design exercise.

---

## 🚫 Non-Goals

This system intentionally does **NOT**:

- **Train or fine-tune models** — This is an inference-only system
- **Optimize for throughput or latency** — Designed for exploration, not production performance
- **Enforce strict semantic validation** — Validation focuses on structure, not business logic correctness
- **Persist datasets in a database** — Outputs are saved as local JSON files only
- **Serve as a production system** — This is a learning exercise, not a production-ready pipeline

These tradeoffs were chosen to prioritize **learning speed, architectural clarity, and understanding of system design patterns** over production concerns.

---

## 🗂️ Proposed Structure

```text
challenge/
├── README.md
├── data_generation/
│   ├── generators.py        # Core generation logic
│   ├── schemas.py           # Output schemas / contracts
│   └── validators.py        # Optional consistency checks
├── prompts/
│   ├── base_prompts.md
│   ├── variation_strategies.md
│   └── domain_templates/
├── models/
│   ├── hf_models.py         # Hugging Face integrations
│   ├── openai_models.py     # OpenAI API usage
│   └── ollama_models.py     # Local models via Ollama
├── ui/
│   └── app.py               # Gradio interface
├── experiments/
│   ├── prompt_diversity.ipynb
│   └── model_comparison.ipynb
└── outputs/
    └── generated_samples/
```

---

## 🤖 Supported Models

### HuggingFace Models

#### Gated Models (Requires Access)
- **Llama 3.1**: `meta-llama/Meta-Llama-3.1-8B-Instruct`, `meta-llama/Meta-Llama-3.1-70B-Instruct`
- **Llama 3.2**: `meta-llama/Llama-3.2-1B-Instruct`, `meta-llama/Llama-3.2-3B-Instruct`
- **Llama 3.3**: `meta-llama/Llama-3.3-8B-Instruct` 
- **Llama 4**: `meta-llama/Llama-4-Scout-17B-16E-Instruct`, `meta-llama/Llama-4-Maverick-17B-128E-Instruct`, `meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8`
- **Gemma 2**: `google/gemma-2-2b-it`, `google/gemma-2-9b-it`, `google/gemma-2-27b-it`

#### Open Models (No Access Required)
- **Phi-3**: `microsoft/Phi-3-mini-4k-instruct`, `microsoft/Phi-3-medium-4k-instruct`
- **Phi-4**: `microsoft/Phi-4-mini-instruct`
- **Qwen 2.5**: `Qwen/Qwen2.5-0.5B-Instruct`, `Qwen/Qwen2.5-1.5B-Instruct`, `Qwen/Qwen2.5-3B-Instruct`, `Qwen/Qwen2.5-7B-Instruct`, `Qwen/Qwen2.5-14B-Instruct`
- **Mistral**: `mistralai/Mistral-7B-Instruct-v0.2`, `mistralai/Mistral-7B-Instruct-v3`
- **TinyLlama**: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`
- **Zephyr**: `HuggingFaceH4/zephyr-7b-beta`, `HuggingFaceH4/zephyr-7b-alpha`
- **DeepSeek Coder**: `deepseek-ai/DeepSeek-Coder-1.3B-Instruct`, `deepseek-ai/DeepSeek-Coder-6.7B-Instruct`
- **Falcon**: `tiiuae/falcon-7b-instruct`
- **OpenELM**: `apple/OpenELM-1_1B-Instruct`

### OpenAI Models
- `gpt-4o`, `gpt-4o-mini`
- `gpt-4-turbo`, `gpt-4`
- `gpt-3.5-turbo`

### Ollama Models (Local)
Requires Ollama running locally. Common models:
- `llama3.2:3b`, `llama3.1:8b`
- `mistral`, `mistral:7b`
- `phi3`, `qwen2.5:7b`
- `gemma2:2b`, `tinyllama`

---

## 🔐 Authentication Setup

**Important:** This system uses environment variables for authentication. Never commit credentials to version control.

1. **Create a `.env` file** in the `challenge/` directory:
   ```bash
   # HuggingFace Token (required for gated models like Llama, Gemma)
   # Get your token from: https://huggingface.co/settings/tokens
   # Make sure it has WRITE permissions
   HF_TOKEN=hf_your_token_here
   
   # OpenAI API Key (required for OpenAI models)
   # Get your key from: https://platform.openai.com/api-keys
   OPENAI_API_KEY=sk-your_key_here
   ```

2. **The `.env` file is already in `.gitignore`** — your credentials will not be committed.

3. **Models requiring authentication** will be marked with `[🔒 Auth Required]` in the UI dropdown.

4. **Authentication status** is displayed at the bottom of the UI, showing which credentials are configured.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd experiments/week_03/challenge
pip install -r requirements.txt
```

### 2. Set Up Authentication

Create a `.env` file in the `challenge/` directory:

```bash
# Copy and edit with your credentials
HF_TOKEN=hf_your_token_here
OPENAI_API_KEY=sk-your_key_here
```

**Get your credentials:**
- **HuggingFace Token**: https://huggingface.co/settings/tokens (needs WRITE permissions)
- **OpenAI API Key**: https://platform.openai.com/api-keys

**Note:** Models requiring authentication will be marked with `[🔒 Auth Required]` in the UI. The authentication status is displayed at the bottom of the UI.

**Ollama (for local models):**
```bash
# Start Ollama service
ollama serve

# Pull models you want to use
ollama pull llama3.2:3b
```

### 3. Launch Gradio UI

```bash
cd experiments/week_03/challenge
python ui/app.py
```

The UI will open at `http://localhost:7860`

### 4. Generate Data

1. Select provider (HuggingFace, OpenAI, or Ollama)
2. Choose a model
3. Select schema type (customer_record, incident_report, etc.)
4. Set number of records
5. Adjust generation parameters:
   - **Temperature**: Controls creativity (0.3-0.5 for structured data, 0.7-1.0 for variety)
   - **Max Tokens**: 💡 **Auto-updates** based on number of records and schema complexity. You can adjust manually if needed.
6. Click "Generate Dataset"
7. View results and download JSON file

**Smart Defaults:**
- The `max_tokens` parameter automatically adjusts when you change the number of records or schema type
- Complex schemas (like `meeting_summary` with nested arrays) get higher token limits
- Simple schemas (like `customer_record`) get lower token limits
- This ensures you get all requested records without manual calculation

### 5. Run Tests

**Quick smoke tests:**
```bash
cd experiments/week_03/challenge
python run_tests.py
```

**Comprehensive testing:**
See `TESTING_GUIDE.md` for complete testing checklist covering:
- Model provider tests (HF, OpenAI, Ollama)
- Schema generation tests
- Validation tests
- UI functionality tests
- Error handling tests
- Integration tests

---

## ✨ Key Features

- **Multi-Provider Support**: HuggingFace (open & gated), OpenAI API, Ollama (local)
- **Smart Token Estimation**: `max_tokens` auto-updates based on record count and schema complexity
- **Schema Filtering**: Automatically removes schema definitions and placeholder values from outputs
- **Authentication Management**: Environment-based auth with visual indicators for required credentials
- **Multiple Prompt Strategies**: Formal, casual, detailed, concise, diverse variations
- **Lightweight Validation**: Structural validation ensures all required fields are present
- **Export to JSON**: Generated datasets saved as JSON files for easy use

## 📊 Supported Schemas

- **customer_record**: Customer data with demographics, purchase history (~150 tokens/record)
- **incident_report**: Support tickets, bug reports, issues (~200 tokens/record)
- **meeting_summary**: Meeting notes with attendees, action items (~400 tokens/record)
- **business_event**: Transactions, subscriptions, events (~250 tokens/record)
- **product_review**: Product reviews with ratings (~200 tokens/record)
- **employee_record**: Employee data with roles, departments (~180 tokens/record)
- **generic_json**: Generic JSON records with variable structure (~300 tokens/record)

*Token estimates shown are approximate and used for auto-calculation of `max_tokens`.*

---

## 🎨 Prompt Strategies

- **default**: Standard prompt
- **formal**: Professional, business tone
- **casual**: Conversational, relaxed tone
- **detailed**: Extra context and information
- **concise**: Brief, minimal information
- **diverse**: Maximum variety in values

---

## 🔬 Experiments

Two Jupyter notebooks for exploration:

1. **`model_comparison.ipynb`**: Compare outputs from different models
2. **`prompt_diversity.ipynb`**: Explore how prompt strategies affect outputs

---

## 🏗️ Architecture

### Model Abstraction

All models implement `BaseModel` interface:
- `generate(prompt, config) -> ModelResponse`
- Works with any provider (HF, OpenAI, Ollama)
- Generation logic is provider-agnostic

### Data Generation Flow

1. **Prompt Construction**: Schema + template + variation strategy
2. **Model Call**: Via `BaseModel` interface
3. **Parsing**: Extract JSON from model output
4. **Validation**: Lightweight structure validation
5. **Cleaning**: Remove extra fields, fix types
6. **Export**: Save to JSON file

### Key Design Decisions

- **Adapter Pattern**: All models share common interface
- **Lazy Loading**: Models loaded only when needed
- **Optional Quantization**: 4-bit quantization for HF models (saves memory)
- **Smart Defaults**: Auto-calculated `max_tokens` based on schema complexity and record count
- **Schema Filtering**: Automatic removal of schema definitions and placeholder values
- **Lightweight Validation**: Structure checks, not semantic validation
- **Graceful Failure**: Errors return structured responses, don't crash

---

## 💡 Usage Examples

### Programmatic Usage

```python
from models import create_model
from models.base import GenerationConfig
from data_generation.generators import DataGenerator
from data_generation.schemas import SchemaType

# Create model
model = create_model("huggingface", "Qwen/Qwen2.5-3B-Instruct")

# Create generator
generator = DataGenerator(model)

# Generate dataset
result = generator.generate_dataset(
    schema_type=SchemaType.CUSTOMER_RECORD,
    num_records=10,
    variation_strategy="diverse",
    config=GenerationConfig(temperature=0.7, max_tokens=512)
)

# Access results
records = result["records"]
print(f"Generated {len(records)} records")
```

---

## 📝 Notes

- **Quantization**: Enabled by default for HuggingFace models to reduce memory usage on consumer GPUs. It should be disabled when output fidelity is critical or when sufficient VRAM is available. Quantization may reduce output quality on smaller models.
- **Memory Management**: HF models can be unloaded with `model.unload()`
- **Error Handling**: All errors return structured responses
- **JSON Parsing**: Handles markdown code blocks, embedded JSON, etc. Extraction is best-effort and may fail for some model outputs.
- **Validation**: Lightweight - checks structure, not business logic

---

## ⚠️ Known Limitations

- **Output quality depends heavily on prompt clarity and model choice** — Different models and prompts produce varying quality results
- **JSON extraction is best-effort, not guaranteed** — Some model outputs may not parse correctly, especially with smaller or less instruction-tuned models
- **Quantization may reduce output quality on smaller models** — Consider disabling quantization for quality-critical use cases
- **Gradio UI is single-user and not designed for concurrency** — The interface is intended for local experimentation, not multi-user deployment
- **No semantic validation** — The system validates structure (required fields, types) but does not verify semantic correctness or business logic

These limitations are intentional and reflect the learning-oriented scope of this challenge.

---

## 🎯 Next Steps

- Experiment with different models and strategies
- Add custom schemas in `data_generation/schemas.py`
- Create custom prompt templates in `prompts/`
- Extend validation logic in `data_generation/validators.py`
- Add new model providers by implementing `BaseModel`

---

## 🔗 Relationship to Mini-Project

This challenge is intentionally **broad and exploratory** — it demonstrates system design patterns, model abstraction, and prompt engineering across multiple providers.

The upcoming **mini-project** will be:
- **Narrower in scope** — Focused on a specific use case or domain
- **Deeper in implementation** — More polished, production-aware patterns
- **More product-focused** — Designed with end-user needs in mind

Not all code from this challenge is expected to be reused in the mini-project. This challenge serves as a **learning foundation** for understanding LLM integration patterns, not as a reusable library.

---

## 📚 References

- [HuggingFace Transformers](https://huggingface.co/docs/transformers)
- [OpenAI API](https://platform.openai.com/docs)
- [Ollama](https://ollama.ai)
- [Gradio](https://gradio.app)