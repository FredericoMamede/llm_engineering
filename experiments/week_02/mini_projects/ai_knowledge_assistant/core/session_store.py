"""
Session store: SQLite-backed persistence for sessions and transcripts.
"""


import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SessionStore:
    """SQLite-backed session store."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.enabled = True
        
        # Default to data/sessions.db relative to this file
        if db_path is None:
            base_dir = Path(__file__).parent.parent / "data"
            base_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(base_dir / "sessions.db")
        
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_id
                ON messages (session_id)
            """)
            conn.commit()

    def save_message(self, session_id: str, role: str, content: str) -> None:
        """Store a message in the database."""
        if not self.enabled:
            return
        
        timestamp = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, role, content, timestamp),
            )
            conn.commit()

    def load_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT role, content, timestamp
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (session_id, limit),
            )
            rows = cursor.fetchall()
        
        return [
            {"role": row[0], "content": row[1], "timestamp": row[2]}
            for row in rows
        ]

    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent sessions with metadata."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT session_id, MIN(timestamp) as started, MAX(timestamp) as last_activity, COUNT(*) as message_count
                FROM messages
                GROUP BY session_id
                ORDER BY last_activity DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
        
        return [
            {
                "session_id": row[0],
                "started": row[1],
                "last_activity": row[2],
                "message_count": row[3],
            }
            for row in rows
        ]

    def delete_session(self, session_id: str) -> int:
        """Delete all messages for a session. Returns count deleted."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM messages WHERE session_id = ?",
                (session_id,),
            )
            conn.commit()
            return cursor.rowcount

    def ensure(self) -> None:
        """Ensure database is ready (re-init if needed)."""
        self._init_db()
