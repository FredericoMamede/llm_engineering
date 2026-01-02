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

## Day 4: Tool Calling / Function Calling

### Tool Calling Fundamentals

**Finding:** Tools enable LLMs to interact with external systems (databases, APIs, functions)
- **Tool definition:** JSON schema describing function (name, description, parameters)
- **Tool call flow:** LLM decides → returns tool_calls → execute → return result → LLM continues
- **Message types:** `assistant` (with tool_calls), `tool` (with tool_call_id), `user`, `system`
- **Tool response format:** Must include `role: "tool"`, `content: result`, `tool_call_id: id`

**Pattern:** Tools enable LLMs to interact with databases, APIs, and external systems

**Tradeoff:**
- **Manual implementation:** Full control, understand mechanics, but complex
- **SDKs (OpenAI Agent SDK):** Easier, but abstracts away understanding

### Function Registry Pattern

**Finding:** Dictionary-based registry eliminates if/elif chains and scales beautifully
- **Registry structure:** `TOOL_REGISTRY = {"tool_name": function_object}`
- **Dynamic lookup:** `func = TOOL_REGISTRY[function_name]; result = func(**arguments)`
- **Easy to extend:** Adding new tool = one line in registry + function definition
- **No if statements:** Dictionary lookup replaces conditional chains

**Benefits:**
- Scales from 2 tools to 200 tools without code changes
- Self-documenting (registry shows all available tools)
- Cleaner, more maintainable code
- Industry-standard pattern for extensible systems

**Pattern:** Function registry > if/elif chains for tool routing

**Tradeoff:**
- **Registry pattern:** Cleaner, more maintainable, but requires discipline
- **If/elif chains:** Simple for 2-3 tools, but becomes unmaintainable quickly

### SQLite for Conversation History

**Finding:** SQLite provides persistent, queryable conversation history for production apps
- **Database schema:** Store `session_id`, `role`, `content`, `tool_calls`, `timestamp`
- **Tool calls storage:** Store as JSON string for assistant messages, tool_call_id for tool messages
- **History reconstruction:** Load from DB, parse tool_calls JSON, reconstruct full conversation
- **Session management:** Use session_id to separate conversations per user/browser

**Key Points:**
- Gradio's in-memory history is ephemeral (lost on restart)
- SQLite enables querying, analysis, and persistence
- Real-world applications need database-backed history
- Tool calls must be properly stored and reconstructed

**Pattern:** SQLite for conversation history > in-memory storage for production apps

**Tradeoff:**
- **SQLite:** Persistent, queryable, production-ready, but requires database setup
- **In-memory:** Simple, fast, but ephemeral (lost on restart)

### Manual Tool Calling Implementation

**Finding:** Manual implementation teaches you what SDKs abstract away
- **Tool call detection:** Check `finish_reason == "tool_calls"` or `message.tool_calls`
- **Tool execution loop:** While tool calls exist → execute → add responses → continue conversation
- **Error handling:** JSON parsing errors, TypeError (wrong args), general exceptions
- **Tool response format:** Must match OpenAI's expected format with tool_call_id

**Complete Flow:**
1. Load conversation from database
2. Add system/user messages
3. Make API call with tools
4. Detect tool calls
5. Execute tools using registry
6. Add tool responses to conversation
7. Continue until no more tool calls
8. Save everything to database

**Pattern:** Manual implementation teaches you what SDKs abstract away

**Tradeoff:**
- **Manual:** Full understanding, but complex
- **SDK:** Easier, but less understanding of mechanics

### Streaming + Tool Calls

**Finding:** Hybrid approach needed - stream when possible, switch to non-streaming for tools
- **The challenge:** Streaming API doesn't provide complete tool call data incrementally
- **Solution:** Detect tool calls in stream → switch to non-streaming → get full tool data → execute → resume streaming
- **finish_reason tracking:** Track from stream chunks (last chunk has finish_reason)
- **Response type handling:** Stream vs ChatCompletion - need to check type before accessing attributes

**Key Implementation:**
- Try streaming first
- Detect tool calls in stream (check `chunk.choices[0].delta.tool_calls`)
- Track `finish_reason` from stream chunks
- If tool calls detected → switch to non-streaming → get full tool data
- Execute tools → add responses to conversation
- Resume streaming for final response

**Pattern:** Hybrid streaming (stream → detect tools → non-stream → execute → stream again)

**Tradeoff:**
- **Pure streaming:** Better UX, but can't handle tool calls
- **Hybrid approach:** Best of both worlds, but more complex logic

### Session Management

**Finding:** Proper session management enables multi-user conversations
- **Session ID generation:** Use `gr.Request` to get user-agent, hash it for unique ID
- **Fallback handling:** If request unavailable, generate UUID
- **Session isolation:** Each session_id gets its own conversation thread in database
- **Database filtering:** Filter queries by session_id for multi-user support

**Pattern:** Session management = unique ID per user + database filtering by session_id

**Tradeoff:**
- **Request-based:** More accurate, but requires Gradio request object
- **UUID fallback:** Always works, but new ID each time (no persistence)

### Error Handling for Tool Execution

**Finding:** Comprehensive error handling essential for production apps
- **JSON parsing errors:** Catch `JSONDecodeError`, return error message to LLM
- **Type errors:** Catch `TypeError` (wrong number/type of arguments)
- **General exceptions:** Catch all exceptions, return descriptive error
- **Error format:** Return errors as tool responses so LLM can handle them

**Error Types Handled:**
- Invalid JSON in tool arguments
- Wrong number/type of arguments
- Runtime errors in tool functions
- Unknown tools (not found in registry)

**Pattern:** Comprehensive error handling = try/except at each failure point + informative error messages

**Tradeoff:**
- **Comprehensive handling:** Robust, but more code
- **Minimal handling:** Simpler, but fails ungracefully

## Day 5: Multi-Modal AI & Enhanced Tool Calling

### Multi-Modal AI Responses

**Finding:** Combining text with image/audio generation creates richer user experiences
- **DALL-E-3:** `openai.images.generate(model="dall-e-3", prompt=..., size="1024x1024")`
- **TTS:** `openai.audio.speech.create(model="tts-1", voice="alloy", input=message)`
- **Image handling:** Base64 encoding for display in UI
- **Audio handling:** Response is streamable audio file

**Pattern:** Multi-modal = multiple API calls + proper handling of each modality

**Tradeoff:**
- **Multi-modal:** Richer UX, but more API calls and cost
- **Text-only:** Simpler, cheaper, but less engaging

### Two-Step Booking Flow (Quote → Confirm)

**Finding:** Real booking systems never complete transactions without showing price first
- **Quote step:** Show full price breakdown, save with unique quote_id
- **Confirm step:** Lookup quote, validate status, create booking, return booking_id
- **Database design:** Separate tables for quotes (pending) and bookings (confirmed)
- **Status tracking:** Track quote status (pending, confirmed, expired)

**Benefits:**
- Prevents accidental bookings
- Matches industry-standard UX
- Allows user to review before committing
- Mirrors real payment flows

**Pattern:** Quote → Confirm separates "show price" from "finalize transaction"

**Tradeoff:**
- **Two-step:** More complex, but safer and better UX
- **One-step:** Simpler, but risk of accidental bookings

### Handling LLM Training Data Cutoff

**Finding:** LLMs cannot be trusted for date handling beyond training cutoff
- **Problem:** LLM might default to dates from training data
- **Solution:** Parse and validate dates in code using `dateutil.parser`
- **Future validation:** Compare against `datetime.now()`, not LLM assumptions
- **Flexible parsing:** Handle various formats ("June 15, 2025", "2025-06-15", "next month")

**Key Insight:**
- Date validation is a **code responsibility**, not LLM responsibility
- Users need to book for dates years in the future
- Real applications must work with actual current dates

**Pattern:** Parse dates in code, validate against real time, don't trust LLM date assumptions

### Complex Tool Definitions

**Finding:** Real-world tools can have 10+ parameters with proper schema design
- **Required vs optional:** Separate required parameters from optional ones
- **Clear descriptions:** LLM uses descriptions to understand what to ask user
- **Type hints:** Use proper JSON schema types (string, integer, etc.)
- **Validation in function:** Tool function validates all inputs before processing

**Example:** Flight quote tool with 11 parameters (8 required, 3 optional)

**Pattern:** Comprehensive tool definitions guide LLM to collect all required information

### Configuration Dictionaries for Business Rules

**Finding:** Use configuration dictionaries instead of hardcoded values
- **Flight times:** Dictionary mapping time slots to display times
- **Class multipliers:** Dictionary mapping class names to price multipliers
- **Tax rates:** Single constant for easy updates

**Benefits:**
- Easy to update without code changes
- Self-documenting (dictionary shows all options)
- Consistent across functions
- Could be loaded from config file/database in production

**Pattern:** Business rules in configuration dictionaries, not scattered hardcoded values

### Normalization Functions

**Finding:** User input varies widely, need normalization to standard values
- **Time normalization:** "morning", "6 AM", "06:00" all → "morning"
- **Class normalization:** "first class", "First", "1st class" all → "first"
- **Fuzzy matching:** Handle variations user might type

**Pattern:** Normalization functions convert user input to standard internal values

### Email Confirmation Simulation

**Finding:** For demos, show what email would contain without actual sending
- **Formatted display:** ASCII art borders, clear sections, all details
- **What would be sent:** Show recipient, booking ID, flight details, price
- **Reusable template:** Same format for booking and cancellation

**Pattern:** Simulated email = formatted string showing what real email would contain

### Enhanced Booking System - Key Learnings

**Summary of Day 5 Extension:**
1. **Two-step flow:** Quote → Confirm (industry standard)
2. **Flight times:** 5 scheduled departure times
3. **Class selection:** Economy (1x), Business (2.5x), First (4x)
4. **Price breakdown:** Base × passengers × class + taxes
5. **Date handling:** Parse and validate beyond LLM training cutoff
6. **Email simulation:** Show what would be sent
7. **Multiple passengers:** Support 1-9
8. **Round trip/one-way:** Optional return date
9. **Cancellation:** Status update + simulated refund

**Why This Matters:**
- Matches real-world booking UX
- Teaches production-ready patterns
- Demonstrates complex tool orchestration
- Shows proper date/validation handling