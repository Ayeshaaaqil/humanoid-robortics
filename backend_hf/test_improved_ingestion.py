#!/usr/bin/env python3
"""
Test script for the improved ingestion service.
This script will test the new chunking, embedding, and storage functionality.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.improved_ingestion_service import ImprovedIngestionService
from src.config.settings import settings


def test_ingestion():
    """
    Test the improved ingestion service with sample documents.
    """
    print("Testing Improved Ingestion Service...")

    # Check if required environment variables are set
    if not settings.COHERE_API_KEY:
        print("Error: COHERE_API_KEY environment variable is not set")
        return False

    if not settings.QDRANT_CLIENT_URL:
        print("Error: QDRANT_CLIENT_URL environment variable is not set")
        return False

    # Initialize the ingestion service
    ingestion_service = ImprovedIngestionService()

    # Define sample document paths (these should exist in your project)
    sample_docs = []

    # Look for markdown files in common documentation directories
    doc_dirs = [
        "docs",
        "src/docs",
        "documentation",
        "content"
    ]

    for doc_dir in doc_dirs:
        if os.path.exists(doc_dir):
            for file in os.listdir(doc_dir):
                if file.endswith(('.md', '.mdx', '.txt')):
                    sample_docs.append(os.path.join(doc_dir, file))

    # If no docs found in common directories, try to create a simple test file
    if not sample_docs:
        test_file = "test_document.md"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("# Test Document\n\n")
            f.write("This is a test document for the RAG system.\n\n")
            f.write("It contains multiple sections to test the chunking functionality.\n\n")
            f.write("## Section 1: Introduction\n\n")
            f.write("The field of artificial intelligence has seen significant advances in recent years.\n")
            f.write("Machine learning algorithms can now process vast amounts of data efficiently.\n\n")
            f.write("## Section 2: Natural Language Processing\n\n")
            f.write("Natural language processing enables computers to understand human language.\n")
            f.write("Modern models can perform tasks like translation, summarization, and question answering.\n\n")
            f.write("## Section 3: Applications\n\n")
            f.write("RAG systems combine retrieval and generation for improved responses.\n")
            f.write("They can access external knowledge sources to provide accurate information.\n")
            f.write("This approach is particularly useful for domain-specific applications.\n")

        sample_docs.append(test_file)
        print(f"Created test document: {test_file}")

    if not sample_docs:
        print("No documents found to test with. Please provide some markdown files to test.")
        return False

    print(f"Found {len(sample_docs)} documents to process: {sample_docs}")

    try:
        # Process the documents
        result = ingestion_service.ingest_documents(sample_docs)

        print("\nIngestion Results:")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Processed documents: {len(result['processed_documents'])}")
        print(f"Failed documents: {len(result['failed_documents'])}")

        if result['failed_documents']:
            print("Failed documents:")
            for doc in result['failed_documents']:
                print(f"  - {doc}")

        # Clean up test file if we created one
        if "test_document.md" in sample_docs:
            os.remove("test_document.md")
            print("Cleaned up test document")

        return True

    except Exception as e:
        print(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_ingestion()
    if success:
        print("\nIngestion test completed successfully!")
    else:
        print("\nIngestion test failed!")
        sys.exit(1)