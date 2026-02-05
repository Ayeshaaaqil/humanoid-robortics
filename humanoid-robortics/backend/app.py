from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Union
from fastapi.responses import StreamingResponse
import json
import logging
import os
from dotenv import load_dotenv
import cohere
from qdrant_client import QdrantClient
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="http://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize Cohere and Qdrant clients
cohere_api_key = os.getenv("COHERE_API_KEY")
qdrant_url = os.getenv("QDRANT_CLIENT_URL") or os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_CLIENT_API_KEY") or os.getenv("QDRANT_API_KEY")

try:
    cohere_client = cohere.Client(cohere_api_key)
    qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
except Exception as e:
    logger.error(f"Failed to initialize clients: {e}")

EMBED_MODEL = "embed-english-v3.0"
COLLECTION_NAME = "document_chunks"

class ChatRequest(BaseModel):
    thread_id: str
    input: Union[str, dict]

@app.post("/api/v1/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"Received chat request: {request}")

    user_message = request.input
    if isinstance(request.input, dict):
        user_message = request.input.get('message', request.input.get('input', str(request.input)))
    else:
        user_message = str(request.input)

    user_message = user_message.strip()
    if not user_message:
        def error_response():
            yield f"data: {json.dumps({'type': 'error', 'content': 'Cannot process empty message'})}\n\n"
        return StreamingResponse(error_response(), media_type="text/event-stream")

    try:
        # 1. Embed the user message
        embed_response = cohere_client.embed(
            texts=[user_message],
            model=EMBED_MODEL,
            input_type="search_query",
        )
        query_embedding = embed_response.embeddings[0]

        # 2. Search Qdrant
        results = qdrant_client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_embedding,
            limit=5,
        )

        context = ""
        for i, hit in enumerate(results):
            content = hit.payload.get("content", "")
            title = hit.payload.get("metadata", {}).get("title", "Untitled")
            context += f"Source {i+1} ({title}):\n{content}\n\n"
        
        # 3. Construct prompt
        prompt = f"""You are an AI assistant for the 'Physical AI and Humanoid Robotics' textbook. 
Answer the user's question based ONLY on the provided context. 
If the information is not in the context, say you don't know based on the book content.

Context:
{context}

User Question: {user_message}

Answer:"""

        # 4. Generate response using Cohere
        chat_response = cohere_client.chat(
            message=prompt,
            model="command",
            stream=True
        )

        def generate_response():
            for event in chat_response:
                if event.event_type == 'text-generation':
                    yield f"data: {json.dumps({'type': 'assistant.response', 'content': event.text})}\n\n"
                elif event.event_type == 'stream-end':
                    break
            yield f"data: {json.dumps({'type': 'end'})}\n\n"

        return StreamingResponse(generate_response(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Error: {e}")
        def error_response():
            yield f"data: {json.dumps({'type': 'error', 'content': f'Server Error: {str(e)}'})}\n\n"
        return StreamingResponse(error_response(), media_type="text/event-stream")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
