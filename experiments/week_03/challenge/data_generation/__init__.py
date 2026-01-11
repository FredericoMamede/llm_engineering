"""
Data Generation Module

Core components for synthetic data generation.
"""

from .generators import DataGenerator
from .schemas import SchemaType, SCHEMAS, get_schema_fields, schema_to_dict
from .validators import validate_record, validate_dataset, clean_record
from .utils import (
    extract_json_from_text,
    extract_json_array_from_text,
    format_record_for_display,
    format_dataset_for_display,
    save_dataset
)

__all__ = [
    "DataGenerator",
    "SchemaType",
    "SCHEMAS",
    "get_schema_fields",
    "schema_to_dict",
    "validate_record",
    "validate_dataset",
    "clean_record",
    "extract_json_from_text",
    "extract_json_array_from_text",
    "format_record_for_display",
    "format_dataset_for_display",
    "save_dataset",
]
