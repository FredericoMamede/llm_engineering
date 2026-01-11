# Synthetic Records Templates

Templates focused on generating high-quality synthetic records.

## High-Quality Records

```
Generate {num_records} high-quality synthetic {schema_type} records.

Quality criteria:
- Realistic values (not random strings)
- Consistent relationships (e.g., dates make sense)
- Appropriate ranges (e.g., ages 18-100, not 1000)
- Diverse but plausible combinations

Schema: {schema}

Output: JSON array.
```

## Edge Case Records

```
Generate {num_records} {schema_type} records including edge cases.

Include:
- Minimum values (e.g., age=18, amount=$0.01)
- Maximum values (e.g., age=100, large amounts)
- Boundary conditions
- Unusual but valid combinations

Schema: {schema}

Output: JSON array.
```

## Training Data Style

```
Generate {num_records} {schema_type} records suitable for ML training.

Requirements:
- Maximum diversity in all fields
- Balanced distributions where applicable
- Representative of real-world variation
- No obvious patterns or repetition

Schema: {schema}

Output: JSON array.
```
