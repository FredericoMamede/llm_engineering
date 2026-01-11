"""
Schema definitions for meeting intelligence output.

Defines the structure of extracted meeting information.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class ActionItem:
    """An action item from the meeting"""
    item: str
    owner: str
    due_date: Optional[str] = None
    priority: Optional[str] = None  # "high", "medium", "low"


@dataclass
class Decision:
    """A decision made during the meeting"""
    decision: str
    rationale: Optional[str] = None
    impact: Optional[str] = None


@dataclass
class Topic:
    """A topic discussed in the meeting"""
    topic: str
    summary: str
    duration_minutes: Optional[int] = None


@dataclass
class MeetingIntelligence:
    """Complete structured output from meeting analysis"""
    # Basic info
    title: str
    date: Optional[str] = None
    duration_minutes: Optional[int] = None
    
    # Participants
    attendees: List[str] = field(default_factory=list)
    organizer: Optional[str] = None
    
    # Content
    summary: str
    topics: List[Topic] = field(default_factory=list)
    decisions: List[Decision] = field(default_factory=list)
    action_items: List[ActionItem] = field(default_factory=list)
    
    # Metadata
    key_insights: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


def meeting_to_dict(meeting: MeetingIntelligence) -> Dict[str, Any]:
    """Convert MeetingIntelligence to dictionary for JSON serialization"""
    return {
        "title": meeting.title,
        "date": meeting.date,
        "duration_minutes": meeting.duration_minutes,
        "attendees": meeting.attendees,
        "organizer": meeting.organizer,
        "summary": meeting.summary,
        "topics": [
            {
                "topic": t.topic,
                "summary": t.summary,
                "duration_minutes": t.duration_minutes
            }
            for t in meeting.topics
        ],
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
                "item": a.item,
                "owner": a.owner,
                "due_date": a.due_date,
                "priority": a.priority
            }
            for a in meeting.action_items
        ],
        "key_insights": meeting.key_insights,
        "next_steps": meeting.next_steps,
        "metadata": meeting.metadata
    }
