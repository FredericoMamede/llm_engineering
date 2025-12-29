"""
Comprehensive test suite for LLM Playground.

Tests all features and combinations to ensure everything works correctly.

NOTE:
- OpenAI tests are skipped if OPENAI_API_KEY is not set
- Ollama tests always run
- Designed for local runs and CI environments
"""
import subprocess
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load .env so skip_if_no_key reflects local keys
load_dotenv(override=True)

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'
PASS = '[PASS]'
FAIL = '[FAIL]'

def run_test(name, command, expected_exit=0, skip_if_no_key=False):
    """Run a test command and check the result."""
    print(f"\n{'='*60}")
    print(f"Test: {name}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    if skip_if_no_key and not os.getenv('OPENAI_API_KEY'):
        print(f"{YELLOW}SKIPPED: OPENAI_API_KEY not set{RESET}")
        return True
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
        )
        
        if result.returncode == expected_exit:
            print(f"{GREEN}{PASS}{RESET}")
            if result.stdout:
                print(f"Output (first 200 chars): {result.stdout[:200]}")
            return True
        else:
            print(f"{RED}{FAIL} (exit code: {result.returncode}, expected: {expected_exit}){RESET}")
            if result.stderr:
                print(f"Error: {result.stderr[:500]}")
            if result.stdout:
                print(f"Output: {result.stdout[:500]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"{RED}{FAIL}: Timeout{RESET}")
        return False
    except Exception as e:
        print(f"{RED}{FAIL}: {e}{RESET}")
        return False

def main():
    """Run all tests."""
    print(f"\n{GREEN}{'='*60}")
    print("LLM Playground - Comprehensive Test Suite")
    print(f"{'='*60}{RESET}\n")
    
    # Change to playground directory (already there, but ensure we're in right place)
    playground_dir = Path(__file__).parent.absolute()
    if Path.cwd() != playground_dir:
        os.chdir(playground_dir)
    
    results = []
    
    # Use 'py' on Windows, 'python' on Unix
    python_cmd = "py" if sys.platform == 'win32' else "python"
    
    # Test 1: Help command
    results.append(("Help command", run_test(
        "Help command",
        [python_cmd, "main.py", "--help"],
        expected_exit=0
    )))
    
    # Test 2: Missing required arguments
    results.append(("Missing arguments", run_test(
        "Missing required arguments",
        [python_cmd, "main.py"],
        expected_exit=2  # argparse error
    )))
    
    # Test 3: Invalid text input (too short)
    results.append(("Invalid text (too short)", run_test(
        "Invalid text input (too short)",
        [python_cmd, "main.py", "--text", "short", "--model", "openai"],
        expected_exit=1
    )))
    
    # Test 4: Invalid URL
    results.append(("Invalid URL", run_test(
        "Invalid URL format",
        [python_cmd, "main.py", "--url", "not-a-url", "--model", "openai"],
        expected_exit=1
    )))
    
    # Test 5: Invalid model provider
    results.append(("Invalid model", run_test(
        "Invalid model provider",
        [python_cmd, "main.py", "--text", "This is a test text that is long enough", "--model", "invalid"],
        expected_exit=2
    )))
    
    # Test 6: Invalid tone
    results.append(("Invalid tone", run_test(
        "Invalid tone",
        [python_cmd, "main.py", "--text", "This is a test text that is long enough", "--model", "openai", "--tone", "invalid"],
        expected_exit=2
    )))
    
    # Test 7: File input (non-existent file)
    results.append(("Non-existent file", run_test(
        "Non-existent file",
        [python_cmd, "main.py", "--file", "nonexistent.txt", "--model", "openai"],
        expected_exit=1
    )))
    
    # Test 8: JSON mode with streaming (should auto-disable)
    test_text = "This is a comprehensive test text that is long enough to pass validation. It contains multiple sentences and should work for testing purposes."
    results.append(("JSON mode auto-disable streaming", run_test(
        "JSON mode with streaming (auto-disable)",
        [python_cmd, "main.py", "--text", test_text, "--model", "openai", "--json-mode", "--stream", "--no-progress"],
        expected_exit=0,
        skip_if_no_key=True
    )))
    
    # Test 9: JSON mode with Ollama (should warn and disable)
    results.append(("JSON mode with Ollama", run_test(
        "JSON mode with Ollama (should warn)",
        [python_cmd, "main.py", "--text", test_text, "--model", "ollama", "--json-mode", "--no-stream", "--no-progress"],
        expected_exit=0
    )))
    
    # Test 10: Basic OpenAI call (if API key available)
    results.append(("Basic OpenAI call", run_test(
        "Basic OpenAI call",
        [python_cmd, "main.py", "--text", test_text, "--model", "openai", "--tone", "professional", "--no-stream", "--no-progress"],
        expected_exit=0,
        skip_if_no_key=True
    )))
    
    # Test 11: OpenAI with custom model name
    results.append(("OpenAI custom model", run_test(
        "OpenAI with custom model name",
        [python_cmd, "main.py", "--text", test_text, "--model", "openai", "--model-name", "gpt-4o-mini", "--no-stream", "--no-progress"],
        expected_exit=0,
        skip_if_no_key=True
    )))
    
    # Test 12: Different tones
    for tone in ["professional", "casual", "technical", "humorous"]:
        results.append((f"Tone: {tone}", run_test(
            f"Test tone: {tone}",
            [python_cmd, "main.py", "--text", test_text, "--model", "openai", "--tone", tone, "--no-stream", "--no-progress"],
            expected_exit=0,
            skip_if_no_key=True
        )))
    
    # Test 13: Show tokens
    results.append(("Show tokens", run_test(
        "Show token usage",
        [python_cmd, "main.py", "--text", test_text, "--model", "openai", "--show-tokens", "--no-stream", "--no-progress"],
        expected_exit=0,
        skip_if_no_key=True
    )))
    
    # Test 14: Show analysis
    results.append(("Show analysis", run_test(
        "Show analysis results",
        [python_cmd, "main.py", "--text", test_text, "--model", "openai", "--show-analysis", "--no-stream", "--no-progress"],
        expected_exit=0,
        skip_if_no_key=True
    )))
    
    # Test 15: JSON output format
    results.append(("JSON output format", run_test(
        "JSON output format",
        [python_cmd, "main.py", "--text", test_text, "--model", "openai", "--format", "json", "--no-stream", "--no-progress"],
        expected_exit=0,
        skip_if_no_key=True
    )))
    
    # Test 16: JSON mode
    results.append(("JSON mode", run_test(
        "JSON mode for structured output",
        [python_cmd, "main.py", "--text", test_text, "--model", "openai", "--json-mode", "--no-stream", "--no-progress"],
        expected_exit=0,
        skip_if_no_key=True
    )))
    
    # Test 17: Translation
    results.append(("Translation", run_test(
        "Translation feature",
        [python_cmd, "main.py", "--text", test_text, "--model", "openai", "--translate", "nl", "--no-stream", "--no-progress"],
        expected_exit=0,
        skip_if_no_key=True
    )))
    
    # Test 18: File input (create test file)
    test_file = Path("test_input.txt")
    try:
        test_file.write_text(test_text)
        results.append(("File input", run_test(
            "File input",
            [python_cmd, "main.py", "--file", "test_input.txt", "--model", "openai", "--no-stream", "--no-progress"],
            expected_exit=0,
            skip_if_no_key=True
        )))
    finally:
        if test_file.exists():
            test_file.unlink()
    
    # Test 19: Output to file
    output_file = Path("test_output.txt")
    try:
        results.append(("Output to file", run_test(
            "Output to file",
            [python_cmd, "main.py", "--text", test_text, "--model", "openai", "--output-file", "test_output.txt", "--no-stream", "--no-progress"],
            expected_exit=0,
            skip_if_no_key=True
        )))
        if output_file.exists():
            print(f"Output file created: {output_file.stat().st_size} bytes")
            output_file.unlink()
    except Exception as e:
        print(f"Error with output file test: {e}")
    
    # Test 20: Ollama (if available)
    results.append(("Ollama basic", run_test(
        "Ollama basic call",
        [python_cmd, "main.py", "--text", test_text, "--model", "ollama", "--no-stream", "--no-progress"],
        expected_exit=0
    )))
    
    # Test 21: Ollama with custom model
    results.append(("Ollama custom model", run_test(
        "Ollama with custom model name",
        [python_cmd, "main.py", "--text", test_text, "--model", "ollama", "--model-name", "llama3.2", "--no-stream", "--no-progress"],
        expected_exit=0
    )))
    
    # Summary
    print(f"\n\n{GREEN}{'='*60}")
    print("Test Summary")
    print(f"{'='*60}{RESET}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    failed = total - passed
    
    for name, result in results:
        status = f"{GREEN}{PASS}{RESET}" if result else f"{RED}{FAIL}{RESET}"
        print(f"{status}: {name}")
    
    print(f"\n{GREEN}Passed: {passed}/{total}{RESET}")
    if failed > 0:
        print(f"{RED}Failed: {failed}/{total}{RESET}")
    
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

