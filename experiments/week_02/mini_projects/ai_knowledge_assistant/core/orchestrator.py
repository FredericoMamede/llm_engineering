"""
Orchestrator: input → intent → prompt profile → tools → LLM response (streamed).

Wires together prompt profiles, model registry, tool calling, and session store.
Handles errors and fallback gracefully.
"""

from typing import Any, Dict, Generator, List, Optional

from core.prompt_profiles import PromptProfiles
from core.model_registry import ModelRegistry
from core.session_store import SessionStore
from tools import TOOLS, handle_tool_calls


class Orchestrator:
    """Main coordination layer for the assistant."""

    def __init__(self) -> None:
        self.prompt_profiles = PromptProfiles()
        self.model_registry = ModelRegistry()
        self.session_store = SessionStore()

    def load_prompts(self, base_dir: str) -> None:
        self.prompt_profiles.load(base_dir)

    def _prepare_messages(
        self,
        user_text: str,
        profile_name: str,
        history: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """Build messages array with system prompt, history, and user message."""
        system_prompt = self.prompt_profiles.build_system_prompt(profile_name)
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        messages.extend(history or [])
        messages.append({"role": "user", "content": user_text})
        return messages

    def chat_stream(
        self,
        user_text: str,
        history: List[Dict[str, str]],
        model_name: str,
        profile_name: str,
        session_id: Optional[str] = None,
    ) -> Generator[str, None, None]:
        """
        Stream the assistant response, with tool calling for capable models.
        
        Flow:
        1. Build messages with system prompt from profile
        2. If model supports tools: non-streaming call to check for tool use
        3. If tools called: execute, add results, then stream continuation
        4. If no tools: stream response directly
        
        Handles errors gracefully with fallback to other models.
        """
        messages = self._prepare_messages(user_text, profile_name, history)

        # Persist user message
        if session_id and self.session_store.enabled:
            self.session_store.save_message(session_id, "user", user_text)

        # Check if model supports tools
        supports_tools = self.model_registry.supports_tools(model_name)

        if supports_tools:
            # Step 1: Non-streaming call to detect tool use (with fallback)
            result = self.model_registry.chat_with_tools(
                model_name, messages, TOOLS, allow_fallback=True
            )
            
            # Handle errors
            if not result.success:
                yield f"⚠️ {result.error}"
                if result.error_type == "auth":
                    yield "\n\n💡 Tip: Check your API key in the .env file."
                return

            # Notify if fallback was used
            if result.fallback_used:
                yield f"ℹ️ *Switched to {result.model_used} due to an issue with the original model.*\n\n"

            response = result.response
            choice = response.choices[0]
            
            # Step 2: Check if tools were called
            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                # Execute tools
                tool_results = handle_tool_calls(choice.message.tool_calls)
                
                # Add assistant message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": choice.message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in choice.message.tool_calls
                    ],
                })
                
                # Add tool results
                messages.extend(tool_results)
                
                # Step 3: Stream continuation after tools (use the model that worked)
                effective_model = result.model_used or model_name
                accumulated = ""
                for chunk in self.model_registry.stream_chat(effective_model, messages):
                    # Handle error markers from stream_chat
                    if chunk.startswith("[ERROR]"):
                        yield f"⚠️ {chunk[7:].strip()}"
                        return
                    if chunk.startswith("[FALLBACK]"):
                        yield f"ℹ️ {chunk[10:].strip()}"
                        continue
                    accumulated += chunk
                    yield chunk
                
                if session_id and self.session_store.enabled:
                    self.session_store.save_message(session_id, "assistant", accumulated)
                return
            
            # No tools called; yield the response content
            content = choice.message.content or ""
            yield content
            
            if session_id and self.session_store.enabled:
                self.session_store.save_message(session_id, "assistant", content)
            return

        # Model doesn't support tools: pure streaming (with error handling)
        accumulated = ""
        for chunk in self.model_registry.stream_chat(model_name, messages):
            # Handle error/fallback markers
            if chunk.startswith("[ERROR]"):
                yield f"⚠️ {chunk[7:].strip()}"
                return
            if chunk.startswith("[FALLBACK]"):
                yield f"ℹ️ {chunk[10:].strip()}"
                continue
            accumulated += chunk
            yield chunk

        if session_id and self.session_store.enabled and accumulated:
            self.session_store.save_message(session_id, "assistant", accumulated)
