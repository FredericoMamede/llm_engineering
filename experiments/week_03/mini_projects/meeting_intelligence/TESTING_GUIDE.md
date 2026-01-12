# Testing Guide — Meeting Intelligence Extractor

> **Purpose:** Comprehensive validation procedures for production readiness  
> **Audience:** Developers and QA engineers  
> **Scope:** Phase 1 (CLI) and Phase 2 (UI) testing

---

## Table of Contents

1. [Pre-Testing Setup](#pre-testing-setup)
2. [Phase 1: CLI Testing](#phase-1-cli-testing)
3. [Phase 2: UI Testing](#phase-2-ui-testing)
4. [Integration Testing](#integration-testing)
5. [Error Handling Validation](#error-handling-validation)
6. [Performance Validation](#performance-validation)
7. [Code Quality Checks](#code-quality-checks)

---

## Pre-Testing Setup

### Environment Verification

```bash
# Navigate to project directory
cd experiments/week_03/mini_projects/meeting_intelligence

# Verify Python version (3.8+ required)
python --version

# Install dependencies
pip install -r requirements.txt

# Verify .env file exists
cat .env
# Expected: HF_TOKEN=your_token_here
```

### Model Access Verification

```bash
# Test HuggingFace authentication
python -c "from huggingface_hub import login; import os; login(token=os.getenv('HF_TOKEN'), add_to_git_credential=False); print('Auth successful')"
```

### Test Data Preparation

Ensure `sample_inputs/meeting.txt` exists and contains valid meeting transcript.

---

## Phase 1: CLI Testing

### Test 1.1: Basic Extraction

**Objective:** Verify core extraction functionality with default parameters.

```bash
python run.py --input sample_inputs/meeting.txt
```

**Expected Results:**
- Model initializes successfully
- Quantization enabled message appears
- Processing completes without errors
- Output file created in `sample_outputs/` with timestamp
- File contains valid JSON matching schema

**Validation Checklist:**
- [ ] Output file exists
- [ ] JSON is valid (parseable)
- [ ] Contains required `summary` field
- [ ] Contains `decisions`, `action_items`, `risks`, `open_questions` arrays
- [ ] All action items have `task` and `owner` fields
- [ ] All decisions have `decision` field

---

### Test 1.2: Custom Output Path

**Objective:** Verify custom output path handling.

```bash
python run.py --input sample_inputs/meeting.txt --output test_output.json
```

**Expected Results:**
- Output saved to specified path
- File contains valid structured JSON
- Console confirms save location

**Validation:**
- [ ] File created at specified path
- [ ] JSON structure matches schema
- [ ] Console message confirms path

---

### Test 1.3: Parameter Customization

**Objective:** Verify configurable generation parameters.

```bash
python run.py --input sample_inputs/meeting.txt --max-tokens 2000 --temperature 0.5
```

**Expected Results:**
- Parameters applied correctly
- Output quality may vary with temperature
- Token limit respected

**Validation:**
- [ ] Console shows correct parameter values
- [ ] Output generated successfully
- [ ] Higher temperature produces more varied output

---

### Test 1.4: Quantization Disabled

**Objective:** Verify CPU/FP16 mode operation.

```bash
python run.py --input sample_inputs/meeting.txt --no-quantization
```

**Expected Results:**
- Quantization disabled message appears
- Model loads in FP16 (if CUDA) or CPU mode
- Extraction completes successfully

**Validation:**
- [ ] Console confirms quantization disabled
- [ ] Model loads without errors
- [ ] Output quality maintained

---

### Test 1.5: Error Handling — Missing File

**Objective:** Verify graceful handling of missing input file.

```bash
python run.py --input nonexistent_file.txt
```

**Expected Results:**
- Error message to stderr
- Exit code 1
- No output file created
- Message: "Error: Transcript file not found: nonexistent_file.txt"

**Validation:**
- [ ] Error message is clear and actionable
- [ ] No stack trace in normal output
- [ ] Process exits cleanly

---

### Test 1.6: Error Handling — Invalid HF Token

**Objective:** Verify authentication error handling.

```bash
# Temporarily set invalid token
export HF_TOKEN=invalid_token
python run.py --input sample_inputs/meeting.txt
```

**Expected Results:**
- RuntimeError with clear message
- Troubleshooting tips displayed
- Exit code 1

**Validation:**
- [ ] Error identifies authentication issue
- [ ] Troubleshooting section provides actionable steps
- [ ] No raw exception stack trace

---

## Phase 2: UI Testing

### Test 2.1: UI Launch

**Objective:** Verify Gradio interface starts correctly.

```bash
python ui/app.py
```

**Expected Results:**
- Server starts on `http://localhost:7860`
- No errors in console
- UI loads with all components visible

**Validation:**
- [ ] Browser opens automatically (or URL provided)
- [ ] Left panel shows file upload and text input
- [ ] Right panel shows output areas
- [ ] "Extract Meeting Intelligence" button visible

---

### Test 2.2: File Upload Extraction

**Objective:** Verify file upload workflow.

**Steps:**
1. Launch UI
2. Click "Upload Transcript File"
3. Select `sample_inputs/meeting.txt`
4. Click "Extract Meeting Intelligence"

**Expected Results:**
- Streaming output appears in real-time
- Structured JSON displays after completion
- File status shows save confirmation
- Output file created in `sample_outputs/`

**Validation:**
- [ ] Streaming output updates token-by-token
- [ ] Final JSON is valid and formatted
- [ ] File path displayed correctly
- [ ] Output file exists and matches displayed JSON

---

### Test 2.3: Text Input Extraction

**Objective:** Verify direct text input workflow.

**Steps:**
1. Launch UI
2. Paste meeting transcript into text box
3. Click "Extract Meeting Intelligence"

**Expected Results:**
- Same behavior as file upload
- Text input processed correctly
- Output matches file upload results

**Validation:**
- [ ] Text input accepted
- [ ] Extraction proceeds normally
- [ ] Output quality equivalent to file upload

---

### Test 2.4: Empty Input Handling

**Objective:** Verify graceful handling of empty input.

**Steps:**
1. Launch UI
2. Leave both file and text inputs empty
3. Click "Extract Meeting Intelligence"

**Expected Results:**
- Error message in file status: "Error: No transcript provided..."
- No extraction attempted
- UI remains responsive

**Validation:**
- [ ] Error message is user-friendly
- [ ] No technical stack trace
- [ ] UI doesn't crash or hang

---

### Test 2.5: Streaming Output Verification

**Objective:** Verify real-time token streaming.

**Steps:**
1. Launch UI with a longer transcript
2. Start extraction
3. Observe streaming output

**Expected Results:**
- Tokens appear incrementally
- Output builds progressively
- No lag or buffering issues

**Validation:**
- [ ] Streaming is smooth and real-time
- [ ] Output accumulates correctly
- [ ] Final result matches streamed content

---

### Test 2.6: Error Handling in UI

**Objective:** Verify user-friendly error messages.

**Test Cases:**

1. **Invalid file format:**
   - Upload non-.txt file
   - Expected: Clear error about file type

2. **Model loading failure:**
   - Temporarily break HF_TOKEN
   - Expected: "Model ran out of memory" or similar user-friendly message

3. **JSON parsing failure:**
   - Use malformed model output (requires mocking)
   - Expected: "Failed to parse structured output" message

**Validation:**
- [ ] All errors are non-technical
- [ ] Messages suggest solutions
- [ ] No stack traces visible to user

---

## Integration Testing

### Test 3.1: CLI and UI Consistency

**Objective:** Verify both interfaces produce identical results.

**Steps:**
1. Run CLI extraction: `python run.py --input sample_inputs/meeting.txt`
2. Run UI extraction with same file
3. Compare outputs

**Expected Results:**
- Both produce valid JSON
- Schema matches in both cases
- Content quality equivalent (may vary slightly due to non-determinism)

**Validation:**
- [ ] Both outputs parse successfully
- [ ] Schema validation passes for both
- [ ] Key fields (summary, decisions, action items) present in both

---

### Test 3.2: Memory Management

**Objective:** Verify proper resource cleanup.

**Steps:**
1. Run multiple extractions sequentially
2. Monitor GPU/CPU memory usage
3. Verify no memory leaks

**Expected Results:**
- Memory usage stable across runs
- No accumulation of VRAM usage
- `unload()` called correctly

**Validation:**
- [ ] Memory returns to baseline after each run
- [ ] No CUDA out-of-memory errors
- [ ] Process memory doesn't grow unbounded

---

## Error Handling Validation

### Test 4.1: File System Errors

**Test Cases:**
- Read-only output directory
- Disk full scenario
- Invalid file permissions

**Expected Behavior:**
- Clear error messages
- No crashes
- Graceful degradation

---

### Test 4.2: Model Generation Errors

**Test Cases:**
- Token limit exceeded
- Invalid prompt template
- Model API failures

**Expected Behavior:**
- User-friendly error messages
- Suggestions for resolution
- No raw exceptions

---

### Test 4.3: JSON Parsing Edge Cases

**Test Cases:**
- Markdown-wrapped JSON
- Trailing text after JSON
- Partial JSON output
- Multiple JSON objects

**Expected Behavior:**
- Fallback parsing strategies succeed
- Valid JSON extracted when possible
- Clear error if extraction fails

---

## Performance Validation

### Test 5.1: Extraction Speed

**Objective:** Establish baseline performance metrics.

**Test:**
```bash
time python run.py --input sample_inputs/meeting.txt
```

**Metrics to Track:**
- Model loading time (first run only)
- Generation time
- Total extraction time

**Expected:**
- First run: ~10-15 seconds (includes model download if not cached)
- Subsequent runs: ~5-10 seconds (model cached)
- Generation: ~3-7 seconds depending on transcript length

---

### Test 5.2: Memory Usage

**Objective:** Verify memory efficiency.

**Tools:**
- `nvidia-smi` for GPU memory
- `psutil` or system monitor for CPU memory

**Expected:**
- VRAM: ~1.5-2GB with quantization
- VRAM: ~6.4GB without quantization
- CPU RAM: ~2-3GB

---

## Code Quality Checks

### Test 6.1: Linter Validation

```bash
# Run linter (if configured)
pylint extractor.py run.py ui/app.py schemas.py

# Or use pyright/pyflakes
pyright .
```

**Expected:**
- No critical errors
- Warnings are acceptable if documented
- Code follows style guidelines

---

### Test 6.2: Import Validation

**Objective:** Verify all imports are used.

**Manual Check:**
- Review each import statement
- Verify usage in code
- Remove unused imports

**Tools:**
- IDE unused import warnings
- `vulture` or similar tools

---

### Test 6.3: Type Hints Validation

**Objective:** Verify type annotations are correct.

**Check:**
- All function signatures have type hints
- Return types specified
- Optional types marked correctly

---

## Test Execution Checklist

### Pre-Commit Validation

Before committing code, verify:

- [ ] All Phase 1 CLI tests pass
- [ ] All Phase 2 UI tests pass
- [ ] Error handling works for all scenarios
- [ ] No linter errors
- [ ] No unused imports
- [ ] Comments are professional and clear
- [ ] Code is reachable (no dead code)
- [ ] Memory management verified
- [ ] Output schema validation passes

### Production Readiness

Before deployment:

- [ ] Full test suite executed
- [ ] Performance benchmarks documented
- [ ] Error messages reviewed for clarity
- [ ] Documentation updated
- [ ] Security review (no hardcoded secrets)
- [ ] Resource limits understood

---

## Troubleshooting Common Issues

### Issue: Model fails to load

**Symptoms:** RuntimeError about model access

**Solutions:**
1. Verify HF_TOKEN is set correctly
2. Check model access permissions on HuggingFace
3. Verify internet connection for model download
4. Check disk space for model cache

---

### Issue: CUDA out of memory

**Symptoms:** RuntimeError during generation

**Solutions:**
1. Enable quantization (default)
2. Reduce max_new_tokens
3. Use shorter transcripts
4. Close other GPU applications

---

### Issue: JSON parsing fails

**Symptoms:** ValueError about JSON extraction

**Solutions:**
1. Increase max_new_tokens
2. Adjust temperature (lower = more structured)
3. Check prompt template for issues
4. Verify model output quality

---

### Issue: UI doesn't stream

**Symptoms:** Output appears all at once

**Solutions:**
1. Verify TextIteratorStreamer is used
2. Check streamer configuration
3. Verify callback is called
4. Test with longer transcripts

---

## Test Data

### Sample Transcript Requirements

For comprehensive testing, maintain:

1. **Short transcript** (< 500 words)
   - Tests basic functionality
   - Fast iteration

2. **Medium transcript** (500-2000 words)
   - Tests normal use case
   - Validates token budgeting

3. **Long transcript** (> 2000 words)
   - Tests edge cases
   - Validates truncation handling

4. **Malformed transcript**
   - Tests error handling
   - Validates robustness

---

## Continuous Testing

### Automated Checks

Consider implementing:

1. **Pre-commit hooks:**
   - Linter validation
   - Import checking
   - Type checking

2. **CI/CD pipeline:**
   - Unit tests for core functions
   - Integration tests for CLI
   - UI smoke tests

3. **Performance regression tests:**
   - Track extraction time
   - Monitor memory usage
   - Alert on degradation

---

## Reporting Test Results

### Test Report Template

```
Test Execution Date: [DATE]
Tester: [NAME]
Environment: [OS, Python version, GPU model]

Phase 1 Results:
- Test 1.1: [PASS/FAIL] - [Notes]
- Test 1.2: [PASS/FAIL] - [Notes]
...

Phase 2 Results:
- Test 2.1: [PASS/FAIL] - [Notes]
...

Issues Found:
- [Issue description]
- [Severity]
- [Steps to reproduce]

Performance Metrics:
- Average extraction time: [X] seconds
- Memory usage: [X] GB
- Model load time: [X] seconds
```

---

**Last Updated:** January 12, 2025  
**Version:** 1.0
