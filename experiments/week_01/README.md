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

---

## Notes

See `notes.md` for detailed insights and concepts to reuse later.

