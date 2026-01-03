# AI Knowledge Assistant (Weeks 1–2 Capstone)

A configurable, prompt-orchestrated assistant for technical teams. It ingests code, errors, documents, URLs, and optionally voice, then responds with structured, explainable answers. This is not “just a chatbot”; it demonstrates clear software boundaries, prompt design, tool usage, and model abstraction.

## Goals
- Show you can design **LLM-powered systems**, not just call APIs.
- Keep responsibilities explicit: input normalization → intent → prompt profile → optional tools → streamed response → persistence.
- Prefer clarity, debuggability, and UX over novelty.

## Core Use Cases (all implemented, staged over 2 days)
1) **Explain & diagnose errors**  
   - Python tracebacks, stack traces, logs.
2) **Review and improve code**  
   - Pasted snippets or uploaded files; quick vs deep review modes.
3) **Summarize & reason over technical documents**  
   - Markdown/TXT or scraped URLs; “What does this mean for me?”
4) **Voice-based technical questions** (optional but planned)  
   - “Explain this error I’m seeing”, “Review this snippet”.

## Prompt Strategy Comparator (defining feature)
Three prompt profiles to compare “thinking styles” on the same input:
- **Concise Expert**: minimal explanation, root cause + fix, senior tone.
- **Teaching Mode**: step-by-step, explains “why”, highlights patterns.
- **Reviewer Mode**: critical, flags risks, suggests alternatives.

You compare quality, latency, and token usage across profiles and models.

## Architecture (prompt-orchestrated)
```
Input (text/code/file/URL/audio)
    ↓
Input normalization (loader)
    ↓
Intent detection (lightweight rules)
    ↓
Prompt selection (profile + task)
    ↓
Optional tool execution (registry)
    ↓
LLM response (streamed)
    ↓
Post-processing (formatting, audio, persistence)
```
The LLM does not choose architecture; code does.

## Folder Structure
```
experiments/week_02/mini_projects/
ai_knowledge_assistant/
├── README.md                # This document
├── app.py                   # Gradio entrypoint (driver)
├── core/
│   ├── orchestrator.py      # Input → prompt → tools → response
│   ├── prompt_profiles.py   # System + task profiles (YAML-backed)
│   ├── model_registry.py    # Multi-model abstraction (config-driven, all providers)
│   ├── session_store.py     # SQLite persistence (sessions, history)
│   └── auth.py              # Simple username/password authentication
├── tools/
│   ├── explain_error.py     # Traceback/log parsing
│   ├── review_code.py       # Quick/deep review modes
│   └── summarize_text.py    # Docs/URL summarization
├── io/
│   ├── audio.py             # Whisper STT + TTS wrappers
│   └── loaders.py           # Text/file/URL ingestion + cleaning
├── prompts/
│   ├── base.yaml            # Base system + shared snippets
│   └── profiles.yaml        # Concise/Teaching/Reviewer profiles
├── data/
│   └── sessions.db          # Created at runtime (gitignored)
└── experiments/
    └── prompt_comparison.ipynb # Side-by-side runs for profiles/models
```

## Implementation Plan (2-day cadence)
**Day 1**
- Core pipeline: input normalization → intent → prompt selection → streaming response.
- Model registry: GPT + Ollama, capability flag for tools.
- Prompt profiles: load from YAML; switch via UI dropdown.
- Tools: implement `explain_error`, `review_code` (quick/deep), `summarize_text`.
- Gradio UI: text/code/file/URL inputs, profile selector, model selector, streaming output.
- Persistence: session store skeleton (SQLite), hook later.

**Day 2**
- Wire persistence (SQLite): save/load sessions and transcripts.
- Add optional audio: Whisper STT for input, TTS for responses.
- Experiments notebook: prompt profile comparison (quality/latency/tokens).
- Polish UX: loading states, error surfacing, trimmed logs.

## Definition of Done
- Runs via `python app.py` and exposes Gradio Blocks UI.
- Supports the 4 core use cases (text/code/file/URL; audio optional but scaffolded).
- Prompt profiles selectable; differences visible in output and metadata.
- Tool registry routes to concrete functions with clear errors on failure.
- Streaming responses for all chat paths.
- SQLite session store created automatically; can replay a session.
- `prompts/*.yaml` externalized; easy to tweak without code changes.

## Setup
1) Python 3.10+ and `pip install -r requirements.txt` (reuse course env).
2) Environment: `.env` with `OPENAI_API_KEY`; Ollama optional (`ollama serve` + `ollama pull llama3.2`).
3) **Authentication (REQUIRED by default)**: Set `USER=your_username` and `PASSWORD=your_password` in `.env`.
   - **For development only**: Set `DISABLE_AUTH=true` to disable authentication.
   - **Security**: Auth is enabled by default (secure by default). App will not start without credentials unless explicitly disabled.
4) **Additional Models**: Add API keys for DeepSeek, Anthropic, Gemini, Groq, Together AI, Mistral in `.env` (see `core/models.yaml` for required keys).
5) Run: `python app.py` (from repo root or project folder).

## Non-Goals (intentionally out of scope for Weeks 1–2)
- Multi-user auth, user accounts, teams/roles (simple username/password implemented).
- Vector DBs / RAG / embeddings.
- LangGraph or multi-agent orchestration.
- Production hosting concerns (TLS, scaling, billing).

## Security & Production Features

### Authentication
- **Secure by Default**: Authentication is **REQUIRED** by default
- **Simple Auth**: Username/password from environment variables
- **Security**: Constant-time comparison prevents timing attacks
- **Development**: Set `DISABLE_AUTH=true` in `.env` to disable (development only)
- **Enforcement**: App will not start without credentials unless explicitly disabled

### Input Validation & Security
- **File Uploads**:
  - Path traversal protection (resolved paths, no directory traversal)
  - File size limits (10MB maximum)
  - Extension whitelist validation
  - Encoding error handling
- **URL Loading**:
  - URL format validation
  - SSRF protection (blocks localhost/private IPs)
  - Proper URL parsing and timeout handling (10s default)
- **Audio Input**:
  - Sample rate validation
  - Duration and amplitude checks
  - Empty audio detection

### Database Security
- **SQL Injection Protection**: All queries use parameterized statements
- **Connection Handling**: Proper error handling for database failures
- **Session Isolation**: Each session is properly isolated

### Error Handling & Resilience
- **Model Failures**: Automatic fallback to alternative models
- **API Errors**: Specific error types (invalid_key, rate_limited, connection_error, etc.)
- **Graceful Degradation**: App continues functioning even if components fail
- **User-Friendly Messages**: Clear, actionable error messages

### Model Registry
- **Multi-Provider Support**: GPT, Ollama, DeepSeek, Anthropic, Gemini, Groq, Together AI, Mistral
- **Startup Validation**: All models with API keys are validated at startup
- **Status Tracking**: Real-time status (ready, invalid_key, rate_limited, offline, etc.)
- **UI Integration**: Models shown with status indicators in dropdown

## Production Readiness

This project is **production-ready** for:
- Internal team tools
- Small to medium deployments
- Educational/learning environments
- Proof-of-concept demonstrations

### Current Security Measures
✅ SQL injection protection  
✅ Path traversal protection  
✅ SSRF protection  
✅ Input validation (files, URLs, audio)  
✅ Authentication (optional, simple)  
✅ Error handling and fallback mechanisms  
✅ Professional code quality (no emojis in code, clear comments)

### Recommended for Large-Scale Production
1. **Replace simple auth** with OAuth/JWT for multi-user scenarios
2. **Add rate limiting** per user/session
3. **Implement structured logging** (files/cloud)
4. **Add monitoring** (health checks, metrics)
5. **Database backups** for session data
6. **HTTPS/TLS** for all connections
7. **Environment-specific configs** (dev/staging/prod)

## Notes
- Keep comments professional and scarce; explain "why" when non-obvious.
- Measure token usage and latency where possible; surface in UI or logs.
- Favor small, composable functions; keep orchestration explicit.
- All Week 1-2 features implemented and tested.
- See `PRODUCTION_READINESS.md` for detailed audit information.

