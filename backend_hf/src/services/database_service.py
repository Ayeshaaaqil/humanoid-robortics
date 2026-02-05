from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator, List, Optional
from datetime import datetime
from ..models.database import ChatSessionDB, ChatMessageDB, Base
from ..config.settings import settings
import json
import logging

logger = logging.getLogger(__name__)

# Create the database engine globally
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=5,        # Default pool size
    max_overflow=10     # Max overflow connections
)

# Create sessionmaker globally
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)

class DatabaseService:
    """
    Service for managing database operations with Neon PostgreSQL.
    """
    
    def __init__(self):
        # We use the global SessionLocal now
        pass
    
    @contextmanager
    def get_db_session(self) -> Generator:
        """
        Context manager for database sessions.
        """
        db = SessionLocal()
        try:
            yield db
        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            db.rollback()
            raise e
        finally:
            db.close()
    
    def create_session(self, session_id: str, user_id: Optional[str] = None) -> bool:
        """
        Create a new chat session.
        
        Args:
            session_id: Unique identifier for the session
            user_id: Optional user identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_db_session() as db:
                session = ChatSessionDB(
                    session_id=session_id,
                    user_id=user_id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    active=True
                )
                db.add(session)
                db.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error creating session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[ChatSessionDB]:
        """
        Retrieve a chat session by ID.
        
        Args:
            session_id: The session ID to retrieve
            
        Returns:
            ChatSessionDB object if found, None otherwise
        """
        try:
            with self.get_db_session() as db:
                session = db.query(ChatSessionDB).filter(ChatSessionDB.session_id == session_id).first()
                return session
        except SQLAlchemyError as e:
            logger.error(f"Error getting session: {e}")
            return None
    
    def deactivate_session(self, session_id: str) -> bool:
        """
        Deactivate a chat session.
        
        Args:
            session_id: The session ID to deactivate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_db_session() as db:
                session = db.query(ChatSessionDB).filter(ChatSessionDB.session_id == session_id).first()
                if session:
                    session.active = False
                    session.updated_at = datetime.utcnow()
                    db.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"Error deactivating session: {e}")
            return False
    
    def save_message(self, message_id: str, session_id: str, role: str, 
                     content: str, sources: Optional[List[dict]] = None) -> bool:
        """
        Save a chat message to the database.
        
        Args:
            message_id: Unique identifier for the message
            session_id: Session ID this message belongs to
            role: 'user' or 'assistant'
            content: The message content
            sources: List of sources used in the response (for assistant messages)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_db_session() as db:
                # Convert sources to JSON string if provided
                sources_json = json.dumps(sources) if sources else None
                
                message = ChatMessageDB(
                    message_id=message_id,
                    session_id=session_id,
                    role=role,
                    content=content,
                    timestamp=datetime.utcnow(),
                    sources=sources_json
                )
                db.add(message)
                db.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error saving message: {e}")
            return False
    
    def get_session_messages(self, session_id: str) -> List[ChatMessageDB]:
        """
        Retrieve all messages for a session.
        
        Args:
            session_id: The session ID to retrieve messages for
            
        Returns:
            List of ChatMessageDB objects
        """
        try:
            with self.get_db_session() as db:
                messages = db.query(ChatMessageDB).filter(
                    ChatMessageDB.session_id == session_id
                ).order_by(ChatMessageDB.timestamp).all()
                return messages
        except SQLAlchemyError as e:
            logger.error(f"Error getting session messages: {e}")
            return []
    
    def get_recent_sessions(self, user_id: str, limit: int = 10) -> List[ChatSessionDB]:
        """
        Retrieve recent sessions for a user.
        
        Args:
            user_id: The user ID to retrieve sessions for
            limit: Maximum number of sessions to return
            
        Returns:
            List of ChatSessionDB objects
        """
        try:
            with self.get_db_session() as db:
                sessions = db.query(ChatSessionDB).filter(
                    ChatSessionDB.user_id == user_id
                ).order_by(ChatSessionDB.updated_at.desc()).limit(limit).all()
                return sessions
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent sessions: {e}")
            return []
