---
# Sample Run — LLM Engineering Playground

This document illustrates **example executions** of the LLM Engineering Playground.
It is intended to demonstrate **expected behavior and flow**, not exact outputs.

Actual results may vary depending on:
- model selection
- prompt configuration
- token limits
- streaming mode
- content length

**Note:** This document has been updated to reflect all improvements including file input, custom model names, JSON output, cost tracking, enhanced logging, progress indicators, and JSON mode for structured output.

---

## Example 1 — URL Input with Streaming and Token Tracking

### Command

```bash
python main.py \
  --url "https://example.com/article" \
  --model openai \
  --tone professional \
  --stream \
  --show-tokens
```

---

### Execution Flow

1. **Input validation**
   * URL provided and validated
   * Flags validated
   * Fail-fast checks passed

2. **Content retrieval**
   * Static HTML fetched via `requests`
   * Parsed with `BeautifulSoup`
   * (If JavaScript-rendered, Playwright fallback is used)
   * Content truncated to `MAX_CONTENT_LENGTH` for cost management

3. **Analysis step**
   * Content length detected
   * Primary topics identified
   * Tone inferred
   * Token usage tracked

4. **Transformation step**
   * Summary generated
   * Bullet points extracted
   * Content rewritten using a professional tone
   * Token usage and cost tracked

5. **Output**
   * Results streamed incrementally to the console
   * Output assembled efficiently using list-based buffering
   * Token usage and cost displayed (if `--show-tokens` enabled)

---

### Example Output (Simplified)

**Summary**

* The article discusses the impact of modern software practices on developer productivity and system reliability.

**Key Points**

* Clear abstractions reduce cognitive load.
* Early validation prevents downstream errors.
* Small, composable components improve maintainability.

**Rewritten (Professional Tone)**

> This article explores how disciplined software engineering practices contribute to more reliable systems and improved developer efficiency.

### Token Usage (if `--show-tokens` enabled)

```
============================================================
Token Usage:
============================================================
Analysis:
  Input:  1,234 tokens
  Output:  456 tokens
  Total:  1,690 tokens
  Cost:   $0.000234

Transform:
  Input:  1,890 tokens
  Output:  789 tokens
  Total:  2,679 tokens
  Cost:   $0.000567

------------------------------------------------------------
Grand Total:
  Input:  3,124 tokens
  Output:  1,245 tokens
  Total:  4,369 tokens
  Cost:   $0.000801
============================================================
```

---

## Example 2 — File Input with Custom Model

### Command

```bash
python main.py \
  --file document.txt \
  --model openai \
  --model-name gpt-4o \
  --tone technical \
  --no-stream \
  --show-analysis
```

---

### Execution Flow

1. **Input validation**
   * File path validated
   * File read with UTF-8 encoding
   * Minimum length requirements satisfied

2. **Analysis**
   * Key themes extracted
   * Technical tone inferred
   * Analysis displayed (if `--show-analysis` enabled)

3. **Transformation**
   * Summary generated
   * Bullet points extracted
   * Text rewritten in a technical tone
   * Custom model (`gpt-4o`) used instead of default

4. **Output**
   * Full response returned after completion
   * No incremental streaming

---

### Example Output (Simplified)

**Summary**

* LLMs are becoming common tools in real-world applications, requiring careful engineering practices for reliability and cost management.

**Key Points**

* Adoption is growing rapidly across industries.
* Engineering discipline is required for production reliability.
* Cost and latency must be managed carefully.
* Proper prompt engineering is essential.

**Rewritten (Technical Tone)**

> Large language models are increasingly deployed in production environments, necessitating robust engineering practices to ensure reliability, manage costs, and optimize latency while maintaining high-quality outputs.

---

## Example 3 — JSON Output Format

### Command

```bash
python main.py \
  --text "Your content here..." \
  --model openai \
  --format json \
  --output-file results.json
```

---

### Execution Flow

1. **Input validation**
   * Text input validated
   * JSON format specified

2. **Pipeline execution**
   * Standard analysis and transformation steps
   * Results collected in structured format

3. **Output**
   * Results formatted as JSON
   * Saved to `results.json`
   * Also displayed to console

---

### Example JSON Output

```json
{
  "analysis": {
    "content": "Analysis results here...",
    "tokens": {
      "input": 1234,
      "output": 456,
      "total": 1690,
      "cost": 0.000234
    }
  },
  "summary": "Generated summary...",
  "bullets": "Key bullet points...",
  "rewritten": "Rewritten content...",
  "tokens": {
    "analysis": {
      "input": 1234,
      "output": 456,
      "total": 1690,
      "cost": 0.000234
    },
    "transform": {
      "input": 1890,
      "output": 789,
      "total": 2679,
      "cost": 0.000567
    }
  }
}
```

---

## Example 4 — Progress Indicators with Non-Streaming

### Command

```bash
python main.py \
  --text "Your content here..." \
  --model openai \
  --tone professional \
  --no-stream \
  --show-tokens
```

---

### Execution Flow

1. **Input validation**
   * Text input validated

2. **Pipeline execution with progress**
   * Progress bar shows: `Analyzing content...` (1/2)
   * Progress bar shows: `Transforming content...` (2/2)
   * Progress bar shows: `Complete` when done

3. **Output**
   * Full response returned after completion
   * Progress indicators provide visual feedback
   * Token usage and costs displayed

---

### Example Output (Simplified)

```
Pipeline: 100%|████████████████| 2/2 [00:15<00:00,  7.5s/step]

**Summary**

* Content summary here...

**Key Points**

* Point 1
* Point 2
* Point 3

**Rewritten (Professional Tone)**

> Rewritten content in professional tone...
```

**Note:** Progress bars are automatically shown when using `--no-stream`. Use `--no-progress` to disable them.

---

## Example 5 — JSON Mode for Structured Output

### Command

```bash
python main.py \
  --text "Your content here..." \
  --model openai \
  --model-name gpt-4o-mini \
  --tone technical \
  --json-mode \
  --no-stream \
  --show-tokens
```

---

### Execution Flow

1. **Input validation**
   * Text input validated
   * JSON mode enabled (requires OpenAI and non-streaming)

2. **Analysis and transformation**
   * Standard pipeline steps
   * JSON mode ensures valid JSON response from LLM
   * More reliable parsing than markdown

3. **Output**
   * Structured JSON response parsed automatically
   * Fallback to markdown parsing if JSON fails

---

### Example Output (Simplified)

**Summary**

* Content summary here...

**Key Points**

* Point 1
* Point 2
* Point 3

**Rewritten (Technical Tone)**

> Rewritten content in technical tone...

**Note:** JSON mode guarantees valid JSON from the LLM, making parsing more reliable. It automatically disables streaming and only works with OpenAI models.

---

## Example 6 — Translation with Ollama

### Command

```bash
python main.py \
  --text "Your content here..." \
  --model ollama \
  --model-name llama3.1 \
  --tone casual \
  --translate nl \
  --show-tokens
```

---

### Execution Flow

1. **Input validation**
   * Text input validated

2. **Analysis and transformation**
   * Standard pipeline steps
   * Custom Ollama model used (`llama3.1`)

3. **Translation**
   * Rewritten content translated to Dutch (nl)
   * Additional LLM call for translation

4. **Output**
   * All results including translation
   * Token usage displayed (cost not available for Ollama)

---

### Example Output (Simplified)

**Summary**

* Content summary here...

**Key Points**

* Point 1
* Point 2
* Point 3

**Rewritten (Casual Tone)**

> Rewritten content in casual tone...

**Translated**

De herschreven inhoud in casual toon...

---

## Notes

### New Features (Post-Improvements)

* **File Input**: Use `--file` to process text files instead of pasting content
* **Custom Models**: Use `--model-name` to specify exact model (e.g., `gpt-4o`, `llama3.1`)
* **JSON Output**: Use `--format json` for machine-readable output
* **Cost Tracking**: Token usage includes cost estimates for OpenAI models (when `--show-tokens` enabled)
* **Enhanced Logging**: Set `LLM_PLAYGROUND_LOG_LEVEL=DEBUG` for detailed logs
* **Retry Logic**: Automatic retries with exponential backoff for transient errors
* **Progress Indicators**: Visual progress bars for pipeline steps (shown automatically with `--no-stream`, disable with `--no-progress`)
* **JSON Mode**: Use `--json-mode` for guaranteed valid JSON output from OpenAI (requires `--no-stream`)

### General Notes

* Token usage and latency are logged internally when available.
* Streaming can be toggled via the `--stream` / `--no-stream` flags.
* Output structure remains consistent across models, but phrasing may differ.
* Cost tracking is only available for OpenAI models (Ollama is free/local).
* This project prioritizes **clarity and correctness** over feature completeness.

### Environment Variables

You can configure behavior via environment variables:
- `LLM_PLAYGROUND_LOG_LEVEL` - Control logging verbosity (INFO, DEBUG, WARNING, ERROR)
- `MAX_CONTENT_LENGTH` - Adjust content limits (default: 2000)
- `MAX_RETRIES` - Configure retry attempts (default: 3)
- `RETRY_BASE_DELAY` - Base delay for exponential backoff (default: 1.0 seconds)

---

## Purpose of This File

This file exists to:

* Clarify expected behavior
* Demonstrate new features and improvements
* Serve as a reference during development
* Show practical usage examples

It is not a benchmark and does not represent final output quality.

---

## Quick Reference

### Input Methods
- `--text "content"` - Raw text input
- `--url "https://..."` - URL to scrape
- `--file path.txt` - Read from file

### Model Selection
- `--model openai` - Use OpenAI (requires API key)
- `--model ollama` - Use Ollama (local, requires Ollama running)
- `--model-name gpt-4o` - Specify custom model name

### Output Options
- `--format text` - Human-readable text (default)
- `--format json` - Machine-readable JSON
- `--output-file results.txt` - Save to file
- `--show-tokens` - Display token usage and costs
- `--show-analysis` - Display analysis results
- `--json-mode` - Use JSON mode for structured output (OpenAI only, requires `--no-stream`)
- `--no-progress` - Disable progress indicators

### Other Options
- `--tone professional|casual|technical|humorous` - Output tone
- `--stream` / `--no-stream` - Enable/disable streaming
- `--translate nl` - Translate to target language (e.g., nl=Dutch)
