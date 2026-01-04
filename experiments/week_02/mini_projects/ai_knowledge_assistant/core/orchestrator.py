"""
Orchestrator: input → intent → prompt profile → tools → LLM response (streamed).

Wires together prompt profiles, model registry, tool calling, and session store.
Handles errors and fallback gracefully.
"""

import time
from typing import Any, Dict, Generator, List, Optional

from core.context_manager import get_context_manager
from core.logger import get_logger, log_performance
from core.prompt_injection import prepare_safe_user_input
from core.prompt_profiles import PromptProfiles
from core.model_registry import ModelRegistry
from core.rate_limiter import get_rate_limiter
from core.session_store import SessionStore
from tools import TOOLS, handle_tool_calls

logger = get_logger(__name__)


class Orchestrator:
    """Main coordination layer for the assistant."""

    def __init__(self) -> None:
        self.prompt_profiles = PromptProfiles()
        self.model_registry = ModelRegistry()
        self.session_store = SessionStore()
        self.rate_limiter = get_rate_limiter()
        self.context_manager = get_context_manager()

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
        start_time = time.time()
        
        # Rate limiting check
        if session_id:
            allowed, error_msg = self.rate_limiter.check_request(session_id)
            if not allowed:
                logger.warning(
                    "Rate limit exceeded",
                    extra={"session_id": session_id, "model": model_name},
                )
                yield f"⚠️ {error_msg}"
                return
        
        # Prompt injection protection
        safe_user_text = prepare_safe_user_input(user_text, sanitize=True)
        
        logger.info(
            "Starting chat stream",
            extra={
                "model": model_name,
                "profile": profile_name,
                "session_id": session_id,
                "has_history": len(history) > 0,
                "input_length": len(user_text),
            },
        )
        
        # Build messages (will be truncated if needed)
        messages = self._prepare_messages(safe_user_text, profile_name, history)
        
        # Context window management (system prompt is already in messages[0])
        needs_truncation, token_count = self.context_manager.should_truncate(messages, system_prompt=None)
        
        if needs_truncation:
            logger.warning(
                "Context window exceeded, truncating",
                extra={
                    "token_count": token_count,
                    "max_tokens": self.context_manager.max_tokens,
                    "message_count": len(messages),
                },
            )
            # Extract system prompt before truncation (it's already in messages)
            system_prompt = messages[0]["content"] if messages and messages[0].get("role") == "system" else None
            messages = self.context_manager.truncate_messages(messages, system_prompt=system_prompt)
        
        # Log context info
        context_info = self.context_manager.get_context_info(messages, system_prompt=None)
        logger.debug("Context window info", extra=context_info)

        # Persist user message
        if session_id and self.session_store.enabled:
            self.session_store.save_message(session_id, "user", user_text)

        # Check if model supports tools
        supports_tools = self.model_registry.supports_tools(model_name)

        if supports_tools:
            # Non-streaming call to detect tool use (with fallback)
            result = self.model_registry.chat_with_tools(
                model_name, messages, TOOLS, allow_fallback=True
            )
            
            # Handle errors
            if not result.success:
                logger.error(
                    "Chat with tools failed",
                    extra={
                        "model": model_name,
                        "error": result.error,
                        "error_type": result.error_type,
                        "fallback_used": result.fallback_used,
                    },
                )
                yield f"⚠️ {result.error}"
                if result.error_type == "auth":
                    yield "\n\n💡 Tip: Check your API key in the .env file."
                return

            # Notify if fallback was used
            if result.fallback_used:
                yield f"ℹ️ *Switched to {result.model_used} due to an issue with the original model.*\n\n"

            response = result.response
            choice = response.choices[0]
            
            # Check if tools were called
            if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
                # Execute tools
                tool_results = handle_tool_calls(choice.message.tool_calls)
                
                # Assistant message with tool calls
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
                
                # Stream continuation after tools (use the model that worked)
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
                
                # Record usage for rate limiting
                if session_id and accumulated:
                    estimated_tokens = self.context_manager.count_tokens(accumulated)
                    self.rate_limiter.record_usage(session_id, tokens=estimated_tokens)
                
                return
            
            # No tools called; yield the response content
            content = choice.message.content or ""
            yield content
            
            if session_id and self.session_store.enabled:
                self.session_store.save_message(session_id, "assistant", content)
            
            # Record usage for rate limiting
            if session_id and content:
                estimated_tokens = self.context_manager.count_tokens(content)
                self.rate_limiter.record_usage(session_id, tokens=estimated_tokens)
            
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
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Record usage for rate limiting (estimate tokens)
        if session_id and accumulated:
            estimated_tokens = self.context_manager.count_tokens(accumulated)
            self.rate_limiter.record_usage(session_id, tokens=estimated_tokens)
        
        log_performance(
            logger,
            "chat_stream",
            duration_ms,
            model=model_name,
            profile=profile_name,
            response_length=len(accumulated),
            tokens_used=estimated_tokens if session_id and accumulated else 0,
        )
