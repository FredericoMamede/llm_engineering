#!/usr/bin/env python3
"""
Quick test runner for Week 3 Challenge
Run: python run_tests.py
"""

import sys
from pathlib import Path

# Challenge added directory to path
sys.path.insert(0, str(Path(__file__).parent))


def run_basic_tests():
    """Run basic smoke tests"""
    print("=" * 60)
    print("Running Basic Tests for Week 3 Challenge")
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
        
        assert len(result["records"]) > 0, "Should generate at least one record"
        print(f"   ✅ Basic generation - PASSED (generated {len(result['records'])} records)")
        
        # Cleanup
        if hasattr(model, 'unload'):
            model.unload()
    except Exception as e:
        print(f"   ❌ Basic generation - FAILED: {e}")
        import traceback
        traceback.print_exc()
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
        
        is_valid, error = validate_record(test_record, SchemaType.CUSTOMER_RECORD)
        assert is_valid, f"Validation failed: {error}"
        print("   ✅ Schema validation - PASSED")
    except Exception as e:
        print(f"   ❌ Schema validation - FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: JSON extraction
    print("\n3. Testing JSON extraction...")
    try:
        from data_generation.utils import extract_json_from_text
        
        text = '```json\n{"test": "value"}\n```'
        result = extract_json_from_text(text)
        assert result is not None, "Should extract JSON"
        assert result["test"] == "value"
        print("   ✅ JSON extraction - PASSED")
    except Exception as e:
        print(f"   ❌ JSON extraction - FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Multiple schemas
    print("\n4. Testing multiple schema types...")
    try:
        model = create_model("huggingface", "Qwen/Qwen2.5-3B-Instruct", use_quantization=True)
        generator = DataGenerator(model)
        
        test_schemas = [
            SchemaType.CUSTOMER_RECORD,
            SchemaType.INCIDENT_REPORT,
            SchemaType.BUSINESS_EVENT,
        ]
        
        for schema in test_schemas:
            result = generator.generate_dataset(
                schema_type=schema,
                num_records=1,
                config=GenerationConfig(temperature=0.7, max_tokens=128)
            )
            assert len(result["records"]) > 0, f"Failed for {schema.value}"
        
        print(f"   ✅ Multiple schemas - PASSED (tested {len(test_schemas)} schemas)")
        
        # Cleanup
        if hasattr(model, 'unload'):
            model.unload()
    except Exception as e:
        print(f"   ❌ Multiple schemas - FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Error handling
    print("\n5. Testing error handling...")
    try:
        from models import create_model
        
        # Test invalid provider
        try:
            model = create_model("invalid_provider", "some-model")
            print("   ⚠️ Error handling - WARNING (should have raised ValueError)")
        except ValueError:
            print("   ✅ Error handling - PASSED (caught invalid provider)")
    except Exception as e:
        print(f"   ❌ Error handling - FAILED: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All basic tests passed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review TESTING_GUIDE.md for comprehensive tests")
    print("2. Test UI: python ui/app.py")
    print("3. Run experiment notebooks")
    print("4. Check git status before committing")
    return True


if __name__ == "__main__":
    success = run_basic_tests()
    sys.exit(0 if success else 1)
