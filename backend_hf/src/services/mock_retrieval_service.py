from typing import List, Dict, Any, Optional
from ..config.settings import settings
import uuid


class MockRetrievalService:
    """
    Mock service for retrieving relevant documents to simulate Qdrant functionality.
    This is for testing purposes when the actual Qdrant service is not available.
    """

    def __init__(self):
        # Initialize with some sample data to simulate retrieval
        self.sample_chunks = [
            {
                "chunk_id": "sample-1",
                "content": "Artificial Intelligence (AI) is intelligence demonstrated by machines, in contrast to the natural intelligence displayed by humans and animals.",
                "document_id": "doc-1",
                "metadata": {"source": "introduction", "page": 1},
                "score": 0.9
            },
            {
                "chunk_id": "sample-2", 
                "content": "Machine learning is a method of data analysis that automates analytical model building. It is a branch of artificial intelligence based on the idea that systems can learn from data.",
                "document_id": "doc-1", 
                "metadata": {"source": "ml-intro", "page": 5},
                "score": 0.85
            },
            {
                "chunk_id": "sample-3",
                "content": "Deep learning is part of a broader family of machine learning methods based on artificial neural networks with representation learning.",
                "document_id": "doc-1",
                "metadata": {"source": "deep-learning", "page": 10},
                "score": 0.8
            },
            {
                "chunk_id": "sample-4",
                "content": "Humanoid robots are robots with physical features resembling the human body. They typically have a head, torso, arms, and legs.",
                "document_id": "doc-2",
                "metadata": {"source": "humanoid-robots", "page": 15},
                "score": 0.95
            },
            {
                "chunk_id": "sample-5",
                "content": "Physical AI combines artificial intelligence with physical systems, enabling robots to interact with the real world intelligently.",
                "document_id": "doc-2",
                "metadata": {"source": "physical-ai", "page": 20},
                "score": 0.92
            }
        ]

    def store_chunks(self, chunks: List[Dict[str, Any]]) -> bool:
        """
        Mock storing document chunks.
        
        Args:
            chunks: List of document chunks with embeddings

        Returns:
            True if successful, False otherwise
        """
        print(f"Mock: Storing {len(chunks)} chunks")
        return True

    def retrieve_relevant_chunks(self, query_embedding: List[float], limit: int = 5,
                                 filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Mock retrieval of relevant document chunks based on the query embedding.
        In a real implementation, this would use vector similarity to find relevant chunks.
        For the mock, we'll return sample chunks regardless of the query.

        Args:
            query_embedding: Embedding of the query (not used in mock)
            limit: Maximum number of chunks to retrieve
            filters: Optional filters to apply to the search (not used in mock)

        Returns:
            List of relevant document chunks
        """
        # Return the top 'limit' chunks from our sample data
        return self.sample_chunks[:limit]

    def retrieve_by_selected_text(self, selected_text: str, embedding_service) -> List[Dict[str, Any]]:
        """
        Mock retrieval based on selected text.

        Args:
            selected_text: The text that the user has selected
            embedding_service: The embedding service to generate query embeddings (not used in mock)

        Returns:
            List of relevant document chunks
        """
        # For the mock, return the first 3 chunks
        return self.sample_chunks[:3]