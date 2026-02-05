import os
from dotenv import load_dotenv
from pathlib import Path
import cohere
from qdrant_client import QdrantClient

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

cohere_api_key = os.getenv("COHERE_API_KEY")
qdrant_url = os.getenv("QDRANT_CLIENT_URL") or os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_CLIENT_API_KEY") or os.getenv("QDRANT_API_KEY")

cohere_client = cohere.Client(cohere_api_key)
qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

try:
    print("Embedding...")
    embed_response = cohere_client.embed(
        texts=["What is physical AI?"],
        model="embed-english-v3.0",
        input_type="search_query",
    )
    query_embedding = embed_response.embeddings[0]
    print("Embedding done.")

    print("Searching Qdrant...")
    results = qdrant_client.search(
        collection_name="document_chunks",
        query_vector=query_embedding,
        limit=5,
    )
    print(f"Search done. Found {len(results)} points.")
    
    for hit in results:
        print(f"Hit ID: {hit.id}")
        print(f"Title: {hit.payload.get('metadata', {}).get('title')}")
        print(f"Snippet: {hit.payload.get('content', '')[:100]}...")

except Exception as e:
    print(f"Test failed: {e}")
