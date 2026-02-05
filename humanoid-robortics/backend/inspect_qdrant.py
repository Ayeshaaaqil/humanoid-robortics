import os
from dotenv import load_dotenv
from pathlib import Path
from qdrant_client import QdrantClient

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

qdrant_url = os.getenv("QDRANT_CLIENT_URL") or os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_CLIENT_API_KEY") or os.getenv("QDRANT_API_KEY")

try:
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    
    print("Fetching one point from 'document_chunks'...")
    points = client.scroll(
        collection_name="document_chunks",
        limit=1,
        with_payload=True
    )[0]
    
    if points:
        print(f"Payload keys: {list(points[0].payload.keys())}")
        print(f"Full payload: {points[0].payload}")
    else:
        print("No points found in 'document_chunks'.")

except Exception as e:
    print(f"Inspection failed: {e}")
