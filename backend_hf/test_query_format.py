#!/usr/bin/env python3
"""
Test script to see the exact return format of query_points method
"""

from qdrant_client import QdrantClient
from src.config.settings import settings
import random

# Initialize client
client = QdrantClient(
    url=settings.QDRANT_CLIENT_URL,
    api_key=settings.QDRANT_CLIENT_API_KEY
)

# Check collection
collection_info = client.get_collection('document_chunks')
print(f'Collection has {collection_info.points_count} points')

# Generate a test embedding
test_vector = [random.random() for _ in range(1024)]

# Test the query_points method
try:
    results = client.query_points(
        collection_name='document_chunks',
        query=test_vector,
        limit=2
    )

    print(f'Type of results: {type(results)}')
    print(f'Dir of results: {[attr for attr in dir(results) if not attr.startswith("_")]}')

    # Check the results attribute
    if hasattr(results, 'points'):
        points = results.points
        print(f'Type of points: {type(points)}')
        print(f'Length of points: {len(points) if hasattr(points, "__len__") else "N/A"}')

        if points and len(points) > 0:
            first_result = points[0]
            print(f'Type of first result: {type(first_result)}')
            print(f'First result: {first_result}')
            print(f'Attributes of first result: {[attr for attr in dir(first_result) if not attr.startswith("_")]}')

            # Check if it has the attributes we expect
            print(f'Has id: {hasattr(first_result, "id")}')
            print(f'Has payload: {hasattr(first_result, "payload")}')
            print(f'Has score: {hasattr(first_result, "score")}')

            if hasattr(first_result, 'payload'):
                print(f'Payload type: {type(first_result.payload)}')
                print(f'Payload: {first_result.payload}')
    else:
        print('Results object does not have a "points" attribute')
        # Let's see what attributes it has
        for attr in dir(results):
            if not attr.startswith('_'):
                val = getattr(results, attr)
                print(f'{attr}: {type(val)} = {val}')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()