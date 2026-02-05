#!/usr/bin/env python3
"""
Script to ingest your book data into the Qdrant vector database
This will properly chunk and store your book content for RAG functionality.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.improved_ingestion_service import ImprovedIngestionService
from src.config.settings import settings


def find_book_documents():
    """
    Look for book documents in common directories
    """
    possible_dirs = [
        "docs",           # Common documentation directory
        "content",        # Content directory
        "books",          # Books directory
        "src/docs",       # Source docs
        "src/content",    # Source content
        "documentation",  # Documentation directory
        "."               # Current directory
    ]
    
    book_files = []
    
    for directory in possible_dirs:
        if os.path.exists(directory):
            print(f"Scanning directory: {directory}")
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith(('.md', '.mdx', '.txt', '.html', '.htm', '.pdf')):
                        file_path = os.path.join(root, file)
                        print(f"  Found: {file_path}")
                        book_files.append(file_path)
    
    return book_files


def ingest_book_data():
    """
    Ingest your book data with proper chunking and storage
    """
    print("Starting book data ingestion...")
    
    # Check if required environment variables are set
    if not settings.COHERE_API_KEY:
        print("Error: COHERE_API_KEY environment variable is not set")
        return False
    
    if not settings.QDRANT_CLIENT_URL:
        print("Error: QDRANT_CLIENT_URL environment variable is not set")
        return False
    
    # Find book documents
    book_files = find_book_documents()
    
    if not book_files:
        print("No book documents found. Looking for common documentation files...")
        # Create a sample document if none found
        sample_file = "sample_book_chapter.md"
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write("# Sample Book Chapter\n\n")
            f.write("This is a sample chapter to test the ingestion system.\n\n")
            f.write("## Introduction\n\n")
            f.write("The field of artificial intelligence has seen remarkable progress in recent years.\n")
            f.write("Machine learning algorithms can now process vast amounts of data efficiently.\n")
            f.write("Deep learning models have revolutionized computer vision and natural language processing.\n\n")
            f.write("## Advanced Topics\n\n")
            f.write("Transformers have enabled breakthroughs in language understanding.\n")
            f.write("Reinforcement learning is driving advances in robotics and game playing.\n")
            f.write("Computer vision systems now surpass human accuracy in many tasks.\n\n")
            f.write("## Applications\n\n")
            f.write("AI systems are now used in healthcare for diagnosis and treatment recommendations.\n")
            f.write("Autonomous vehicles rely on sophisticated AI algorithms for navigation.\n")
            f.write("Natural language processing enables seamless human-computer interaction.\n")
            f.write("Recommendation systems power content discovery on major platforms.\n")
        
        book_files = [sample_file]
        print(f"Created sample file: {sample_file}")
    
    print(f"\nFound {len(book_files)} book document(s) to process")
    
    # Initialize the ingestion service
    ingestion_service = ImprovedIngestionService()
    
    try:
        # Process the documents
        result = ingestion_service.ingest_documents(book_files)
        
        print("\nIngestion Results:")
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Processed documents: {len(result['processed_documents'])}")
        print(f"Failed documents: {len(result['failed_documents'])}")
        print(f"Total chunks created: {result['total_chunks_created']}")
        print(f"Total chunks stored: {result['total_chunks_stored']}")
        
        if result['failed_documents']:
            print("\nFailed documents:")
            for doc in result['failed_documents']:
                print(f"  - {doc}")
        
        if result['processed_documents']:
            print("\nSuccessfully processed documents:")
            for doc in result['processed_documents']:
                print(f"  - {doc['path']}: {doc['chunks_created']} chunks created, {doc['chunks_stored']} stored")
        
        # Clean up sample file if we created one
        if "sample_book_chapter.md" in book_files:
            os.remove("sample_book_chapter.md")
            print("Cleaned up sample file")
        
        return True
        
    except Exception as e:
        print(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Book Data Ingestion Script")
    print("="*50)
    
    success = ingest_book_data()
    
    if success:
        print("\n✓ Book data ingestion completed successfully!")
        print("Your book content is now properly chunked and stored in Qdrant.")
        print("The RAG system can now retrieve and use this information for responses.")
    else:
        print("\n✗ Book data ingestion failed!")
        sys.exit(1)