"""
Core Data Generation Logic

Orchestrates model calls, prompt construction, and output parsing.
This is the main entry point for generating synthetic datasets.
"""

import json
from typing import List, Dict, Any, Optional

from models.base import BaseModel, GenerationConfig
from .schemas import SchemaType, schema_to_dict
from .validators import validate_dataset, clean_record
from .utils import extract_json_array_from_text, extract_json_from_text, save_dataset


class DataGenerator:
    """
    Main class for generating synthetic datasets.
    
    Responsibilities:
    - Construct prompts from templates and strategies
    - Call models via BaseModel interface
    - Parse and validate generated outputs
    - Handle errors gracefully
    
    Design decisions:
    - Separates prompt construction from generation
    - Uses BaseModel interface (works with any provider)
    - Lightweight validation (structure, not semantics)
    - Returns raw results + cleaned results
    """
    
    def __init__(self, model: BaseModel):
        """
        Args:
            model: Model instance (HF, OpenAI, or Ollama)
        """
        self.model = model
    
    def generate_dataset(
        self,
        schema_type: SchemaType,
        num_records: int = 5,
        prompt_template: Optional[str] = None,
        variation_strategy: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a dataset of synthetic records.
        
        Args:
            schema_type: Type of records to generate
            num_records: Number of records to generate
            prompt_template: Custom prompt template (or use default)
            variation_strategy: Strategy for varying prompts (or use default)
            config: Generation parameters (temperature, max_tokens, etc.)
            output_file: Optional file path to save results
            
        Returns:
            Dict with:
            - "records": List of generated records
            - "cleaned_records": Validated/cleaned records
            - "raw_output": Original model output
            - "metadata": Generation metadata
        """
        if config is None:
            config = GenerationConfig()
        
        # Build prompt
        prompt = self._build_prompt(
            schema_type=schema_type,
            num_records=num_records,
            template=prompt_template,
            variation=variation_strategy
        )
        
        # Generate
        try:
            response = self.model.generate(prompt, config=config)
            raw_output = response.text
        except Exception as e:
            return {
                "records": [],
                "cleaned_records": [],
                "raw_output": "",
                "error": str(e),
                "metadata": {
                    "model": self.model.model_name,
                    "provider": self.model.provider,
                    "schema_type": schema_type.value,
                    "num_records_requested": num_records,
                }
            }
        
        # Parse output
        records = self._parse_output(raw_output)
        
        # Filter out schema definitions (objects that look like schema metadata)
        records = self._filter_schema_definitions(records)
        
        # Clean and validate
        cleaned_records = []
        for record in records:
            cleaned = clean_record(record, schema_type)
            cleaned_records.append(cleaned)
        
        # Validate dataset
        is_valid, validation_error = validate_dataset(
            cleaned_records,
            schema_type,
            min_records=1
        )
        
        result = {
            "records": cleaned_records,
            "cleaned_records": cleaned_records,  # Same for now, but could differ
            "raw_output": raw_output,
            "metadata": {
                "model": self.model.model_name,
                "provider": self.model.provider,
                "schema_type": schema_type.value,
                "num_records_requested": num_records,
                "num_records_generated": len(cleaned_records),
                "is_valid": is_valid,
                "validation_error": validation_error,
            }
        }
        
        # Save if requested
        if output_file:
            save_dataset(cleaned_records, output_file)
            result["metadata"]["output_file"] = output_file
        
        return result
    
    def _build_prompt(
        self,
        schema_type: SchemaType,
        num_records: int,
        template: Optional[str] = None,
        variation: Optional[str] = None
    ) -> str:
        """
        Build generation prompt from template and schema.
        
        If template is provided, use it. Otherwise, construct default prompt.
        """
        if template:
            # Use custom template (user can inject {schema}, {num_records}, etc.)
            prompt = template.format(
                schema=json.dumps(schema_to_dict(schema_type), indent=2),
                num_records=num_records,
                schema_type=schema_type.value
            )
        else:
            # Default prompt construction
            schema_dict = schema_to_dict(schema_type)
            
            # Create example structure (just field names, not schema definition)
            example_fields = list(schema_dict.keys())
            
            prompt = f"""Generate {num_records} synthetic {schema_type.value.replace('_', ' ')} records.

Each record must be a JSON object with these fields: {', '.join(example_fields)}

CRITICAL REQUIREMENTS:
- Generate EXACTLY {num_records} data records with REAL, ACTUAL VALUES
- Each record must have all fields: {', '.join(example_fields)}
- Use realistic, diverse values for each field (real names, emails, dates, numbers, etc.)
- Do NOT include example templates, schema definitions, or placeholder values
- Do NOT include any records with placeholder text like <Field Name>
- Output ONLY a JSON array of {num_records} objects with actual data values

Example of what a record should look like (use this as reference, but generate {num_records} unique records):
- customer_id: "CUST123456" (not "<Customer Id>")
- name: "John Smith" (not "<Name>")
- email: "john@example.com" (not "<Email>")
- age: 35 (not "<Age>")
- etc.

Output format: A JSON array containing exactly {num_records} data records with real values, nothing else.
"""
        
        # Apply variation strategy if provided
        if variation:
            prompt = self._apply_variation(prompt, variation)
        
        return prompt
    
    def _apply_variation(self, prompt: str, strategy: str) -> str:
        """
        Apply variation strategy to prompt.
        
        Strategies modify tone, style, or detail level.
        """
        strategy = strategy.lower()
        
        if strategy == "formal":
            prompt = "Using a formal, professional tone:\n\n" + prompt
        elif strategy == "casual":
            prompt = "Using a casual, conversational tone:\n\n" + prompt
        elif strategy == "detailed":
            prompt = "Include extra detail and context:\n\n" + prompt
        elif strategy == "concise":
            prompt = "Be concise and brief:\n\n" + prompt
        elif strategy == "diverse":
            prompt = "Ensure maximum diversity in values:\n\n" + prompt
        
        return prompt
    
    def _filter_schema_definitions(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter out objects that look like schema definitions or example templates.
        
        Removes:
        - Schema definitions (nested objects with 'type', 'required', 'description')
        - Example templates (values wrapped in < > placeholders)
        - Records where most/all values are placeholders
        """
        import re
        
        filtered = []
        for record in records:
            # Check if this looks like a schema definition
            # Schema definitions have values that are objects with 'type', 'required', 'description'
            is_schema_definition = False
            placeholder_count = 0
            total_fields = 0
            
            for key, value in record.items():
                total_fields += 1
                
                # Check for schema metadata structure
                if isinstance(value, dict):
                    if "type" in value and ("required" in value or "description" in value):
                        is_schema_definition = True
                        break
                
                # Check for placeholder values (wrapped in < >)
                if isinstance(value, str) and re.match(r'^<[^>]+>$', value.strip()):
                    placeholder_count += 1
            
            # Skip if it's a schema definition
            if is_schema_definition:
                continue
            
            # Skip if most/all values are placeholders (likely an example template)
            if total_fields > 0 and placeholder_count >= (total_fields * 0.7):  # 70% or more are placeholders
                continue
            
            # Include the record
            filtered.append(record)
        
        return filtered
    
    def _parse_output(
        self,
        raw_output: str
    ) -> List[Dict[str, Any]]:
        """
        Parse model output into list of records.
        
        Handles:
        - JSON arrays
        - Single JSON objects (wraps in list)
        - Markdown code blocks
        - Text with embedded JSON
        """
        # Try to extract JSON array first
        records = extract_json_array_from_text(raw_output)
        
        if records:
            return records
        
        # Try single JSON object
        single_record = extract_json_from_text(raw_output)
        if single_record:
            return [single_record]
        
        # Fallback: Try to parse as multiple JSON objects
        # This is a best-effort approach
        records = []
        lines = raw_output.split("\n")
        current_json = ""
        brace_count = 0
        
        for line in lines:
            current_json += line + "\n"
            brace_count += line.count("{") - line.count("}")
            
            if brace_count == 0 and current_json.strip():
                # Try to parse this as a JSON object
                parsed = extract_json_from_text(current_json)
                if parsed:
                    records.append(parsed)
                current_json = ""
        
        # If we found at least one record, return it
        if records:
            return records
        
        # Last resort: Return empty list
        return []
