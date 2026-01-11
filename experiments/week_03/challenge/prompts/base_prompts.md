# Base Prompts for Synthetic Data Generation

This file contains reusable prompt templates for generating synthetic data.

## Prompt Structure

All prompts follow this pattern:
1. **Task description**: What to generate
2. **Schema specification**: Expected structure
3. **Requirements**: Quality and format constraints
4. **Output format**: How to structure the response

## Default Template

```
Generate {num_records} synthetic {schema_type} records.

Each record must be a JSON object with the following structure:
{schema}

Requirements:
- All fields must be present
- Use realistic, diverse values
- Ensure data variety across records
- Output ONLY valid JSON array, no markdown or explanations

Output format: A JSON array of {num_records} objects.
```

## Custom Templates

### Customer Records

```
Generate {num_records} diverse customer records for an e-commerce platform.

Each record should represent a unique customer with realistic attributes:
- Customer demographics (age, location)
- Purchase history and preferences
- Account status and engagement

Schema: {schema}

Output: JSON array of customer objects.
```

### Incident Reports

```
Create {num_records} synthetic incident reports for a support system.

Each report should describe a different type of issue:
- Technical problems
- Service requests
- Bug reports
- Feature requests

Ensure variety in severity, status, and resolution details.

Schema: {schema}

Output: JSON array of incident objects.
```

### Meeting Summaries

```
Generate {num_records} meeting summary records.

Each summary should cover different meeting types:
- Team standups
- Project planning
- Client meetings
- Technical reviews

Include realistic attendees, action items, and decisions.

Schema: {schema}

Output: JSON array of meeting summary objects.
```

## Usage Notes

- Templates use `{schema}`, `{num_records}`, and `{schema_type}` as placeholders
- These are replaced at runtime by the generator
- You can create custom templates for specific use cases
- Keep prompts clear and explicit about JSON format requirements
