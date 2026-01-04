"""
Model registry: config-driven, multi-provider support.

Supports any OpenAI-compatible API. Add models in models.yaml.
All models with API keys are validated at startup.
Invalid models are tracked and shown as disabled in UI.
"""

import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

import requests
import yaml
from openai import OpenAI, AuthenticationError, APIConnectionError, RateLimitError

from core.logger import get_logger

logger = get_logger(__name__)


class ModelStatus(Enum):
    """Model availability status."""
    READY = "ready"              # Validated and working
    INVALID_KEY = "invalid_key"  # API key is invalid
    RATE_LIMITED = "rate_limited"  # Temporarily rate limited (key is valid)
    CONNECTION_ERROR = "connection_error"  # Cannot reach API
    MODEL_NOT_FOUND = "model_not_found"  # Model doesn't exist on provider
    NOT_CONFIGURED = "not_configured"  # No API key in .env
    LOCAL_OFFLINE = "local_offline"  # Local service not running
    UNKNOWN_ERROR = "unknown_error"  # Other error


@dataclass
class ModelEntry:
    """A registered model with its client and metadata."""
    name: str
    provider: str
    model: str
    client: Optional[OpenAI]
    supports_tools: bool = False
    local: bool = False
    status: ModelStatus = ModelStatus.NOT_CONFIGURED
    status_message: str = ""
    
    @property
    def is_available(self) -> bool:
        """Model is ready to use."""
        return self.status == ModelStatus.READY
    
    @property
    def is_temporarily_unavailable(self) -> bool:
        """Model might work later (rate limit, connection issue)."""
        return self.status in (ModelStatus.RATE_LIMITED, ModelStatus.CONNECTION_ERROR)
    
    def __repr__(self) -> str:
        return f"ModelEntry({self.name}, status={self.status.value}, available={self.is_available})"


@dataclass
class ChatResult:
    """Result of a chat operation with error info."""
    success: bool
    content: Optional[str] = None
    response: Optional[Any] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    model_used: Optional[str] = None
    fallback_used: bool = False


class ModelRegistry:
    """
    Config-driven model registry with mandatory validation.
    
    Features:
    - Loads model definitions from models.yaml
    - Validates ALL models with API keys at startup
    - Tracks status of every model (ready/invalid/offline)
    - Provides UI-friendly status info for disabled display
    """

    def __init__(self, config_path: Optional[str] = None) -> None:
        self.models: Dict[str, ModelEntry] = {}
        self._fallback_order: List[str] = []
        
        if config_path is None:
            config_path = str(Path(__file__).parent / "models.yaml")
        
        self._load_config(config_path)
        self._build_fallback_order()
        
        # Log startup status
        self._log_status()

    def _load_config(self, config_path: str) -> None:
        """Load models from YAML config and validate all with keys."""
        if not Path(config_path).exists():
            logger.warning(f"Config not found at {config_path}, using defaults.")
            self._register_defaults()
            return

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        models_config = config.get("models", {})
        
        logger.info("Validating models...")
        for name, spec in models_config.items():
            self._register_and_validate(name, spec)
        
        ready_count = sum(1 for m in self.models.values() if m.is_available)
        total_configured = sum(1 for m in self.models.values() if m.status != ModelStatus.NOT_CONFIGURED)
        
        if ready_count == 0:
            logger.warning("No models available. Check your API keys in .env")
        else:
            logger.info(f"{ready_count}/{total_configured} models ready")

    def _register_and_validate(self, name: str, spec: Dict[str, Any]) -> None:
        """Register a model and validate its API key."""
        api_key_env = spec.get("api_key_env")
        base_url = spec.get("base_url")
        is_local = spec.get("local", False)
        
        # Check API key availability
        if api_key_env:
            api_key = os.getenv(api_key_env)
            if not api_key:
                # No key configured - register as NOT_CONFIGURED
                self.models[name] = ModelEntry(
                    name=name,
                    provider=spec.get("provider", "unknown"),
                    model=spec.get("model", name),
                    client=None,
                    supports_tools=spec.get("supports_tools", False),
                    local=is_local,
                    status=ModelStatus.NOT_CONFIGURED,
                    status_message=f"Set {api_key_env} in .env to enable",
                )
                return
        else:
            api_key = "not-needed"
        
        # Check local service availability
        if is_local and base_url:
            if not self._check_local_service(base_url):
                self.models[name] = ModelEntry(
                    name=name,
                    provider=spec.get("provider", "unknown"),
                    model=spec.get("model", name),
                    client=None,
                    supports_tools=spec.get("supports_tools", False),
                    local=is_local,
                    status=ModelStatus.LOCAL_OFFLINE,
                    status_message="Local service not running. Start with: ollama serve",
                )
                return
        
        # Build client
        client_kwargs: Dict[str, Any] = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        extra_headers = spec.get("extra_headers")
        if extra_headers:
            client_kwargs["default_headers"] = extra_headers
        
        try:
            client = OpenAI(**client_kwargs)
            
            entry = ModelEntry(
                name=name,
                provider=spec.get("provider", "unknown"),
                model=spec.get("model", name),
                client=client,
                supports_tools=spec.get("supports_tools", False),
                local=is_local,
                status=ModelStatus.UNKNOWN_ERROR,  # Will be updated by validation
                status_message="Validating...",
            )
            
            # Validate the key with a real API call
            self._validate_model(entry)
            self.models[name] = entry
            
        except Exception as e:
            self.models[name] = ModelEntry(
                name=name,
                provider=spec.get("provider", "unknown"),
                model=spec.get("model", name),
                client=None,
                supports_tools=spec.get("supports_tools", False),
                local=is_local,
                status=ModelStatus.UNKNOWN_ERROR,
                status_message=str(e),
            )

    def _validate_model(self, entry: ModelEntry) -> None:
        """Validate a model with a minimal API call. Updates entry status in place."""
        if entry.client is None:
            entry.status = ModelStatus.UNKNOWN_ERROR
            entry.status_message = "No client available"
            return
        
        try:
            # Minimal validation call
            entry.client.chat.completions.create(
                model=entry.model,
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=1,
            )
            entry.status = ModelStatus.READY
            entry.status_message = "Validated and ready"
            logger.info(f"{entry.name}: Ready", extra={"model": entry.name, "status": "ready"})
            
        except AuthenticationError as e:
            entry.status = ModelStatus.INVALID_KEY
            entry.status_message = "Invalid API key"
            entry.client = None  # Clear client for security
            logger.warning(f"{entry.name}: Invalid API key", extra={"model": entry.name, "status": "invalid_key"})
            
        except RateLimitError as e:
            # Rate limited means key IS valid, just can't use right now
            entry.status = ModelStatus.RATE_LIMITED
            entry.status_message = "Rate limited - try again later"
            logger.warning(f"{entry.name}: Rate limited (key is valid)", extra={"model": entry.name, "status": "rate_limited"})
            
        except APIConnectionError as e:
            entry.status = ModelStatus.CONNECTION_ERROR
            entry.status_message = "Cannot connect to API"
            logger.error(f"{entry.name}: Connection error", extra={"model": entry.name, "status": "connection_error"})
            
        except Exception as e:
            error_str = str(e).lower()
            
            # Check for model not found errors
            if "model" in error_str and ("not found" in error_str or "does not exist" in error_str):
                entry.status = ModelStatus.MODEL_NOT_FOUND
                entry.status_message = f"Model '{entry.model}' not available"
                logger.warning(f"{entry.name}: Model not found", extra={"model": entry.name, "status": "model_not_found"})
            
            # Check for auth errors that might not be AuthenticationError
            elif "401" in error_str or "unauthorized" in error_str or "invalid" in error_str:
                entry.status = ModelStatus.INVALID_KEY
                entry.status_message = "Invalid API key"
                entry.client = None
                logger.warning(f"{entry.name}: Invalid API key", extra={"model": entry.name, "status": "invalid_key"})
            
            # Check for rate limit errors
            elif "429" in error_str or "rate" in error_str or "quota" in error_str:
                entry.status = ModelStatus.RATE_LIMITED
                entry.status_message = "Rate limited - try again later"
                logger.warning(f"{entry.name}: Rate limited (key is valid)", extra={"model": entry.name, "status": "rate_limited"})
            
            else:
                entry.status = ModelStatus.UNKNOWN_ERROR
                entry.status_message = str(e)[:100]  # Truncate long errors
                logger.error(f"{entry.name}: {entry.status_message}", extra={"model": entry.name, "status": "unknown_error", "error": str(e)[:200]})

    def _check_local_service(self, base_url: str, timeout: int = 2) -> bool:
        """Check if a local service is running."""
        try:
            check_url = base_url.replace("/v1", "")
            requests.get(check_url, timeout=timeout)
            return True
        except Exception:
            return False

    def _build_fallback_order(self) -> None:
        """Build priority order for fallback (only ready models)."""
        provider_priority = {"openai": 0, "anthropic": 1, "deepseek": 2, "groq": 3, "ollama": 10}
        
        ready_models = [n for n, m in self.models.items() if m.is_available]
        self._fallback_order = sorted(
            ready_models,
            key=lambda n: provider_priority.get(self.models[n].provider, 5)
        )

    def _register_defaults(self) -> None:
        """Fallback: register OpenAI if available."""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            client = OpenAI(api_key=api_key)
            entry = ModelEntry(
                name="GPT",
                provider="openai",
                model="gpt-4o-mini",
                client=client,
                supports_tools=True,
            )
            self._validate_model(entry)
            self.models["GPT"] = entry

    def _log_status(self) -> None:
        """Log status summary at startup."""
        logger.info("Model Registry Status")
        for name, entry in self.models.items():
            log_level = {
                ModelStatus.READY: logging.INFO,
                ModelStatus.RATE_LIMITED: logging.WARNING,
                ModelStatus.CONNECTION_ERROR: logging.WARNING,
                ModelStatus.INVALID_KEY: logging.WARNING,
                ModelStatus.MODEL_NOT_FOUND: logging.WARNING,
                ModelStatus.LOCAL_OFFLINE: logging.WARNING,
                ModelStatus.NOT_CONFIGURED: logging.DEBUG,
                ModelStatus.UNKNOWN_ERROR: logging.ERROR,
            }.get(entry.status, logging.INFO)
            
            logger.log(
                log_level,
                f"{name}: {entry.status_message}",
                extra={"model": name, "status": entry.status.value, "status_message": entry.status_message},
            )

    def _get_fallback(self, exclude: str) -> Optional[str]:
        """Get the next available model for fallback."""
        for name in self._fallback_order:
            if name != exclude:
                return name
        return None

    def _classify_error(self, error: Exception) -> Tuple[str, str]:
        """Classify an error and return (error_type, message)."""
        error_str = str(error).lower()
        
        if isinstance(error, AuthenticationError) or "401" in error_str:
            return "auth", "Invalid API key"
        elif isinstance(error, RateLimitError) or "429" in error_str:
            return "rate_limit", "Rate limit exceeded"
        elif isinstance(error, APIConnectionError):
            return "connection", "Cannot connect to API"
        else:
            return "unknown", str(error)

    # === Public API ===

    def get_available(self) -> List[str]:
        """Return list of READY model names only."""
        return [n for n, m in self.models.items() if m.is_available]

    def get_all_configured(self) -> List[str]:
        """Return all models that have API keys configured (for UI display)."""
        return [n for n, m in self.models.items() if m.status != ModelStatus.NOT_CONFIGURED]

    def get(self, name: str) -> Optional[ModelEntry]:
        """Get a model entry by name."""
        return self.models.get(name)

    def is_available(self, name: str) -> bool:
        """Check if a model is ready to use."""
        entry = self.get(name)
        return entry.is_available if entry else False

    def supports_tools(self, name: str) -> bool:
        """Check if a model supports tool calling."""
        entry = self.get(name)
        return entry.supports_tools if entry and entry.is_available else False

    def get_status(self, name: str) -> Tuple[ModelStatus, str]:
        """Get status and message for a model."""
        entry = self.get(name)
        if entry:
            return entry.status, entry.status_message
        return ModelStatus.NOT_CONFIGURED, "Model not found"

    def get_ui_choices(self) -> List[Tuple[str, str]]:
        """
        Return choices for Gradio dropdown with status indicators.
        
        Format: [(display_label, value), ...]
        Ready models: "GPT-4o-mini ✓"
        Unavailable: "DeepSeek ✗ (Invalid API key)"
        """
        choices = []
        for name, entry in self.models.items():
            # Skip unconfigured models
            if entry.status == ModelStatus.NOT_CONFIGURED:
                continue
            
            if entry.is_available:
                label = f"{name} ✓"
            elif entry.is_temporarily_unavailable:
                label = f"{name} ⚠ ({entry.status_message})"
            else:
                label = f"{name} ✗ ({entry.status_message})"
            
            choices.append((label, name))
        
        # Sort: available first, then by name
        choices.sort(key=lambda x: (0 if "✓" in x[0] else 1, x[1]))
        return choices

    def validate_selection(self, name: str) -> Tuple[bool, str]:
        """
        Validate if a model can be used. Returns (ok, message).
        
        Use this when user selects a model to show appropriate warning.
        """
        entry = self.get(name)
        if not entry:
            return False, f"Model '{name}' not found"
        
        if entry.is_available:
            return True, "Ready"
        
        if entry.status == ModelStatus.INVALID_KEY:
            return False, f"❌ Invalid API key for {name}. Please check your .env file."
        elif entry.status == ModelStatus.RATE_LIMITED:
            return False, f"⚠️ {name} is rate limited. Try again later or select another model."
        elif entry.status == ModelStatus.CONNECTION_ERROR:
            return False, f"⚠️ Cannot connect to {name}. Check your network."
        elif entry.status == ModelStatus.MODEL_NOT_FOUND:
            return False, f"❌ Model '{entry.model}' not available from {entry.provider}."
        elif entry.status == ModelStatus.LOCAL_OFFLINE:
            return False, f"⚠️ {name} is offline. Start the local service first."
        else:
            return False, f"❌ {name} unavailable: {entry.status_message}"

    def revalidate(self, name: str) -> bool:
        """Re-validate a specific model (e.g., after user fixes their key)."""
        entry = self.get(name)
        if not entry or entry.client is None:
            return False
        
        self._validate_model(entry)
        self._build_fallback_order()
        return entry.is_available

    def revalidate_all(self) -> Dict[str, bool]:
        """Re-validate all models. Returns {name: is_available}."""
        results = {}
        for name, entry in self.models.items():
            if entry.client is not None:
                self._validate_model(entry)
            results[name] = entry.is_available
        self._build_fallback_order()
        return results

    def chat_with_tools(
        self,
        model_name: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        allow_fallback: bool = True,
    ) -> ChatResult:
        """Non-streaming chat with optional tool calling and fallback."""
        entry = self.get(model_name)
        
        # Check if model is available
        if not entry or not entry.is_available:
            ok, msg = self.validate_selection(model_name)
            if not ok:
                # Try fallback
                if allow_fallback:
                    fallback = self._get_fallback(model_name)
                    if fallback:
                        result = self.chat_with_tools(fallback, messages, tools, allow_fallback=False)
                        result.fallback_used = True
                        return result
                
                return ChatResult(
                    success=False,
                    error=msg,
                    error_type="unavailable",
                    model_used=model_name,
                )

        kwargs: Dict[str, Any] = {"model": entry.model, "messages": messages}
        if tools and entry.supports_tools:
            kwargs["tools"] = tools

        try:
            # Retry logic for API calls
            from core.retry import retry_api_call
            response = retry_api_call(
                entry.client.chat.completions.create,
                max_retries=3,
                base_delay=1.0,
                **kwargs
            )
            return ChatResult(
                success=True,
                response=response,
                content=response.choices[0].message.content,
                model_used=model_name,
            )
        except Exception as e:
            error_type, error_msg = self._classify_error(e)
            
            # Try fallback
            if allow_fallback:
                fallback = self._get_fallback(model_name)
                if fallback:
                    result = self.chat_with_tools(fallback, messages, tools, allow_fallback=False)
                    result.fallback_used = True
                    return result
            
            return ChatResult(
                success=False,
                error=error_msg,
                error_type=error_type,
                model_used=model_name,
            )

    def stream_chat(
        self,
        model_name: str,
        messages: List[Dict[str, Any]],
        allow_fallback: bool = True,
    ) -> Generator[str, None, None]:
        """Stream chat completions with error handling and fallback."""
        entry = self.get(model_name)
        
        # Check if model is available
        if not entry or not entry.is_available:
            ok, msg = self.validate_selection(model_name)
            if not ok:
                if allow_fallback:
                    fallback = self._get_fallback(model_name)
                    if fallback:
                        yield f"[FALLBACK] {msg} Switching to {fallback}...\n\n"
                        yield from self.stream_chat(fallback, messages, allow_fallback=False)
                        return
                yield f"[ERROR] {msg}"
            return

        try:
            # Retry logic for streaming calls
            from core.retry import retry_api_call
            stream = retry_api_call(
                entry.client.chat.completions.create,
                max_retries=3,
                base_delay=1.0,
                model=entry.model,
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            _, error_msg = self._classify_error(e)
            
            if allow_fallback:
                fallback = self._get_fallback(model_name)
                if fallback:
                    yield f"[FALLBACK] Error with {model_name}: {error_msg}. Switching to {fallback}...\n\n"
                    yield from self.stream_chat(fallback, messages, allow_fallback=False)
                    return
            
            yield f"[ERROR] {error_msg}"

    def info(self) -> Dict[str, Dict[str, Any]]:
        """Return detailed info about all models."""
        return {
            name: {
                "provider": entry.provider,
                "model": entry.model,
                "supports_tools": entry.supports_tools,
                "local": entry.local,
                "status": entry.status.value,
                "status_message": entry.status_message,
                "available": entry.is_available,
            }
            for name, entry in self.models.items()
        }

    def status(self) -> str:
        """Return a human-readable status summary."""
        lines = ["Model Registry Status:", "=" * 50]
        for name, entry in self.models.items():
            tag = "[OK]" if entry.is_available else ("[WARN]" if entry.is_temporarily_unavailable else "[FAIL]")
            lines.append(f"  {tag} {name}: {entry.status_message}")
        lines.append("=" * 50)
        return "\n".join(lines)
