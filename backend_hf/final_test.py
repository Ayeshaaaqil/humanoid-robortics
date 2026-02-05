#!/usr/bin/env python3
"""
Final test to confirm the RAG system is working correctly
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.embedding_service import EmbeddingService
from src.services.retrieval_service import RetrievalService
from src.services.generation_service import GenerationService
from src.config.settings import settings


def final_test():
    """
    Final test to confirm the RAG system is working
    """
    print("Final RAG System Test")
    print("="*40)

    # Check if required environment variables are set
    if not settings.COHERE_API_KEY:
        print("Error: COHERE_API_KEY environment variable is not set")
        return False

    if not settings.QDRANT_CLIENT_URL:
        print("Error: QDRANT_CLIENT_URL environment variable is not set")
        return False

    try:
        print("Initializing services...")
        embedding_service = EmbeddingService()
        retrieval_service = RetrievalService()
        generation_service = GenerationService()

        print("PASS: Services initialized successfully")

        # Test query about Physical AI
        query = "What is Physical AI?"
        print(f"\nProcessing query: '{query}'")

        # Step 1: Generate embedding
        query_embedding = embedding_service.embed_text(query)
        print(f"PASS: Generated embedding with {len(query_embedding)} dimensions")

        # Step 2: Retrieve relevant chunks
        relevant_chunks = retrieval_service.retrieve_relevant_chunks(
            query_embedding=query_embedding,
            limit=3
        )

        print(f"PASS: Retrieved {len(relevant_chunks)} relevant chunks")

        if len(relevant_chunks) == 0:
            print("WARN: No relevant chunks found")
            return False

        # Step 3: Generate answer
        answer = generation_service.generate_answer(
            query=query,
            context_chunks=relevant_chunks
        )

        print(f"PASS: Generated answer successfully")
        print(f"\nQuery: {query}")
        print(f"Answer: {answer}")

        # Verify the answer contains relevant information
        if len(answer) > 10 and "not available" not in answer.lower():
            print("\nPASS: RAG system is working correctly!")
            print("PASS: Your chatbot can now answer questions about Physical AI")
            return True
        else:
            print("\nWARN: Answer might not be satisfactory")
            return False

    except Exception as e:
        print(f"Error during final test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = final_test()

    if success:
        print("\nSUCCESS: Your RAG chatbot is now fully functional!")
        print("PASS: Book content has been properly ingested")
        print("PASS: Retrieval system is working")
        print("PASS: Generation service is working")
        print("PASS: Full RAG pipeline is operational")
        print("\nThe chatbot can now answer questions about your Physical AI & Humanoid Robotics book!")
    else:
        print("\nFAILURE: There are still issues with the RAG system")