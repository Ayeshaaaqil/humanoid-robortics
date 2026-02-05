from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class DocumentChunk(BaseModel):
    """
    Represents a chunk of the book content that has been processed and embedded for retrieval.
    """
    chunk_id: str
    document_id: str
    content: str
    metadata: Dict[str, Any]  # Additional information (chapter, section, file_path, etc.)
    embedding: Optional[list] = None  # The vector representation of the content
    created_at: datetime
    updated_at: datetime


class Document(BaseModel):
    """
    Represents a source document (e.g., a book chapter) that has been processed.
    """
    document_id: str
    title: str
    file_path: str
    version: str
    checksum: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime