# Prompt Variation Strategies

Strategies for varying prompts to generate more diverse datasets.

## Purpose

Different variation strategies modify:
- **Tone**: Formal vs. casual
- **Style**: Detailed vs. concise
- **Focus**: Diversity, realism, edge cases
- **Complexity**: Simple vs. complex records

## Available Strategies

### 1. Formal
**Effect**: Professional, business-like tone
**Use case**: Corporate data, official records
**Example**: "Using a formal, professional tone: ..."

### 2. Casual
**Effect**: Conversational, relaxed tone
**Use case**: User-generated content, reviews
**Example**: "Using a casual, conversational tone: ..."

### 3. Detailed
**Effect**: Extra context and information
**Use case**: Rich datasets, comprehensive records
**Example**: "Include extra detail and context: ..."

### 4. Concise
**Effect**: Brief, minimal information
**Use case**: Quick generation, minimal data
**Example**: "Be concise and brief: ..."

### 5. Diverse
**Effect**: Maximum variety in values
**Use case**: Training data, testing edge cases
**Example**: "Ensure maximum diversity in values: ..."

## Implementation

Strategies are applied as prefixes to base prompts in `generators.py`.

This can be extended by:
- Adding new strategy keywords
- Combining multiple strategies
- Creating domain-specific variations

## Custom Strategies

To add a custom strategy, modify `_apply_variation()` in `generators.py`:

```python
elif strategy == "your_strategy":
    prompt = "Your custom prefix:\n\n" + prompt
```
