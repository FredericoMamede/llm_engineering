# Week 1 Learning Notes

## Scraper Optimization

**Problem:** Original code parses HTML twice (inefficient, 2 HTTP requests)

**Solution:** Class-based approach with lazy evaluation
- Parse once in `__init__`, reuse `soup` object
- Use `@property` decorators for computed values
- Cache results with `_attribute = None` pattern

**Pattern:** When multiple functions need same expensive operation → extract to class with caching

**Key insight:** `@property` makes methods look like attributes (`scraper.content` vs `scraper.get_content()`), enables lazy evaluation

---

## JavaScript-Ready Scraping

**Problem:** `requests` only gets static HTML; fails on JavaScript-rendered sites

**Solution:** Playwright runs a real browser, executes JavaScript, extracts rendered HTML

**Tradeoff:** Browser overhead (slower, more resources) vs. compatibility (handles React/Vue/Angular)

**Pattern:** Use `requests` for static sites, Playwright for JS-heavy sites. Can implement fallback strategy.

---

## LLM Model Selection: Local vs Frontier

**Frontier Models (OpenAI, Claude, Gemini):**
- Best quality, reasoning, capabilities
- Cloud-based, paid API
- Data leaves your machine
- Low latency (fast inference)

**Local Models (Ollama):**
- Free, runs on your machine
- Data stays private
- Lower quality than frontier
- Variable latency (depends on hardware)

**OpenAI-Compatible Endpoints:**
- Standard format: Chat Completions API
- Works with OpenAI client library
- Ollama, Google Gemini, others support it
- Enables easy model switching

**Model Selection Strategy:**
- Use frontier for production, quality-critical tasks
- Use local for privacy, cost-sensitive, experimentation
- Can implement fallback (try local, fallback to frontier)

---

## LLM Model Types

**Base Models:**
- Untrained/foundation models
- Better for fine-tuning to learn new skills
- Starting point for custom applications

**Chat/Instruct Models:**
- Trained for conversation and instruction following
- Better for interactive use cases, creative content generation
- Most common for general applications

**Reasoning Models:**
- Enhanced with reasoning capabilities
- Better for problem-solving, complex logic, step-by-step thinking
- Examples: DeepSeek-R1, Claude Opus (reasoning mode)

**Hybrid Models:**
- Combine chat and reasoning capabilities
- Flexible for multiple use cases

**Selection Strategy:**
- Base: When you need to fine-tune for specific domain
- Chat: General applications, user interaction
- Reasoning: Complex problems, logic-heavy tasks

---

## Frontier Models: Strengths and Limitations

**OpenAI GPT:**
- Strengths: Strong coding, general capability, fast
- Limitations: Training cutoff, can make confident mistakes

**Anthropic Claude:**
- Strengths: Safety-focused, concise, humorous, practitioner-favored
- Limitations: Similar to GPT in specialized domains

**Google Gemini:**
- Strengths: Multimodal, strong reasoning
- Limitations: Variable performance across tasks

**x.ai Grok:**
- Strengths: Real-time data access, conversational
- Limitations: Newer, less proven

**DeepSeek:**
- Strengths: Strong reasoning, cost-effective
- Limitations: Less established ecosystem

**Common Limitations Across Frontier Models:**
- Not PhD-level in specialized domains (but improving)
- Limited knowledge beyond training cutoff
- Can confidently make mistakes
- Code may use legacy APIs/models
- Curious blindspots in reasoning

**Key Insight:** As models converge in capability, price and specific strengths become differentiators.

---

## Agentic AI Patterns

**Deep Research:**
- Multi-step research agent
- Synthesizes information from multiple sources
- Good for comprehensive analysis

**Claude Code:**
- Code-focused agent mode
- Iterative code generation and refinement
- Better than Stack Overflow for coding help

**Agent Mode:**
- Autonomous task completion
- Multi-step reasoning and execution
- Pattern: Plan → Execute → Verify → Iterate

**Outsmart Game:**
- LLM competition framework (edwarddonner.com)
- Compares models head-to-head on same tasks
- Useful for understanding relative strengths

---

## Transformers Architecture

**Core Innovation:** Attention mechanism allows models to focus on relevant parts of input

**Evolution:** LSTMs → Transformers
- LSTMs: Sequential processing, limited context
- Transformers: Parallel processing, long-range dependencies via attention
- Attention: Model learns which parts of input to focus on

**Why It Matters:**
- Enables processing entire sequences in parallel (faster training)
- Better at capturing long-range dependencies
- Foundation for all modern LLMs (GPT, Claude, Gemini)

---

## Parameters: Model Scale

**Parameter Count = Model Size:**
- Millions: Early models, limited capability
- Billions: Current standard (1B-70B range)
- Trillions: Frontier models (GPT-4 estimated 1T+)

**Examples:**
- LLaMA 3.2: 1B, 3B variants
- GPT-3: 175B parameters
- GPT-4: Estimated 1T+ parameters
- DeepSeek: Various sizes, cost-effective

**Tradeoffs:**
- More parameters = better capability, but slower inference, higher memory
- Diminishing returns: 3B → 70B shows improvement, but 70B → 1T may not be proportional
- Parameter count is one factor; architecture and training data matter too

---

## Tokens and Tokenization

**What Are Tokens:**
- Sub-word units (not characters, not words)
- GPT tokenizer breaks text into meaningful chunks
- Example: "banoffee" → ["ban", "offee"] (2 tokens)

**Why Tokens Matter:**
- API pricing based on tokens (input + output)
- Context windows measured in tokens
- Token count ≠ character count (varies by language, content)

**Tokenization with tiktoken:**
```python
import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4")
tokens = encoding.encode("text here")
```

**Key Insight:** Tokenization is model-specific. Different models use different tokenizers.

---

## Stateless LLMs: The Illusion of Memory

**Critical Understanding:**
- Every LLM API call is completely stateless
- No built-in memory between calls
- "Memory" is an illusion created by passing full conversation history

**How It Works:**
```python
# First call - no context
messages = [
    {"role": "user", "content": "Hi! I'm Ed!"}
]

# Second call - must include previous conversation
messages = [
    {"role": "user", "content": "Hi! I'm Ed!"},
    {"role": "assistant", "content": "Hi Ed! How can I help?"},
    {"role": "user", "content": "What's my name?"}  # Now it knows
]
```

**Implications:**
- Must manage conversation history in application code
- Longer conversations = more tokens = higher cost
- Context window limits how much history can be included
- This is how ChatGPT works - full conversation passed every time

**Pattern:** As AI engineers, we implement conversation management (memory) in our applications.

---

## Context Windows and API Costs

**Context Window:**
- Maximum tokens a model can process in one call
- Includes both input (prompt) and output (response)
- Examples: GPT-4o-mini ~128K tokens, Claude Opus ~200K tokens

**API Cost Structure:**
- Charged per token (input + output)
- Input tokens: prompt, system message, conversation history
- Output tokens: model's response
- Longer conversations = more input tokens = higher cost

**Cost Management:**
- Truncate old conversation history when approaching limits
- Use summarization to compress history
- Consider local models for long conversations (no per-token cost)
- Monitor token usage in production

**Tradeoff:** More context = better responses but higher cost and latency.

---

## Concepts to Reuse Later

- Parse once, extract multiple times (BeautifulSoup pattern)
- `@property` + `None` check = lazy evaluation pattern
- `_name` = private cache, `name` = public property
- Class-based caching for expensive operations (network, parsing)
- Playwright for JavaScript-rendered content (when `requests` fails)
- OpenAI-compatible endpoints for model abstraction
- Model comparison pattern (local vs frontier, different sizes)
- Model type selection (base vs chat vs reasoning)
- Agentic AI patterns (research, code, autonomous agents)
- Stateless LLM pattern: manage conversation history in application
- Tokenization for cost estimation and context management
- Context window management strategies (truncation, summarization)
