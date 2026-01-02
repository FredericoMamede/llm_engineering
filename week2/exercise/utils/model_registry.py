# Model Registry - Unified interface for multiple LLM providers
#
# Pattern: Model registry with (client, model_name, capabilities) tuples
# Combines: Multi-model support + streaming + tool calling
# 
# Key insight: Tool calling + streaming requires a two-step flow:
# 1. Non-streaming call to detect if tools are needed
# 2. Streaming call for the final response

import os
import requests
from typing import List, Dict, Any, Generator
from openai import OpenAI
from dotenv import load_dotenv

from .prompts import create_system_prompt, EXPERTISE_LEVELS
from .tools import TOOLS, handle_tool_calls

load_dotenv(override=True)


class TechnicalAssistant:
    """
    Multi-model technical assistant with streaming and tool calling.
    
    Supports:
    - Multiple providers (GPT, Ollama) via unified interface
    - Streaming responses for better UX
    - Dynamic expertise-based system prompts
    - Tool calling for enhanced capabilities (GPT only)
    """
    
    def __init__(self):
        """Initialize model clients and build the registry."""
        # OpenAI client - always available if API key exists
        self.openai_client = OpenAI()
        
        # Ollama client - only if local server is running
        # Check availability with a quick health check
        self.ollama_available = False
        self.ollama_client = None
        try:
            requests.get("http://localhost:11434/", timeout=2)
            self.ollama_client = OpenAI(
                api_key="ollama", 
                base_url="http://localhost:11434/v1"
            )
            self.ollama_available = True
            print("Ollama detected and available")
        except Exception:
            print("Ollama not running - only OpenAI models available")
        
        # Model registry: {display_name: (client, model_name, supports_tools)}
        # Third element tracks tool support - Ollama doesn't support OpenAI-style tools
        self.models: Dict[str, tuple] = {
            "GPT": (self.openai_client, "gpt-4o-mini", True),
        }
        
        if self.ollama_available:
            self.models["Ollama"] = (self.ollama_client, "llama3.2", False)
    
    def get_available_models(self) -> List[str]:
        """Return list of available model display names for UI dropdowns."""
        return list(self.models.keys())
    
    def chat(
        self,
        message: str,
        history: List[Dict[str, str]],
        model_name: str,
        expertise_level: str = "intermediate"
    ) -> Generator[str, None, None]:
        """
        Chat with streaming, dynamic prompts, and tool calling.
        
        Flow for tool-capable models (GPT):
        1. Make non-streaming call with tools to check if LLM wants tools
        2. If tools requested: execute them, add results, then stream continuation
        3. If no tools: return the response directly
        
        Flow for non-tool models (Ollama):
        1. Stream response directly
        
        Args:
            message: User message
            history: Conversation history from Gradio
            model_name: Display name from get_available_models()
            expertise_level: "beginner", "intermediate", or "advanced"
        
        Yields:
            Accumulated response text for streaming display
        """
        if model_name not in self.models:
            yield f"Error: Model '{model_name}' not available."
            return
        
        client, model, supports_tools = self.models[model_name]
        
        # Build dynamic system prompt based on expertise
        system_prompt = create_system_prompt(expertise_level)
        
        # Convert Gradio history format to OpenAI format
        api_history = [{"role": h["role"], "content": h["content"]} for h in history]
        
        # Construct messages: system + history + current user message
        messages = [
            {"role": "system", "content": system_prompt},
        ] + api_history + [
            {"role": "user", "content": message}
        ]
        
        try:
            # === TOOL-CAPABLE MODEL FLOW ===
            if supports_tools:
                # Step 1: Non-streaming call to detect tool requests
                # Cannot stream and detect tools simultaneously
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=TOOLS
                )
                
                assistant_message = response.choices[0].message
                
                # Step 2: Check if LLM wants to use tools
                if assistant_message.tool_calls:
                    # Execute all requested tools
                    tool_responses = handle_tool_calls(assistant_message)
                    
                    # Add tool interaction to conversation
                    messages.append(assistant_message)
                    messages.extend(tool_responses)
                    
                    # Step 3: Stream the final response after tool execution
                    stream = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        stream=True
                    )
                    
                    result = ""
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content or ""
                        result += delta
                        yield result
                else:
                    # No tools needed - return response directly
                    if assistant_message.content:
                        yield assistant_message.content
                    else:
                        yield "I couldn't generate a response. Please try again."
            
            # === NON-TOOL MODEL FLOW (Ollama) ===
            else:
                # Simple streaming without tool checking
                stream = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True
                )
                
                result = ""
                for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    result += delta
                    yield result
                    
        except Exception as e:
            yield f"Error: {type(e).__name__}: {str(e)}"
    
    def chat_streaming_only(
        self,
        message: str,
        history: List[Dict[str, str]],
        model_name: str,
        expertise_level: str = "intermediate"
    ) -> Generator[str, None, None]:
        """
        Simple streaming chat without tool calling.
        
        Use this when you want pure streaming without the overhead
        of tool detection. Useful for Phase 1 demo or when tools
        aren't needed.
        """
        if model_name not in self.models:
            yield f"Error: Model '{model_name}' not available."
            return
        
        client, model, _ = self.models[model_name]
        system_prompt = create_system_prompt(expertise_level)
        api_history = [{"role": h["role"], "content": h["content"]} for h in history]
        
        messages = [
            {"role": "system", "content": system_prompt},
        ] + api_history + [
            {"role": "user", "content": message}
        ]
        
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            
            result = ""
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                result += delta
                yield result
        except Exception as e:
            yield f"Error: {type(e).__name__}: {str(e)}"
