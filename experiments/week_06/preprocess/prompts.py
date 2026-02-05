"""
Day 2 — Deterministic prompt templates for LLM preprocessing.

Rewriting product text to a standard format. Does not leak price (label).
"""

# Single system prompt for description rewriting (course convention).
# Token usage: ~50–80 system + variable user (raw product text).
SYSTEM_PROMPT = """Create a concise description of a product. Respond only in this format. Do not include part numbers.
Title: Rewritten short precise title
Category: eg Electronics
Brand: Brand name
Description: 1 sentence description
Details: 1 sentence on features"""
