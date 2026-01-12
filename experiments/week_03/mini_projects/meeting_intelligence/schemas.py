"""
Schema definitions for meeting intelligence output.

Defines the structure of extracted meeting information.
Focused on actionable business intelligence.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ActionItem:
    """An action item from the meeting"""
    task: str
    owner: str
    due_date: Optional[str] = None


@dataclass
class Decision:
    """A decision made during the meeting"""
    decision: str
    rationale: Optional[str] = None
    impact: Optional[str] = None


@dataclass
class MeetingIntelligence:
    """
    Complete structured output from meeting analysis.
    
    Focused on actionable business intelligence:
    - Summary for quick understanding
    - Decisions for tracking what was decided
    - Action items for accountability
    - Risks for proactive management
    - Open questions for follow-up
    """
    summary: str
    decisions: List[Decision] = field(default_factory=list)
    action_items: List[ActionItem] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    open_questions: List[str] = field(default_factory=list)


def meeting_to_dict(meeting: MeetingIntelligence) -> Dict[str, Any]:
    """Convert MeetingIntelligence to dictionary for JSON serialization"""
    return {
        "summary": meeting.summary,
        "decisions": [
            {
                "decision": d.decision,
                "rationale": d.rationale,
                "impact": d.impact
            }
            for d in meeting.decisions
        ],
        "action_items": [
            {
                "task": a.task,
                "owner": a.owner,
                "due_date": a.due_date
            }
            for a in meeting.action_items
        ],
        "risks": meeting.risks,
        "open_questions": meeting.open_questions
    }


def validate_meeting_dict(data: Any) -> bool:
    """
    Lightweight validation of meeting intelligence dictionary.
    
    Checks for required fields and basic structure.
    Returns True if valid, False otherwise.
    """
    if not isinstance(data, dict):
        return False
    
    # Required field
    if "summary" not in data or not isinstance(data["summary"], str):
        return False
    
    # Optional but should be lists if present
    for field_name in ["decisions", "action_items", "risks", "open_questions"]:
        if field_name in data and not isinstance(data[field_name], list):
            return False
    
    return True
