"""
Interactive Session Memory for Multitemporal Change Intelligence.
Caches the complete TemporalChangeScene so follow-up questions, filters,
and spatial queries reuse the stored representation without re-running models.
"""

import time
from typing import Dict, List, Optional
from ..schemas import ChangeRegion, TemporalChangeScene


class SessionState:
    """Stores the complete change scene and active conversational context."""

    def __init__(self, session_id: str, scene: TemporalChangeScene):
        self.session_id = session_id
        self.scene = scene
        self.created_at = time.time()
        self.last_accessed = time.time()
        self.history: List[Dict[str, str]] = []  # List of {"role": "user"|"agent", "content": "..."}
        self.active_regions: List[ChangeRegion] = list(scene.regions)
        self.active_category: Optional[str] = None
        self.active_change_type: Optional[str] = None


class ChangeSessionManager:
    """
    In-memory session registry with automated TTL expiration.
    """

    def __init__(self, ttl_seconds: int = 3600):
        self._sessions: Dict[str, SessionState] = {}
        self.ttl_seconds = ttl_seconds

    def create_session(self, session_id: str, scene: TemporalChangeScene) -> SessionState:
        """Create or replace a session with a fresh scene representation."""
        state = SessionState(session_id=session_id, scene=scene)
        self._sessions[session_id] = state
        self._clean_expired()
        return state

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Retrieve existing session and update access timestamp."""
        state = self._sessions.get(session_id)
        if state:
            state.last_accessed = time.time()
        return state

    def add_interaction(self, session_id: str, user_question: str, agent_response: str):
        """Append to dialogue history."""
        state = self.get_session(session_id)
        if state:
            state.history.append({"role": "user", "content": user_question})
            state.history.append({"role": "agent", "content": agent_response})

    def update_active_selection(
        self,
        session_id: str,
        regions: List[ChangeRegion],
        category: Optional[str] = None,
        change_type: Optional[str] = None
    ):
        """Update active subset of regions for contextual follow-up questions."""
        state = self.get_session(session_id)
        if state:
            state.active_regions = regions
            state.active_category = category
            state.active_change_type = change_type

    def _clean_expired(self):
        """Evict sessions that exceed TTL."""
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if (now - s.last_accessed) > self.ttl_seconds]
        for sid in expired:
            del self._sessions[sid]


# Global singleton instance
session_manager = ChangeSessionManager()
