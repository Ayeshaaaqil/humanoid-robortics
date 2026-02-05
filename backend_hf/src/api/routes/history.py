from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from src.services.database_service import DatabaseService


router = APIRouter()

# Response models
class GetChatHistoryResponse(BaseModel):
    session_id: str
    messages: list[dict]


@router.get("/history/{session_id}", response_model=GetChatHistoryResponse, operation_id="get_chat_history_v1")
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
                import json
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


@router.delete("/session/{session_id}", response_model=DeleteSessionResponse, operation_id="delete_session_v1")
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