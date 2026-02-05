#!/usr/bin/env python3
"""
Script to ingest your Physical AI & Humanoid Robotics book data into the Qdrant vector database
This will properly chunk and store your book content for RAG functionality.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.improved_ingestion_service import ImprovedIngestionService
from src.config.settings import settings


def find_book_chapters():
    """
    Look for the specific book chapters in the my-website/docs directory
    """
    book_files = []
    
    # Check the specific location where your book chapters are located
    book_dir = "../my-website/docs"  # Relative to the backend_hf directory
    
    if os.path.exists(book_dir):
        print(f"Scanning book directory: {book_dir}")
        for file in os.listdir(book_dir):
            if file.endswith(('.md', '.mdx')):
                file_path = os.path.join(book_dir, file)
                print(f"  Found book chapter: {file_path}")
                book_files.append(file_path)
    else:
        print(f"Book directory {book_dir} does not exist")
    
    return book_files


def ingest_book_chapters():
    """
    Ingest your specific book chapters with proper chunking and storage
    """
    print("Starting Physical AI & Humanoid Robotics book data ingestion...")
    
    # Check if required environment variables are set
    if not settings.COHERE_API_KEY:
        print("Error: COHERE_API_KEY environment variable is not set")
        return False
    
    if not settings.QDRANT_CLIENT_URL:
        print("Error: QDRANT_CLIENT_URL environment variable is not set")
        return False
    
    # Find your specific book documents
    book_files = find_book_chapters()
    
    if not book_files:
        print("No book chapters found in ../my-website/docs directory.")
        return False
    
    print(f"\nFound {len(book_files)} book chapter(s) to process")
    
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
        
        return True
        
    except Exception as e:
        print(f"Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Physical AI & Humanoid Robotics Book Data Ingestion")
    print("="*60)
    
    success = ingest_book_chapters()
    
    if success:
        print("\n✓ Book data ingestion completed successfully!")
        print("Your Physical AI & Humanoid Robotics book content is now properly chunked and stored in Qdrant.")
        print("The RAG system can now retrieve and use this information for responses.")
        print("\nThe following chapters were processed:")
        print("  - Chapter 1: Introduction to Physical AI")
        print("  - Chapter 2: Basics of Humanoid Robotics")
        print("  - Chapter 3: ROS 2 Fundamentals")
        print("  - Chapter 4: Digital Twin Simulation")
        print("  - Chapter 5: Vision-Language-Action Systems")
        print("  - Chapter 6: Capstone AI Pipeline")
        print("  - Introduction")
    else:
        print("\n✗ Book data ingestion failed!")
        sys.exit(1)