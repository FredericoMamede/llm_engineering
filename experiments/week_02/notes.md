# Week 2 Learning Notes

## Overview

Bullet-point insights from Week 2 experiments. Focus on **why** things work, not just **what** works.

## Day 1: Frontier Model APIs

### Multi-Provider API Setup

**Problem:** Need to connect to multiple LLM providers with different APIs

**Solution:** Use OpenAI-compatible endpoints or abstraction layers

**Key Techniques:**
- OpenAI client with `base_url` parameter for compatible providers
- Native client libraries for provider-specific features
- Abstraction layers (LiteLLM, LangChain, OpenRouter) for unified interface

**Provider URLs:**
```python
anthropic_url = "https://api.anthropic.com/v1/"
gemini_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
deepseek_url = "https://api.deepseek.com"
groq_url = "https://api.groq.com/openai/v1"
grok_url = "https://api.x.ai/v1"
openrouter_url = "https://openrouter.ai/api/v1"
ollama_url = "http://localhost:11434/v1"
```

**Pattern:** 
- Use OpenAI client for OpenAI-compatible providers (Gemini, DeepSeek, Groq, Grok, Ollama)
- Use native libraries when you need provider-specific features
- Use abstraction layers when you want to switch models easily

**Tradeoff:**
- Unified interface (OpenAI client) = simpler code, but limited to common features
- Native libraries = full feature access, but more code complexity
- Abstraction layers = easiest switching, but another dependency

---

### Model Comparison and Testing

**Key Insights:**
- **GPT-5 models:** Support `reasoning_effort` parameter (minimal, low, medium, high)
  - Higher effort = better reasoning, but slower and more expensive
- **Model strengths vary:**
  - GPT: Strong coding, general capability, fast
  - Claude: Safety-focused, concise, humorous
  - Gemini: Multimodal, strong reasoning
  - DeepSeek: Strong reasoning, cost-effective
  - Groq: Fast inference, open-source models
  - Grok: Real-time data access, conversational

**Testing Strategy:**
- Test same task across multiple models
- Compare quality, cost, latency
- Use reasoning puzzles to test capabilities
- Game theory dilemmas reveal model decision-making

**Pattern:** Always test multiple models for production use cases to find best fit

---

### Local Models with Ollama

**Problem:** Need free, private model inference

**Solution:** Run Ollama locally, use OpenAI-compatible endpoint

**Setup:**
```bash
ollama serve  # Start server
ollama pull llama3.2  # Download model
```

**Usage:**
```python
ollama = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
response = ollama.chat.completions.create(model="llama3.2", messages=messages)
```

**Tradeoffs:**
- **Local models:** Free, private, but lower quality, variable latency
- **Cloud models:** Better quality, consistent latency, but paid, data leaves machine

**Pattern:** Use local for privacy/experimentation, cloud for production quality

---

### Abstraction Layers

**LiteLLM:**
- Lightweight, simple API
- Cost tracking built-in (`response._hidden_params["response_cost"]`)
- Easy model switching: `completion(model="openai/gpt-4.1", messages=...)`
- Supports many providers

**LangChain:**
- Heavyweight framework
- More features (chains, agents, memory)
- More complex, but powerful for complex workflows
- Good for production applications

**OpenRouter:**
- Unified interface for many models
- One API key for multiple providers
- Good for experimentation and comparison
- Access to models not directly available

**Pattern:** 
- Simple use cases → LiteLLM
- Complex workflows → LangChain
- Experimentation → OpenRouter

---

### Prompt Caching

**Problem:** Repeatedly sending same large context is expensive

**Solution:** Use prompt caching to cache static content

**How It Works:**
- Static content (instructions, examples) cached on first call
- Subsequent calls reuse cached content (much cheaper)
- Variable content (user-specific data) placed at end

**Provider Differences:**

**OpenAI:**
- 4x cheaper for cached content
- Requires exact prefix matches
- Place static content at beginning, variable at end

**Anthropic:**
- 25% MORE to prime cache (first call)
- 10x cheaper to reuse cached content
- Must explicitly mark what to cache

**Gemini:**
- Supports both implicit and explicit caching
- Automatic caching for repeated prefixes

**Real Example (Hamlet):**
- First call: 53,208 tokens, $0.5339
- Second call: 53,208 tokens, 52,216 cached, $0.1423
- **Savings: ~73% on second call**

**Pattern:**
```python
# Structure prompt for caching
messages = [
    {"role": "system", "content": "Static instructions..."},  # Cached
    {"role": "user", "content": "Static examples..."},      # Cached
    {"role": "user", "content": f"Variable: {user_data}"}   # Not cached
]
```

**When to Use:**
- Large static context (documents, examples, instructions)
- Repeated calls with same base prompt
- Cost-sensitive applications

---

### Multi-Model Conversations

**Problem:** Create conversations between multiple chatbots with different personalities

**Solution:** Two approaches - choose based on complexity needs

#### Approach 1: Structured Messages (More Complex)

**Message Structure:**
```python
messages = [
    {"role": "system", "content": "You are a chatbot who..."},  # Personality
    {"role": "user", "content": "Hi there"},                    # First message
    {"role": "assistant", "content": "Hello!"},                 # Response
    {"role": "user", "content": "How are you?"}                 # Next message
]
```

**4-Way Conversation Pattern:**
```python
# Each model sees conversation from all others
for gpt, gemini, ollama, deepseek in zip(gpt_messages, gemini_messages, ollama_messages, deepseek_messages):
    messages.append({"role": "user", "content": f"GPT: {gpt}"})
    messages.append({"role": "user", "content": f"Gemini: {gemini}"})
    messages.append({"role": "user", "content": f"Ollama: {ollama}"})
    messages.append({"role": "assistant", "content": deepseek})  # This model's response
```

**When to use:** Need fine-grained control over message structure

#### Approach 2: Simple List + Narrative (Easier!) ⭐

**Pattern:**
```python
# Single conversation list
conversation = ["GPT: Hi", "Gemini: Hi", "Ollama: Hello"]

# System prompt mentions other participants
system_prompt = """You are GPT, argumentative chatbot.
You are in a conversation with Gemini and Ollama."""

# User prompt includes full conversation as narrative
user_prompt = f"""You are GPT, in conversation with Gemini and Ollama.
The conversation so far is as follows:
{chr(10).join(conversation)}
Now respond as GPT."""

# Just append after each response
conversation.append(f"GPT: {response}")
```

**Key Benefits:**
- **One list** instead of multiple message lists
- **Simple append** after each response
- **Reuse same template** for user prompt
- **Easier to debug** - conversation is just a list of strings
- **More reliable** for multi-way conversations

**When to use:** Default choice - simpler and more maintainable

**Pattern:**
- Build history incrementally (just append to list)
- Each model sees all previous exchanges (full conversation in user prompt)
- System prompt controls personality and mentions other participants
- Can create 2-way, 3-way, 4-way+ conversations

**Business Relevance:**
- Foundation for conversational AI assistants
- Multi-agent systems
- Debate/discussion simulations
- Testing model interactions

---

## Day 2: Gradio UI Development

### Gradio Basics

**Problem:** Need to create user interfaces for LLM applications quickly

**Solution:** Use Gradio framework - simple Python library for building UIs

**Key Concepts:**
- **Interface creation:** `gr.Interface(fn=function, inputs=[...], outputs=[...])`
- **Component types:** Textbox, Dropdown, Markdown, etc.
- **Launch options:** `share=True` (public link), `inbrowser=True` (auto-open), `auth=("user", "pass")` (password)
- **Examples:** Pre-populate UI with example inputs

**Basic Pattern:**
```python
import gradio as gr

def my_function(input_text):
    # Process input
    return output_text

gr.Interface(
    fn=my_function,
    inputs=gr.Textbox(label="Input:"),
    outputs=gr.Textbox(label="Output:"),
    examples=["example1", "example2"],
    flagging_mode="never"
).launch()
```

**Tradeoff:**
- **Gradio:** Fast prototyping, simple, but limited customization
- **Custom web app:** Full control, but much more complex
- **Pattern:** Use Gradio for demos/prototypes/MVPs, custom for production

---

### Streaming with Generators

**Problem:** LLM responses take time - want to show progress to user

**Solution:** Use Python generators with `yield` keyword for streaming

**How It Works:**
```python
def stream_llm(prompt):
    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result  # Yield accumulated result each time
```

**Key Points:**
- **Generator function:** Must use `yield`, not `return`
- **Gradio auto-detection:** Gradio automatically detects generator functions
- **Incremental updates:** UI updates as each chunk arrives
- **User experience:** Much better than waiting for complete response

**Pattern:**
- Use `yield` for streaming (real-time updates)
- Use `return` for one-shot responses (complete at once)
- Accumulate response in loop, yield after each chunk

**Tradeoff:**
- **Streaming:** Better UX, but more complex code (generators)
- **One-shot:** Simpler code, but user waits for complete response

---

### Multi-Model UI with Class-Based Design

**Problem:** Want to support multiple models in UI without code duplication

**Solution:** Class-based architecture with model registry pattern

**Pattern:**
```python
class BrochureGenerator:
    def __init__(self):
        # Initialize all clients
        self.openai_client = OpenAI()
        
        # Check Ollama availability
        try:
            requests.get("http://localhost:11434/", timeout=2)
            self.ollama_client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
            self.ollama_available = True
        except:
            self.ollama_available = False
        
        # Model registry: maps display name to (client, model_name)
        self.models = {
            "GPT": (self.openai_client, "gpt-4.1-mini"),
        }
        if self.ollama_available:
            self.models["Ollama"] = (self.ollama_client, "llama3.2")
    
    def stream_brochure(self, company_name, url, model_name):
        # Unified method - works for all models
        client, model = self.models[model_name]
        # ... streaming logic ...
        yield response
```

**Key Benefits:**
- **No duplication:** Single method works for all models
- **Easy to extend:** Just add to `models` dictionary
- **Self-documenting:** Registry shows what's available
- **Automatic detection:** Only includes models that are available
- **Clean architecture:** Encapsulates all model logic

**Pattern:**
- Model registry: Dictionary mapping names to (client, model_name) tuples
- Unified method: Single function that works with any model in registry
- Automatic detection: Check availability, only include if ready
- Easy extension: Add new models by updating dictionary

**Tradeoff:**
- **Class-based:** Cleaner, more maintainable, but requires class design
- **Separate functions:** Simpler initially, but duplicates code as models grow

---

## Key Learnings

### Multi-Provider APIs
- OpenAI-compatible endpoints enable easy model switching
- Native libraries offer provider-specific features
- Abstraction layers simplify multi-provider code
- Pattern: Choose interface based on needs (simple → unified, complex → native)

### Model Selection
- Test multiple models for production use cases
- Consider quality, cost, latency, privacy
- Use local models for privacy/experimentation
- Use cloud models for production quality

### Cost Optimization
- Prompt caching can save 70%+ on repeated calls
- Structure prompts for caching (static first, variable last)
- Monitor token usage in production
- Consider local models for long conversations

### Conversation Management
- LLMs are stateless; manage history in application
- Message structure: system (personality) + user/assistant (history)
- Full conversation history needed for context
- Pattern: Build incrementally, each model sees all exchanges

### UI Development with Gradio
- Gradio is perfect for demos, prototypes, and MVPs
- Streaming requires generator pattern (`yield` not `return`)
- Class-based design with model registry simplifies multi-model UIs
- Pattern: Use Gradio for fast prototyping, custom web for production

## Tradeoffs Observed

### Cost vs Quality
- Frontier models: Higher cost, better quality
- Local models: Free, lower quality
- Prompt caching: Reduces cost for repeated calls
- Example: Caching Hamlet text saved 73% on second call

### Latency vs Accuracy
- Higher reasoning effort = better accuracy, but slower
- Local models: Variable latency (hardware-dependent)
- Cloud models: Consistent latency
- Streaming: Better UX, but more complex code

### Privacy vs Capability
- Local models: Private, but limited capability
- Cloud models: Better capability, but data leaves machine
- Pattern: Use local for sensitive data, cloud for general use

### Prototyping vs Production
- Gradio: Fast prototyping, simple, but limited customization
- Custom web: Full control, but much more complex
- Streaming: Better UX, but requires generator pattern
- Pattern: Use Gradio for demos/MVPs, custom for production apps

## Reusable Patterns

### Multi-Provider Setup
```python
# Pattern: Unified interface for multiple providers
providers = {
    "openai": OpenAI(),
    "gemini": OpenAI(api_key=google_key, base_url=gemini_url),
    "deepseek": OpenAI(api_key=deepseek_key, base_url=deepseek_url),
    "ollama": OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
}
```

### Conversation History Management
```python
# Pattern: Build conversation history incrementally
def call_model(messages_history, system_prompt, new_user_message):
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(messages_history)  # Full history
    messages.append({"role": "user", "content": new_user_message})
    return client.chat.completions.create(model=model, messages=messages)
```

### Prompt Caching Structure
```python
# Pattern: Static content first, variable content last
messages = [
    {"role": "system", "content": static_instructions},  # Cached
    {"role": "user", "content": static_examples},         # Cached
    {"role": "user", "content": f"Variable: {data}"}     # Not cached
]
```

### Model Comparison
```python
# Pattern: Test same task across multiple models
def compare_models(task, models):
    results = {}
    for model_name, client in models.items():
        response = client.chat.completions.create(model=model, messages=task)
        results[model_name] = {
            "response": response.choices[0].message.content,
            "cost": calculate_cost(response),
            "latency": measure_latency(response)
        }
    return results
```

### Gradio Streaming Pattern
```python
# Pattern: Streaming LLM responses to Gradio UI
def stream_llm(prompt):
    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result  # Yield accumulated result for real-time updates
```

### Class-Based Multi-Model UI
```python
# Pattern: Unified model interface with class and registry
class LLMGenerator:
    def __init__(self):
        self.models = {
            "GPT": (openai_client, "gpt-4.1-mini"),
            "Ollama": (ollama_client, "llama3.2")
        }
    
    def generate(self, prompt, model_name):
        client, model = self.models[model_name]
        # Unified logic for all models
        stream = client.chat.completions.create(model=model, messages=messages, stream=True)
        result = ""
        for chunk in stream:
            result += chunk.choices[0].delta.content or ""
            yield result
```

## Questions to Explore Further

- [ ] How to implement automatic model selection based on task?
- [ ] What's the optimal prompt caching strategy for different use cases?
- [ ] How to handle rate limits across multiple providers?
- [ ] What's the best way to manage conversation history for very long conversations?
- [ ] How to implement fallback strategies (local → cloud)?
- [ ] What are the best practices for multi-agent systems?

## References

- Course material: Week 2 Day 1 & Day 2 notebooks
- OpenAI API docs: https://platform.openai.com/docs
- Anthropic API docs: https://docs.anthropic.com
- LiteLLM docs: https://docs.litellm.ai
- LangChain docs: https://python.langchain.com
- OpenRouter docs: https://openrouter.ai/docs
- Ollama docs: https://ollama.ai/docs
- Gradio docs: https://www.gradio.app/guides/quickstart


