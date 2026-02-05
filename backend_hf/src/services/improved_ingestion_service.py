import os
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
from ..config.settings import settings
from ..services.embedding_service import EmbeddingService
from ..services.retrieval_service import RetrievalService


class AdvancedTextChunker:
    """
    Advanced text chunker that meets the specified requirements:
    - Chunk size: 400-600 tokens
    - Overlap: 50-100 tokens
    - Preserves sentence boundaries
    - Removes empty or duplicate chunks
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 75):
        """
        Initialize the chunker with specified parameters.

        Args:
            chunk_size: Target chunk size in tokens (400-600 tokens as per requirements)
            overlap: Overlap size in tokens (50-100 tokens as per requirements)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        # Approximate tokenization: 1 token ~ 4 characters for English text
        self.char_per_token = 4
        self.max_chunk_chars = chunk_size * self.char_per_token
        self.overlap_chars = overlap * self.char_per_token

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in the text.
        This is a simple estimation: 1 token ~ 4 characters for English text.
        """
        return len(text) // self.char_per_token

    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Chunk the text according to the specified requirements.

        Args:
            text: The text to chunk
            metadata: Additional metadata to include with each chunk

        Returns:
            List of chunks with content and metadata
        """
        if not text or not text.strip():
            self.logger.warning("Empty text provided for chunking")
            return []

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        chunks = []
        start_idx = 0

        while start_idx < len(text):
            # Determine the end index for the current chunk
            end_idx = start_idx + self.max_chunk_chars

            # If we're at the end of the text, take the remaining part
            if end_idx >= len(text):
                chunk_text = text[start_idx:]
            else:
                # Find the chunk of text
                chunk_text = text[start_idx:end_idx]

                # Try to break at sentence boundary
                last_sentence_end = max(
                    chunk_text.rfind('. ', 0, -10),  # Prefer period
                    chunk_text.rfind('? ', 0, -10),  # Then question mark
                    chunk_text.rfind('! ', 0, -10),  # Then exclamation mark
                    chunk_text.rfind('. ', 0, -10)   # Fallback to period again
                )

                if last_sentence_end > len(chunk_text) // 2:  # Only if it's not too early
                    end_idx = start_idx + last_sentence_end + 2
                    chunk_text = text[start_idx:end_idx]
                else:
                    # If no good sentence break found, try word boundary
                    last_space = chunk_text.rfind(' ', len(chunk_text) // 2, -10)
                    if last_space > 0:
                        end_idx = start_idx + last_space
                        chunk_text = text[start_idx:end_idx]

            # Create chunk with metadata
            chunk = {
                "content": chunk_text.strip(),
                "metadata": {
                    "start_pos": start_idx,
                    "end_pos": end_idx,
                    "chunk_index": len(chunks),
                    "token_count": self.estimate_tokens(chunk_text),
                    **(metadata or {})
                }
            }

            # Add the chunk if it's not empty
            if chunk["content"].strip():
                chunks.append(chunk)

            # Move start index with overlap
            if end_idx >= len(text):
                break  # We've reached the end

            # Calculate next start position with overlap
            # Only apply overlap if we have enough text remaining
            remaining_chars = len(text) - end_idx
            if remaining_chars > self.max_chunk_chars // 2:  # Only if remaining text is substantial
                overlap_start = end_idx - self.overlap_chars
                start_idx = max(overlap_start, start_idx + 1)  # Ensure we move forward
            else:
                # For the last chunk, don't apply overlap if remaining text is too small
                start_idx = end_idx

        # Remove empty or duplicate chunks
        chunks = self._remove_empty_and_duplicate_chunks(chunks)

        self.logger.info(f"Text chunked into {len(chunks)} chunks")
        return chunks

    def _remove_empty_and_duplicate_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove empty chunks and duplicate chunks.

        Args:
            chunks: List of chunks to clean

        Returns:
            Cleaned list of chunks
        """
        seen_content = set()
        cleaned_chunks = []

        for chunk in chunks:
            content = chunk["content"].strip()

            # Skip empty chunks
            if not content:
                continue

            # Skip duplicate chunks
            content_hash = hash(content)
            if content_hash in seen_content:
                continue

            seen_content.add(content_hash)
            cleaned_chunks.append(chunk)

        if len(cleaned_chunks) < len(chunks):
            removed_count = len(chunks) - len(cleaned_chunks)
            self.logger.info(f"Removed {removed_count} empty or duplicate chunks")

        return cleaned_chunks


class ImprovedIngestionService:
    """
    Improved ingestion service that follows all the specified requirements:
    - Proper chunking with overlap
    - Correct Qdrant storage
    - Proper embedding
    - Comprehensive logging
    """

    def __init__(self):
        self.chunker = AdvancedTextChunker(chunk_size=500, overlap=75)  # Within 400-600 token range
        self.embedding_service = EmbeddingService()
        self.retrieval_service = RetrievalService()

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Validate that the Qdrant collection exists and has correct vector dimensions
        self._validate_qdrant_collection()

    def _validate_qdrant_collection(self):
        """
        Validate that the Qdrant collection exists and has the correct vector dimensions.
        """
        try:
            # Check if collection exists and get its info
            collection_info = self.retrieval_service.client.get_collection(
                self.retrieval_service.collection_name
            )

            # The Cohere embed-multilingual-v3.0 model produces 1024-dimensional vectors
            expected_size = 1024
            actual_size = collection_info.config.params.vectors.size

            if actual_size != expected_size:
                self.logger.warning(
                    f"Qdrant collection has vector size {actual_size}, "
                    f"but expected {expected_size}. This may cause issues."
                )
            else:
                self.logger.info(
                    f"Qdrant collection validated with correct vector size: {expected_size}"
                )
        except Exception as e:
            self.logger.error(f"Error validating Qdrant collection: {e}")
            # Collection will be created with correct dimensions when first chunk is stored

    def ingest_documents(self, document_paths: List[str], force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Ingest documents with improved chunking, embedding, and storage.

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
        Process a document into chunks for RAG.

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
        document_id = f"doc_{hash(file_path)}_{str(uuid.uuid4())[:8]}"

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