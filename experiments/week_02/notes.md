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
- **Component configuration:** `label`, `info`, `lines` parameters for customization
- **Launch options:** 
  - `share=True` (public link via HTTP tunneling - may be blocked by corporate firewalls/antivirus)
  - `inbrowser=True` (auto-open browser)
  - `auth=("user", "pass")` (password protection - use .env for production!)
- **Flagging mode:** `flagging_mode="never"` disables the flag button (useful for demos)
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

**Important Notes:**
- **share=True warning:** Uses HTTP tunneling (like ngrok) - may be blocked by antivirus/corporate firewalls
- **Dark mode:** Gradio respects user's browser/system preferences (recommended). Can force dark mode with `js` parameter, but not recommended for accessibility
- **Authentication:** Use `.env` file for passwords in production, never hardcode!

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

## Day 3: Conversational AI with Gradio ChatInterface

### Gradio ChatInterface

**Problem:** Need to build conversational AI chatbots with multi-turn conversation support

**Solution:** Use Gradio's `ChatInterface` component - purpose-built for conversations

**Key Concepts:**
- **ChatInterface:** `gr.ChatInterface(fn=chat, type="messages")` - specialized for conversations
- **Callback signature:** `chat(message, history)` - Gradio manages history automatically
- **History format:** Gradio provides history as list of `{"role": "...", "content": "..."}` dicts
- **Message conversion:** Must convert Gradio history to API format

**Basic Pattern:**
```python
def chat(message, history):
    # Convert Gradio history to API format
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    
    # Build messages: system + history + new user message
    messages = [
        {"role": "system", "content": system_message},
    ] + history + [
        {"role": "user", "content": message}
    ]
    
    # Call API
    response = openai.chat.completions.create(model=MODEL, messages=messages)
    return response.choices[0].message.content

# Launch ChatInterface
gr.ChatInterface(fn=chat, type="messages").launch()
```

**Key Differences from Interface:**
- **ChatInterface:** Purpose-built for conversations, manages history automatically
- **Interface:** General-purpose, you manage state yourself
- **History:** ChatInterface provides conversation history, Interface doesn't
- **UI:** ChatInterface has chat-like UI, Interface is more flexible

**Pattern:** Use ChatInterface for conversations, Interface for general I/O

**Tradeoff:**
- **ChatInterface:** Easier for conversations, but less flexible
- **Interface:** More flexible, but you manage conversation state yourself

---

### System Messages for Context and Behavior

**Problem:** Need to control chatbot personality, behavior, and business logic

**Solution:** Use system messages to set context, personality, and constraints

**How It Works:**
- System message is first in messages array
- Defines personality, role, and behavior
- Can include examples (one-shot prompting)
- Persists across entire conversation

**Basic Pattern:**
```python
system_message = """You are a helpful assistant in a clothes store. 
You should try to gently encourage the customer to try items that are on sale. 
Hats are 60% off, and most other items are 50% off.

For example, if the customer says 'I'm looking to buy a hat', 
you could reply something like, 'Wonderful - we have lots of hats - including 
several that are part of our sales event.'

Encourage the customer to buy hats if they are unsure what to get."""

def chat(message, history):
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    messages = [
        {"role": "system", "content": system_message},
    ] + history + [
        {"role": "user", "content": message}
    ]
    # ... API call ...
```

**One-Shot Prompting in System Messages:**
- Include examples directly in system message
- Model learns from examples without needing few-shot in each message
- More efficient than repeating examples in every user message
- Pattern: System message = instructions + examples + constraints

**Business Applications:**
- Product information (prices, availability, features)
- Business rules (what to recommend, what to avoid)
- Tone and personality (friendly, professional, encouraging)
- Constraints (what not to sell, what to emphasize)

**Pattern:**
- System message = personality + context + examples + constraints
- User/Assistant messages = actual conversation history
- System message persists, conversation history grows

---

### Streaming in ChatInterface

**Problem:** Want real-time streaming in conversational interfaces

**Solution:** Use generator pattern with `yield` - same as regular Interface

**How It Works:**
```python
def chat(message, history):
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    messages = [
        {"role": "system", "content": system_message},
    ] + history + [
        {"role": "user", "content": message}
    ]
    
    # Enable streaming
    stream = openai.chat.completions.create(
        model=MODEL, 
        messages=messages, 
        stream=True
    )
    
    # Accumulate and yield
    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        yield response  # Yield accumulated result (not return!)
```

**Key Points:**
- **Same pattern:** Generator with `yield` works in ChatInterface too
- **Auto-detection:** Gradio automatically detects generator functions
- **Incremental updates:** UI updates as each chunk arrives
- **Better UX:** Users see responses as they generate, feels more natural

**Pattern:** Use `yield` for streaming, `return` for one-shot responses

---

### Dynamic System Message Modification

**Problem:** Need to adapt system message based on user input or conversation state

**Solution:** Conditionally modify system message before API call

**Pattern:**
```python
def chat(message, history):
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    
    # Start with base system message
    relevant_system_message = system_message
    
    # Modify based on user input
    if 'belt' in message.lower():
        relevant_system_message += " The store does not sell belts; if you are asked for belts, be sure to point out other items on sale."
    
    # Build messages with modified system message
    messages = [
        {"role": "system", "content": relevant_system_message},
    ] + history + [
        {"role": "user", "content": message}
    ]
    
    # ... API call ...
```

**Use Cases:**
- **Keyword detection:** Add context when specific topics mentioned
- **Edge cases:** Handle special cases dynamically
- **Contextual rules:** Add rules based on conversation flow
- **Adaptive behavior:** Change behavior based on user needs

**Pattern:**
- Base system message = core personality and rules
- Dynamic extension = additional context when needed
- Check user message or conversation state before modifying

**Tradeoff:**
- **Static system message:** Simpler, but less flexible
- **Dynamic modification:** More flexible, but more complex logic

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

### Conversational AI with ChatInterface
- ChatInterface is purpose-built for multi-turn conversations
- System messages control personality, context, and behavior
- History management: Convert Gradio history to API format
- Dynamic system message modification enables adaptive behavior
- Pattern: System message = personality + context, History = conversation

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

### Gradio ChatInterface Pattern
```python
# Pattern: Conversational AI with ChatInterface
def chat(message, history):
    # Convert Gradio history to API format
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    
    # Build messages: system + history + new user message
    messages = [
        {"role": "system", "content": system_message},
    ] + history + [
        {"role": "user", "content": message}
    ]
    
    # Streaming response
    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        yield response

# Launch ChatInterface
gr.ChatInterface(fn=chat, type="messages").launch()
```

### Dynamic System Message Pattern
```python
# Pattern: Modify system message based on user input
def chat(message, history):
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    
    # Base system message
    relevant_system_message = system_message
    
    # Dynamic modification based on keywords
    if 'keyword' in message.lower():
        relevant_system_message += " Additional context for keyword..."
    
    # Build messages with modified system message
    messages = [
        {"role": "system", "content": relevant_system_message},
    ] + history + [
        {"role": "user", "content": message}
    ]
    
    # ... API call ...
```

## Day 4: Tool Calling / Function Calling

### Tool Calling Fundamentals

**Problem:** Need LLM to interact with external systems (databases, APIs, functions)

**Solution:** Tool calling - LLM can call Python functions as tools

**Key Concepts:**
- **Tool definition:** JSON schema describing function (name, description, parameters)
- **Tool call flow:** LLM decides → returns tool_calls → execute → return result → LLM continues
- **Message types:** `assistant` (with tool_calls), `tool` (with tool_call_id), `user`, `system`
- **Tool response:** Must include `role: "tool"`, `content: result`, `tool_call_id: id`

**Tool Definition Format:**
```python
tool_definition = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to a destination city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to"
            }
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": tool_definition}]
```

**Tool Call Detection:**
```python
response = openai.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tools
)

# Check if LLM wants to call a tool
if response.choices[0].finish_reason == "tool_calls":
    assistant_message = response.choices[0].message
    # assistant_message.tool_calls contains list of tool calls
```

**Tool Execution:**
```python
for tool_call in assistant_message.tool_calls:
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    tool_call_id = tool_call.id
    
    # Execute function
    result = function(**arguments)
    
    # Return tool response
    tool_response = {
        "role": "tool",
        "content": result,
        "tool_call_id": tool_call_id
    }
```

**Pattern:** Tools enable LLMs to interact with databases, APIs, and external systems

**Tradeoff:**
- **Manual implementation:** Full control, understand mechanics, but complex
- **SDKs (OpenAI Agent SDK):** Easier, but abstracts away understanding

---

### Function Registry Pattern

**Problem:** If/elif chains don't scale when adding new tools

**Solution:** Dictionary-based registry for tool routing

**Registry Structure:**
```python
TOOL_REGISTRY: Dict[str, Callable] = {
    "get_ticket_price": get_ticket_price,
    "set_ticket_price": set_ticket_price,
}

# Dynamic lookup and execution
function_name = tool_call.function.name
func = TOOL_REGISTRY[function_name]
arguments = json.loads(tool_call.function.arguments)
result = func(**arguments)  # Unpack dict as keyword arguments
```

**Benefits:**
- **No if statements:** Dictionary lookup replaces conditional chains
- **Easy to extend:** Adding new tool = one line in registry + function definition
- **Scales beautifully:** Works with 2 tools or 200 tools
- **Clean code:** Self-documenting (registry shows all available tools)

**Pattern:** Function registry > if/elif chains for tool routing

**Tradeoff:**
- **Registry pattern:** Cleaner, more maintainable, but requires discipline
- **If/elif chains:** Simple for 2-3 tools, but becomes unmaintainable quickly

---

### SQLite for Conversation History

**Problem:** Gradio's in-memory history is ephemeral (lost on restart)

**Solution:** Store conversation history in SQLite database

**Database Schema:**
```python
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT,
    tool_calls TEXT,  # JSON string for assistant messages, tool_call_id for tool messages
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
CREATE INDEX IF NOT EXISTS idx_session ON conversations(session_id)
```

**Saving Messages:**
```python
def save_message(session_id: str, role: str, content: str, tool_calls: Optional[str] = None):
    with sqlite3.connect(DB_CONVERSATIONS) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO conversations (session_id, role, content, tool_calls) VALUES (?, ?, ?, ?)',
            (session_id, role, content, tool_calls)
        )
        conn.commit()
```

**Loading Conversation:**
```python
def load_conversation(session_id: str) -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_CONVERSATIONS) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT role, content, tool_calls FROM conversations WHERE session_id = ? ORDER BY id',
            (session_id,)
        )
        rows = cursor.fetchall()
        
        messages = []
        for role, content, tool_calls_json in rows:
            msg = {"role": role, "content": content or ""}
            
            # Reconstruct assistant messages with tool_calls
            if role == "assistant" and tool_calls_json:
                tool_calls_data = json.loads(tool_calls_json)
                msg["tool_calls"] = tool_calls_data
            
            # Reconstruct tool messages with tool_call_id
            elif role == "tool" and tool_calls_json:
                msg["tool_call_id"] = tool_calls_json  # tool_calls column stores tool_call_id for tool messages
            
            messages.append(msg)
        
        return messages
```

**Key Points:**
- **Tool calls storage:** Store as JSON string for assistant messages
- **Tool call ID storage:** Store tool_call_id in tool_calls column for tool messages
- **History reconstruction:** Parse JSON, reconstruct full conversation for API
- **Session management:** Filter by session_id for multi-user support

**Pattern:** SQLite for conversation history > in-memory storage for production apps

**Tradeoff:**
- **SQLite:** Persistent, queryable, production-ready, but requires database setup
- **In-memory:** Simple, fast, but ephemeral (lost on restart)

---

### Manual Tool Calling Implementation

**Problem:** SDKs abstract away the mechanics - need to understand what happens under the hood

**Solution:** Implement tool calling manually to learn the complete flow

**Complete Flow:**
```python
def chat(message: str, history, session_id: str):
    # 1. Load conversation from database
    messages = load_conversation(session_id)
    
    # 2. Add system message if first message
    if not messages:
        messages = [{"role": "system", "content": system_message}]
        save_message(session_id, "system", system_message)
    
    # 3. Add user message
    messages.append({"role": "user", "content": message})
    save_message(session_id, "user", message)
    
    # 4. Initial API call (try streaming)
    response = openai.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        stream=True
    )
    
    # 5. Detect tool calls in stream
    accumulated_content = ""
    tool_calls_detected = False
    finish_reason = None
    
    for chunk in response:
        if chunk.choices[0].delta.content:
            accumulated_content += chunk.choices[0].delta.content
            yield accumulated_content
        
        if chunk.choices[0].delta.tool_calls:
            tool_calls_detected = True
        
        if chunk.choices[0].finish_reason:
            finish_reason = chunk.choices[0].finish_reason
    
    # 6. If tool calls detected, switch to non-streaming
    if tool_calls_detected or finish_reason == "tool_calls":
        response = openai.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools
        )
        
        # 7. Handle tool calls loop
        while response.choices[0].finish_reason == "tool_calls":
            assistant_message = response.choices[0].message
            
            # Save assistant message with tool calls
            tool_calls_json = json.dumps([tc.model_dump() for tc in assistant_message.tool_calls])
            save_message(session_id, "assistant", assistant_message.content or "", tool_calls_json)
            messages.append(assistant_message)
            
            # Execute tools
            tool_responses = handle_tool_calls(assistant_message)
            messages.extend(tool_responses)
            
            # Save tool responses
            for tool_resp in tool_responses:
                save_message(session_id, "tool", tool_resp["content"], tool_resp.get("tool_call_id"))
            
            # Continue conversation
            response = openai.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
                stream=True
            )
            
            # Stream response after tool execution
            accumulated_content = ""
            finish_reason = None
            more_tool_calls_detected = False
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    accumulated_content += chunk.choices[0].delta.content
                    yield accumulated_content
                
                if chunk.choices[0].delta.tool_calls:
                    more_tool_calls_detected = True
                    break
                
                if chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
            
            # Check if more tool calls needed
            if more_tool_calls_detected or finish_reason == "tool_calls":
                response = openai.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=tools
                )
            else:
                if accumulated_content:
                    save_message(session_id, "assistant", accumulated_content)
                break
```

**Key Learnings:**
- **Tool call detection:** Check `finish_reason == "tool_calls"` or `message.tool_calls`
- **Tool execution loop:** While tool calls exist → execute → add responses → continue
- **Streaming challenge:** Can't get complete tool call data from stream, need non-streaming call
- **Response type handling:** Stream vs ChatCompletion - need to check type before accessing

**Pattern:** Manual implementation teaches you what SDKs abstract away

---

### Streaming + Tool Calls

**Problem:** Streaming provides better UX, but tool calls require complete data

**Solution:** Hybrid approach - stream when possible, switch to non-streaming for tools

**The Challenge:**
- Streaming API doesn't provide complete tool call data incrementally
- Need full tool call info (function name, arguments, ID) to execute
- Can't execute tools from partial stream data

**Solution Pattern:**
1. Try streaming first
2. Detect tool calls in stream (check `chunk.choices[0].delta.tool_calls`)
3. Track `finish_reason` from stream chunks (last chunk has it)
4. If tool calls detected → switch to non-streaming → get full tool data
5. Execute tools → add responses to conversation
6. Resume streaming for final response

**Key Implementation Details:**
```python
# Track finish_reason from stream chunks (not from Stream object)
finish_reason = None
for chunk in response:
    if chunk.choices[0].finish_reason:
        finish_reason = chunk.choices[0].finish_reason  # Last chunk has finish_reason

# Check response type before accessing (Stream vs ChatCompletion)
try:
    if hasattr(response, 'choices') and response.choices:
        final_content = response.choices[0].message.content
except (AttributeError, TypeError):
    # Response is a Stream or already consumed
    pass
```

**Pattern:** Hybrid streaming (stream → detect tools → non-stream → execute → stream again)

**Tradeoff:**
- **Pure streaming:** Better UX, but can't handle tool calls
- **Hybrid approach:** Best of both worlds, but more complex logic

---

### Session Management

**Problem:** Each user/browser needs separate conversation history

**Solution:** Generate unique session_id per user, filter database by session_id

**Session ID Generation:**
```python
def chat_wrapper(message, history, request: gr.Request = None):
    try:
        if request and hasattr(request, 'headers') and request.headers:
            user_agent = request.headers.get('user-agent', '')
            session_id = f"session_{hash(user_agent) % 1000000}"
        else:
            session_id = f"session_{uuid.uuid4().hex[:8]}"
    except Exception:
        session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    for response in chat(message, history, session_id):
        yield response
```

**Key Points:**
- Use `gr.Request` to get user-specific information
- Hash user-agent for consistent session ID per browser
- Fallback to UUID if request unavailable
- Filter database queries by session_id

**Pattern:** Session management = unique ID per user + database filtering by session_id

**Tradeoff:**
- **Request-based:** More accurate, but requires Gradio request object
- **UUID fallback:** Always works, but new ID each time (no persistence)

---

### Error Handling for Tool Execution

**Problem:** Tools can fail in many ways (invalid JSON, wrong arguments, runtime errors)

**Solution:** Comprehensive error handling at each failure point

**Error Handling Pattern:**
```python
def handle_tool_calls(message) -> List[Dict[str, Any]]:
    responses = []
    
    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        
        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            responses.append({
                "role": "tool",
                "content": f"Error: Invalid tool arguments JSON. {str(e)}",
                "tool_call_id": tool_call.id
            })
            continue
        
        if function_name in TOOL_REGISTRY:
            func = TOOL_REGISTRY[function_name]
            try:
                result = func(**arguments)
                responses.append({
                    "role": "tool",
                    "content": result,
                    "tool_call_id": tool_call.id
                })
            except TypeError as e:
                # Wrong number of arguments or wrong argument names
                responses.append({
                    "role": "tool",
                    "content": f"Error: Function {function_name} received invalid arguments. {str(e)}",
                    "tool_call_id": tool_call.id
                })
            except Exception as e:
                # Any other error from the function itself
                responses.append({
                    "role": "tool",
                    "content": f"Error executing {function_name}: {str(e)}",
                    "tool_call_id": tool_call.id
                })
        else:
            responses.append({
                "role": "tool",
                "content": f"Error: Unknown tool '{function_name}'",
                "tool_call_id": tool_call.id
            })
    
    return responses
```

**Error Types Handled:**
- **JSON parsing errors:** Invalid JSON in tool arguments
- **Type errors:** Wrong number/type of arguments
- **General exceptions:** Runtime errors in tool functions
- **Unknown tools:** Tool not found in registry

**Pattern:** Comprehensive error handling = try/except at each failure point + informative error messages

**Tradeoff:**
- **Comprehensive handling:** Robust, but more code
- **Minimal handling:** Simpler, but fails ungracefully

---

### Tool Calling Patterns

**Tool Definition Pattern:**
```python
# Define tool function
def get_ticket_price(destination_city: str) -> str:
    # ... implementation ...
    return f"Ticket price to {city} is ${price:.2f}"

# Define tool schema
tool_definition = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to a destination city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to"
            }
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

# Register in tools list
tools = [{"type": "function", "function": tool_definition}]
```

**Function Registry Pattern:**
```python
TOOL_REGISTRY: Dict[str, Callable] = {
    "get_ticket_price": get_ticket_price,
    "set_ticket_price": set_ticket_price,
}

def handle_tool_calls(message) -> List[Dict[str, Any]]:
    responses = []
    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        func = TOOL_REGISTRY[function_name]
        result = func(**arguments)
        
        responses.append({
            "role": "tool",
            "content": result,
            "tool_call_id": tool_call.id
        })
    return responses
```

**SQLite Conversation History Pattern:**
```python
# Save message
def save_message(session_id: str, role: str, content: str, tool_calls: Optional[str] = None):
    with sqlite3.connect(DB_CONVERSATIONS) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO conversations (session_id, role, content, tool_calls) VALUES (?, ?, ?, ?)',
            (session_id, role, content, tool_calls)
        )
        conn.commit()

# Load conversation
def load_conversation(session_id: str) -> List[Dict[str, Any]]:
    with sqlite3.connect(DB_CONVERSATIONS) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT role, content, tool_calls FROM conversations WHERE session_id = ? ORDER BY id',
            (session_id,)
        )
        rows = cursor.fetchall()
        
        messages = []
        for role, content, tool_calls_json in rows:
            msg = {"role": role, "content": content or ""}
            if role == "assistant" and tool_calls_json:
                msg["tool_calls"] = json.loads(tool_calls_json)
            elif role == "tool" and tool_calls_json:
                msg["tool_call_id"] = tool_calls_json
            messages.append(msg)
        return messages
```

**Hybrid Streaming Pattern:**
```python
# Try streaming first
response = openai.chat.completions.create(..., stream=True)

# Detect tool calls
tool_calls_detected = False
finish_reason = None
for chunk in response:
    if chunk.choices[0].delta.tool_calls:
        tool_calls_detected = True
    if chunk.choices[0].finish_reason:
        finish_reason = chunk.choices[0].finish_reason

# Switch to non-streaming if tools detected
if tool_calls_detected or finish_reason == "tool_calls":
    response = openai.chat.completions.create(..., stream=False)
    # Handle tool calls...
    # Resume streaming after tools executed
```

## Day 5: Multi-Modal AI & Enhanced Tool Calling

### Multi-Modal AI Responses

**Problem:** Many applications need more than text responses (images, audio)

**Solution:** Combine text responses with DALL-E-3 image generation and TTS audio

**DALL-E-3 Integration:**
```python
def artist(city):
    image_response = openai.images.generate(
        model="dall-e-3",
        prompt=f"An image representing a vacation in {city}",
        size="1024x1024",
        n=1,
        response_format="b64_json"
    )
    image_base64 = image_response.data[0].b64_json
    image_data = base64.b64decode(image_base64)
    return Image.open(BytesIO(image_data))
```

**TTS Integration:**
```python
def talker(message):
    response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
        input=message
    )
    audio_path = "output.mp3"
    response.stream_to_file(audio_path)
    return audio_path
```

**Key Points:**
- **Image format:** Use `response_format="b64_json"` for base64 encoded images
- **Audio format:** Response is streamable audio file (mp3)
- **Combining with tools:** Can call image/audio generation as tool result
- **Size options:** DALL-E supports 1024x1024, 1792x1024, 1024x1792

**Pattern:** Multi-modal = multiple API calls + proper handling of each modality

**Tradeoff:**
- **Multi-modal:** Richer UX, but more API calls and cost
- **Text-only:** Simpler, cheaper, but less engaging

---

### Enhanced Flight Booking System (My Extension)

**Problem:** Simple booking systems don't match real-world UX

**Solution:** Implement realistic two-step booking with complete flight details

**Key Features Implemented:**
- **Two-step flow:** Quote → Confirm (never charge without showing price)
- **Flight times:** 5 scheduled departure times (6AM, 10AM, 2PM, 6PM, 9PM)
- **Class selection:** Economy (1x), Business (2.5x), First Class (4x)
- **Price breakdown:** Base fare × passengers × class multiplier + taxes
- **Email confirmation:** Simulated email showing booking details
- **Multiple passengers:** Support 1-9 passengers
- **Round trip/one-way:** Optional return date
- **Cancellation:** Cancel with simulated refund

**Configuration Pattern:**
```python
# Flight times configuration
FLIGHT_TIMES = {
    "morning": "06:00 AM",
    "mid-morning": "10:00 AM",
    "afternoon": "02:00 PM",
    "evening": "06:00 PM",
    "night": "09:00 PM"
}

# Class multipliers
CLASS_MULTIPLIERS = {
    "economy": 1.0,
    "business": 2.5,
    "first": 4.0
}

# Tax rate
TAX_RATE = 0.12
```

**Why Two-Step Flow:**
- Real booking systems NEVER complete transactions without showing price
- Prevents accidental bookings
- Matches industry-standard UX
- Allows user to review before committing
- Mirrors real payment flows (show total → confirm → charge)

**Pattern:** Quote → Confirm separates "show price" from "finalize transaction"

---

### Handling LLM Training Data Cutoff

**Problem:** LLMs are trained on data up to a specific date, can't assume current dates

**Solution:** Parse and validate dates in code, not relying on LLM assumptions

**Date Parsing with dateutil:**
```python
from dateutil import parser

def parse_date(date_str):
    """Parse various date formats into YYYY-MM-DD format.
    
    Why we need this: LLMs are trained on data up to a certain cutoff date.
    Users need to book flights for future dates (2025, 2026, etc.), so we must 
    parse and validate dates beyond the training cutoff.
    """
    try:
        parsed_date = parser.parse(date_str)
        return parsed_date.strftime("%Y-%m-%d")
    except:
        return date_str  # Let validation catch invalid dates
```

**Future Date Validation:**
```python
def validate_date(date_str, must_be_future=True):
    """Validate a date string and optionally check if it's in the future."""
    try:
        parsed = parse_date(date_str)
        date_obj = datetime.strptime(parsed, "%Y-%m-%d").date()
        
        if must_be_future and date_obj < datetime.now().date():
            return False, f"Date {parsed} must be in the future. Today is {datetime.now().date()}"
        
        return True, parsed
    except Exception as e:
        return False, f"Invalid date format: {date_str}"
```

**Key Points:**
- **Flexible parsing:** dateutil handles "June 15, 2025", "2025-06-15", "next month", etc.
- **Future validation:** Compare against real `datetime.now()`, not LLM assumptions
- **Standard format:** Convert all dates to `YYYY-MM-DD` internally
- **Clear errors:** Return helpful error messages for invalid dates

**Pattern:** Parse dates in code, validate against real time, don't trust LLM date assumptions

**Why This Matters:**
- LLM might default to dates from training data
- Users need to book for future dates beyond training cutoff
- Real applications must work with actual current dates
- Date validation is a code responsibility, not LLM responsibility

---

### Complex Tool Definitions

**Problem:** Real-world tools have many parameters (10+)

**Solution:** Define comprehensive tool schemas with required and optional parameters

**Example: Flight Quote Tool (10+ parameters):**
```python
quote_function = {
    "name": "get_flight_quote",
    "description": """Generate a detailed flight quote with price breakdown. 
    IMPORTANT: Only call this when you have ALL required information.""",
    "parameters": {
        "type": "object",
        "properties": {
            "passenger_name": {
                "type": "string",
                "description": "Full name of the primary passenger"
            },
            "email": {
                "type": "string",
                "description": "Email address for booking confirmation"
            },
            "origin_city": {
                "type": "string",
                "description": "City where the flight departs from"
            },
            "destination_city": {
                "type": "string",
                "description": "City where the flight arrives"
            },
            "departure_date": {
                "type": "string",
                "description": "Departure date (e.g., '2025-06-15', 'June 15, 2025')"
            },
            "departure_time": {
                "type": "string",
                "description": "Preferred departure time: 'morning' (6AM), 'mid-morning' (10AM), etc."
            },
            "flight_class": {
                "type": "string",
                "description": "Class of travel: 'economy', 'business', or 'first'"
            },
            "num_passengers": {
                "type": "integer",
                "description": "Number of passengers (1-9)"
            },
            "return_date": {
                "type": "string",
                "description": "Return date for round trips (optional)"
            },
            "return_time": {
                "type": "string",
                "description": "Preferred return flight time (optional)"
            },
            "phone": {
                "type": "string",
                "description": "Phone number (optional)"
            }
        },
        "required": ["passenger_name", "email", "origin_city", "destination_city", 
                    "departure_date", "departure_time", "flight_class", "num_passengers"],
        "additionalProperties": False
    }
}
```

**Key Points:**
- **Required vs optional:** Separate required parameters from optional ones
- **Clear descriptions:** LLM uses descriptions to understand what to ask user
- **Type hints:** Use proper JSON schema types (string, integer, etc.)
- **Validation in function:** Tool function validates all inputs before processing

**Pattern:** Comprehensive tool definitions guide LLM to collect all required information

---

### Quote → Confirm Workflow Pattern

**Problem:** Single-step bookings can lead to accidental transactions

**Solution:** Separate quote generation from booking confirmation

**Quote Function:**
```python
def get_flight_quote(...) -> str:
    """Generate quote with price breakdown, save to database, return quote_id."""
    
    # Validate all inputs
    # Calculate pricing
    base_fare_total = base_fare_per_person * num_passengers
    subtotal = base_fare_total * class_multiplier
    taxes = subtotal * TAX_RATE
    total_price = subtotal + taxes
    
    # Generate quote ID
    quote_id = f"QT-{uuid.uuid4().hex[:8].upper()}"
    
    # Save quote to database (status='pending')
    # Return formatted quote with price breakdown and quote_id
    return quote_with_price_breakdown
```

**Confirm Function:**
```python
def confirm_booking(quote_id: str) -> str:
    """Confirm booking from quote, create booking record, return booking_id."""
    
    # Lookup quote by ID
    # Check quote status (must be 'pending')
    # Create booking record
    booking_id = f"FLT-{uuid.uuid4().hex[:8].upper()}"
    
    # Update quote status to 'confirmed'
    # Generate email confirmation
    return confirmation_with_booking_id
```

**Database Schema:**
```sql
-- Quotes table (pending transactions)
CREATE TABLE quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id TEXT UNIQUE NOT NULL,
    passenger_name TEXT NOT NULL,
    email TEXT NOT NULL,
    -- ... all flight details ...
    total_price REAL NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending, confirmed, expired
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME
)

-- Bookings table (confirmed transactions)
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id TEXT UNIQUE NOT NULL,
    quote_id TEXT NOT NULL,  -- Reference to original quote
    -- ... all flight details ...
    status TEXT DEFAULT 'confirmed',  -- confirmed, cancelled
    confirmation_sent_at DATETIME
)
```

**Pattern:** Quote → Confirm = two database tables (quotes, bookings) + status tracking

---

### Normalization Functions

**Problem:** User input varies (e.g., "morning", "6 AM", "06:00")

**Solution:** Normalize user input to standard values

**Time Normalization:**
```python
def normalize_flight_time(time_str):
    """Convert various time descriptions to our standard time slots."""
    time_lower = time_str.lower().strip()
    
    # Direct matches
    if time_lower in FLIGHT_TIMES:
        return time_lower
    
    # Fuzzy matching
    if "6" in time_lower and ("am" in time_lower or "morning" in time_lower):
        return "morning"
    elif "10" in time_lower or "mid" in time_lower:
        return "mid-morning"
    elif "2" in time_lower or "14" in time_lower or "afternoon" in time_lower:
        return "afternoon"
    elif "6" in time_lower and ("pm" in time_lower or "evening" in time_lower):
        return "evening"
    elif "9" in time_lower or "21" in time_lower or "night" in time_lower:
        return "night"
    
    # Default
    return "morning"
```

**Class Normalization:**
```python
def normalize_class(class_str):
    """Convert various class descriptions to our standard classes."""
    class_lower = class_str.lower().strip()
    
    if "first" in class_lower:
        return "first"
    elif "business" in class_lower:
        return "business"
    else:
        return "economy"
```

**Pattern:** Normalization functions convert user input to standard internal values

---

### Email Confirmation Simulation

**Problem:** Need to show email confirmations without actual email sending

**Solution:** Generate formatted email content for display

**Email Generator:**
```python
def generate_email_confirmation(booking):
    """Generate a simulated email confirmation (what would be sent)."""
    return f"""
════════════════════════════════════════════════════════════════
                    ✈️ FlightAI BOOKING CONFIRMATION
════════════════════════════════════════════════════════════════

Dear {booking['passenger_name']},

Your flight has been successfully booked!

📋 BOOKING REFERENCE: {booking['booking_id']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLIGHT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Route:      {booking['origin_city']} → {booking['destination_city']}
  Date:       {booking['departure_date']}
  Time:       {booking['departure_time']}
  Class:      {booking['flight_class'].title()}
  Passengers: {booking['num_passengers']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRICE BREAKDOWN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Base Fare:  ${booking['base_fare']:.2f}
  Class:      ×{booking['class_multiplier']}
  Taxes:      ${booking['taxes']:.2f}
  TOTAL:      ${booking['total_price']:.2f}

This confirmation has been sent to: {booking['email']}
════════════════════════════════════════════════════════════════
"""
```

**Pattern:** Simulated email = formatted string showing what real email would contain

---

### Enhanced Tool Calling Patterns

**Two-Step Transaction Pattern:**
```python
# Step 1: Quote (no commitment)
quote_function = {
    "name": "get_flight_quote",
    "description": "Generate a quote. Only call when you have ALL information.",
    # ... parameters ...
}

# Step 2: Confirm (finalize)
confirm_function = {
    "name": "confirm_booking",
    "description": "Confirm booking from quote. Only call when customer confirms.",
    "parameters": {
        "type": "object",
        "properties": {
            "quote_id": {
                "type": "string",
                "description": "The quote ID to confirm (format: QT-XXXXXXXX)"
            }
        },
        "required": ["quote_id"],
        "additionalProperties": False
    }
}
```

**Validation in Tool Functions:**
```python
def get_flight_quote(...):
    # Validate all required fields
    if not all([passenger_name, email, origin_city, destination_city, ...]):
        return "ERROR: Missing required information."
    
    # Validate email format
    if "@" not in email or "." not in email:
        return f"ERROR: Invalid email format: {email}"
    
    # Validate origin != destination
    if origin_city.lower() == destination_city.lower():
        return "ERROR: Origin and destination cannot be the same."
    
    # Validate date
    valid, result = validate_date(departure_date)
    if not valid:
        return f"ERROR: {result}"
    
    # ... proceed with quote generation ...
```

**Pattern:** Comprehensive validation in tool functions ensures data integrity

---

## Questions to Explore Further

- [ ] How to implement automatic model selection based on task?
- [ ] What's the optimal prompt caching strategy for different use cases?
- [ ] How to handle rate limits across multiple providers?
- [ ] What's the best way to manage conversation history for very long conversations?
- [ ] How to implement fallback strategies (local → cloud)?
- [ ] What are the best practices for multi-agent systems?
- [ ] How to implement conversation memory/context window management?
- [ ] What's the best pattern for multi-turn conversation evaluation?
- [ ] How to handle conversation state persistence across sessions?
- [ ] How to implement actual email sending (SendGrid, AWS SES)?
- [ ] What's the best pattern for payment processing with tool calling?
- [ ] How to handle multi-modal responses in streaming?

## References

- Course material: Week 2 Day 1-5 notebooks
- OpenAI API docs: https://platform.openai.com/docs
- Anthropic API docs: https://docs.anthropic.com
- LiteLLM docs: https://docs.litellm.ai
- LangChain docs: https://python.langchain.com
- OpenRouter docs: https://openrouter.ai/docs
- Ollama docs: https://ollama.ai/docs
- Gradio docs: https://www.gradio.app/guides/quickstart
- DALL-E API docs: https://platform.openai.com/docs/guides/images
- TTS API docs: https://platform.openai.com/docs/guides/text-to-speech
- dateutil docs: https://dateutil.readthedocs.io/


