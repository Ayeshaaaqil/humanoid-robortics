import os
import logging
from typing import List, Dict, Any
from pathlib import Path
from ..services.embedding_service import EmbeddingService
from ..services.improved_retrieval_service import ImprovedRetrievalService
from ..services.improved_ingestion_service import AdvancedTextChunker


class IngestionService:
    """
    Service for ingesting documents from the Docusaurus book and processing them for RAG.
    Updated to use improved chunking, storage, and embedding services.
    """

    def __init__(self):
        # Use the improved text chunker with proper parameters
        self.chunker = AdvancedTextChunker(chunk_size=500, overlap=75)  # Within 400-600 token range
        self.embedding_service = EmbeddingService()
        self.retrieval_service = ImprovedRetrievalService()

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def ingest_documents(self, document_paths: List[str], force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Ingests documents and processes them for RAG with improved chunking and storage.

        Args:
            document_paths: List of paths to documents to be processed
            force_reprocess: Whether to reprocess documents even if they already exist

        Returns:
            Dictionary with processing results
        """
        processed_documents = []
        failed_documents = []
        total_chunks_created = 0
        total_chunks_stored = 0

        for path in document_paths:
            try:
                # Check if file exists
                if not os.path.exists(path):
                    failed_documents.append(f"File not found: {path}")
                    self.logger.error(f"File not found: {path}")
                    continue

                # Process the document based on its type
                if path.endswith(('.md', '.mdx', '.txt', '.html', '.htm')):
                    result = self._process_document(path, force_reprocess)
                    processed_documents.append({
                        "path": path,
                        "chunks_created": result["chunks_created"],
                        "chunks_stored": result["chunks_stored"]
                    })
                    total_chunks_created += result["chunks_created"]
                    total_chunks_stored += result["chunks_stored"]
                    self.logger.info(f"Successfully processed {path}: {result['chunks_created']} chunks created, {result['chunks_stored']} stored")
                else:
                    failed_documents.append(f"Unsupported file type: {path}")
                    self.logger.warning(f"Unsupported file type: {path}")
            except Exception as e:
                error_msg = f"Error processing {path}: {str(e)}"
                failed_documents.append(error_msg)
                self.logger.error(error_msg)
                import traceback
                self.logger.error(traceback.format_exc())

        result = {
            "status": "success",
            "processed_documents": processed_documents,
            "failed_documents": failed_documents,
            "total_chunks_created": total_chunks_created,
            "total_chunks_stored": total_chunks_stored,
            "message": f"Processed {len(processed_documents)} documents, {len(failed_documents)} failed. "
                      f"Created {total_chunks_created} chunks, stored {total_chunks_stored} in Qdrant"
        }

        self.logger.info(result["message"])
        return result

    def _process_document(self, file_path: str, force_reprocess: bool = False) -> Dict[str, int]:
        """
        Process a document into chunks for RAG with improved chunking.

        Args:
            file_path: Path to the document file
            force_reprocess: Whether to reprocess even if already processed

        Returns:
            Dictionary with counts of created and stored chunks
        """
        # Read the document file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # Extract document metadata
        document_title = Path(file_path).stem
        document_id = f"doc_{hash(file_path)}_{str(Path(file_path).stem)}"

        self.logger.info(f"Processing document: {document_title} (ID: {document_id})")

        # Prepare document metadata
        doc_metadata = {
            "title": document_title,
            "file_path": file_path,
            "document_id": document_id
        }

        # Chunk the content with overlap and context preservation
        chunks = self.chunker.chunk_text(content, doc_metadata)

        self.logger.info(f"Created {len(chunks)} chunks for document {document_title}")

        # Add document-specific metadata to each chunk
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                "content": chunk["content"],
                "document_id": document_id,
                "metadata": {
                    **chunk["metadata"],  # Include chunk-specific metadata
                    "title": document_title,
                    "file_path": file_path,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                },
                "chunk_id": f"{document_id}_chunk_{i}"
            }
            processed_chunks.append(chunk_data)

        # Generate embeddings for the chunks
        try:
            processed_chunks_with_embeddings = self.embedding_service.embed_document_chunks(processed_chunks)
            self.logger.info(f"Successfully generated embeddings for {len(processed_chunks)} chunks")
        except Exception as e:
            self.logger.error(f"Error generating embeddings for document {document_title}: {e}")
            raise

        # Store the chunks in Qdrant
        success = self.retrieval_service.store_chunks(processed_chunks_with_embeddings)

        if success:
            self.logger.info(f"Successfully stored {len(processed_chunks)} chunks for document {document_title} in Qdrant")
        else:
            self.logger.error(f"Failed to store chunks for document {document_title} in Qdrant")
            raise Exception("Failed to store chunks in Qdrant")

        return {
            "chunks_created": len(processed_chunks),
            "chunks_stored": len(processed_chunks) if success else 0
        }