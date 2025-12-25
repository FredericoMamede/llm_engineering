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

## Concepts to Reuse Later

- Parse once, extract multiple times (BeautifulSoup pattern)
- `@property` + `None` check = lazy evaluation pattern
- `_name` = private cache, `name` = public property
- Class-based caching for expensive operations (network, parsing)
- Playwright for JavaScript-rendered content (when `requests` fails)
- OpenAI-compatible endpoints for model abstraction
- Model comparison pattern (local vs frontier, different sizes)
