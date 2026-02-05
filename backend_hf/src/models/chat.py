from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatSession(BaseModel):
    """
    Represents a conversation session between a user and the chatbot.
    """
    session_id: str
    user_id: Optional[str] = None  # Identifier for the user (if available)
    created_at: datetime
    updated_at: datetime
    active: bool = True


class ChatMessage(BaseModel):
    """
    Represents a single message in a chat conversation.
    """
    message_id: str
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    sources: Optional[List[Dict[str, Any]]] = None  # References to document chunks used in the response