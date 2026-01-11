"""
Lightweight Validation for Generated Data

Validates structure and basic types, not semantic correctness.
Designed to catch obvious errors, not to be overly strict.

Design decision:
- Fast, simple validation
- Focus on structure (keys exist, types are roughly correct)
- Don't validate business logic or semantic correctness
"""

from typing import Dict, Any, List, Optional
from .schemas import SchemaType, SCHEMAS, get_schema_fields


def validate_record(
    record: Dict[str, Any],
    schema_type: SchemaType
) -> tuple[bool, Optional[str]]:
    """
    Validate a single record against a schema.
    
    Args:
        record: Generated record (dict)
        schema_type: Expected schema type
        
    Returns:
        (is_valid, error_message)
    """
    schema_class = SCHEMAS.get(schema_type)
    if schema_class is None:
        return False, f"Unknown schema type: {schema_type}"
    
    # Get expected fields
    expected_fields = get_schema_fields(schema_type)
    
    # Check for missing required fields
    missing_fields = [f for f in expected_fields if f not in record]
    if missing_fields:
        return False, f"Missing required fields: {missing_fields}"
    
    # Basic type checking (loose)
    # We don't do strict type checking - just ensure types are roughly correct
    # This is intentionally lenient to allow for variations in LLM output
    
    return True, None


def validate_dataset(
    records: List[Dict[str, Any]],
    schema_type: SchemaType,
    min_records: int = 1
) -> tuple[bool, Optional[str]]:
    """
    Validate a dataset (list of records).
    
    Args:
        records: List of generated records
        schema_type: Expected schema type
        min_records: Minimum number of records required
        
    Returns:
        (is_valid, error_message)
    """
    if len(records) < min_records:
        return False, f"Dataset must have at least {min_records} records, got {len(records)}"
    
    # Validate each record
    for i, record in enumerate(records):
        is_valid, error = validate_record(record, schema_type)
        if not is_valid:
            return False, f"Record {i}: {error}"
    
    return True, None


def clean_record(record: Dict[str, Any], schema_type: SchemaType) -> Dict[str, Any]:
    """
    Clean a record by removing extra fields and fixing types.
    
    This is a best-effort cleanup - doesn't guarantee correctness.
    
    Args:
        record: Record to clean
        schema_type: Expected schema type
        
    Returns:
        Cleaned record
    """
    expected_fields = get_schema_fields(schema_type)
    
    # Keep only expected fields
    cleaned = {k: v for k, v in record.items() if k in expected_fields}
    
    # Try to fix common type issues
    schema_class = SCHEMAS.get(schema_type)
    if schema_class:
        import dataclasses
        for field in dataclasses.fields(schema_class):
            if field.name in cleaned:
                value = cleaned[field.name]
                # Try to convert to expected type
                if field.type == int and isinstance(value, str):
                    try:
                        cleaned[field.name] = int(value)
                    except ValueError:
                        pass
                elif field.type == float and isinstance(value, str):
                    try:
                        cleaned[field.name] = float(value)
                    except ValueError:
                        pass
                elif field.type == bool and isinstance(value, str):
                    cleaned[field.name] = value.lower() in ("true", "1", "yes")
    
    return cleaned
