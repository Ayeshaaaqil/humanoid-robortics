from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from src.models.chat import ChatMessage
from src.services.ingestion_service import IngestionService
from src.services.embedding_service import EmbeddingService
from src.services.retrieval_service import RetrievalService
from src.services.mock_retrieval_service import MockRetrievalService
from src.services.generation_service import GenerationService
from src.services.database_service import DatabaseService
from src.api.dependencies import get_embedding_service, get_generation_service, get_db_service
from src.config.settings import settings
import json
import logging

logger = logging.getLogger(__name__)


router = APIRouter()

# Request/Response models
class ChatRequest(BaseModel):
    session_id: str
    message: str
    mode: str = "full-book"  # "full-book" or "selected-text"
    selected_text: str = ""  # Required when mode is "selected-text"


class ChatResponse(BaseModel):
    session_id: str
    response: str
    sources: List[Dict[str, Any]]
    timestamp: str


def get_retrieval_service():
    """
    Dependency that returns a retrieval service, falling back to mock if the real one fails.
    """
    try:
        from src.api.dependencies import get_retrieval_service as get_real_retrieval_service
        return get_real_retrieval_service()
    except Exception as e:
        logger.warning(f"Real retrieval service failed: {e}. Falling back to mock service.")
        return MockRetrievalService()


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    embedding_service: EmbeddingService = Depends(get_embedding_service),
    generation_service: GenerationService = Depends(get_generation_service),
    db_service: DatabaseService = Depends(get_db_service)
) -> ChatResponse:
    """
    Main endpoint for chat interactions with the RAG system.
    """
    try:
        # Get retrieval service (real or mock)
        retrieval_service = get_retrieval_service()

        # Check if session exists, create if not
        existing_session = db_service.get_session(request.session_id)
        if not existing_session:
            db_service.create_session(request.session_id)

        # Save user message to database
        user_message_id = str(uuid4())
        db_service.save_message(
            message_id=user_message_id,
            session_id=request.session_id,
            role="user",
            content=request.message
        )

        # Generate embedding for the user's message
        query_embedding = embedding_service.embed_text(request.message)

        # Retrieve relevant chunks based on the query
        relevant_chunks = []

        if request.mode == "selected-text" and request.selected_text:
            # Use only the selected text for context
            relevant_chunks = retrieval_service.retrieve_by_selected_text(
                request.selected_text, embedding_service
            )
        else:
            # Use the full book for context
            relevant_chunks = retrieval_service.retrieve_relevant_chunks(
                query_embedding, limit=5
            )

        # Generate the answer using the retrieved context
        answer = generation_service.generate_answer(
            query=request.message,
            context_chunks=relevant_chunks,
            mode=request.mode
        )

        # Save assistant response to database
        assistant_message_id = str(uuid4())
        db_service.save_message(
            message_id=assistant_message_id,
            session_id=request.session_id,
            role="assistant",
            content=answer,
            sources=relevant_chunks
        )

        # Format the response
        response = ChatResponse(
            session_id=request.session_id,
            response=answer,
            sources=[{
                "chunk_id": chunk["chunk_id"],
                "content_snippet": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"],
                "document_id": chunk["document_id"],
                "metadata": chunk["metadata"]
            } for chunk in relevant_chunks],
            timestamp=datetime.now().isoformat()
        )

        return response
    except Exception as e:
        import traceback
        logger.error(f"Error processing chat request: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")


class GetChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]


@router.get("/history/{session_id}", response_model=GetChatHistoryResponse)
async def get_chat_history(session_id: str) -> GetChatHistoryResponse:
    """
    Retrieves chat history for a specific session.
    """
    try:
        db_service = DatabaseService()

        # Get messages from database
        db_messages = db_service.get_session_messages(session_id)

        # Convert to the expected format
        messages = []
        for db_msg in db_messages:
            msg_dict = {
                "message_id": db_msg.message_id,
                "session_id": db_msg.session_id,
                "role": db_msg.role,
                "content": db_msg.content,
                "timestamp": db_msg.timestamp.isoformat()
            }

            # Add sources if it's an assistant message
            if db_msg.role == "assistant" and db_msg.sources:
                try:
                    msg_dict["sources"] = json.loads(db_msg.sources)
                except json.JSONDecodeError:
                    msg_dict["sources"] = []

            messages.append(msg_dict)

        return GetChatHistoryResponse(
            session_id=session_id,
            messages=messages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")


class DeleteSessionResponse(BaseModel):
    status: str
    message: str


@router.delete("/session/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(session_id: str) -> DeleteSessionResponse:
    """
    Deletes a chat session and its history.
    """
    try:
        db_service = DatabaseService()

        # In a real implementation, we would delete the session and messages from the database
        # For now, we'll just deactivate the session
        success = db_service.deactivate_session(session_id)

        if success:
            return DeleteSessionResponse(
                status="success",
                message="Session deactivated successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")