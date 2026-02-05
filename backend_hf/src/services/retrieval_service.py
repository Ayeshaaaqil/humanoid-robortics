from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
from ..config.settings import settings
import uuid


class RetrievalService:
    """
    Service for retrieving relevant documents using Qdrant.
    """

    def __init__(self):
        # Initialize Qdrant client
        if settings.QDRANT_CLIENT_API_KEY:
            self.client = QdrantClient(
                url=settings.QDRANT_CLIENT_URL,
                api_key=settings.QDRANT_CLIENT_API_KEY,
                prefer_grpc=False  # Use HTTP instead of gRPC for cloud instances
            )
        else:
            self.client = QdrantClient(url=settings.QDRANT_CLIENT_URL)

        # Define collection name
        self.collection_name = "document_chunks"

        # Create collection if it doesn't exist
        self._create_collection()

    def _create_collection(self):
        """
        Create the Qdrant collection if it doesn't exist.
        """
        try:
            # Check if collection exists
            self.client.get_collection(self.collection_name)
        except:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=1024, distance=models.Distance.COSINE),
            )

    def store_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Store document chunks in Qdrant.

        Args:
            chunks: List of document chunks with embeddings

        Returns:
            True if successful, False otherwise
        """
        try:
            points = []
            for chunk in chunks:
                point_id = str(uuid.uuid4())
                points.append(
                    models.PointStruct(
                        id=point_id,
                        vector=chunk.get("embedding", []),
                        payload={
                            "content": chunk["content"],
                            "document_id": chunk.get("document_id", ""),
                            "metadata": chunk.get("metadata", {}),
                            "chunk_id": chunk.get("chunk_id", point_id)
                        }
                    )
                )

            self.client.upsert(collection_name=self.collection_name, points=points)
            return True
        except Exception as e:
            print(f"Error storing chunks: {e}")
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

            # Use the search method (older API that's more widely supported)
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

            return relevant_chunks
        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            import traceback
            traceback.print_exc()
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
            print(f"Error retrieving by selected text: {e}")
            return []