import os
from dotenv import load_dotenv
from pathlib import Path
from qdrant_client import QdrantClient

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
print(f"Loading .env from: {env_path}")
load_dotenv(dotenv_path=env_path)

# Initialize Qdrant client
qdrant_url = os.getenv("QDRANT_CLIENT_URL") or os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_CLIENT_API_KEY") or os.getenv("QDRANT_API_KEY")

print(f"URL found: {'Yes' if qdrant_url else 'No'}")
print(f"API Key found: {'Yes' if qdrant_api_key else 'No'}")

try:
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    collections = client.get_collections()
    print("Connection successful!")
    print(f"Collections: {[c.name for c in collections.collections]}")
    
    # Check for specific collection
    exists = client.collection_exists("document_chunks")
    print(f"Collection 'document_chunks' exists: {exists}")
    
except Exception as e:
    print(f"Connection failed: {e}")
