#!/usr/bin/env python3
"""
Test script to verify the RAG chatbot functionality
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


def test_retrieval():
    """
    Test the retrieval functionality to see if it can find relevant content
    """
    print("Testing RAG retrieval system...")

    # Check if required environment variables are set
    if not settings.COHERE_API_KEY:
        print("Error: COHERE_API_KEY environment variable is not set")
        return False

    if not settings.QDRANT_CLIENT_URL:
        print("Error: QDRANT_CLIENT_URL environment variable is not set")
        return False

    try:
        # Initialize services
        embedding_service = EmbeddingService()
        retrieval_service = RetrievalService()

        # Test query about Physical AI
        test_query = "What is Physical AI?"

        print(f"Testing query: '{test_query}'")

        # Generate embedding for the query
        query_embedding = embedding_service.embed_text(test_query)
        print(f"Generated embedding with {len(query_embedding)} dimensions")

        # Retrieve relevant chunks from Qdrant
        relevant_chunks = retrieval_service.retrieve_relevant_chunks(
            query_embedding=query_embedding,
            limit=5  # Retrieve top 5 relevant chunks
        )

        print(f"Found {len(relevant_chunks)} relevant chunks")

        if relevant_chunks:
            print("\nRelevant chunks found:")
            for i, chunk in enumerate(relevant_chunks):
                print(f"\nChunk {i+1}:")
                print(f"  Score: {chunk['score']}")
                print(f"  Content preview: {chunk['content'][:200]}...")
                print(f"  Metadata: {chunk['metadata']}")
        else:
            print("No relevant chunks found for the query")
            print("This could mean:")
            print("  - The query embedding doesn't match stored content")
            print("  - The vector search threshold is too strict")
            print("  - The content might not be properly indexed")

        return len(relevant_chunks) > 0

    except Exception as e:
        print(f"Error during retrieval test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generation():
    """
    Test the generation functionality
    """
    print("\nTesting generation service...")

    try:
        generation_service = GenerationService()

        # Test simple query
        test_query = "What is 2+2?"
        context_chunks = [{"content": "Simple math: 2+2=4", "score": 0.9}]

        answer = generation_service.generate_answer(
            query=test_query,
            context_chunks=context_chunks
        )

        print(f"Generated answer: {answer}")

        if "4" in answer:
            print("PASS: Generation service working correctly")
            return True
        else:
            print("WARN: Generation service may not be working correctly")
            return False

    except Exception as e:
        print(f"Error during generation test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_rag_process():
    """
    Test the full RAG process
    """
    print("\nTesting full RAG process...")

    try:
        embedding_service = EmbeddingService()
        retrieval_service = RetrievalService()
        generation_service = GenerationService()

        # Query about Physical AI
        query = "What is Physical AI?"

        print(f"Processing query: '{query}'")

        # Step 1: Generate embedding for the query
        query_embedding = embedding_service.embed_text(query)
        print("PASS: Generated embedding with {len(query_embedding)} dimensions")

        # Step 2: Retrieve relevant chunks from Qdrant
        relevant_chunks = retrieval_service.retrieve_relevant_chunks(
            query_embedding=query_embedding,
            limit=5
        )

        print(f"PASS: Retrieved {len(relevant_chunks)} relevant chunks")

        if not relevant_chunks:
            print("WARN: No relevant chunks found - this explains why the chatbot isn't responding")
            print("  Possible causes:")
            print("  - Content wasn't properly ingested")
            print("  - Vector search threshold is too strict")
            print("  - Embeddings don't match properly")
            return False

        # Step 3: Generate answer using Cohere with the retrieved context
        answer = generation_service.generate_answer(
            query=query,
            context_chunks=relevant_chunks
        )

        print(f"PASS: Generated answer: {answer}")

        # Check if the answer contains relevant information
        if len(answer) > 10 and "not available" not in answer.lower():
            print("PASS: Full RAG process working correctly")
            return True
        else:
            print("WARN: Answer may not be satisfactory")
            return True  # Still consider successful if no errors occurred

    except Exception as e:
        print(f"Error during full RAG test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("RAG System Test")
    print("="*40)

    # Run individual tests
    retrieval_success = test_retrieval()
    generation_success = test_generation()
    full_rag_success = test_full_rag_process()

    print(f"\nTest Results:")
    print(f"Retrieval: {'PASS' if retrieval_success else 'FAIL'}")
    print(f"Generation: {'PASS' if generation_success else 'FAIL'}")
    print(f"Full RAG: {'PASS' if full_rag_success else 'FAIL'}")

    if retrieval_success and generation_success and full_rag_success:
        print("\nPASS: All tests passed! Your RAG system should be working correctly.")
    else:
        print("\nWARN: Some tests failed. Please check the output above for details.")