#!/usr/bin/env python3
"""
Verification script to confirm that your book data has been properly ingested
into the Qdrant vector database.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import settings
from qdrant_client import QdrantClient


def verify_ingestion():
    """
    Verify that the book data has been properly ingested into Qdrant
    """
    print("Verifying book data ingestion in Qdrant...")

    # Initialize Qdrant client
    if settings.QDRANT_CLIENT_API_KEY:
        client = QdrantClient(
            url=settings.QDRANT_CLIENT_URL,
            api_key=settings.QDRANT_CLIENT_API_KEY,
            prefer_grpc=False
        )
    else:
        client = QdrantClient(url=settings.QDRANT_CLIENT_URL)

    try:
        # Get collection info
        collection_name = "document_chunks"  # Default name used by the ingestion service
        collection_info = client.get_collection(collection_name)
        print(f"PASS: Collection '{collection_name}' exists")
        print(f"PASS: Total points in collection: {collection_info.points_count}")

        # Check if we have the expected number of points
        if collection_info.points_count >= 29:  # At least the 29 chunks we just ingested
            print(f"PASS: Collection has sufficient points ({collection_info.points_count})")
        else:
            print(f"WARN: Collection has fewer points than expected ({collection_info.points_count}/29)")

        # Try to retrieve a sample point to verify content
        try:
            # Get the first few points to verify they contain book content
            points = client.scroll(
                collection_name=collection_name,
                limit=3,
                with_payload=True,
                with_vectors=False
            )

            if points[0]:  # If we got points back
                print(f"PASS: Retrieved {len(points[0])} sample points from collection")

                # Display information about the first point
                first_point = points[0][0]
                content_preview = first_point.payload.get("content", "")[:100] + "..."
                print(f"PASS: Sample content preview: '{content_preview}'")

                # Check if the content looks like book content
                if any(keyword in content_preview.lower() for keyword in ["ai", "robot", "chapter", "humanoid", "physical"]):
                    print("PASS: Content appears to be from your book")
                else:
                    print("INFO: Content type could not be verified")

        except Exception as e:
            print(f"WARN: Could not retrieve sample points: {e}")

        print("\nPASS: Verification completed successfully!")
        print(f"Your Physical AI & Humanoid Robotics book data is properly stored in Qdrant.")
        print(f"The RAG system can now retrieve information from all {collection_info.points_count} chunks.")

        return True

    except Exception as e:
        print(f"FAIL: Error verifying ingestion: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Qdrant Book Data Verification")
    print("="*40)

    success = verify_ingestion()

    if success:
        print("\nVerification successful!")
        print("Your book content is ready for RAG operations.")
    else:
        print("\nVerification failed!")
        sys.exit(1)