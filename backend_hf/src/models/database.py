from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Optional


Base = declarative_base()


class ChatSessionDB(Base):
    """
    Database model for chat sessions.
    """
    __tablename__ = "chat_sessions"
    
    session_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Optional user identifier
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)


class ChatMessageDB(Base):
    """
    Database model for chat messages.
    """
    __tablename__ = "chat_messages"
    
    message_id = Column(String, primary_key=True, index=True)
    session_id = Column(String, index=True)  # Foreign key to chat_sessions
    role = Column(String)  # 'user' or 'assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sources = Column(Text)  # JSON string of sources used in the response