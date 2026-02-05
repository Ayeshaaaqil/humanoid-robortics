import cohere
from typing import List, Dict, Any
from ..config.settings import settings


class EmbeddingService:
    """
    Service for generating embeddings using Cohere.
    """
    
    def __init__(self):
        self.client = cohere.Client(settings.COHERE_API_KEY)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using Cohere.
        
        Args:
            texts: List of texts to generate embeddings for
            
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        if not texts:
            return []
        
        # Generate embeddings using Cohere with proper input_type for v3 model
        response = self.client.embed(
            texts=texts,
            model='embed-multilingual-v3.0',  # Using multilingual model for technical content
            input_type="search_document"  # Required for v3 models
        )
        
        return response.embeddings
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to generate embedding for
            
        Returns:
            Embedding as a list of floats
        """
        embeddings = self.generate_embeddings([text])
        return embeddings[0] if embeddings else []
    
    def embed_document_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of document chunks.
        
        Args:
            chunks: List of document chunks with content
            
        Returns:
            List of document chunks with embeddings added
        """
        if not chunks:
            return []
        
        # Extract texts for embedding
        texts = [chunk["content"] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i]
        
        return chunks