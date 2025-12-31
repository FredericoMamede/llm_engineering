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
