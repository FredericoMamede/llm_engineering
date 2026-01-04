"""
Structured logging: JSON-formatted logs with rotation and levels.

Features:
- Structured JSON logging for easy parsing
- File-based logging with rotation
- Configurable log levels
- Request/response logging (with PII sanitization)
- Performance metrics logging
"""

import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, Optional

# Export access_logger and log_access for use in other modules
__all__ = [
    "get_logger",
    "log_request",
    "log_response",
    "log_error",
    "log_performance",
    "log_access",
    "access_logger",
    "error_logger",
]

from dotenv import load_dotenv

load_dotenv(override=True)

# Default configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
ENABLE_FILE_LOGGING = os.getenv("ENABLE_FILE_LOGGING", "true").lower() == "true"
LOG_DIR = Path(__file__).parent.parent / "data" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log file paths
APP_LOG_FILE = LOG_DIR / "app.log"
ERROR_LOG_FILE = LOG_DIR / "errors.log"
ACCESS_LOG_FILE = LOG_DIR / "access.log"


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Extra fields from record
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Module and function info
        log_data["module"] = record.module
        log_data["function"] = record.funcName
        log_data["line"] = record.lineno
        
        return json.dumps(log_data, default=str)


class SanitizedFormatter(StructuredFormatter):
    """Formatter that sanitizes sensitive data."""
    
    SENSITIVE_PATTERNS = [
        r"sk-[a-zA-Z0-9]{32,}",  # OpenAI API keys
        r"Bearer\s+[a-zA-Z0-9\-_\.]+",  # Bearer tokens
        r"password['\"]?\s*[:=]\s*['\"]?[^'\"]+",  # Passwords
        r"api[_-]?key['\"]?\s*[:=]\s*['\"]?[a-zA-Z0-9]+",  # API keys
    ]
    
    def format(self, record: logging.LogRecord) -> str:
        """Format and sanitize log record."""
        import re
        
        message = record.getMessage()
        
        # Sanitize sensitive patterns
        for pattern in self.SENSITIVE_PATTERNS:
            message = re.sub(pattern, "[REDACTED]", message, flags=re.IGNORECASE)
        
        # Create sanitized record
        sanitized_record = logging.LogRecord(
            name=record.name,
            level=record.levelno,
            pathname=record.pathname,
            lineno=record.lineno,
            msg=message,
            args=(),
            exc_info=record.exc_info,
        )
        sanitized_record.__dict__.update(record.__dict__)
        sanitized_record.msg = message
        
        return super().format(sanitized_record)


class FlushingRotatingFileHandler(RotatingFileHandler):
    """RotatingFileHandler that flushes after each emit."""
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record and flush immediately."""
        super().emit(record)
        self.flush()


def setup_logger(name: str, log_file: Optional[Path] = None, level: str = LOG_LEVEL) -> logging.Logger:
    """
    Set up a logger with structured formatting.
    
    Args:
        name: Logger name (typically __name__)
        log_file: Optional log file path (if None, only console)
        level: Log level (DEBUG, INFO, WARN, ERROR)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level, logging.INFO))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "[%(levelname)s] %(name)s: %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if enabled and file specified)
    if ENABLE_FILE_LOGGING and log_file:
        try:
            file_handler = FlushingRotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = SanitizedFormatter()
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # If file logging fails, log to console
            logger.warning(f"Failed to set up file logging: {e}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance with file logging.
    
    All loggers write to app.log, and ERROR level logs also go to errors.log.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance with file handlers
    """
    logger = setup_logger(name, APP_LOG_FILE, LOG_LEVEL)
    
    # Error handler if not already present
    if ENABLE_FILE_LOGGING:
        # If error handler already exists
        has_error_handler = any(
            isinstance(h, RotatingFileHandler) and h.baseFilename == str(ERROR_LOG_FILE)
            for h in logger.handlers
        )
        
        if not has_error_handler:
            # Error handler that only logs ERROR and above
            try:
                error_handler = FlushingRotatingFileHandler(
                    ERROR_LOG_FILE,
                    maxBytes=10 * 1024 * 1024,  # 10MB
                    backupCount=5,
                    encoding="utf-8",
                )
                error_handler.setLevel(logging.ERROR)
                error_formatter = SanitizedFormatter()
                error_handler.setFormatter(error_formatter)
                logger.addHandler(error_handler)
            except Exception:
                pass  # If error logging fails, continue without it
    
    return logger


def log_request(logger: logging.Logger, endpoint: str, method: str = "POST", **kwargs) -> None:
    """Log an API request with sanitization."""
    logger.info(
        "API request",
        extra={
            "type": "request",
            "endpoint": endpoint,
            "method": method,
            **{k: v for k, v in kwargs.items() if k not in ["api_key", "password", "token"]},
        },
    )


def log_response(logger: logging.Logger, endpoint: str, status: str, latency_ms: float, **kwargs) -> None:
    """Log an API response with metrics."""
    logger.info(
        "API response",
        extra={
            "type": "response",
            "endpoint": endpoint,
            "status": status,
            "latency_ms": round(latency_ms, 2),
            **kwargs,
        },
    )


def log_error(logger: logging.Logger, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """Log an error with context."""
    logger.error(
        f"Error: {str(error)}",
        exc_info=error,
        extra={
            "type": "error",
            "error_type": type(error).__name__,
            **(context or {}),
        },
    )


def log_performance(logger: logging.Logger, operation: str, duration_ms: float, **metrics) -> None:
    """Log performance metrics."""
    logger.info(
        f"Performance: {operation}",
        extra={
            "type": "performance",
            "operation": operation,
            "duration_ms": round(duration_ms, 2),
            **metrics,
        },
    )


# Main application logger
app_logger = setup_logger("ai_knowledge_assistant", APP_LOG_FILE, LOG_LEVEL)
error_logger = setup_logger("ai_knowledge_assistant.errors", ERROR_LOG_FILE, "ERROR")
access_logger = setup_logger("ai_knowledge_assistant.access", ACCESS_LOG_FILE, "INFO")


def log_access(action: str, session_id: Optional[str] = None, **kwargs) -> None:
    """
    Log user access/activity to access.log.
    
    Args:
        action: Action description (e.g., "chat_request", "model_selected", "file_uploaded")
        session_id: Optional session identifier
        **kwargs: Additional context (model, profile, file_name, etc.)
    """
    access_logger.info(
        f"Access: {action}",
        extra={
            "type": "access",
            "action": action,
            "session_id": session_id,
            **{k: v for k, v in kwargs.items() if k not in ["api_key", "password", "token"]},
        },
    )

