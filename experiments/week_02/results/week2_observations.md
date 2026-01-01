# Week 2 Observations

## Day 1: Frontier Model APIs

### Multi-Provider Setup

**Finding:** OpenAI-compatible endpoints enable easy model switching
- Many providers (Gemini, DeepSeek, Groq, Grok, Ollama) support OpenAI API format
- Can use same client library with different `base_url`
- Reduces code complexity significantly

**Tradeoff:** Unified interface vs native libraries
- Unified: Simpler code, but limited to common features
- Native: Full feature access, but more complexity

### Prompt Caching

**Finding:** Significant cost savings (70%+ on repeated calls)
- Real example: Caching 52K tokens of Hamlet saved ~73% on second call
- Structure matters: Static content first, variable content last
- Provider differences in implementation

**Provider Comparison:**
- OpenAI: 4x cheaper for cached content
- Anthropic: 25% more to prime, 10x cheaper to reuse
- Gemini: Automatic caching for repeated prefixes

### Multi-Model Conversations

**Finding:** Two approaches - simple is better for most cases
- **Simple approach:** Single conversation list + narrative prompt (easier!)
- **Structured approach:** Complex message building with roles (more control)
- System prompt defines personality and mentions other participants
- Full conversation history needed for context

**Pattern:** 
- Simple: One list, append responses, reuse template
- Structured: Build history incrementally with role-based messages
- Both work, but simple approach is more maintainable

### Model Comparison

**Finding:** Different models excel at different tasks
- GPT: Strong coding, general capability
- Claude: Safety-focused, concise, humorous
- Gemini: Multimodal, strong reasoning
- DeepSeek: Strong reasoning, cost-effective
- Local (Ollama): Free, private, but lower quality

**Strategy:** Test multiple models for production use cases

## Day 2: Gradio UI Development

### Gradio Basics

**Finding:** Gradio makes UI creation incredibly simple
- Basic interface: `gr.Interface(fn=function, inputs=[...], outputs=[...])`
- Component types: Textbox, Dropdown, Markdown for different needs
- Sharing: `share=True` for public links, `inbrowser=True` for auto-open
- Authentication: Easy password protection

**Tradeoff:** Fast prototyping vs customization
- Gradio: Fast, simple, but limited customization
- Custom web: Full control, but much more complex

### Streaming with Generators

**Finding:** Generator pattern enables real-time streaming in UI
- Must use `yield` keyword, not `return`
- Gradio automatically detects generator functions
- Better UX: users see responses as they generate

**Pattern:**
- Accumulate response in loop
- Yield after each chunk
- UI updates incrementally

### Class-Based Multi-Model Design

**Finding:** Model registry pattern simplifies multi-model UIs
- Single class encapsulates all model logic
- Dictionary maps model names to (client, model_name) tuples
- Unified method works for all models
- No code duplication, easy to extend

**Benefits:**
- Cleaner code than separate functions per model
- Self-documenting (registry shows available models)
- Automatic detection (only includes available models)
- Easy to add new models (just update dictionary)

**Pattern:** Class with model registry > separate functions per model

## Day 3: Conversational AI with ChatInterface

### Gradio ChatInterface

**Finding:** ChatInterface is purpose-built for conversations, much easier than managing state manually
- **Specialized component:** `gr.ChatInterface(fn=chat, type="messages")` handles conversation UI
- **Automatic history:** Gradio manages conversation history, provides it to callback function
- **Callback signature:** `chat(message, history)` - simple and clean
- **History format:** Gradio provides history as list of `{"role": "...", "content": "..."}` dicts

**Key Differences:**
- **ChatInterface:** Purpose-built for conversations, manages history automatically
- **Interface:** General-purpose, you manage state yourself
- **Pattern:** Use ChatInterface for conversations, Interface for general I/O

**Tradeoff:** 
- ChatInterface: Easier for conversations, but less flexible
- Interface: More flexible, but you manage conversation state yourself

### System Messages for Context and Behavior

**Finding:** System messages are powerful for controlling chatbot personality and business logic
- **Placement:** Always first in messages array: `[system] + history + [user]`
- **One-shot prompting:** Include examples in system message to guide behavior
- **Business context:** Perfect for business rules, product info, constraints, tone
- **Persistence:** System message persists across entire conversation

**Pattern:**
- System message = personality + context + examples + constraints
- User/Assistant messages = actual conversation history
- System message defines "who" the chatbot is, history defines "what" was said

**Business Applications:**
- Product information (prices, availability, features)
- Business rules (what to recommend, what to avoid)
- Tone and personality (friendly, professional, encouraging)
- Constraints (what not to sell, what to emphasize)

### Streaming in ChatInterface

**Finding:** Same generator pattern works seamlessly in ChatInterface
- **Generator pattern:** Use `yield` not `return` - same as regular Interface
- **Auto-detection:** Gradio automatically detects generator functions
- **Better UX:** Users see responses as they generate, feels more natural in conversations

**Pattern:**
- Accumulate response in loop
- Yield after each chunk
- UI updates incrementally

### Dynamic System Message Modification

**Finding:** Conditionally modifying system message enables adaptive behavior
- **Base + extension:** Start with base system message, extend conditionally
- **Keyword detection:** Check user message for keywords, append context if needed
- **Edge cases:** Handle special cases dynamically without cluttering base message

**Pattern:**
```python
relevant_system_message = system_message  # Base
if 'keyword' in message.lower():
    relevant_system_message += " Additional context..."  # Extension
```

**Use Cases:**
- Keyword detection (add context when specific topics mentioned)
- Edge cases (handle special cases dynamically)
- Contextual rules (add rules based on conversation flow)
- Adaptive behavior (change behavior based on user needs)

**Tradeoff:**
- **Static system message:** Simpler, but less flexible
- **Dynamic modification:** More flexible, but more complex logic