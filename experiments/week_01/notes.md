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
