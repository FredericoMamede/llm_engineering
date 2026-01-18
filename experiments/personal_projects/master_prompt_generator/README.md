# Master Prompt Generator

> **The Ultimate Prompt Engineering Platform** - A lifelong, world-class tool for generating, evaluating, and refining prompts using AI-powered meta-prompting.

**Location**: `experiments/personal_projects/master_prompt_generator/`

> This is **not a course exercise** - it's an independent, production-ready prompt engineering platform designed for long-term use.

---

## 🎯 What This Project Does

This is a **comprehensive prompt generation system** that:

- ✅ Generates **production-ready prompts** for any use case using meta-prompting
- ✅ Supports **all prompt techniques** (zero-shot, few-shot, CoT, role-based, etc.)
- ✅ Covers **every category** (business, technical, creative, education, etc.)
- ✅ Evaluates **prompt quality** automatically (6 metrics, 0-10 scale)
- ✅ Refines prompts through **iterative improvement** with versioning
- ✅ Provides **model-specific adaptations** (optimized for Claude, GPT, Llama, etc.)
- ✅ Detects **anti-patterns** and suggests fixes
- ✅ Analyzes **token economics** and cost tradeoffs
- ✅ Enforces **lifecycle integrity** (cannot misuse the system)
- ✅ Provides **simple Gradio UI** for inspection and control

---

## 🚫 What This Project Is NOT

This project explicitly does **NOT** include:

- ❌ **RAG systems** - No retrieval-augmented generation
- ❌ **Agent frameworks** - No autonomous agents or multi-agent orchestration
- ❌ **Long-term memory** - No persistent memory systems
- ❌ **Workflow automation** - No background jobs or automated task execution
- ❌ **Fine-tuning replacement** - Not a substitute for model fine-tuning
- ❌ **AI that builds AI** - Focused on prompt engineering only
- ❌ **Dashboards or analytics** - UI is for inspection, not analytics

**Focus**: Prompt generation + evaluation + refinement only.

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up API keys
# 1. Copy the example file
cp .env.example .env

# 2. Edit .env and add your API keys
# At minimum, you need one of:
#   - ANTHROPIC_API_KEY (recommended for prompt generation)
#   - OPENAI_API_KEY
#   - GOOGLE_API_KEY
# Or use Ollama locally (no key needed)

# Run the app
python ui/app.py
```

**Note**: The `.env` file is gitignored. Create it from `.env.example` and add your actual API keys.

---

## 📋 Features

### Core Capabilities

1. **Intelligent Prompt Generation**
   - Meta-prompting using best-in-class LLMs
   - Context-aware generation
   - Automatic technique selection
   - **Model-specific adaptation** (optimized for Claude, GPT, Llama, etc.)

2. **Comprehensive Coverage**
   - 8+ prompt techniques
   - 50+ use case categories
   - 4 complexity tiers

3. **Quality Assurance**
   - Automatic evaluation (0-10 scale, 6 criteria)
   - **Anti-pattern detection** (12+ prompt smells)
   - Best practices checking
   - LLM-as-judge validation
   - **Regression detection** across versions

4. **Token Economics & Cost Analysis**
   - Token estimation (input/output)
   - Cost calculation per model
   - Efficiency scoring
   - Optimization suggestions
   - Cost-quality tradeoff analysis

5. **Prompt Lifecycle & Versioning**
   - Full lifecycle tracking (Draft → Generated → Evaluated → Refined → Approved → Archived)
   - Semantic versioning (MAJOR.MINOR.PATCH)
   - Parent-child relationships
   - Change tracking and regression detection

6. **User-Friendly Interface**
   - Simple Gradio UI
   - Real-time generation
   - Test interface
   - Export options
   - History and versioning

### Supported Prompt Types

- **Zero-Shot**: Direct instructions
- **Few-Shot**: With examples
- **Chain-of-Thought**: Step-by-step reasoning
- **Role/Persona**: Character definition
- **Structured Output**: JSON/XML formats
- **Prompt Chaining**: Multi-step workflows
- **Self-Consistency**: Multiple reasoning paths
- **Reflection**: Self-critique and improvement

### Use Case Categories

- **Business**: Emails, reports, meetings, analysis
- **Technical**: Code generation, explanation, review
- **Creative**: Writing, storytelling, content creation
- **Education**: Explanations, tutoring, study guides
- **Analysis**: Research, data analysis, summaries
- **Communication**: Translation, tone transformation
- **Problem Solving**: Decision making, troubleshooting
- **And many more...**

---

## 🏗️ Project Structure

```
master_prompt_generator/
├── README.md                    # This file
├── SETUP.md                     # Setup guide
├── requirements.txt             # Dependencies
├── .env.example                 # Environment variables template
│
├── core/                        # Core logic
│   ├── prompt_generator.py     # Generation engine
│   ├── prompt_evaluator.py     # Quality assessment
│   ├── prompt_refiner.py       # Iterative improvement
│   ├── approval_logic.py       # Approval gates
│   ├── orchestrator.py         # End-to-end coordination
│   ├── model_manager.py        # LLM client management
│   ├── lifecycle_guard.py     # Lifecycle enforcement
│   ├── version_guard.py        # Version integrity
│   ├── breaking_change_detector.py  # Breaking change detection
│   ├── prompt_smell_detector.py     # Anti-pattern detection
│   └── token_economics.py     # Cost analysis
│
├── ui/                          # User interface
│   └── app.py                  # Minimal inspection UI
│
├── tests/                       # Tests
│   ├── test_phase_c.py         # Phase C tests
│   └── test_core_loop.py       # Core loop test
│
├── config/                      # Configuration
│   └── model_prompt_profiles.yaml  # Model adaptations
│
└── docs/                        # Documentation
    ├── architecture/            # Design docs
    ├── phases/                  # Phase completion docs
    ├── status/                  # Status reports
    └── testing/                 # Testing documentation
```

---

## 🎨 UI Overview

The minimal inspection UI provides:

1. **Input Panel**: Use case, category, complexity, context, requirements, target model
2. **Generated Prompt**: Full prompt text display
3. **Metadata Display**: Version, lifecycle state, parent version, model adaptations
4. **Quality Metrics**: Overall score + 6-metric breakdown
5. **Anti-Patterns**: Detected issues with severity and fix suggestions
6. **Token Economics**: Cost, efficiency, tradeoff analysis
7. **Approval Status**: Current state with blockers (if any)
8. **Manual Controls**: Generate, Evaluate, Refine, Approve buttons

**Note**: This is an **inspection console**, not a dashboard. All operations are explicit and user-triggered.

---

## 🔧 Configuration

### Supported Models

The system supports a curated set of **free/open-source** and **paid/frontier** models.

#### 🆓 Free / Open-Source Models (No API Key Required)

These models run locally via Ollama (when installed and running):

**Llama (Meta)**
- `llama3.2:latest` - Latest Llama 3.2 (recommended)
- `llama3.1:8b` - Llama 3.1 8B
- `llama3.1:70b` - Llama 3.1 70B (requires significant resources)

**Note**: LLaMA-4 requires gated Hugging Face access (see Advanced/Gated Models section below).

**Mixtral (Mistral AI)**
- `mixtral:8x7b` - Mixtral 8x7B (strong reasoning)

**Note**: 8x22b not widely packaged.

**Mistral (Mistral AI)**
- `mistral:7b` - Mistral 7B

**Gemma (Google)**
- `gemma3:270m` - Gemma 3 270M (lightweight)
- `gemma2:9b` - Gemma 2 9B
- `gemma2:27b` - Gemma 2 27B

**Qwen (Alibaba)**
- `qwen2.5-coder` - Qwen 2.5 Coder (excellent for technical prompts)
- `qwen2.5:72b`, `qwen2.5:32b`, `qwen2.5:14b`, `qwen2.5:7b` - Various sizes

**DeepSeek**
- `deepseek-r1` - DeepSeek R1 (reasoning)
- `deepseek-coder-v2` - DeepSeek Coder v2 (reasoning + code)

**Note**: Free models require Ollama to be installed and running locally. See [Setup Guide](SETUP.md).

---

#### 💳 Paid / Frontier Models (API Key Required)

These models require API keys but provide best-in-class quality:

**Claude (Anthropic)** - Recommended for prompt generation
- `claude-opus` - Best reasoning + long-context
- `claude-sonnet` - Best overall quality (recommended)
- `claude-haiku` - Fast, cost-effective

**Note**: Anthropic uses stable family names (not version-specific IDs).

**Required**: `ANTHROPIC_API_KEY`

**GPT (OpenAI)**
- `gpt-5` - Latest GPT (officially released 2026)
- `gpt-4o` - Excellent reasoning + structured output
- `gpt-4o-mini` - Low-cost tier

**Note**: Deprecated models (gpt-4-turbo, gpt-4, gpt-3.5-turbo) removed.

**Required**: `OPENAI_API_KEY`

**Gemini (Google)**
- `gemini-2.5-pro` - Strong general reasoning
- `gemini-1.5-pro` - Alternative
- `gemini-1.5-flash` - Fast, cost-effective

**Note**: Gemini 3 is experimental/preview - not included.

**Required**: `GOOGLE_API_KEY`

---

### 🔐 Advanced / Gated Models

Some models require **gated access** (approval + credentials) and are marked as **advanced**:

**LLaMA-4 (Meta)** - Gated Hugging Face Access
- `meta-llama/Llama-4-Scout-17B-16E-Instruct`
- `meta-llama/Llama-4-Maverick-17B-128E-Instruct`

**Required**: 
- Hugging Face account with **gated model approval**
- `HUGGINGFACE_TOKEN` environment variable

**What "Gated" Means**:
- Model requires explicit approval from the provider
- Not available via local runtimes (e.g., Ollama)
- Not "generally available" - requires application/approval process
- Advanced users can enable explicitly with proper credentials

**Behavior**:
- Models appear in UI dropdown with 🔒 when token/approval missing
- Clear error message: "Requires gated Hugging Face access"
- No silent fallbacks or auto-selection
- Identical behavior to paid API models (GPT, Claude)

This is **intentional and transparent** - the system shows all supported models, including gated ones, so users understand what's possible with proper setup.

---

### Model Availability vs Capability

**Critical Distinction**:
- **Capability** = What models the system supports (defined in `model_prompt_profiles.yaml`)
- **Availability** = What models you can actually use (based on API keys, local runtime)

**Important**: Models may appear **disabled** (🔒) in the UI if:
- Required API keys are not configured
- Local runtime (Ollama) is not running
- Gated access credentials are missing (for Hugging Face gated models)

**Behavior**:
- All supported models appear in the UI dropdown
- Unavailable models are clearly marked with 🔒 and reason
- Attempting to use an unavailable model shows a clear error message
- No silent fallbacks or auto-selection

**Model Presence ≠ Model Usability**

This ensures **explicit, predictable behavior** - you always know what's available and why.

### Environment Variables

**Setup Steps**:

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys (at least one required):
   ```bash
   # Anthropic (RECOMMENDED for prompt generation)
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   
   # OpenAI (for GPT models)
   OPENAI_API_KEY=sk-your-key-here
   
   # Google (for Gemini models)
   GOOGLE_API_KEY=your-key-here
   
   # Hugging Face (for gated models like LLaMA-4)
   HUGGINGFACE_TOKEN=hf_your-token-here
   ```

3. **Getting API Keys**:
   - **Anthropic** (recommended): https://console.anthropic.com/settings/keys
   - **OpenAI**: https://platform.openai.com/api-keys
   - **Google**: https://makersuite.google.com/app/apikey
   - **Hugging Face** (for gated models): https://huggingface.co/settings/tokens
     - Requires gated model approval: https://huggingface.co/meta-llama/Llama-4-Scout-17B-16E-Instruct

4. **Free Option**: Use Ollama locally (no API key needed)
   - Install Ollama: https://ollama.ai
   - Run: `ollama serve`
   - Models like `llama3.2:latest` will work without keys

**Note**: The `.env` file is gitignored and will not be committed to version control.

---

## 📊 Quality Metrics

Prompts are evaluated on:

- **Clarity** (0-10): Instructions are unambiguous
- **Completeness** (0-10): All requirements addressed
- **Structure** (0-10): Well-organized and formatted
- **Best Practices** (0-10): Follows guidelines
- **Specificity** (0-10): Appropriate detail level
- **Reusability** (0-10): Can be adapted/parameterized

**Target**: Average score > 8.0/10

---

## 🧪 Testing

- Manual UI testing scenarios: `docs/testing/UI_TESTING_EXAMPLES.md`


```bash
# Run tests
pytest tests/

# Test specific component
pytest tests/test_prompt_generator.py

# Test UI
python ui/app.py
```

---

## 🛡️ Guarantees

This system provides **defensive correctness**:

- ✅ **Lifecycle Integrity**: Cannot approve without evaluation, cannot refine archived prompts
- ✅ **Version Integrity**: Versions are monotonic, parent relationships are valid, approved versions are immutable
- ✅ **Regression Protection**: Cannot approve prompts with regressions (hard block)
- ✅ **Breaking Change Detection**: Major version increments required for breaking changes
- ✅ **Explicit Failures**: All errors are clear and explainable, no silent failures

See [docs/architecture/](docs/architecture/) for detailed design.

---

## 📚 Documentation

- **[Setup Guide](SETUP.md)**: Complete setup instructions
- **[Architecture Docs](docs/architecture/)**: Design, lifecycle, integration guides
- **[Phase Documentation](docs/phases/)**: Implementation phases and checklists
- **[Status Reports](docs/status/)**: Project status and completion reports

---

## 🎯 Use Cases

### Example 1: Business Email
```
Use Case: Professional Email Writing
Category: Business
Tier: Intermediate
Context: "Write a follow-up email after a client meeting"
```

### Example 2: Code Explanation
```
Use Case: Code Explanation
Category: Technical
Tier: Advanced
Context: "Explain this Python function to a beginner"
```

### Example 3: Creative Writing
```
Use Case: Story Generation
Category: Creative
Tier: Expert
Context: "Generate a sci-fi short story prompt"
```

---

## ✅ Status

**Project Status**: ✅ **COMPLETE AND PRODUCTION-READY**

- ✅ Phase B: Core MVP Implementation
- ✅ Phase C: Lifecycle & Version Integrity
- ✅ Phase D: Minimal UI
- ✅ Phase E: Tests

See [docs/status/FINAL_STATUS.md](docs/status/FINAL_STATUS.md) for details.

---

## 🤝 Contributing

This is a learning project, but contributions are welcome:

1. Extract more prompts from repository
2. Add new prompt techniques
3. Improve evaluation metrics
4. Enhance UI/UX
5. Add more use case categories

---

## 📝 License

Educational project - use freely for learning and development.

---

## 🙏 Acknowledgments

- All prompt patterns learned from the repository
- Prompt engineering research and best practices
- LLM providers (OpenAI, Anthropic, Google, Meta, etc.)

---

**Build the best prompts. Build them with Master Prompt Generator.** 🚀
