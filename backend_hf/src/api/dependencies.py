from fastapi import Depends
from typing import Generator
from functools import lru_cache
from src.services.database_service import DatabaseService
from src.services.embedding_service import EmbeddingService
from src.services.retrieval_service import RetrievalService
from src.services.generation_service import GenerationService
import logging

logger = logging.getLogger(__name__)

@lru_cache()
def get_embedding_service() -> EmbeddingService:
    return EmbeddingService()

def get_retrieval_service():
    """
    Returns a RetrievalService instance, but handles initialization errors gracefully.
    """
    try:
        from src.services.retrieval_service import RetrievalService
        return RetrievalService()
    except Exception as e:
        logger.error(f"Failed to initialize RetrievalService: {e}")
        # Re-raise the exception so it can be caught by the fallback in chat.py
        raise

@lru_cache()
def get_generation_service() -> GenerationService:
    return GenerationService()

def get_db_service() -> DatabaseService:
    """
    Returns a DatabaseService instance.
    Note: DatabaseService methods now use get_db_session internally context managers,
    so we don't strictly need to inject the session into the service instance itself
    if we keep the current design of DatabaseService.

    However, the current design of DatabaseService uses `self.get_db_session()` which uses global `SessionLocal`.
    So creating a new instance is cheap (it has no state).
    """
    return DatabaseService()
