"""
Weakness tracking: Local JSON persistence for missed concepts.

Tracks concepts that candidates struggle with based on evaluation feedback.
"""

from typing import List, Dict, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
from pathlib import Path


@dataclass
class WeaknessEntry:
    """A tracked weakness/concept."""
    concept: str
    first_seen: str
    last_seen: str
    occurrences: int = 1
    related_questions: List[str] = field(default_factory=list)
    related_topics: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "concept": self.concept,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "occurrences": self.occurrences,
            "related_questions": self.related_questions,
            "related_topics": list(self.related_topics)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeaknessEntry":
        """Create from dictionary."""
        return cls(
            concept=data["concept"],
            first_seen=data["first_seen"],
            last_seen=data["last_seen"],
            occurrences=data.get("occurrences", 1),
            related_questions=data.get("related_questions", []),
            related_topics=set(data.get("related_topics", []))
        )


class WeaknessTracker:
    """Tracks and persists candidate weaknesses."""
    
    def __init__(self, weaknesses_file: Optional[Path] = None):
        """
        Initialize weakness tracker.
        
        Args:
            weaknesses_file: Path to JSON file for persistence (optional)
        """
        if weaknesses_file is None:
            weaknesses_file = Path(__file__).parent.parent / "data" / "weaknesses.json"
        self.weaknesses_file = Path(weaknesses_file)
        self.weaknesses_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.weaknesses: Dict[str, WeaknessEntry] = {}
        self._load()
    
    def _load(self):
        """Load weaknesses from disk."""
        if not self.weaknesses_file.exists():
            return
        
        try:
            with open(self.weaknesses_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for concept, entry_data in data.items():
                self.weaknesses[concept] = WeaknessEntry.from_dict(entry_data)
        except Exception:
            # If loading fails, start fresh
            self.weaknesses = {}
    
    def _save(self):
        """Save weaknesses to disk."""
        data = {
            concept: entry.to_dict()
            for concept, entry in self.weaknesses.items()
        }
        
        with open(self.weaknesses_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def record_missed_concepts(
        self,
        concepts: List[str],
        question: str,
        topic: Optional[str] = None
    ):
        """
        Record missed concepts from an evaluation.
        
        Args:
            concepts: List of missed concepts
            question: The question that revealed these weaknesses
            topic: Optional topic/category
        """
        now = datetime.now().isoformat()
        
        for concept in concepts:
            concept_lower = concept.lower().strip()
            
            if concept_lower in self.weaknesses:
                # Update existing entry
                entry = self.weaknesses[concept_lower]
                entry.last_seen = now
                entry.occurrences += 1
                if question not in entry.related_questions:
                    entry.related_questions.append(question)
                if topic:
                    entry.related_topics.add(topic)
            else:
                # Create new entry
                self.weaknesses[concept_lower] = WeaknessEntry(
                    concept=concept,
                    first_seen=now,
                    last_seen=now,
                    occurrences=1,
                    related_questions=[question],
                    related_topics={topic} if topic else set()
                )
        
        self._save()
    
    def get_weaknesses(self, min_occurrences: int = 1) -> List[WeaknessEntry]:
        """
        Get tracked weaknesses.
        
        Args:
            min_occurrences: Minimum number of occurrences to include
        
        Returns:
            List of weakness entries, sorted by occurrences (descending)
        """
        weaknesses = [
            entry for entry in self.weaknesses.values()
            if entry.occurrences >= min_occurrences
        ]
        
        return sorted(weaknesses, key=lambda x: x.occurrences, reverse=True)
    
    def get_weakness_summary(self, top_n: int = 10) -> str:
        """
        Get a formatted summary of top weaknesses.
        
        Args:
            top_n: Number of weaknesses to include
        
        Returns:
            Formatted markdown string
        """
        weaknesses = self.get_weaknesses()[:top_n]
        
        if not weaknesses:
            return "No tracked weaknesses yet. Keep practicing!"
        
        lines = ["## Tracked Weaknesses\n"]
        
        for i, entry in enumerate(weaknesses, 1):
            lines.append(
                f"**{i}. {entry.concept}**\n"
                f"- Occurrences: {entry.occurrences}\n"
                f"- First seen: {entry.first_seen[:10]}\n"
                f"- Last seen: {entry.last_seen[:10]}"
            )
            
            if entry.related_topics:
                topics = ", ".join(sorted(entry.related_topics))
                lines.append(f"- Topics: {topics}")
            
            if entry.related_questions:
                lines.append(f"- Related questions: {len(entry.related_questions)}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def clear_weakness(self, concept: str):
        """Remove a tracked weakness."""
        concept_lower = concept.lower().strip()
        if concept_lower in self.weaknesses:
            del self.weaknesses[concept_lower]
            self._save()
    
    def clear_all(self):
        """Clear all tracked weaknesses."""
        self.weaknesses = {}
        self._save()
