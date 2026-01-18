# Master Prompt Generator

> **The Ultimate Prompt Engineering Platform** - A lifelong, world-class tool for generating, evaluating, and refining prompts using AI-powered meta-prompting.

**Location**: `experiments/personal_projects/master_prompt_generator/`

> This is **not a course exercise** - it's an independent, production-ready prompt engineering platform designed for long-term use.

---

## 🎯 What This Project Does

This is a **comprehensive prompt generation system** that:

- ✅ Analyzes **700+ prompts** from the repository to learn patterns
- ✅ Generates **production-ready prompts** for any use case
- ✅ Supports **all prompt techniques** (zero-shot, few-shot, CoT, role-based, etc.)
- ✅ Covers **every category** (business, technical, creative, education, etc.)
- ✅ Evaluates **prompt quality** automatically
- ✅ Refines prompts through **iterative improvement**
- ✅ Provides **simple Gradio UI** for complex prompt generation

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
├── PROJECT_DESIGN.md            # Comprehensive design document
├── requirements.txt             # Dependencies
├── .env.example                 # Environment variables template
│
├── core/                        # Core logic
│   ├── prompt_analyzer.py      # Repository prompt analysis
│   ├── prompt_generator.py     # Generation engine
│   ├── prompt_evaluator.py    # Quality assessment
│   ├── prompt_refiner.py       # Iterative improvement
│   └── model_manager.py        # LLM client management
│
├── ui/                          # User interface
│   ├── app.py                  # Main Gradio app
│   ├── components.py           # UI components
│   └── styles.css              # Custom styling
│
├── prompts/                     # Prompt templates
│   ├── meta_prompts/           # Prompts for generating prompts
│   ├── evaluation_prompts/     # Evaluation prompts
│   └── refinement_prompts/     # Refinement prompts
│
├── data/                        # Data and templates
│   ├── repo_prompts/           # Extracted repository prompts
│   ├── templates/             # Prompt templates
│   ├── examples/               # Example prompts
│   └── evaluation/             # Test cases
│
└── utils/                       # Utilities
    ├── prompt_parser.py        # Prompt parsing
    ├── pattern_matcher.py      # Pattern identification
    └── metrics.py             # Evaluation metrics
```

---

## 🎨 UI Preview

The interface includes:

1. **Use Case Selector**: Choose category and complexity
2. **Context Input**: Describe your task
3. **Advanced Options**: Select techniques and preferences
4. **Model Selection**: Choose LLM (free or paid)
5. **Generated Prompt**: View with quality score
6. **Test Interface**: Try prompt with sample input
7. **History**: Browse saved prompts

---

## 🔧 Configuration

### Model Selection

**Free Tier (Recommended for testing)**:
- Llama 3.2 8B (Ollama) - Fast, local, good quality

**Paid Tier (Recommended for production)**:
- Claude Sonnet 4.5 - Best overall quality
- GPT-4o - Excellent reasoning
- Gemini 2.5 Pro - Cost-effective

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
   ```

3. **Getting API Keys**:
   - **Anthropic** (recommended): https://console.anthropic.com/settings/keys
   - **OpenAI**: https://platform.openai.com/api-keys
   - **Google**: https://makersuite.google.com/app/apikey

4. **Free Option**: Use Ollama locally (no API key needed)
   - Install Ollama: https://ollama.ai
   - Run: `ollama serve`
   - Models like `llama-3.2-8b` will work without keys

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

```bash
# Run tests
pytest tests/

# Test specific component
pytest tests/test_prompt_generator.py

# Test UI
python ui/app.py
```

---

## 📚 Documentation

- **[PROJECT_DESIGN.md](PROJECT_DESIGN.md)**: Comprehensive design document
  - Repository prompt analysis
  - LLM selection rationale
  - System architecture
  - Implementation plan

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

## 🚧 Roadmap

- [x] Project design and architecture
- [ ] Phase 1: Foundation (prompt analyzer, basic UI)
- [ ] Phase 2: Core features (generation, evaluation)
- [ ] Phase 3: Enhancement (advanced UI, history)
- [ ] Phase 4: Polish (testing, documentation, deployment)

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
