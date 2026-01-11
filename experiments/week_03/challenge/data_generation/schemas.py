"""
Output Schemas for Synthetic Data Generation

Defines the structure of generated data records.
Schemas are loosely enforced - we validate structure but not content quality.

Design decision:
- Schemas are Python dataclasses/dicts, not strict JSON Schema
- Validation is lightweight (check keys exist, types are roughly correct)
- Focus on structure, not semantic correctness
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class SchemaType(str, Enum):
    """Types of schemas we support"""
    CUSTOMER_RECORD = "customer_record"
    INCIDENT_REPORT = "incident_report"
    MEETING_SUMMARY = "meeting_summary"
    BUSINESS_EVENT = "business_event"
    PRODUCT_REVIEW = "product_review"
    EMPLOYEE_RECORD = "employee_record"
    GENERIC_JSON = "generic_json"


@dataclass
class CustomerRecord:
    """Schema for customer data records"""
    customer_id: str
    name: str
    email: str
    age: int
    city: str
    country: str
    signup_date: str
    total_purchases: float
    preferred_category: str
    is_active: bool


@dataclass
class IncidentReport:
    """Schema for incident/issue reports"""
    incident_id: str
    title: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    status: str  # "open", "in_progress", "resolved", "closed"
    reported_by: str
    reported_date: str
    assigned_to: Optional[str]
    resolution: Optional[str]


@dataclass
class MeetingSummary:
    """Schema for meeting summaries"""
    meeting_id: str
    title: str
    date: str
    attendees: List[str]
    duration_minutes: int
    key_points: List[str]
    action_items: List[Dict[str, str]]  # [{"item": "...", "owner": "...", "due_date": "..."}]
    decisions: List[str]


@dataclass
class BusinessEvent:
    """Schema for business events/transactions"""
    event_id: str
    event_type: str  # "purchase", "refund", "subscription", etc.
    timestamp: str
    customer_id: str
    amount: float
    currency: str
    metadata: Dict[str, Any]


@dataclass
class ProductReview:
    """Schema for product reviews"""
    review_id: str
    product_id: str
    product_name: str
    reviewer_name: str
    rating: int  # 1-5
    review_text: str
    verified_purchase: bool
    helpful_count: int
    review_date: str


@dataclass
class EmployeeRecord:
    """Schema for employee records"""
    employee_id: str
    name: str
    email: str
    department: str
    role: str
    hire_date: str
    salary: float
    manager_id: Optional[str]
    skills: List[str]


# Schema registry
SCHEMAS = {
    SchemaType.CUSTOMER_RECORD: CustomerRecord,
    SchemaType.INCIDENT_REPORT: IncidentReport,
    SchemaType.MEETING_SUMMARY: MeetingSummary,
    SchemaType.BUSINESS_EVENT: BusinessEvent,
    SchemaType.PRODUCT_REVIEW: ProductReview,
    SchemaType.EMPLOYEE_RECORD: EmployeeRecord,
}


def get_schema_fields(schema_type: SchemaType) -> List[str]:
    """Get field names for a schema type"""
    schema_class = SCHEMAS.get(schema_type)
    if schema_class is None:
        return []
    
    # Get fields from dataclass
    import dataclasses
    return [field.name for field in dataclasses.fields(schema_class)]


def schema_to_dict(schema_type: SchemaType) -> Dict[str, Any]:
    """
    Convert schema to a dictionary representation.
    Useful for prompt generation - shows LLM what structure we want.
    """
    schema_class = SCHEMAS.get(schema_type)
    if schema_class is None:
        return {}
    
    import dataclasses
    fields = {}
    for field in dataclasses.fields(schema_class):
        field_type = field.type
        # Simplify type representation for prompts
        if field_type == str:
            type_str = "string"
        elif field_type == int:
            type_str = "integer"
        elif field_type == float:
            type_str = "float"
        elif field_type == bool:
            type_str = "boolean"
        elif hasattr(field_type, "__origin__"):  # List, Optional, Dict
            if field_type.__origin__ is list:
                type_str = "list"
            elif field_type.__origin__ is dict:
                type_str = "dictionary"
            else:
                type_str = "any"
        else:
            type_str = "any"
        
        fields[field.name] = {
            "type": type_str,
            "required": True,
            "description": f"{field.name.replace('_', ' ').title()}"
        }
    
    return fields
