# Week 2 Experiments

**Learning Lab - Week 2 Concepts**

This directory contains experiments and explorations for Week 2 of the LLM Engineering course.

## Purpose

This is a **learning lab**, not a portfolio project. Experiments here are:
- Small, focused explorations
- Documentation of insights and tradeoffs
- Practice with Week 2 concepts
- Reusable patterns for future independent projects

## Structure

- `notebooks/` - Jupyter notebooks exploring specific concepts
- `mini_projects/` - Complete mini-projects demonstrating Week 2 patterns
- `datasets/` - Small example datasets for testing
- `configs/` - Configuration files (prompts, models)
- `scripts/` - Helper scripts for automation
- `results/` - Summary observations and findings
- `outputs/` - Generated artifacts (gitignored)

## Day 1: Frontier Model APIs

### What I'm Testing

#### 1. Multi-Provider API Setup (`notebooks/00_multi_provider_setup.ipynb`)
**What:** Connect to multiple LLM providers (OpenAI, Anthropic, Gemini, DeepSeek, Groq, Grok, Ollama) using unified interface

**Why:**
- Understand how to use OpenAI-compatible endpoints
- Learn abstraction patterns for model switching
- Compare different providers' APIs and capabilities
- Practice with native client libraries (Google, Anthropic)

**What I learned:**
- OpenAI client library can work with multiple providers via `base_url`
- OpenAI-compatible endpoints enable easy model switching
- Native libraries (Google `genai`, Anthropic `Anthropic`) offer provider-specific features
- Pattern: Unified interface for multiple providers reduces code complexity

#### 2. Model Comparison and Testing (`notebooks/05_model_comparison.ipynb`)
**What:** Test different models on same tasks (puzzles, reasoning, dilemmas)

**Why:**
- Understand model strengths and weaknesses
- Learn when to use which model
- Compare quality vs cost vs latency
- Test reasoning capabilities with `reasoning_effort` parameter

**What I learned:**
- GPT-5 models support `reasoning_effort` parameter (minimal, low, medium, high)
- Different models excel at different tasks (reasoning, creativity, safety)
- Cost varies significantly between providers
- Pattern: Test multiple models to find best fit for specific use case

#### 3. Local Models with Ollama (`notebooks/00_multi_provider_setup.ipynb`)
**What:** Run models locally using Ollama

**Why:**
- Understand local vs cloud tradeoffs
- Learn to use OpenAI client with local endpoints
- Practice with free, private model inference

**What I learned:**
- Ollama runs on `localhost:11434/v1` with OpenAI-compatible API
- Local models: free, private, but lower quality than frontier
- Can use same OpenAI client library for local and cloud models
- Pattern: Local for privacy/experimentation, cloud for production quality

#### 4. Abstraction Layers (`notebooks/00_multi_provider_setup.ipynb`)
**What:** Use LiteLLM, LangChain, and OpenRouter for unified model access

**Why:**
- Understand different abstraction approaches
- Learn lightweight vs heavyweight frameworks
- Compare ease of use and flexibility

**What I learned:**
- **LiteLLM:** Lightweight, simple API, cost tracking built-in
- **LangChain:** Heavyweight, more features, more complex
- **OpenRouter:** Unified interface, access to many models
- Pattern: Choose abstraction based on needs (simple → LiteLLM, complex → LangChain)

#### 5. Prompt Caching (`notebooks/04_prompt_caching.ipynb`)
**What:** Implement and measure cost savings from prompt caching

**Why:**
- Understand cost optimization techniques
- Learn provider-specific caching implementations
- Measure actual cost savings

**What I learned:**
- **OpenAI:** 4x cheaper for cached content (exact prefix matches required)
- **Anthropic:** 25% more to prime cache, 10x cheaper to reuse
- **Gemini:** Supports both implicit and explicit caching
- Pattern: Place static content at beginning, variable content at end
- Real example: Caching 52K tokens of Hamlet saved ~73% on second call

#### 6. Multi-Model Conversations (`notebooks/06_multi_model_conversations.ipynb`)
**What:** Create conversations between multiple chatbots with different personalities

**Why:**
- Understand conversation history management
- Learn message structure for multi-turn interactions
- Practice building agentic AI patterns
- Compare two approaches: structured vs simple

**What I learned:**
- **Two approaches:**
  - **Structured messages:** Complex but fine-grained control
  - **Simple list + narrative:** Easier! One list, append responses, reuse template
- Message structure: `[{"role": "system/user/assistant", "content": "..."}]`
- Each model needs full conversation history to maintain context
- System prompts define personality, user/assistant messages build history
- **Simple approach pattern:** Single conversation list, narrative-style user prompt, just append after each response
- Can create 2-way, 3-way, 4-way conversations with different personalities

## Day 2: Gradio UI Development

### What I'm Testing

#### 1. Gradio Basics (`notebooks/06_gradio_intro.ipynb`)
**What:** Build simple user interfaces for LLM applications using Gradio

**Why:**
- Create demos and prototypes quickly
- Build internal tools for power users
- Share LLM applications with others
- Learn streaming UI patterns

**What I learned:**
- **Simple interface creation:** `gr.Interface(fn=function, inputs=[...], outputs=[...])`
- **Component types:** Textbox, Dropdown, Markdown for different input/output needs
- **Streaming support:** Use generators with `yield` keyword for real-time updates
- **Sharing options:** `share=True` for public links, `inbrowser=True` for auto-open
- **Authentication:** Easy password protection with `auth=("user", "pass")`
- Pattern: Gradio is perfect for demos, prototypes, and MVPs

#### 2. Streaming with Generators (`notebooks/06_gradio_intro.ipynb`)
**What:** Implement real-time streaming responses in Gradio UI

**Why:**
- Better user experience (see responses as they generate)
- Understand Python generator pattern
- Learn how to stream LLM responses to UI

**What I learned:**
- **Generator pattern:** Function must `yield` values, not `return` once
- **Streaming structure:** `for chunk in stream: yield accumulated_response`
- **Gradio auto-detection:** Gradio automatically detects generator functions
- Pattern: Use `yield` for streaming, `return` for one-shot responses

#### 3. Multi-Model UI with Class-Based Design (`week1/day5.ipynb`)
**What:** Build brochure generator UI supporting multiple models (GPT, Ollama) with unified class

**Why:**
- Learn class-based architecture for multi-model support
- Understand model registry pattern
- Practice clean code organization

**What I learned:**
- **Class-based approach:** Encapsulate all model logic in one class
- **Model registry pattern:** Dictionary mapping model names to (client, model_name) tuples
- **Unified interface:** Single `stream_brochure` method works for all models
- **Automatic detection:** Check Ollama availability, only include if running
- **Benefits:** No code duplication, easy to extend, self-documenting
- Pattern: Class with model registry is cleaner than separate functions per model

#### 4. UI Component Types (`notebooks/06_gradio_intro.ipynb`)
**What:** Use different Gradio components for different needs

**Why:**
- Understand when to use which component
- Learn component configuration options
- Build professional-looking UIs

**What I learned:**
- **Textbox:** For text input/output, configurable with `lines`, `label`, `info`
- **Dropdown:** For model selection, predefined options
- **Markdown:** For rich text output (formatted responses)
- **Examples:** Pre-populate UI with example inputs
- Pattern: Choose component based on data type and user interaction needs

## Day 3: Conversational AI with Gradio ChatInterface

### What I'm Testing

#### 1. Gradio ChatInterface (`week2/day3.ipynb`)
**What:** Build conversational AI chatbots using Gradio's ChatInterface component

**Why:**
- ChatInterface is specifically designed for multi-turn conversations
- Learn how to manage conversation history in UI applications
- Understand system message patterns for behavior control
- Practice dynamic prompt modification based on user input

**What I learned:**
- **ChatInterface vs Interface:** `gr.ChatInterface(fn=chat, type="messages")` is purpose-built for conversations
- **Callback signature:** `chat(message, history)` - Gradio automatically manages history
- **History format:** Gradio provides history as list of `{"role": "...", "content": "..."}` dicts
- **Message structure:** Must convert Gradio history to API format: `[system] + history + [user_message]`
- Pattern: ChatInterface handles UI complexity, you just manage the conversation logic

#### 2. System Messages for Context and Behavior (`week2/day3.ipynb`)
**What:** Use system messages to control chatbot personality and behavior

**Why:**
- System messages set the tone and context for entire conversation
- Enable one-shot prompting (examples in system message)
- Control business logic and constraints
- Define role and personality without cluttering user messages

**What I learned:**
- **System message placement:** Always first in messages array: `[system] + history + [user]`
- **One-shot prompting:** Include examples in system message to guide behavior
- **Business context:** System messages perfect for business rules, product info, constraints
- **Dynamic modification:** Can modify system message based on user input (e.g., detect keywords)
- Pattern: System message = personality + context + examples, User/Assistant = conversation history

#### 3. Streaming in ChatInterface (`week2/day3.ipynb`)
**What:** Implement streaming responses in conversational interfaces

**Why:**
- Better UX in conversations (see responses as they generate)
- Same generator pattern works in ChatInterface
- Real-time feedback feels more natural in chat

**What I learned:**
- **Generator pattern:** Same as regular Interface - use `yield` not `return`
- **Streaming structure:** `for chunk in stream: yield accumulated_response`
- **ChatInterface compatibility:** Works seamlessly with generator functions
- Pattern: Streaming in ChatInterface uses same generator pattern as regular Interface

#### 4. Dynamic System Message Modification (`week2/day3.ipynb`)
**What:** Modify system message based on user input or conversation state

**Why:**
- Handle edge cases dynamically
- Add context when needed
- Adapt behavior based on user requests
- Maintain flexibility while keeping base system message

**What I learned:**
- **Keyword detection:** Check user message for keywords, append to system message if needed
- **Conditional logic:** `if 'keyword' in message.lower(): system_message += "..."` 
- **Base + extension:** Keep base system message, extend conditionally
- Pattern: Start with base system message, extend dynamically based on conversation needs

## Notebooks

1. `00_multi_provider_setup.ipynb` - Setting up multiple API providers
2. `01_prompt_variations.ipynb` - Testing different prompt structures
3. `02_reasoning_and_constraints.ipynb` - Chain-of-thought and constraint handling
4. `03_structured_outputs_json.ipynb` - JSON mode and structured outputs
5. `04_prompt_caching.ipynb` - Prompt caching cost optimization
6. `05_model_comparison.ipynb` - Comparing different models on same tasks
7. `06_multi_model_conversations.ipynb` - Multi-model conversation patterns
8. `06_gradio_intro.ipynb` - Building simple UIs with Gradio (Day 2)
9. `week2/day3.ipynb` - Conversational AI with ChatInterface (Day 3)

## Mini Projects

- `multi_provider_chat/` - CLI tool for chatting with multiple providers
  - Unified interface for OpenAI, Anthropic, Gemini, DeepSeek, Groq, Grok, Ollama
  - Model comparison mode
  - Cost tracking
  - Conversation history management

## Setup

1. Ensure `.env` file exists in project root with required API keys:
   ```
   OPENAI_API_KEY=xxxx
   ANTHROPIC_API_KEY=xxxx
   GOOGLE_API_KEY=xxxx
   DEEPSEEK_API_KEY=xxxx
   GROQ_API_KEY=xxxx
   GROK_API_KEY=xxxx
   OPENROUTER_API_KEY=xxxx
   ```

2. For local models, ensure Ollama is running:
   ```bash
   ollama serve
   ollama pull llama3.2
   ```

3. Install dependencies: `pip install -r requirements.txt` (if applicable)

4. Run notebooks individually or use `scripts/run_notebooks_smoke.py` for quick validation

## Notes

See `notes.md` for:
- Key learnings from each experiment
- Tradeoffs observed (cost, latency, accuracy)
- Ideas to extract for future projects
- Provider-specific patterns and best practices


