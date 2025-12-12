"""
Conversation history management for Schedule AI Agent.
Implements storage and retrieval of chat conversations with RAG capabilities.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """Represents a single message in the conversation."""
    timestamp: str
    role: str  # 'user' or 'assistant'
    content: str
    message_type: str = 'text'  # 'text', 'appointment_created', 'appointment_modified', etc.
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ConversationSession:
    """Represents a conversation session with all messages."""
    session_id: str
    created_at: str
    updated_at: str
    messages: List[ConversationMessage]
    user_info: Optional[Dict[str, Any]] = None
    appointment_history: Optional[List[Dict[str, Any]]] = None

class ConversationHistoryManager:
    """Manages conversation history with RAG capabilities."""

    def __init__(self, storage_path: str = "conversation_history"):
        """
        Initialize conversation history manager.

        Args:
            storage_path: Directory path to store conversation data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.sessions_file = self.storage_path / "sessions.json"
        self.sessions_dir = self.storage_path / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)

        # Load existing sessions index
        self._load_sessions_index()

    def _load_sessions_index(self):
        """Load the sessions index file."""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.sessions_index = json.load(f)
            except Exception as e:
                logger.error(f"Error loading sessions index: {e}")
                self.sessions_index = {}
        else:
            self.sessions_index = {}

    def _save_sessions_index(self):
        """Save the sessions index file."""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving sessions index: {e}")

    def _get_session_file(self, session_id: str) -> Path:
        """Get the file path for a session."""
        # Use hash to avoid filesystem issues with long session IDs
        session_hash = hashlib.md5(session_id.encode()).hexdigest()
        return self.sessions_dir / f"{session_hash}.json"

    def create_session(self, session_id: str, user_info: Optional[Dict[str, Any]] = None) -> ConversationSession:
        """
        Create a new conversation session.

        Args:
            session_id: Unique session identifier
            user_info: Optional user information

        Returns:
            Created conversation session
        """
        now = datetime.now().isoformat()
        session = ConversationSession(
            session_id=session_id,
            created_at=now,
            updated_at=now,
            messages=[],
            user_info=user_info,
            appointment_history=[]
        )

        # Save session
        self.save_session(session)

        # Update index
        self.sessions_index[session_id] = {
            "created_at": now,
            "updated_at": now,
            "message_count": 0
        }
        self._save_sessions_index()

        logger.info(f"Created new session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Retrieve a conversation session.

        Args:
            session_id: Session identifier

        Returns:
            Conversation session if found, None otherwise
        """
        session_file = self._get_session_file(session_id)

        if not session_file.exists():
            return None

        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Convert messages back to ConversationMessage objects
            messages = []
            for msg_data in session_data.get("messages", []):
                messages.append(ConversationMessage(**msg_data))

            session_data["messages"] = messages

            return ConversationSession(**session_data)

        except Exception as e:
            logger.error(f"Error loading session {session_id}: {e}")
            return None

    def save_session(self, session: ConversationSession):
        """
        Save a conversation session.

        Args:
            session: Conversation session to save
        """
        session.updated_at = datetime.now().isoformat()

        # Convert to dict for JSON serialization
        session_dict = asdict(session)

        # Convert messages to dict format
        session_dict["messages"] = [asdict(msg) for msg in session.messages]

        session_file = self._get_session_file(session.session_id)

        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_dict, f, indent=2, ensure_ascii=False)

            # Update index
            self.sessions_index[session.session_id] = {
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "message_count": len(session.messages)
            }
            self._save_sessions_index()

        except Exception as e:
            logger.error(f"Error saving session {session.session_id}: {e}")

    def add_message(self, session_id: str, role: str, content: str,
                   message_type: str = 'text', metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a message to a conversation session.

        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            message_type: Type of message
            metadata: Optional metadata

        Returns:
            True if message was added successfully, False otherwise
        """
        session = self.get_session(session_id)

        if session is None:
            # Create new session if it doesn't exist
            session = self.create_session(session_id)

        message = ConversationMessage(
            timestamp=datetime.now().isoformat(),
            role=role,
            content=content,
            message_type=message_type,
            metadata=metadata
        )

        session.messages.append(message)
        self.save_session(session)

        logger.info(f"Added {role} message to session {session_id}")
        return True

    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[ConversationMessage]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session identifier
            limit: Optional limit on number of messages to return

        Returns:
            List of conversation messages
        """
        session = self.get_session(session_id)

        if session is None:
            return []

        messages = session.messages

        if limit:
            messages = messages[-limit:]

        return messages

    def search_conversations(self, session_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search through conversation history using simple keyword matching.

        Args:
            session_id: Session identifier
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of matching message contexts with metadata
        """
        session = self.get_session(session_id)

        if session is None:
            return []

        query_lower = query.lower()
        results = []

        for i, message in enumerate(session.messages):
            if query_lower in message.content.lower():
                # Get context (previous 2 messages and next 2 messages)
                start_idx = max(0, i - 2)
                end_idx = min(len(session.messages), i + 3)

                context_messages = session.messages[start_idx:end_idx]

                result = {
                    "matching_message": asdict(message),
                    "context": [asdict(msg) for msg in context_messages],
                    "relevance_score": self._calculate_relevance(message.content, query),
                    "position_in_conversation": i,
                    "total_messages": len(session.messages)
                }

                results.append(result)

        # Sort by relevance score and limit results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def _calculate_relevance(self, text: str, query: str) -> float:
        """
        Calculate a simple relevance score for text matching query.

        Args:
            text: Text to score
            query: Query string

        Returns:
            Relevance score (0.0 to 1.0)
        """
        text_lower = text.lower()
        query_lower = query.lower()

        # Exact match gets highest score
        if query_lower in text_lower:
            return 1.0

        # Partial word matches get lower scores
        query_words = query_lower.split()
        text_words = text_lower.split()

        matches = sum(1 for word in query_words if word in text_lower)
        score = matches / len(query_words) if query_words else 0.0

        return score

    def extract_appointment_info(self, session_id: str) -> Dict[str, Any]:
        """
        Extract appointment-related information from conversation history.

        Args:
            session_id: Session identifier

        Returns:
            Dictionary with extracted appointment information
        """
        session = self.get_session(session_id)

        if session is None:
            return {}

        appointment_info = {
            "user_name": None,
            "user_email": None,
            "service_types": [],
            "mentioned_dates": [],
            "mentioned_times": [],
            "last_appointment": None,
            "appointment_count": 0
        }

        # Extract information from messages
        for message in session.messages:
            content_lower = message.content.lower()

            # Extract email
            if '@' in message.content and not appointment_info["user_email"]:
                words = message.content.split()
                for word in words:
                    if '@' in word and '.' in word:
                        appointment_info["user_email"] = word.strip('.,!?')
                        break

            # Extract name (simple heuristic)
            if message.role == 'user' and not appointment_info["user_name"]:
                # Look for patterns like "Mi chiamo", "Sono", etc.
                if 'mi chiamo' in content_lower:
                    parts = message.content.split('mi chiamo')
                    if len(parts) > 1:
                        name = parts[1].strip().split()[0]
                        appointment_info["user_name"] = name.capitalize()
                elif 'sono' in content_lower:
                    parts = message.content.split('sono')
                    if len(parts) > 1:
                        name_candidate = parts[1].strip().split()[0]
                        if name_candidate.istitle():
                            appointment_info["user_name"] = name_candidate

            # Count appointment creations
            if message.message_type == 'appointment_created':
                appointment_info["appointment_count"] += 1
                if message.metadata:
                    appointment_info["last_appointment"] = message.metadata

        return appointment_info

    def get_recent_context(self, session_id: str, message_count: int = 10) -> str:
        """
        Get recent conversation context as formatted string for agent input.

        Args:
            session_id: Session identifier
            message_count: Number of recent messages to include

        Returns:
            Formatted conversation context
        """
        messages = self.get_conversation_history(session_id, limit=message_count)

        if not messages:
            return "Nessuna conversazione precedente."

        context_parts = ["=== CONTESTO CONVERSAZIONE PRECEDENTE ==="]

        for message in messages:
            role_label = "Utente" if message.role == "user" else "Assistente"
            timestamp = datetime.fromisoformat(message.timestamp).strftime("%H:%M")

            context_parts.append(f"[{timestamp}] {role_label}: {message.content}")

        context_parts.append("=== FINE CONTESTO ===")

        return "\n".join(context_parts)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a conversation session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted successfully, False otherwise
        """
        session_file = self._get_session_file(session_id)

        try:
            if session_file.exists():
                session_file.unlink()

            # Remove from index
            if session_id in self.sessions_index:
                del self.sessions_index[session_id]
                self._save_sessions_index()

            logger.info(f"Deleted session: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            return False

    def get_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all sessions.

        Returns:
            Dictionary with session information
        """
        return self.sessions_index.copy()

# Global conversation history manager instance
conversation_manager = ConversationHistoryManager()