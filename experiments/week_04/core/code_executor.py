"""
Code execution utilities for compiled languages.

This module handles compilation and execution of C++ and Rust code
with proper error handling and result reporting.
"""

import subprocess
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path


@dataclass
class CompileResult:
    """Result of a compilation attempt."""

    success: bool
    stdout: str
    stderr: str
    error_message: Optional[str] = None


@dataclass
class RunResult:
    """Result of a code execution attempt."""

    success: bool
    stdout: str
    stderr: str
    error_message: Optional[str] = None


class CodeExecutor:
    """Handles compilation and execution of code."""

    def __init__(
        self,
        compile_command: List[str],
        run_command: List[str],
        source_file: str = "main.cpp",
    ):
        """
        Initialize code executor.

        Args:
            compile_command: Command to compile the code
            run_command: Command to run the compiled code
            source_file: Path to source file
        """
        self.compile_command = compile_command
        self.run_command = run_command
        self.source_file = Path(source_file)

    def compile(self) -> CompileResult:
        """Compile the source file."""
        try:
            result = subprocess.run(
                self.compile_command,
                check=True,
                text=True,
                capture_output=True,
                timeout=60,
            )
            return CompileResult(
                success=True,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        except subprocess.CalledProcessError as e:
            return CompileResult(
                success=False,
                stdout=e.stdout,
                stderr=e.stderr,
                error_message=f"Compilation failed: {e.stderr}",
            )
        except subprocess.TimeoutExpired:
            return CompileResult(
                success=False,
                stdout="",
                stderr="",
                error_message="Compilation timed out after 60 seconds",
            )
        except Exception as e:
            return CompileResult(
                success=False,
                stdout="",
                stderr="",
                error_message=f"Compilation error: {str(e)}",
            )

    def run(self) -> RunResult:
        """Run the compiled code."""
        try:
            result = subprocess.run(
                self.run_command,
                check=True,
                text=True,
                capture_output=True,
                timeout=30,
            )
            return RunResult(
                success=True,
                stdout=result.stdout,
                stderr=result.stderr,
            )
        except subprocess.CalledProcessError as e:
            return RunResult(
                success=False,
                stdout=e.stdout,
                stderr=e.stderr,
                error_message=f"Execution failed: {e.stderr}",
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                success=False,
                stdout="",
                stderr="",
                error_message="Execution timed out after 30 seconds",
            )
        except Exception as e:
            return RunResult(
                success=False,
                stdout="",
                stderr="",
                error_message=f"Execution error: {str(e)}",
            )

    def compile_and_run(self) -> tuple[CompileResult, Optional[RunResult]]:
        """Compile and run the code, returning both results."""
        compile_result = self.compile()
        if not compile_result.success:
            return compile_result, None

        run_result = self.run()
        return compile_result, run_result
