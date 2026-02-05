from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from src.models.document import Document
from src.services.improved_ingestion_service import ImprovedIngestionService
from pydantic import BaseModel
import logging


router = APIRouter()

# Setup logging
logger = logging.getLogger(__name__)

# Request models
class IngestRequest(BaseModel):
    document_paths: list[str]
    force_reprocess: bool = False


@router.post("/ingest")
async def ingest_documents(request: IngestRequest) -> Dict[str, Any]:
    """
    Ingest documents with improved chunking, embedding, and storage.
    """
    try:
        # Use the improved ingestion service
        ingestion_service = ImprovedIngestionService()

        # Process documents with the improved service
        result = ingestion_service.ingest_documents(
            document_paths=request.document_paths,
            force_reprocess=request.force_reprocess
        )

        logger.info(f"Ingestion completed: {result['message']}")
        return result

    except Exception as e:
        logger.error(f"Error ingesting documents: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error ingesting documents: {str(e)}")