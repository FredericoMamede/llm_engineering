# Week 1 Experiments

## What I'm Testing

### 1. Scraper Optimization (`prompt_variations.ipynb`)
**What:** Compare function-based vs. class-based scraper implementation

**Why:** 
- The original code parses HTML twice (inefficient)
- Want to understand when classes are better than functions
- Learn performance optimization patterns

**What I learned:**
- Class-based approach: parse once, access multiple times
- Lazy evaluation with `@property` decorators
- Tradeoff: more code complexity vs. better performance
- Pattern: extract expensive operations into reusable classes

### 2. JavaScript-Ready Scraping (`prompt_variations.ipynb`)
**What:** Implement Playwright scraper for JavaScript-rendered websites

**Why:**
- `requests` fails on modern JS-heavy sites (React, Vue, etc.)
- Need to handle dynamic content for LLM summarization
- Understand when to use browser automation vs. simple HTTP requests

**What I learned:**
- Playwright runs real browser, executes JS, extracts rendered HTML
- Tradeoff: browser overhead (slower, more resources) vs. compatibility
- Pattern: Use `requests` for static sites, Playwright for JS-heavy sites
- Can implement fallback strategy (try `requests` first, fallback to Playwright)

### 3. Model Comparison (`model_params_comparison.ipynb`)
**What:** Compare different LLM models (local vs frontier, different sizes)

**Why:**
- Understand tradeoffs between model types
- Learn when to use which model
- Compare quality vs cost vs privacy

**What I learned:**
- Frontier models (OpenAI): Better quality, paid, cloud-based
- Local models (Ollama): Free, private, lower quality
- OpenAI-compatible endpoints enable easy model switching
- Model size affects speed and quality (1B vs 3B vs larger)
- Can implement model selection strategy based on requirements

---

## Day 3: LLM Types and Frontier Models (Theory)

**No lab/exercise - theory and exploration focused**

**Topics covered:**
1. **LLM Types:** Base, Chat/Instruct, Reasoning models - understanding when to use each
2. **Frontier Models:** GPT, Claude, Gemini, Grok, DeepSeek - strengths and limitations
3. **Model Testing:** Web UI exploration, Deep Research tool, agent modes
4. **Agentic AI:** Deep Research, Claude Code, Agent Mode - practical applications
5. **Model Competition:** Outsmart game (edwarddonner.com) - comparing models head-to-head

**Key insights:**
- Base models: Better for fine-tuning, learning new skills
- Chat/Instruct: Better for interactive use, creative content
- Reasoning: Better for problem-solving, complex logic
- Frontier models converging in capability; price becoming differentiator
- Claude favored by practitioners (humor, safety, conciseness)
- All frontier models strong at synthesizing information and nuanced answers

---

## Day 4: Transformers, Tokens, and LLM Fundamentals (Theory + Code)

**Topics covered:**
1. **Transformers Architecture:** Foundation behind GPT and modern LLMs
2. **LSTMs to Transformers:** Evolution, attention mechanism, emergent intelligence
3. **Parameters:** Scale from millions to trillions (GPT, LLaMA, DeepSeek)
4. **Tokens:** What tokens are, how GPT tokenizes text
5. **Tokenization:** Practical tokenization with tiktoken library
6. **Stateless LLMs:** Understanding the "illusion of memory"
7. **Context Windows & Costs:** Token limits, API pricing, context management

**Key insights:**
- Transformers use attention mechanism (key innovation over LSTMs)
- Parameters scale determines capability (1B → 3B → 175B → 1T+)
- Tokens ≠ characters (e.g., "banoffee" = "ban" + "offee" = 2 tokens)
- Every LLM call is stateless; "memory" is passing full conversation history
- Context window limits affect what can be processed in one call
- API costs scale with tokens (input + output), longer conversations cost more

---

## Notes

See `notes.md` for detailed insights and concepts to reuse later.

