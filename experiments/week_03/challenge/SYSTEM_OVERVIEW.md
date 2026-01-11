# Complete System Overview - Week 3 Challenge

> **Comprehensive documentation of all files, functionality, and system components**

---

## 📁 Project Structure

```
challenge/
├── README.md                          # Main documentation
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git ignore rules
├── .env                               # Environment variables (not in git)
├── run_tests.py                       # Automated smoke tests
├── TESTING_GUIDE.md                   # Comprehensive testing guide
├── HUGGINGFACE_CACHE_GUIDE.md         # HF model cache management (not in git)
├── SYSTEM_OVERVIEW.md                 # This file
│
├── models/                            # Model provider implementations
│   ├── __init__.py                    # Factory function & exports
│   ├── base.py                        # BaseModel interface & data classes
│   ├── hf_models.py                   # HuggingFace model adapter
│   ├── openai_models.py               # OpenAI API adapter
│   └── ollama_models.py               # Ollama local adapter
│
├── data_generation/                    # Core generation logic
│   ├── __init__.py
│   ├── generators.py                  # Main DataGenerator class
│   ├── schemas.py                     # Schema definitions & types
│   ├── validators.py                  # Validation & cleaning logic
│   └── utils.py                       # JSON extraction & file utilities
│
├── prompts/                           # Prompt templates
│   ├── base_prompts.md                # Base prompt instructions
│   ├── variation_strategies.md         # Prompt variation strategies
│   └── domain_templates/               # Domain-specific templates
│       ├── generic.md
│       ├── business.md
│       └── synthetic_records.md
│
├── ui/                                # Gradio web interface
│   └── app.py                         # Main UI application
│
├── experiments/                       # Jupyter notebooks
│   ├── model_comparison.ipynb         # Compare model outputs
│   └── prompt_diversity.ipynb         # Explore prompt strategies
│
└── outputs/                           # Generated datasets (not in git)
    └── generated_samples/             # JSON output files
```

---

## 🔐 Environment Variables (.env)

**Location:** `challenge/.env` (not committed to git)

**Required Variables:**

```bash
# HuggingFace Token (for gated models like Llama, Gemma)
# Get from: https://huggingface.co/settings/tokens
# Must have WRITE permissions
HF_TOKEN=hf_your_token_here

# OpenAI API Key (for OpenAI models)
# Get from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your_key_here
```

**Usage:**
- Loaded automatically by `ui/app.py` using `python-dotenv`
- Checked at startup to determine which models are available
- Models requiring auth are marked with `[🔒 Auth Required]` in UI

---

## 🚫 Git Ignore Rules (.gitignore)

**What's Ignored:**

1. **Generated Outputs:**
   - `outputs/generated_samples/*.json`
   - `outputs/generated_samples/*.jsonl`

2. **Python Cache:**
   - `__pycache__/`
   - `*.pyc`, `*.pyo`, `*.pyd`

3. **Gradio Cache:**
   - `.gradio/`

4. **Jupyter Checkpoints:**
   - `.ipynb_checkpoints/`

5. **Environment Files:**
   - `.env`
   - `.env.local`

6. **Model Files (if downloaded locally):**
   - `*.safetensors`
   - `*.bin`
   - `*.pt`
   - `*.pth`

7. **OS Files:**
   - `.DS_Store` (macOS)
   - `Thumbs.db` (Windows)

8. **Personal Reference Guides:**
   - `HUGGINGFACE_CACHE_GUIDE.md` (personal documentation)

**Note:** Model cache is stored in `~/.cache/huggingface/` (system cache, not in project)

---

## 📦 Dependencies (requirements.txt)

### Core Dependencies
- `torch>=2.0.0` - PyTorch for HuggingFace models
- `transformers>=4.35.0` - HuggingFace transformers library
- `huggingface-hub>=0.19.0` - HF model hub access
- `openai>=1.0.0` - OpenAI API client
- `gradio>=4.0.0` - Web UI framework
- `requests>=2.31.0` - HTTP requests (for Ollama)
- `python-dotenv>=1.0.0` - Environment variable loading

### Optional Dependencies
- `bitsandbytes>=0.41.0` - 4-bit quantization for HF models
- `accelerate>=0.25.0` - Model loading acceleration
- `jupyter>=1.0.0` - Jupyter notebooks
- `ipykernel>=6.25.0` - Jupyter kernel

---

## 📄 File-by-File Documentation

### Core Documentation

#### `README.md`
**Purpose:** Main project documentation

**Contents:**
- Challenge objective and design principles
- Non-goals and known limitations
- Quick start guide
- Authentication setup
- Supported models and schemas
- Architecture overview
- Usage examples
- Key features (including auto-update token estimation)

**Key Sections:**
- 🎯 Challenge Objective
- 🧠 Why This Matters
- 🧱 Design Principles
- 🚫 Non-Goals
- 🔐 Authentication Setup
- 🚀 Quick Start
- ✨ Key Features
- 📊 Supported Schemas
- 🏗️ Architecture
- 💡 Usage Examples

---

#### `TESTING_GUIDE.md`
**Purpose:** Comprehensive testing checklist

**Contents:**
- Pre-testing checklist (environment, dependencies, auth)
- 10 test categories:
  1. Model Provider Tests (HF, OpenAI, Ollama)
  2. Schema Generation Tests
  3. Prompt Strategy Tests
  4. Validation Tests
  5. Utility Function Tests
  6. Error Handling Tests
  7. UI Tests (Manual)
  8. Integration Tests
  9. Memory Management Tests
  10. Edge Cases
- Common issues and troubleshooting
- Pre-commit checklist

**Structure:**
- Each test includes: Objective, Steps, Expected Results, Code Examples
- Tests are organized by component
- Includes both automated and manual tests

---

#### `HUGGINGFACE_CACHE_GUIDE.md` (Not in Git)
**Purpose:** Personal reference for managing HuggingFace model cache

**Contents:**
- Where models are stored (cache location)
- How to see cached models (PowerShell commands)
- How to delete models
- How caching works
- Model size reference table
- Cache management tips
- Common issues and solutions
- Quick reference commands

---

#### `run_tests.py`
**Purpose:** Automated smoke tests for quick validation

**Functionality:**
- **Test 1:** Basic generation (HF model, customer records)
- **Test 2:** Schema validation
- **Test 3:** JSON extraction from text
- **Test 4:** Multiple schema types
- **Test 5:** Error handling (invalid provider)

**Usage:**
```bash
cd experiments/week_03/challenge
python run_tests.py
```

**Output:**
- Prints test results (✅ PASSED / ❌ FAILED)
- Returns exit code 0 on success, 1 on failure
- Provides next steps after completion

---

### Models Module (`models/`)

#### `models/base.py`
**Purpose:** Abstract base class and common data structures

**Key Components:**

1. **`GenerationConfig` (dataclass):**
   - `temperature: float = 0.7`
   - `max_tokens: int = 512`
   - `top_p: Optional[float] = None`
   - `seed: Optional[int] = None`
   - `stop_sequences: Optional[List[str]] = None`

2. **`ModelResponse` (dataclass):**
   - `text: str` - Generated text
   - `model_name: str` - Model identifier
   - `provider: str` - Provider name
   - `metadata: Optional[Dict[str, Any]]` - Additional info

3. **`BaseModel` (ABC):**
   - Abstract class defining common interface
   - Methods:
     - `generate(prompt, config) -> ModelResponse` (abstract)
     - `is_loaded() -> bool` (abstract)
   - All providers must implement this interface

**Design Pattern:** Adapter Pattern - allows swapping providers without changing generation logic

---

#### `models/__init__.py`
**Purpose:** Factory function and module exports

**Key Function:**
- `create_model(provider, model_name, **kwargs) -> BaseModel`
  - Factory function to instantiate models
  - Supports: "huggingface", "openai", "ollama"
  - Returns appropriate model adapter instance

**Exports:**
- All model classes
- Model dictionaries (HF_MODELS, OPENAI_MODELS, OLLAMA_MODELS)
- Helper functions

---

#### `models/hf_models.py`
**Purpose:** HuggingFace model adapter implementation

**Key Components:**

1. **`HF_MODELS` Dictionary:**
   - **Gated Models** (requires access + HF_TOKEN):
     - Llama 3.1: `Meta-Llama-3.1-8B-Instruct`, `Meta-Llama-3.1-70B-Instruct`
     - Llama 3.2: `Llama-3.2-1B-Instruct`, `Llama-3.2-3B-Instruct`
     - Llama 3.3: `Llama-3.3-8B-Instruct`
     - Llama 4: `Llama-4-Scout-17B-16E-Instruct`, `Llama-4-Maverick-17B-128E-Instruct`, `Llama-4-Maverick-17B-128E-Instruct-FP8`
     - Gemma 2: `gemma-2-2b-it`, `gemma-2-9b-it`, `gemma-2-27b-it`
   - **Open Models** (no auth required):
     - Microsoft: Phi-3-mini, Phi-3-medium, Phi-4-mini
     - Alibaba: Qwen 2.5 (0.5B, 1.5B, 3B, 7B)
     - Mistral: Mistral-7B-Instruct
     - TinyLlama: TinyLlama-1.1B-Chat
     - Zephyr: Zephyr-7B-beta
     - And more...

2. **`HuggingFaceModel` Class:**
   - Implements `BaseModel` interface
   - **Features:**
     - Lazy loading (model loaded on first `generate()` call)
     - Optional 4-bit quantization (reduces memory)
     - Chat template application (for instruct models)
     - Token passing for gated models
     - Memory management (`unload()` method)
   - **Methods:**
     - `generate(prompt, config) -> ModelResponse`
     - `is_loaded() -> bool`
     - `unload()` - Free model from memory
     - `_load_model()` - Internal lazy loading
     - `_get_quantization_config()` - Create quantization config

**Authentication:**
- Reads `HF_TOKEN` from environment or constructor
- Passes token to `from_pretrained()` calls for gated models
- Uses `huggingface_hub.login()` for authentication

---

#### `models/openai_models.py`
**Purpose:** OpenAI API adapter implementation

**Key Components:**

1. **`OPENAI_MODELS` Dictionary:**
   - `gpt-4o` - Latest GPT-4 optimized
   - `gpt-4o-mini` - Smaller, faster, cheaper
   - `gpt-4-turbo` - GPT-4 Turbo
   - `gpt-4` - Standard GPT-4
   - `gpt-3.5-turbo` - Legacy GPT-3.5

2. **`OpenAIModel` Class:**
   - Implements `BaseModel` interface
   - Uses `openai.OpenAI` client
   - Maps `GenerationConfig` to OpenAI API parameters
   - Handles API errors gracefully

**Authentication:**
- Reads `OPENAI_API_KEY` from environment or constructor
- Uses OpenAI API (no local caching)

---

#### `models/ollama_models.py`
**Purpose:** Ollama local model adapter

**Key Components:**

1. **`OLLAMA_MODELS` Dictionary:**
   - `llama3.2:3b`, `llama3.2`
   - `llama3.1:8b`
   - `mistral`, `mistral:7b`
   - `phi3`
   - `qwen2.5:7b`
   - `gemma2:2b`
   - `tinyllama`

2. **`OllamaModel` Class:**
   - Implements `BaseModel` interface
   - Uses `requests` to call local Ollama API
   - Default endpoint: `http://localhost:11434/api/generate`
   - Maps `GenerationConfig` to Ollama API parameters
   - Handles connection errors

**Requirements:**
- Ollama must be running: `ollama serve`
- Models must be pulled: `ollama pull llama3.2:3b`

---

### Data Generation Module (`data_generation/`)

#### `data_generation/schemas.py`
**Purpose:** Define output schemas and data structures

**Key Components:**

1. **`SchemaType` Enum:**
   - `CUSTOMER_RECORD`
   - `INCIDENT_REPORT`
   - `MEETING_SUMMARY`
   - `BUSINESS_EVENT`
   - `PRODUCT_REVIEW`
   - `EMPLOYEE_RECORD`
   - `GENERIC_JSON`

2. **Schema Dataclasses:**
   - `CustomerRecord` - 10 fields (id, name, email, age, city, country, signup_date, total_purchases, preferred_category, is_active)
   - `IncidentReport` - 8 fields (id, title, description, severity, status, reported_by, reported_date, assigned_to, resolution)
   - `MeetingSummary` - 7 fields (id, title, date, attendees[], duration_minutes, key_points[], action_items[], decisions[])
   - `BusinessEvent` - 6 fields (id, event_type, timestamp, customer_id, amount, currency, metadata{})
   - `ProductReview` - 9 fields (id, product_id, product_name, reviewer_name, rating, review_text, verified_purchase, helpful_count, review_date)
   - `EmployeeRecord` - 8 fields (id, name, email, department, role, hire_date, salary, is_active)

3. **`SCHEMAS` Dictionary:**
   - Maps `SchemaType` to dataclass

4. **Helper Functions:**
   - `schema_to_dict(schema_type) -> Dict` - Convert schema to dict for prompts
   - `get_schema_fields(schema_type) -> List[str]` - Get field names

---

#### `data_generation/generators.py`
**Purpose:** Core generation orchestration logic

**Key Class: `DataGenerator`**

**Main Method: `generate_dataset()`**
- **Inputs:**
  - `schema_type: SchemaType`
  - `num_records: int = 5`
  - `prompt_template: Optional[str] = None`
  - `variation_strategy: Optional[str] = None`
  - `config: Optional[GenerationConfig] = None`
  - `output_file: Optional[str] = None`
- **Process:**
  1. Build prompt (`_build_prompt()`)
  2. Call model (`model.generate()`)
  3. Parse output (`_parse_output()`)
  4. Filter schema definitions (`_filter_schema_definitions()`)
  5. Clean records (`clean_record()`)
  6. Validate dataset (`validate_dataset()`)
  7. Save to file (if requested)
- **Returns:**
  - Dict with: `records`, `cleaned_records`, `raw_output`, `metadata`

**Helper Methods:**
- `_build_prompt()` - Construct prompt from template + schema + variation
- `_apply_variation()` - Apply variation strategy (formal, casual, detailed, etc.)
- `_parse_output()` - Extract JSON from model output
- `_filter_schema_definitions()` - Remove schema definitions and placeholder values

**Key Features:**
- Schema definition filtering (removes objects with type/required/description keys)
- Placeholder filtering (removes records with `<Field Name>` values)
- Graceful error handling
- Returns structured error responses

---

#### `data_generation/validators.py`
**Purpose:** Lightweight validation and cleaning

**Key Functions:**

1. **`validate_record(record, schema_type) -> (bool, Optional[str])`**
   - Checks if record has all required fields
   - Returns `(is_valid, error_message)`

2. **`validate_dataset(records, schema_type, min_records=1) -> (bool, Optional[str])`**
   - Validates entire dataset
   - Checks minimum record count
   - Returns `(is_valid, error_message)`

3. **`clean_record(record, schema_type) -> Dict`**
   - Removes extra fields (keeps only schema fields)
   - Fixes type issues (string to int/float/bool)
   - Returns cleaned record

**Validation Approach:**
- Lightweight: Structure only, not semantic correctness
- Best-effort type conversion
- Focuses on required fields presence

---

#### `data_generation/utils.py`
**Purpose:** Utility functions for parsing and file operations

**Key Functions:**

1. **`extract_json_from_text(text) -> Optional[Dict]`**
   - Extracts single JSON object from text
   - Handles markdown code blocks (```json)
   - Handles plain JSON
   - Returns None if no valid JSON found

2. **`extract_json_array_from_text(text) -> Optional[List[Dict]]`**
   - Extracts JSON array from text
   - Handles markdown code blocks
   - Handles plain JSON arrays
   - Returns None if no valid JSON found

3. **`format_dataset_for_display(records, max_records=10) -> str`**
   - Formats records for UI display
   - Shows first N records
   - Human-readable format

4. **`save_dataset(records, filepath, format="json") -> None`**
   - Saves dataset to file
   - Supports JSON and JSONL formats
   - Creates directory if needed

---

### Prompts Module (`prompts/`)

#### `prompts/base_prompts.md`
**Purpose:** Foundational prompt instructions

**Contents:**
- Prompt structure guidelines
- Default template
- Custom templates for specific schemas
- Usage notes

**Template Placeholders:**
- `{schema}` - Schema definition
- `{num_records}` - Number of records
- `{schema_type}` - Schema type name

---

#### `prompts/variation_strategies.md`
**Purpose:** Define prompt variation strategies

**Strategies:**
- **default**: Standard prompt
- **formal**: Professional, business tone
- **casual**: Conversational, relaxed tone
- **detailed**: Extra context and information
- **concise**: Brief, minimal information
- **diverse**: Maximum variety in values

**Usage:** Applied to base prompt to modify tone/style

---

#### `prompts/domain_templates/`
**Purpose:** Domain-specific prompt templates

**Files:**
- `generic.md` - Generic templates
- `business.md` - Business-focused templates
- `synthetic_records.md` - Templates emphasizing realism

---

### UI Module (`ui/`)

#### `ui/app.py`
**Purpose:** Gradio web interface

**Key Components:**

1. **Environment Setup:**
   - Loads `.env` file using `python-dotenv`
   - Reads `HF_TOKEN` and `OPENAI_API_KEY`
   - Checks authentication status

2. **Model Management:**
   - `get_available_models()` - Filters models based on auth
   - Marks models requiring auth with `[🔒 Auth Required]`
   - Updates model dropdown based on provider

3. **Smart Token Estimation:**
   - `estimate_max_tokens(num_records, schema_type) -> int`
   - Calculates recommended tokens based on:
     - Number of records
     - Schema complexity (tokens per record)
   - Auto-updates when `num_records` or `schema_type` changes

4. **UI Components:**
   - Provider selection (radio buttons)
   - Model dropdown (updates based on provider)
   - Schema type dropdown
   - Number of records slider (1-50)
   - Variation strategy dropdown
   - Temperature slider (0.0-2.0)
   - Max tokens slider (100-4000, auto-updates)
   - Quantization checkbox (HF only)
   - Generate button
   - Output display (text + JSON + file download)

5. **Main Function: `generate_data()`**
   - Orchestrates model creation
   - Calls `DataGenerator.generate_dataset()`
   - Formats output for display
   - Saves to file
   - Returns (display_text, json_output, file_path)

6. **Change Handlers:**
   - `provider.change()` - Updates model list
   - `num_records.change()` - Auto-updates max_tokens
   - `schema_type.change()` - Auto-updates max_tokens

**Features:**
- Authentication status display
- Error messages with helpful hints
- File download
- Real-time token estimation

---

### Experiments (`experiments/`)

#### `experiments/model_comparison.ipynb`
**Purpose:** Compare outputs from different models

**Usage:**
- Test same prompt with different models
- Compare output quality
- Analyze differences

---

#### `experiments/prompt_diversity.ipynb`
**Purpose:** Explore how prompt strategies affect output

**Usage:**
- Test different variation strategies
- Analyze output diversity
- Understand prompt impact

---

## 🔄 System Flow

### Generation Pipeline

1. **User Input (UI):**
   - Selects provider, model, schema, records, parameters

2. **Model Creation:**
   - `create_model()` factory creates appropriate adapter
   - Model loads (lazy loading for HF)

3. **Prompt Construction:**
   - `DataGenerator._build_prompt()`:
     - Gets schema definition
     - Applies variation strategy
     - Constructs final prompt

4. **Generation:**
   - `model.generate(prompt, config)`
   - Returns `ModelResponse` with text

5. **Parsing:**
   - `extract_json_array_from_text()` extracts JSON
   - Handles markdown, plain JSON, etc.

6. **Filtering:**
   - `_filter_schema_definitions()` removes:
     - Schema definitions (objects with type/required/description)
     - Placeholder values (strings like `<Field Name>`)

7. **Cleaning:**
   - `clean_record()` removes extra fields
   - Fixes type issues

8. **Validation:**
   - `validate_dataset()` checks structure
   - Ensures all required fields present

9. **Output:**
   - Formatted for display
   - Saved to JSON file
   - Returned to UI

---

## 🎯 Key Features

### 1. Smart Token Estimation
- **Function:** `estimate_max_tokens(num_records, schema_type)`
- **Logic:**
  - Base tokens per record varies by schema (150-400)
  - Multiplies by number of records
  - Adds 30% buffer for JSON formatting
  - Rounds to nearest 50
  - Clamps to 200-4000 range
- **Auto-updates:** When `num_records` or `schema_type` changes

### 2. Schema Filtering
- **Function:** `_filter_schema_definitions(records)`
- **Removes:**
  - Objects with nested dicts containing `type`, `required`, `description`
  - Records where 70%+ fields are placeholders (`<Field Name>`)
- **Purpose:** Ensures only actual data records in output

### 3. Authentication Management
- **Environment-based:** Uses `.env` file (not in UI)
- **Visual Indicators:** Models marked with `[🔒 Auth Required]`
- **Status Display:** Shows which credentials are configured
- **Error Messages:** Clear hints when auth is missing

### 4. Multi-Provider Support
- **Unified Interface:** All providers implement `BaseModel`
- **Easy Switching:** Change provider without code changes
- **Provider-Specific Features:**
  - HF: Quantization, lazy loading, token passing
  - OpenAI: API key, rate limiting handled
  - Ollama: Local inference, no auth needed

---

## 🧪 Testing

### Automated Tests (`run_tests.py`)

**5 Basic Tests:**
1. Basic generation (HF model)
2. Schema validation
3. JSON extraction
4. Multiple schema types
5. Error handling

**Run:**
```bash
python run_tests.py
```

### Comprehensive Tests (`TESTING_GUIDE.md`)

**10 Test Categories:**
1. Model Provider Tests
2. Schema Generation Tests
3. Prompt Strategy Tests
4. Validation Tests
5. Utility Function Tests
6. Error Handling Tests
7. UI Tests (Manual)
8. Integration Tests
9. Memory Management Tests
10. Edge Cases

**Each test includes:**
- Objective
- Steps
- Expected results
- Code examples

---

## 📊 Supported Models

### HuggingFace (29 models)
- **Gated (12):** Llama 3.1 (2), Llama 3.2 (2), Llama 3.3 (1), Llama 4 (3), Gemma 2 (3)
- **Open (17):** Qwen (5), Phi (3), Mistral (2), TinyLlama (1), Zephyr (2), DeepSeek (2), Falcon (1), OpenELM (1)

### OpenAI (5 models)
- `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo`

### Ollama (9 models)
- `llama3.2:3b`, `llama3.2`, `llama3.1:8b`, `mistral`, `mistral:7b`, `phi3`, `qwen2.5:7b`, `gemma2:2b`, `tinyllama`

---

## 📋 Supported Schemas

1. **customer_record** (~150 tokens/record)
2. **incident_report** (~200 tokens/record)
3. **meeting_summary** (~400 tokens/record)
4. **business_event** (~250 tokens/record)
5. **product_review** (~200 tokens/record)
6. **employee_record** (~180 tokens/record)
7. **generic_json** (~300 tokens/record)

---

## 🎨 Prompt Strategies

- **default** - Standard prompt
- **formal** - Professional tone
- **casual** - Conversational tone
- **detailed** - Extra context
- **concise** - Brief information
- **diverse** - Maximum variety

---

## 🔧 Configuration

### Generation Parameters

- **Temperature:** 0.0-2.0 (default: 0.7)
  - Lower = more deterministic
  - Higher = more creative

- **Max Tokens:** 100-4000 (auto-calculated)
  - Based on records × schema complexity
  - Can be adjusted manually

- **Quantization:** Boolean (HF only, default: True)
  - Reduces memory usage
  - May slightly affect quality

---

## 🚀 Quick Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
# Add HF_TOKEN and OPENAI_API_KEY
```

### Run Tests
```bash
python run_tests.py
```

### Launch UI
```bash
python ui/app.py
# Opens at http://localhost:7860
```

### Check HF Cache
```powershell
# List models
Get-ChildItem "$env:USERPROFILE\.cache\huggingface\hub" -Directory | Where-Object { $_.Name -like "models--*" }

# Check size
Get-ChildItem "$env:USERPROFILE\.cache\huggingface\hub" -Recurse | Measure-Object -Property Length -Sum
```

---

## 📝 File Summary Table

| File | Purpose | Key Functionality |
|------|---------|-------------------|
| `README.md` | Main docs | Project overview, setup, usage |
| `TESTING_GUIDE.md` | Testing docs | Comprehensive test checklist |
| `HUGGINGFACE_CACHE_GUIDE.md` | Personal ref | HF cache management |
| `SYSTEM_OVERVIEW.md` | This file | Complete system documentation |
| `requirements.txt` | Dependencies | Python package list |
| `.gitignore` | Git rules | What to ignore |
| `.env` | Secrets | API keys (not in git) |
| `run_tests.py` | Test script | Automated smoke tests |
| `models/base.py` | Base interface | Abstract BaseModel class |
| `models/__init__.py` | Factory | `create_model()` function |
| `models/hf_models.py` | HF adapter | HuggingFace model support |
| `models/openai_models.py` | OpenAI adapter | OpenAI API support |
| `models/ollama_models.py` | Ollama adapter | Local Ollama support |
| `data_generation/generators.py` | Core logic | DataGenerator class |
| `data_generation/schemas.py` | Schema defs | Schema types and structures |
| `data_generation/validators.py` | Validation | Record validation & cleaning |
| `data_generation/utils.py` | Utilities | JSON extraction, file ops |
| `ui/app.py` | Web UI | Gradio interface |
| `prompts/base_prompts.md` | Base prompts | Prompt templates |
| `prompts/variation_strategies.md` | Variations | Prompt strategies |
| `experiments/*.ipynb` | Notebooks | Exploration notebooks |

---

## 🎯 System Capabilities

✅ **Multi-Provider:** HF, OpenAI, Ollama  
✅ **Smart Defaults:** Auto token estimation  
✅ **Schema Filtering:** Removes definitions & placeholders  
✅ **Authentication:** Environment-based, visual indicators  
✅ **Validation:** Lightweight structure checks  
✅ **Error Handling:** Graceful failures  
✅ **Export:** JSON file generation  
✅ **UI:** User-friendly Gradio interface  
✅ **Testing:** Automated + comprehensive guides  

---

*Last updated: 2025-01-11*
