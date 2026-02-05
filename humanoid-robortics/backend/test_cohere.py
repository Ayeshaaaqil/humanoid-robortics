import os
from dotenv import load_dotenv
from pathlib import Path
import cohere

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
print(f"Loading .env from: {env_path}")
load_dotenv(dotenv_path=env_path)

cohere_api_key = os.getenv("COHERE_API_KEY")
print(f"API Key found: {'Yes' if cohere_api_key else 'No'}")

try:
    client = cohere.Client(cohere_api_key)
    print("Client initialized")
    
    print("Testing embed...")
    embed = client.embed(
        texts=["Hello world"],
        model="embed-english-v3.0",
        input_type="search_query"
    )
    print("Embed successful")
    
    print("Testing chat...")
    documents = [
        {"title": "Test Doc", "snippet": "This is a test snippet.", "id": "1"}
    ]
    response = client.chat(
        message="Hello",
        documents=documents
    )
    print(f"Chat successful. Response: {response.text}")
    
except Exception as e:
    print(f"Cohere test failed: {e}")
