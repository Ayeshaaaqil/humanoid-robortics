from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
from ..config.settings import settings
import uuid
import logging


class ImprovedRetrievalService:
    """
    Improved service for retrieving relevant documents using Qdrant.
    Ensures collection is created with correct parameters.
    """

    def __init__(self):
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize Qdrant client
        if settings.QDRANT_CLIENT_API_KEY:
            self.client = QdrantClient(
                url=settings.QDRANT_CLIENT_URL,
                api_key=settings.QDRANT_CLIENT_API_KEY,
                prefer_grpc=False  # Using REST API to avoid compatibility issues
            )
        else:
            self.client = QdrantClient(url=settings.QDRANT_CLIENT_URL)

        # Define collection name - using a consistent name as per requirements
        self.collection_name = "document_chunks"  # Or use a setting if you prefer

        # Create collection if it doesn't exist
        self._create_collection()

    def _create_collection(self):
        """
        Create the Qdrant collection if it doesn't exist with correct parameters.
        """
        try:
            # Check if collection exists
            collection_info = self.client.get_collection(self.collection_name)
            self.logger.info(f"Collection '{self.collection_name}' already exists with {collection_info.points_count} points")
        except Exception:
            # Collection doesn't exist, create it with correct parameters
            # Cohere embed-multilingual-v3.0 produces 1024-dimensional vectors
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
            )
            self.logger.info(f"Collection '{self.collection_name}' created successfully with 1024-dimensional vectors")

    def store_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Store document chunks in Qdrant with validation.

        Args:
            chunks: List of document chunks with embeddings

        Returns:
            True if successful, False otherwise
        """
        try:
            points = []
            for chunk in chunks:
                # Validate embedding dimensions
                embedding = chunk.get("embedding", [])
                if not embedding:
                    self.logger.error(f"Chunk missing embedding: {chunk.get('chunk_id', 'unknown')}")
                    continue
                
                if len(embedding) != 1024:  # Cohere embed-multilingual-v3.0 dimensions
                    self.logger.error(f"Invalid embedding dimension {len(embedding)} for chunk {chunk.get('chunk_id', 'unknown')}, expected 1024")
                    continue

                # Generate a unique ID for the point
                point_id = str(uuid.uuid4())
                
                points.append(
                    models.PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload={
                            "content": chunk["content"],
                            "document_id": chunk.get("document_id", ""),
                            "metadata": chunk.get("metadata", {}),
                            "chunk_id": chunk.get("chunk_id", point_id)
                        }
                    )
                )

            if not points:
                self.logger.warning("No valid points to store in Qdrant")
                return False

            # Upsert points to Qdrant
            self.client.upsert(collection_name=self.collection_name, points=points)
            
            self.logger.info(f"Successfully stored {len(points)} chunks in Qdrant collection '{self.collection_name}'")
            return True
        except Exception as e:
            self.logger.error(f"Error storing chunks in Qdrant: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def retrieve_relevant_chunks(self, query_embedding: List[float], limit: int = 5,
                                 filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks based on the query embedding.

        Args:
            query_embedding: Embedding of the query
            limit: Maximum number of chunks to retrieve
            filters: Optional filters to apply to the search

        Returns:
            List of relevant document chunks
        """
        try:
            # Validate embedding dimensions
            if len(query_embedding) != 1024:  # Expected dimension for Cohere embeddings
                self.logger.error(f"Invalid query embedding dimension: {len(query_embedding)}, expected 1024")
                return []

            # Prepare filters if provided
            qdrant_filters = None
            if filters:
                filter_conditions = []
                for key, value in filters.items():
                    filter_conditions.append(
                        models.FieldCondition(
                            key=f"metadata.{key}",
                            match=models.MatchValue(value=value)
                        )
                    )

                if filter_conditions:
                    qdrant_filters = models.Filter(must=filter_conditions)

            # Perform search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=qdrant_filters
            )

            # Format results
            relevant_chunks = []
            for result in results:
                chunk = {
                    "chunk_id": result.payload.get("chunk_id", result.id),
                    "content": result.payload["content"],
                    "document_id": result.payload.get("document_id", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score
                }
                relevant_chunks.append(chunk)

            self.logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks")
            return relevant_chunks
        except Exception as e:
            self.logger.error(f"Error retrieving chunks from Qdrant: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []

    def retrieve_by_selected_text(self, selected_text: str, embedding_service) -> List[Dict[str, Any]]:
        """
        Retrieve chunks that are most relevant to the selected text only.

        Args:
            selected_text: The text that the user has selected
            embedding_service: The embedding service to generate query embeddings

        Returns:
            List of relevant document chunks
        """
        try:
            # Generate embedding for the selected text
            query_embedding = embedding_service.embed_text(selected_text)

            # Retrieve relevant chunks
            return self.retrieve_relevant_chunks(query_embedding, limit=10)
        except Exception as e:
            self.logger.error(f"Error retrieving by selected text: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return []