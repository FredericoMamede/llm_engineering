#!/usr/bin/env python3
"""
Quick smoke test for Week 2 notebooks.

This script validates that notebooks can be executed without errors.
It does NOT validate output correctness - that's for manual review.

Usage:
    python scripts/run_notebooks_smoke.py
"""

import subprocess
import sys
from pathlib import Path

# Notebooks to test
NOTEBOOKS = [
    "01_prompt_variations.ipynb",
    "02_reasoning_and_constraints.ipynb",
    "03_structured_outputs_json.ipynb",
    "04_streaming_vs_non_streaming.ipynb",
    "05_model_comparison.ipynb",
    "06_gradio_intro.ipynb",
    "07_tool_calling.ipynb",
]

def test_notebook(notebook_path: Path) -> bool:
    """Test if a notebook executes without errors."""
    print(f"Testing {notebook_path.name}...", end=" ")
    
    try:
        result = subprocess.run(
            ["jupyter", "nbconvert", "--to", "notebook", "--execute", str(notebook_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print("✓ PASS")
            return True
        else:
            print("✗ FAIL")
            print(f"  Error: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ TIMEOUT")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    """Run smoke tests on all notebooks."""
    script_dir = Path(__file__).parent
    notebooks_dir = script_dir.parent / "notebooks"
    
    if not notebooks_dir.exists():
        print(f"Error: {notebooks_dir} does not exist")
        sys.exit(1)
    
    print("Week 2 Notebooks - Smoke Test\n")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for notebook_name in NOTEBOOKS:
        notebook_path = notebooks_dir / notebook_name
        if not notebook_path.exists():
            print(f"{notebook_name}: ✗ NOT FOUND")
            failed += 1
            continue
        
        if test_notebook(notebook_path):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()


