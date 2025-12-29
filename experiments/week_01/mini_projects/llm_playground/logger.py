"""
Logging configuration for LLM Playground.

Week 1 learning: Proper logging is essential for debugging and monitoring.
Replaces print statements with structured logging that can be controlled via environment variables.
"""
import logging
import os
import sys
from typing import Optional

# Default log format (consistent with production patterns)
DEFAULT_FORMAT = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"

# Log level mapping
LOG_LEVELS = {
    'CRITICAL': logging.CRITICAL,
    'ERROR': logging.ERROR,
    'WARNING': logging.WARNING,
    'INFO': logging.INFO,
    'DEBUG': logging.DEBUG
}


def init_logger(name: str = 'llm_playground', level: Optional[str] = None) -> logging.Logger:
    """
    Initialize and configure logger for the application.
    
    Week 1 learning: Centralized logging configuration ensures consistent formatting
    and makes it easy to adjust verbosity via environment variables.
    
    Log level can be set via:
    - LLM_PLAYGROUND_LOG_LEVEL environment variable
    - level parameter (takes precedence)
    
    Args:
        name: Logger name (default: 'llm_playground')
        level: Optional log level override (INFO, DEBUG, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if logger already configured
    if logger.handlers:
        return logger
    
    # Get log level from environment or parameter
    env_level = os.getenv('LLM_PLAYGROUND_LOG_LEVEL', 'INFO')
    log_level = level or env_level
    
    # Set logger level
    logger.setLevel(LOG_LEVELS.get(log_level.upper(), logging.INFO))
    
    # Console handler (stderr for errors, stdout for info)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logger.level)
    
    # Formatter
    formatter = logging.Formatter(DEFAULT_FORMAT, datefmt=DEFAULT_DATEFMT)
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    # Prevent propagation to root logger (avoid duplicate messages)
    logger.propagate = False
    
    return logger


# Create module-level logger instance
# Week 1 learning: Module-level logger allows easy import and use across files
# Usage: from logger import logger; logger.info("message")
logger = init_logger()

