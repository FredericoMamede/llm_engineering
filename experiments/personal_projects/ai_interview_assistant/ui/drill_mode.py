"""
Drill Mode: Iterative questioning with conversation history.

This module provides conversation state management for drill/practice sessions.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""
    question: str
    answer: str
    mode: str
    timestamp: str
    evaluation: Optional[Dict[str, Any]] = None


@dataclass
class DrillSession:
    """A drill/practice session with conversation history."""
    session_id: str
    started_at: str
    turns: List[ConversationTurn] = field(default_factory=list)
    current_topic: Optional[str] = None
    
    def add_turn(
        self,
        question: str,
        answer: str,
        mode: str,
        evaluation: Optional[Dict[str, Any]] = None
    ):
        """Add a conversation turn."""
        turn = ConversationTurn(
            question=question,
            answer=answer,
            mode=mode,
            timestamp=datetime.now().isoformat(),
            evaluation=evaluation
        )
        self.turns.append(turn)
    
    def get_context_summary(self, max_turns: int = 3) -> str:
        """Get a summary of recent conversation for context."""
        if not self.turns:
            return ""
        
        recent_turns = self.turns[-max_turns:]
        context_parts = []
        
        for turn in recent_turns:
            context_parts.append(f"Q: {turn.question}")
            context_parts.append(f"A: {turn.answer[:200]}...")
        
        return "\n\n".join(context_parts)


class DrillModeManager:
    """Manages drill mode sessions and conversation history."""
    
    def __init__(self, sessions_dir: Optional[Path] = None):
        """
        Initialize drill mode manager.
        
        Args:
            sessions_dir: Directory to store session data (optional)
        """
        if sessions_dir is None:
            sessions_dir = Path(__file__).parent.parent / "data" / "sessions"
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session: Optional[DrillSession] = None
    
    def start_session(self, initial_topic: Optional[str] = None) -> str:
        """Start a new drill session."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_session = DrillSession(
            session_id=session_id,
            started_at=datetime.now().isoformat(),
            current_topic=initial_topic
        )
        return session_id
    
    def end_session(self):
        """End the current session and save it."""
        if self.current_session:
            self._save_session(self.current_session)
            self.current_session = None
    
    def add_turn(
        self,
        question: str,
        answer: str,
        mode: str,
        evaluation: Optional[Dict[str, Any]] = None
    ):
        """Add a turn to the current session."""
        if not self.current_session:
            self.start_session()
        
        self.current_session.add_turn(question, answer, mode, evaluation)
    
    def get_conversation_context(self, max_turns: int = 3) -> str:
        """Get conversation context for follow-up questions."""
        if not self.current_session:
            return ""
        
        return self.current_session.get_context_summary(max_turns)
    
    def _save_session(self, session: DrillSession):
        """Save a session to disk."""
        session_file = self.sessions_dir / f"{session.session_id}.json"
        
        session_data = {
            "session_id": session.session_id,
            "started_at": session.started_at,
            "current_topic": session.current_topic,
            "turns": [
                {
                    "question": turn.question,
                    "answer": turn.answer,
                    "mode": turn.mode,
                    "timestamp": turn.timestamp,
                    "evaluation": turn.evaluation
                }
                for turn in session.turns
            ]
        }
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    def load_session(self, session_id: str) -> Optional[DrillSession]:
        """Load a session from disk."""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        session = DrillSession(
            session_id=session_data["session_id"],
            started_at=session_data["started_at"],
            current_topic=session_data.get("current_topic")
        )
        
        for turn_data in session_data.get("turns", []):
            session.add_turn(
                question=turn_data["question"],
                answer=turn_data["answer"],
                mode=turn_data["mode"],
                evaluation=turn_data.get("evaluation")
            )
        
        return session
