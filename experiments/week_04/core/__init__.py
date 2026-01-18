"""
Core utilities for Week 4 code generation experiments.

This module provides shared functionality for:
- System information gathering
- Multi-provider model client setup
- Code execution (compile & run)
"""

from .system_info import retrieve_system_info, rust_toolchain_info
from .model_clients import get_model_clients, ModelClients
from .code_executor import CodeExecutor, CompileResult, RunResult

__all__ = [
    "retrieve_system_info",
    "rust_toolchain_info",
    "get_model_clients",
    "ModelClients",
    "CodeExecutor",
    "CompileResult",
    "RunResult",
]
