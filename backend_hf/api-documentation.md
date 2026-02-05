# RAG Chatbot API Documentation

This document describes the API endpoints for the RAG Chatbot backend service.

## Endpoints

### POST /api/v1/chat

Main endpoint for chat interactions with the RAG system.

#### Request

**Content-Type**: `application/json`

**Body**:
```json
{
  "session_id": "string",
  "message": "string",
  "mode": "full-book|selected-text",
  "selected_text": "string (optional)"
}
```

**Fields**:
- `session_id`: Unique identifier for the chat session (will be created if doesn't exist)
- `message`: The user's question or message
- `mode`: The mode of operation - either "full-book" or "selected-text"
- `selected_text`: The text selected by the user (required when mode is "selected-text", optional otherwise)

**Example Request**:
```json
{
  "session_id": "sess_123456789",
  "message": "What are the key principles of physical AI?",
  "mode": "full-book"
}
```

**Example Request with Selected Text**:
```json
{
  "session_id": "sess_123456789",
  "message": "Explain this concept in simpler terms",
  "mode": "selected-text",
  "selected_text": "Physical AI combines machine learning with physics-based modeling to create more robust robotic systems that can interact effectively with the real world."
}
```

#### Response

**Success Response** (200 OK):
```json
{
  "session_id": "string",
  "response": "string",
  "sources": [
    {
      "chunk_id": "string",
      "content_snippet": "string",
      "document_id": "string",
      "metadata": {}
    }
  ],
  "timestamp": "string (ISO 8601 format)"
}
```

**Error Response** (500 Internal Server Error):
```json
{
  "detail": "string (error message)"
}
```

**Example Success Response**:
```json
{
  "session_id": "sess_123456789",
  "response": "Physical AI combines machine learning with physics-based modeling to create more robust robotic systems...",
  "sources": [
    {
      "chunk_id": "chunk_abc123",
      "content_snippet": "Physical AI combines machine learning with physics-based modeling to create more robust...",
      "document_id": "doc_789",
      "metadata": {
        "heading": "Introduction to Physical AI",
        "prev_heading": "Chapter 1"
      }
    }
  ],
  "timestamp": "2025-12-21T10:30:45.123456"
}
```

### GET /api/v1/history/{session_id}

Retrieves chat history for a specific session.

#### Request

**Path Parameters**:
- `session_id`: The session ID to retrieve history for

#### Response

**Success Response** (200 OK):
```json
{
  "session_id": "string",
  "messages": [
    {
      "message_id": "string",
      "session_id": "string",
      "role": "user|assistant",
      "content": "string",
      "timestamp": "string (ISO 8601 format)",
      "sources": "array (present only for assistant messages)"
    }
  ]
}
```

### DELETE /api/v1/session/{session_id}

Deactivates a chat session.

#### Request

**Path Parameters**:
- `session_id`: The session ID to deactivate

#### Response

**Success Response** (200 OK):
```json
{
  "status": "success",
  "message": "Session deactivated successfully"
}
```

**Not Found Response** (404 Not Found):
```json
{
  "detail": "Session not found"
}
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Requested resource not found
- `500 Internal Server Error`: Server error

## CORS Configuration

The API is configured to allow requests from:
- `https://physical-ai-humanoid-robotics-textb-six.vercel.app` (production Vercel domain)
- `http://localhost:3000`, `http://localhost:3001`, `http://localhost:8080` (local development)

## Security

- All API keys and sensitive credentials are stored in environment variables
- The API does not expose any secrets to the client
- Requests are validated server-side to prevent unauthorized access