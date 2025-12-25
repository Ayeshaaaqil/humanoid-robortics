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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware to allow requests from local Docusaurus instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://my-website-two-weld-92.vercel.app/"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

# Initialize Cohere and Qdrant clients
cohere_api_key = os.getenv("COHERE_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

cohere_client = cohere.Client(cohere_api_key)
qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

EMBED_MODEL = "embed-english-v3.0"
COLLECTION_NAME = "document_chunks"

# Pydantic model for the request body
class ChatRequest(BaseModel):
    thread_id: str
    input: Union[str, dict]  # Accept both string and dict to handle different input formats

@app.post("/api/v1/chat")
async def chat_v1(request: ChatRequest):
    logger.info(f"Received chat request: {request}")

    # Extract the actual message content from input (whether it's a string or dict)
    user_message = request.input
    if isinstance(request.input, dict):
        # If input is a dict, try to get the 'message' field
        if 'message' in request.input:
            user_message = request.input['message']
        elif 'input' in request.input:
            user_message = request.input['input']
        else:
            user_message = str(request.input)  # Convert the whole dict to string if no specific field
    else:
        user_message = str(request.input)  # Ensure it's a string

    user_message = user_message.strip()
    if not user_message:
        def error_response():
            yield f"data: {json.dumps({'type': 'error', 'content': 'Cannot process empty message'})}\n\n"
        return StreamingResponse(error_response(), media_type="text/event-stream")

    # Process the message with RAG
    try:
        # 1. Embed the user message
        embed_response = cohere_client.embed(
            texts=[user_message],
            model=EMBED_MODEL,
            input_type="search_query",
        )
        query_embedding = embed_response.embeddings[0]

        # 2. Search Qdrant for relevant documents
        results = qdrant_client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=5,
        )

        documents = []
        for hit in results.points:
            documents.append({
                "title": hit.payload.get("url", "") if hit.payload else "",
                "snippet": hit.payload.get("text", "") if hit.payload else "",
                "id": str(hit.id),
            })

        # 3. Generate response using Cohere
        chat_response = cohere_client.chat(
            message=user_message,
            documents=documents,
            stream=False,
        )

        def generate_response():
            yield f"data: {json.dumps({'type': 'assistant.response', 'content': chat_response.text})}\n\n"
            yield f"data: {json.dumps({'type': 'end'})}\n\n"

        return StreamingResponse(generate_response(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        def error_response():
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        return StreamingResponse(error_response(), media_type="text/event-stream")

# Also keep the original endpoint for compatibility
@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    # Call the same function as the v1 endpoint
    return await chat_v1(request)

@app.get("/")
async def root():
    return {"status": "Server running OK"}

@app.get("/api/test")
async def test_endpoint():
    return {"message": "Test endpoint is working"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

