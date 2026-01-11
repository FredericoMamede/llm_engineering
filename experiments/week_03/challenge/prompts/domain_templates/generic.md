# Generic Domain Templates

Templates for general-purpose synthetic data generation.

## Multi-Record Generation

```
Generate {num_records} synthetic records of type {schema_type}.

Schema structure:
{schema}

Instructions:
- Create realistic, varied data
- Ensure each record is unique
- Follow the schema exactly
- Output as JSON array only
```

## Single Record with Context

```
Generate one {schema_type} record with the following context:
{context}

Schema:
{schema}

Output: Single JSON object.
```

## Batch Generation with Constraints

```
Generate {num_records} {schema_type} records with these constraints:
- Constraint 1: {constraint1}
- Constraint 2: {constraint2}

Schema:
{schema}

Ensure all records satisfy the constraints.
```
