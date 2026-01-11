# Business Domain Templates

Templates for business-oriented synthetic data.

## Customer Records

```
Generate {num_records} customer records for a B2C e-commerce platform.

Each customer should have:
- Realistic demographics (age 18-80, diverse locations)
- Purchase history (0-50 purchases, varying amounts)
- Preferences (different product categories)
- Account status (active/inactive based on recency)

Schema: {schema}

Output: JSON array of customer objects.
```

## Business Events

```
Create {num_records} business event records representing transactions.

Event types should include:
- Purchases (most common)
- Refunds (less common)
- Subscriptions (recurring)
- Cancellations (occasional)

Ensure realistic timestamps, amounts, and metadata.

Schema: {schema}

Output: JSON array of event objects.
```

## Employee Records

```
Generate {num_records} employee records for a mid-size company.

Include:
- Various departments (Engineering, Sales, Marketing, HR, etc.)
- Different roles and seniority levels
- Realistic salary ranges by role
- Reporting relationships (manager_id)

Schema: {schema}

Output: JSON array of employee objects.
```
