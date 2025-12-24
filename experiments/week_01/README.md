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

---

## Notes

See `notes.md` for detailed insights and concepts to reuse later.

