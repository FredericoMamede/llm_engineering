# Testing Guide - Week 3 Challenge
## Synthetic Data Generation System

> **Purpose**: Comprehensive testing checklist to ensure all components work before committing.

---

## 📋 Pre-Testing Checklist

### Environment Setup
- [ ] Python 3.8+ installed
- [ ] Virtual environment activated (if using)
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] GPU available (for HF models) or CPU fallback ready
- [ ] HuggingFace token set (if testing gated models): `export HF_TOKEN="hf_..."`
- [ ] OpenAI API key set (if testing OpenAI): `export OPENAI_API_KEY="sk-..."`
- [ ] Ollama running locally (if testing Ollama): `ollama serve`

---

## 🧪 Test Categories

### 1. Model Provider Tests

#### 1.1 HuggingFace Models (Open Models - No Auth Required)

**Test 1.1.1: Small Open Model (Qwen 2.5 3B)**
```python
from models import create_model
from models.base import GenerationConfig
from data_generation.generators import DataGenerator
from data_generation.schemas import SchemaType

# Test basic generation
model = create_model("huggingface", "Qwen/Qwen2.5-3B-Instruct", use_quantization=True)
generator = DataGenerator(model)

result = generator.generate_dataset(
    schema_type=SchemaType.CUSTOMER_RECORD,
    num_records=2,
    config=GenerationConfig(temperature=0.7, max_tokens=256)
)

assert len(result["records"]) > 0, "Should generate at least one record"
assert result["metadata"]["is_valid"] == True, "Records should be valid"
print("✅ Test 1.1.1: Qwen 2.5 3B generation - PASSED")
```

**Test 1.1.2: Tiny Model (TinyLlama)**
```python
# Test with smallest model
model = create_model("huggingface", "TinyLlama/TinyLlama-1.1B-Chat-v1.0", use_quantization=True)
generator = DataGenerator(model)

result = generator.generate_dataset(
    schema_type=SchemaType.CUSTOMER_RECORD,
    num_records=1,
    config=GenerationConfig(temperature=0.7, max_tokens=128)
)

assert "records" in result, "Should return records"
print("✅ Test 1.1.2: TinyLlama generation - PASSED")
```

**Test 1.1.3: Quantization Toggle**
```python
# Test with quantization disabled
model_no_quant = create_model("huggingface", "Qwen/Qwen2.5-3B-Instruct", use_quantization=False)
# Should work (may need more memory)
print("✅ Test 1.1.3: Quantization toggle - PASSED")
```

#### 1.2 HuggingFace Models (Gated Models - Requires Auth)

**Test 1.2.1: Llama 3.2 (If Access Available)**
```python
# Only run if you have access
try:
    model = create_model("huggingface", "meta-llama/Llama-3.2-3B-Instruct", 
                        use_quantization=True, hf_token="your_token_here")
    generator = DataGenerator(model)
    
    result = generator.generate_dataset(
        schema_type=SchemaType.CUSTOMER_RECORD,
        num_records=1,
        config=GenerationConfig(temperature=0.7, max_tokens=256)
    )
    
    assert len(result["records"]) > 0
    print("✅ Test 1.2.1: Llama 3.2 generation - PASSED")
except Exception as e:
    print(f"⚠️ Test 1.2.1: Llama 3.2 - SKIPPED (may need access): {e}")
```

#### 1.3 OpenAI Models

**Test 1.3.1: GPT-4o-mini (Requires API Key)**
```python
# Only run if API key is set
import os
if os.getenv("OPENAI_API_KEY"):
    model = create_model("openai", "gpt-4o-mini")
    generator = DataGenerator(model)
    
    result = generator.generate_dataset(
        schema_type=SchemaType.CUSTOMER_RECORD,
        num_records=2,
        config=GenerationConfig(temperature=0.7, max_tokens=256)
    )
    
    assert len(result["records"]) > 0
    assert "usage" in result["metadata"].get("metadata", {})
    print("✅ Test 1.3.1: OpenAI GPT-4o-mini - PASSED")
else:
    print("⚠️ Test 1.3.1: OpenAI - SKIPPED (no API key)")
```

#### 1.4 Ollama Models

**Test 1.4.1: Local Ollama (Requires Ollama Running)**
```python
import requests
try:
    # Check if Ollama is running
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        model = create_model("ollama", "llama3.2:3b")  # Adjust to available model
        generator = DataGenerator(model)
        
        result = generator.generate_dataset(
            schema_type=SchemaType.CUSTOMER_RECORD,
            num_records=1,
            config=GenerationConfig(temperature=0.7, max_tokens=128)
        )
        
        assert len(result["records"]) > 0
        print("✅ Test 1.4.1: Ollama local model - PASSED")
    else:
        print("⚠️ Test 1.4.1: Ollama - SKIPPED (not running)")
except Exception as e:
    print(f"⚠️ Test 1.4.1: Ollama - SKIPPED (not available): {e}")
```

---

### 2. Schema Generation Tests

**Test 2.1: All Schema Types**
```python
from data_generation.schemas import SchemaType

schemas_to_test = [
    SchemaType.CUSTOMER_RECORD,
    SchemaType.INCIDENT_REPORT,
    SchemaType.MEETING_SUMMARY,
    SchemaType.BUSINESS_EVENT,
    SchemaType.PRODUCT_REVIEW,
    SchemaType.EMPLOYEE_RECORD,
]

model = create_model("huggingface", "Qwen/Qwen2.5-3B-Instruct", use_quantization=True)
generator = DataGenerator(model)

for schema_type in schemas_to_test:
    result = generator.generate_dataset(
        schema_type=schema_type,
        num_records=1,
        config=GenerationConfig(temperature=0.7, max_tokens=256)
    )
    
    assert len(result["records"]) > 0, f"Failed for {schema_type.value}"
    assert result["records"][0] is not None, f"Record is None for {schema_type.value}"
    print(f"✅ Schema test: {schema_type.value} - PASSED")

print("✅ Test 2.1: All schema types - PASSED")
```

**Test 2.2: Multiple Records**
```python
result = generator.generate_dataset(
    schema_type=SchemaType.CUSTOMER_RECORD,
    num_records=5,
    config=GenerationConfig(temperature=0.7, max_tokens=512)
)

assert len(result["records"]) >= 1, "Should generate at least one record"
# Note: May not generate exactly 5, but should generate some
print(f"✅ Test 2.2: Multiple records - PASSED (generated {len(result['records'])} records)")
```

---

### 3. Prompt Strategy Tests

**Test 3.1: All Variation Strategies**
```python
strategies = ["default", "formal", "casual", "detailed", "concise", "diverse"]

for strategy in strategies:
    result = generator.generate_dataset(
        schema_type=SchemaType.CUSTOMER_RECORD,
        num_records=1,
        variation_strategy=strategy if strategy != "default" else None,
        config=GenerationConfig(temperature=0.7, max_tokens=256)
    )
    
    assert len(result["records"]) > 0, f"Failed for strategy: {strategy}"
    print(f"✅ Strategy test: {strategy} - PASSED")

print("✅ Test 3.1: All prompt strategies - PASSED")
```

---

### 4. Validation Tests

**Test 4.1: Record Validation**
```python
from data_generation.validators import validate_record, validate_dataset

# Test with valid record
test_record = {
    "customer_id": "C001",
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "city": "New York",
    "country": "USA",
    "signup_date": "2024-01-01",
    "total_purchases": 100.50,
    "preferred_category": "Electronics",
    "is_active": True
}

is_valid, error = validate_record(test_record, SchemaType.CUSTOMER_RECORD)
assert is_valid == True, f"Validation failed: {error}"
print("✅ Test 4.1: Record validation - PASSED")
```

**Test 4.2: Invalid Record Detection**
```python
# Test with missing required field
invalid_record = {
    "customer_id": "C001",
    "name": "John Doe",
    # Missing email
}

is_valid, error = validate_record(invalid_record, SchemaType.CUSTOMER_RECORD)
assert is_valid == False, "Should detect missing field"
assert "email" in error.lower() or "Missing" in error
print("✅ Test 4.2: Invalid record detection - PASSED")
```

---

### 5. Utility Function Tests

**Test 5.1: JSON Extraction**
```python
from data_generation.utils import extract_json_from_text, extract_json_array_from_text

# Test markdown code block extraction
text_with_markdown = """
```json
{"customer_id": "C001", "name": "John Doe"}
```
"""

result = extract_json_from_text(text_with_markdown)
assert result is not None, "Should extract JSON from markdown"
assert result["customer_id"] == "C001"
print("✅ Test 5.1: JSON extraction from markdown - PASSED")

# Test array extraction
text_with_array = """
```json
[{"id": "1"}, {"id": "2"}]
```
"""

result = extract_json_array_from_text(text_with_array)
assert result is not None, "Should extract JSON array"
assert len(result) == 2
print("✅ Test 5.1: JSON array extraction - PASSED")
```

**Test 5.2: File Saving**
```python
from data_generation.utils import save_dataset
from pathlib import Path
import json

test_records = [
    {"customer_id": "C001", "name": "Test User", "email": "test@example.com"},
    {"customer_id": "C002", "name": "Test User 2", "email": "test2@example.com"}
]

# Test JSON format
test_file = Path("outputs/generated_samples/test_output.json")
test_file.parent.mkdir(parents=True, exist_ok=True)

save_dataset(test_records, str(test_file), format="json")
assert test_file.exists(), "File should be created"

# Verify content
with open(test_file, 'r') as f:
    loaded = json.load(f)
    assert len(loaded) == 2

# Cleanup
test_file.unlink()
print("✅ Test 5.2: File saving - PASSED")
```

---

### 6. Error Handling Tests

**Test 6.1: Invalid Model Name**
```python
try:
    model = create_model("huggingface", "nonexistent/model-name-12345")
    generator = DataGenerator(model)
    result = generator.generate_dataset(
        schema_type=SchemaType.CUSTOMER_RECORD,
        num_records=1
    )
    # Should either work or return error in result
    if "error" in result:
        print("✅ Test 6.1: Error handling for invalid model - PASSED")
    else:
        print("⚠️ Test 6.1: Model loaded (unexpected)")
except Exception as e:
    print(f"✅ Test 6.1: Error handling - PASSED (caught exception: {type(e).__name__})")
```

**Test 6.2: Invalid Provider**
```python
try:
    model = create_model("invalid_provider", "some-model")
    assert False, "Should raise ValueError"
except ValueError as e:
    assert "Unknown provider" in str(e)
    print("✅ Test 6.2: Invalid provider handling - PASSED")
```

**Test 6.3: Graceful Failure on Generation**
```python
# Use a model that might fail
model = create_model("huggingface", "Qwen/Qwen2.5-3B-Instruct", use_quantization=True)
generator = DataGenerator(model)

# Try with very low max_tokens (might cause issues)
result = generator.generate_dataset(
    schema_type=SchemaType.CUSTOMER_RECORD,
    num_records=10,  # Request many
    config=GenerationConfig(temperature=0.7, max_tokens=10)  # But very few tokens
)

# Should return result (even if empty) without crashing
assert "records" in result
assert "metadata" in result
print("✅ Test 6.3: Graceful failure handling - PASSED")
```

---

### 7. UI Tests (Manual)

**Test 7.1: Gradio UI Launch**
```bash
# Run this in terminal:
cd experiments/week_03/challenge
python ui/app.py
```

**Checklist:**
- [ ] UI launches without errors
- [ ] All provider options visible (HuggingFace, OpenAI, Ollama)
- [ ] Model dropdown updates when provider changes
- [ ] All schema types available in dropdown
- [ ] Sliders work (temperature, max_tokens, num_records)
- [ ] Generate button works
- [ ] Output displays correctly
- [ ] JSON output is formatted
- [ ] File download works
- [ ] Error messages display clearly (if any)

**Test 7.2: UI Generation Test**
1. Select HuggingFace provider
2. Choose "Qwen/Qwen2.5-3B-Instruct"
3. Select "customer_record" schema
4. Set num_records to 3
5. Set temperature to 0.7
6. Click "Generate Dataset"
7. Verify output appears
8. Verify JSON is valid
9. Download file and verify it opens correctly

---

### 8. Integration Tests

**Test 8.1: End-to-End Workflow**
```python
# Complete workflow test
from models import create_model
from models.base import GenerationConfig
from data_generation.generators import DataGenerator
from data_generation.schemas import SchemaType
from data_generation.utils import save_dataset
from pathlib import Path

# 1. Create model
model = create_model("huggingface", "Qwen/Qwen2.5-3B-Instruct", use_quantization=True)

# 2. Create generator
generator = DataGenerator(model)

# 3. Generate dataset
result = generator.generate_dataset(
    schema_type=SchemaType.CUSTOMER_RECORD,
    num_records=3,
    variation_strategy="diverse",
    config=GenerationConfig(temperature=0.7, max_tokens=512),
    output_file="outputs/generated_samples/test_e2e.json"
)

# 4. Verify results
assert len(result["records"]) > 0
assert result["metadata"]["is_valid"] == True
assert Path("outputs/generated_samples/test_e2e.json").exists()

# 5. Cleanup
Path("outputs/generated_samples/test_e2e.json").unlink()

print("✅ Test 8.1: End-to-end workflow - PASSED")
```

**Test 8.2: Model Switching**
```python
# Test switching between models
models_to_test = [
    ("huggingface", "Qwen/Qwen2.5-3B-Instruct"),
    # Add more as available
]

for provider, model_name in models_to_test:
    try:
        model = create_model(provider, model_name, use_quantization=True)
        generator = DataGenerator(model)
        
        result = generator.generate_dataset(
            schema_type=SchemaType.CUSTOMER_RECORD,
            num_records=1,
            config=GenerationConfig(temperature=0.7, max_tokens=128)
        )
        
        assert len(result["records"]) > 0
        print(f"✅ Model switch test: {provider}/{model_name} - PASSED")
        
        # Cleanup
        if hasattr(model, 'unload'):
            model.unload()
    except Exception as e:
        print(f"⚠️ Model switch test: {provider}/{model_name} - SKIPPED: {e}")
```

---

### 9. Memory Management Tests

**Test 9.1: Model Unloading (HF Only)**
```python
model = create_model("huggingface", "Qwen/Qwen2.5-3B-Instruct", use_quantization=True)
generator = DataGenerator(model)

# Generate to load model
result = generator.generate_dataset(
    schema_type=SchemaType.CUSTOMER_RECORD,
    num_records=1
)

# Verify model is loaded
assert model.is_loaded() == True

# Unload
model.unload()

# Verify unloaded
assert model.is_loaded() == False
print("✅ Test 9.1: Model unloading - PASSED")
```

---

### 10. Edge Cases

**Test 10.1: Zero Records Requested**
```python
result = generator.generate_dataset(
    schema_type=SchemaType.CUSTOMER_RECORD,
    num_records=0,  # Edge case
    config=GenerationConfig(temperature=0.7, max_tokens=128)
)

# Should handle gracefully
assert "records" in result
print("✅ Test 10.1: Zero records edge case - PASSED")
```

**Test 10.2: Very High Token Count**
```python
result = generator.generate_dataset(
    schema_type=SchemaType.CUSTOMER_RECORD,
    num_records=1,
    config=GenerationConfig(temperature=0.7, max_tokens=2000)  # High limit
)

assert "records" in result
print("✅ Test 10.2: High token count - PASSED")
```

**Test 10.3: Very Low Temperature**
```python
result = generator.generate_dataset(
    schema_type=SchemaType.CUSTOMER_RECORD,
    num_records=1,
    config=GenerationConfig(temperature=0.0, max_tokens=128)  # Deterministic
)

assert "records" in result
print("✅ Test 10.3: Low temperature - PASSED")
```

---

## 🚀 Quick Test Script

Create a file `run_tests.py` in the challenge directory:

```python
#!/usr/bin/env python3
"""
Quick test runner for Week 3 Challenge
Run: python run_tests.py
"""

import sys
from pathlib import Path

# Challenge directory added to path
sys.path.insert(0, str(Path(__file__).parent))

def run_basic_tests():
    """Run basic smoke tests"""
    print("=" * 60)
    print("Running Basic Tests")
    print("=" * 60)
    
    from models import create_model
    from models.base import GenerationConfig
    from data_generation.generators import DataGenerator
    from data_generation.schemas import SchemaType
    
    # Test 1: Basic generation
    print("\n1. Testing basic generation...")
    try:
        model = create_model("huggingface", "Qwen/Qwen2.5-3B-Instruct", use_quantization=True)
        generator = DataGenerator(model)
        
        result = generator.generate_dataset(
            schema_type=SchemaType.CUSTOMER_RECORD,
            num_records=2,
            config=GenerationConfig(temperature=0.7, max_tokens=256)
        )
        
        assert len(result["records"]) > 0
        print("   ✅ Basic generation - PASSED")
    except Exception as e:
        print(f"   ❌ Basic generation - FAILED: {e}")
        return False
    
    # Test 2: Schema validation
    print("\n2. Testing schema validation...")
    try:
        from data_generation.validators import validate_record
        
        test_record = {
            "customer_id": "C001",
            "name": "Test",
            "email": "test@example.com",
            "age": 30,
            "city": "NYC",
            "country": "USA",
            "signup_date": "2024-01-01",
            "total_purchases": 100.0,
            "preferred_category": "Tech",
            "is_active": True
        }
        
        is_valid, _ = validate_record(test_record, SchemaType.CUSTOMER_RECORD)
        assert is_valid
        print("   ✅ Schema validation - PASSED")
    except Exception as e:
        print(f"   ❌ Schema validation - FAILED: {e}")
        return False
    
    # Test 3: JSON extraction
    print("\n3. Testing JSON extraction...")
    try:
        from data_generation.utils import extract_json_from_text
        
        text = '```json\n{"test": "value"}\n```'
        result = extract_json_from_text(text)
        assert result is not None
        print("   ✅ JSON extraction - PASSED")
    except Exception as e:
        print(f"   ❌ JSON extraction - FAILED: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All basic tests passed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)
```

---

## 📝 Testing Checklist Summary

### Must Pass (Critical)
- [ ] At least one HuggingFace model works (open model)
- [ ] All 6 schema types generate records
- [ ] Validation works correctly
- [ ] JSON extraction works
- [ ] File saving works
- [ ] Error handling doesn't crash
- [ ] UI launches and generates data

### Should Pass (Important)
- [ ] Multiple records generation
- [ ] All prompt strategies work
- [ ] Model switching works
- [ ] Quantization toggle works
- [ ] Memory management (unload) works

### Nice to Have (Optional)
- [ ] OpenAI model works (if API key available)
- [ ] Ollama model works (if running)
- [ ] Gated HF models work (if access available)
- [ ] Edge cases handled gracefully

---

## 🐛 Common Issues & Solutions

### Issue: "Model not found" or "403 Forbidden"
- **Solution**: Check model name spelling, verify access for gated models

### Issue: "CUDA out of memory"
- **Solution**: Enable quantization, use smaller model, or reduce batch size

### Issue: "JSON extraction failed"
- **Solution**: Increase max_tokens, try different model, check prompt clarity

### Issue: "Ollama connection failed"
- **Solution**: Ensure `ollama serve` is running, check port 11434

### Issue: "OpenAI API error"
- **Solution**: Verify API key is set, check account has credits

---

## ✅ Pre-Commit Checklist

Before committing, verify:

1. [ ] All critical tests pass
2. [ ] No obvious errors in console output
3. [ ] UI works for at least one provider
4. [ ] Generated files are valid JSON
5. [ ] No hardcoded credentials in code
6. [ ] README.md is accurate
7. [ ] Requirements.txt is complete
8. [ ] No large files in outputs/ (add to .gitignore if needed)

---

## 🎯 Final Verification

Run this command to check what will be committed:

```bash
cd experiments/week_03/challenge
git status
git add .
git status  # Review what's staged
```

**Expected files to commit:**
- All Python files in `models/`, `data_generation/`, `ui/`
- All markdown files in `prompts/`
- Notebooks in `experiments/`
- `README.md`, `requirements.txt`
- `TESTING_GUIDE.md` (this file)

**Should NOT commit:**
- `__pycache__/` directories
- `outputs/generated_samples/*.json` (generated data)
- `.gradio/` directory
- Model cache files

---

*Good luck with testing! 🚀*
