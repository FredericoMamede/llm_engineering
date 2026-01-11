"""
Utility Functions for Data Generation

Helper functions for parsing, formatting, and processing generated data.
"""

import json
import re
from typing import List, Dict, Any, Optional


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from text that may contain markdown or other formatting.
    
    Handles common cases:
    - JSON wrapped in ```json code blocks
    - JSON wrapped in ``` code blocks
    - Plain JSON
    - JSON with trailing text
    
    Returns:
        Parsed JSON dict, or None if no valid JSON found
    """
    # Try to find JSON in code blocks
    json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    match = re.search(json_block_pattern, text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON object directly
    json_object_pattern = r'\{.*\}'
    match = re.search(json_object_pattern, text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try parsing entire text as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    
    return None


def extract_json_array_from_text(text: str) -> Optional[List[Dict[str, Any]]]:
    """
    Extract JSON array from text.
    
    Similar to extract_json_from_text but looks for arrays.
    """
    # Try to find JSON array in code blocks
    json_block_pattern = r'```(?:json)?\s*(\[.*?\])\s*```'
    match = re.search(json_block_pattern, text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON array directly
    json_array_pattern = r'\[.*\]'
    match = re.search(json_array_pattern, text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Try parsing entire text as JSON
    try:
        parsed = json.loads(text.strip())
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    
    return None


def format_record_for_display(record: Dict[str, Any]) -> str:
    """Format a record as a readable string"""
    lines = []
    for key, value in record.items():
        if isinstance(value, (list, dict)):
            value_str = json.dumps(value, indent=2)
        else:
            value_str = str(value)
        lines.append(f"{key}: {value_str}")
    return "\n".join(lines)


def format_dataset_for_display(records: List[Dict[str, Any]], max_records: int = 10) -> str:
    """Format a dataset for display"""
    if not records:
        return "No records generated."
    
    display_count = min(len(records), max_records)
    lines = [f"Generated {len(records)} records (showing first {display_count}):\n"]
    
    for i, record in enumerate(records[:display_count]):
        lines.append(f"\n--- Record {i+1} ---")
        lines.append(format_record_for_display(record))
    
    if len(records) > max_records:
        lines.append(f"\n... and {len(records) - max_records} more records")
    
    return "\n".join(lines)


def save_dataset(
    records: List[Dict[str, Any]],
    filepath: str,
    format: str = "json"
):
    """
    Save dataset to file.
    
    Args:
        records: List of records to save
        filepath: Output file path
        format: "json" or "jsonl" (JSON Lines)
    """
    if format == "json":
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
    elif format == "jsonl":
        with open(filepath, "w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    else:
        raise ValueError(f"Unknown format: {format}. Supported: 'json', 'jsonl'")
