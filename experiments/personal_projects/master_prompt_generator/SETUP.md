# Setup Guide

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

**Option A: Using .env file (Recommended)**

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   # At minimum, you need ONE of these:
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   # OR
   OPENAI_API_KEY=sk-your-key-here
   # OR
   GOOGLE_API_KEY=your-key-here
   ```

3. The `.env` file is gitignored and won't be committed.

**Option B: Environment Variables (Alternative)**

Set environment variables directly:
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Linux/Mac
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Option C: Free Local Models (Ollama)**

No API keys needed:
1. Install Ollama: https://ollama.ai
2. Run: `ollama serve`
3. Pull a model: `ollama pull llama3.2:8b`
4. Use models like `llama-3.2-8b` in the UI

---

## Getting API Keys

### Anthropic (Claude) - Recommended
- **Why**: Best for prompt generation quality
- **Get key**: https://console.anthropic.com/settings/keys
- **Cost**: ~$3-15 per 1M input tokens

### OpenAI (GPT)
- **Why**: Excellent reasoning, JSON mode
- **Get key**: https://platform.openai.com/api-keys
- **Cost**: ~$5-15 per 1M input tokens

### Google (Gemini)
- **Why**: Cost-effective, fast
- **Get key**: https://makersuite.google.com/app/apikey
- **Cost**: ~$1.25-7 per 1M input tokens

---

## Verify Setup

### Test Command Line

```bash
python test_core_loop.py
```

This will:
- Generate a test prompt
- Evaluate it
- Show version history
- Display metadata

### Test UI

```bash
python ui/app.py
```

Opens Gradio interface in browser.

---

## Troubleshooting

### "No client available for model"

**Problem**: API key not set or invalid.

**Solution**:
1. Check `.env` file exists and has correct keys
2. Verify key format (no extra spaces, correct prefix)
3. Test key with provider's API directly

### "Connection refused" (Ollama)

**Problem**: Ollama not running.

**Solution**:
```bash
# Start Ollama
ollama serve

# In another terminal, verify it's running
curl http://localhost:11434/api/tags
```

### Import Errors

**Problem**: Dependencies not installed.

**Solution**:
```bash
pip install -r requirements.txt
```

---

## Minimum Requirements

**To run the system, you need**:
- ✅ Python 3.8+
- ✅ At least ONE API key (Anthropic, OpenAI, or Google)
- ✅ OR Ollama running locally

**Recommended**:
- Anthropic API key (best quality for prompt generation)
- OR OpenAI API key (good alternative)

---

## Next Steps

Once setup is complete:
1. Run `python ui/app.py` to start the UI
2. Or use `python test_core_loop.py` to test the core loop
3. See `README.md` for usage examples
