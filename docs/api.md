# 🔌 API Documentation

## Full-Stack RAG Application API Reference

This document provides comprehensive documentation for the RAG application's REST API and WebSocket endpoints.

## 📡 Base URLs

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`
- **API Version**: `v1`

## 🔐 Authentication

Currently, authentication is optional and disabled by default. When enabled:
- **Type**: JWT Bearer Token
- **Header**: `Authorization: Bearer <token>`

## 📊 Response Format

### Success Response
```json
{
  "data": {},
  "message": "Success",
  "status": "success"
}
```

### Error Response
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": "Additional details",
  "status": "error"
}
```

## 🏥 Health & Status

### Health Check
Check if the API is running.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "service": "RAG Application API",
  "version": "1.0.0"
}
```

### System Status
Get detailed system information.

**Endpoint**: `GET /status`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "service": "RAG Application API",
  "version": "1.0.0",
  "environment": "development",
  "components": {
    "database": {
      "status": "healthy",
      "connection": "connected"
    },
    "ai_providers": {
      "status": "healthy",
      "available": ["openai", "anthropic"],
      "count": 2
    },
    "embeddings": {
      "status": "healthy",
      "available_providers": {
        "openai": ["text-embedding-3-small", "text-embedding-3-large"]
      },
      "total_providers": 2
    }
  }
}
```

## 👤 Profiles

### List Profiles
Get all AI profiles.

**Endpoint**: `GET /api/v1/profiles`

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50)

**Response**:
```json
{
  "profiles": [
    {
      "id": 1,
      "name": "General Assistant",
      "description": "General purpose Q&A assistant",
      "prompt": "You are a helpful assistant...",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "settings": {
        "max_context_chunks": 5,
        "chunk_size": 1000,
        "chunk_overlap": 200
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 50
}
```

### Get Profile
Get a specific profile by ID.

**Endpoint**: `GET /api/v1/profiles/{profile_id}`

**Parameters**:
- `profile_id`: Profile ID (integer)

**Response**:
```json
{
  "id": 1,
  "name": "General Assistant",
  "description": "General purpose Q&A assistant",
  "prompt": "You are a helpful assistant...",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "settings": {
    "max_context_chunks": 5,
    "chunk_size": 1000,
    "chunk_overlap": 200
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Create Profile
Create a new AI profile.

**Endpoint**: `POST /api/v1/profiles`

**Request Body**:
```json
{
  "name": "Technical Expert",
  "description": "Technical documentation assistant",
  "prompt": "You are a technical expert...",
  "provider": "anthropic",
  "model": "claude-3-sonnet",
  "settings": {
    "max_context_chunks": 8,
    "chunk_size": 1500,
    "chunk_overlap": 300
  }
}
```

**Response**: `201 Created` with profile object

### Update Profile
Update an existing profile.

**Endpoint**: `PUT /api/v1/profiles/{profile_id}`

**Request Body**: Same as create, all fields optional

**Response**: Updated profile object

### Delete Profile
Delete a profile and all associated data.

**Endpoint**: `DELETE /api/v1/profiles/{profile_id}`

**Response**: `204 No Content`

## 📄 Documents

### List Documents
Get documents for a profile.

**Endpoint**: `GET /api/v1/documents`

**Query Parameters**:
- `profile_id` (optional): Filter by profile ID
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50)

**Response**:
```json
{
  "documents": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "document.pdf",
      "original_filename": "My Document.pdf",
      "file_size": 1048576,
      "mime_type": "application/pdf",
      "upload_date": "2024-01-01T00:00:00Z",
      "processed": true,
      "profile_id": 1,
      "document_metadata": {
        "pages": 10,
        "title": "Document Title"
      }
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 50
}
```

### Get Document
Get document details.

**Endpoint**: `GET /api/v1/documents/{document_id}`

**Response**: Document object with chunks count

### Upload Document
Upload a new document.

**Endpoint**: `POST /api/v1/documents/upload`

**Content-Type**: `multipart/form-data`

**Form Data**:
- `file`: Document file (PDF, DOCX, TXT, MD)
- `profile_id`: Profile ID (integer)

**Response**:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "status": "uploaded",
  "processing": true
}
```

### Process Document
Process an uploaded document (extract text and generate embeddings).

**Endpoint**: `POST /api/v1/documents/process`

**Request Body**:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "profile_id": 1
}
```

**Response**:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "chunks_created": 0,
  "estimated_time": "2-5 minutes"
}
```

### Delete Document
Delete a document and all its chunks.

**Endpoint**: `DELETE /api/v1/documents/{document_id}`

**Response**: `204 No Content`

## 💬 Chat

### List Chat Sessions
Get chat sessions for a profile.

**Endpoint**: `GET /api/v1/chat/sessions`

**Query Parameters**:
- `profile_id` (optional): Filter by profile ID
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 50)

**Response**:
```json
{
  "sessions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "profile_id": 1,
      "session_name": "Chat about documents",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "message_count": 10
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 50
}
```

### Create Chat Session
Create a new chat session.

**Endpoint**: `POST /api/v1/chat/sessions`

**Request Body**:
```json
{
  "profile_id": 1,
  "session_name": "New Chat Session"
}
```

**Response**: `201 Created` with session object

### Get Chat Session
Get session details with message history.

**Endpoint**: `GET /api/v1/chat/sessions/{session_id}`

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "profile_id": 1,
  "session_name": "Chat about documents",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "messages": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "role": "user",
      "content": "What is this document about?",
      "timestamp": "2024-01-01T00:00:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "role": "assistant",
      "content": "This document discusses...",
      "context_chunks": [
        {
          "chunk_id": "550e8400-e29b-41d4-a716-446655440003",
          "content": "Relevant text chunk...",
          "document_filename": "document.pdf",
          "similarity": 0.85
        }
      ],
      "timestamp": "2024-01-01T00:00:01Z"
    }
  ]
}
```

### Send Message
Send a message to a chat session.

**Endpoint**: `POST /api/v1/chat/query`

**Request Body**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "profile_id": 1,
  "message": "What is this document about?",
  "max_context_chunks": 5
}
```

**Response**:
```json
{
  "user_message_id": "550e8400-e29b-41d4-a716-446655440001",
  "assistant_message_id": "550e8400-e29b-41d4-a716-446655440002",
  "response": "This document discusses...",
  "context_chunks": [
    {
      "chunk_id": "550e8400-e29b-41d4-a716-446655440003",
      "content": "Relevant text chunk...",
      "document_filename": "document.pdf",
      "similarity": 0.85
    }
  ],
  "response_time": 2.5
}
```

### Delete Chat Session
Delete a chat session and all messages.

**Endpoint**: `DELETE /api/v1/chat/sessions/{session_id}`

**Response**: `204 No Content`

## 🔍 Search

### Semantic Search
Perform semantic search across documents.

**Endpoint**: `POST /api/v1/search`

**Request Body**:
```json
{
  "query": "machine learning algorithms",
  "profile_id": 1,
  "limit": 10,
  "similarity_threshold": 0.7
}
```

**Response**:
```json
{
  "results": [
    {
      "chunk_id": "550e8400-e29b-41d4-a716-446655440003",
      "content": "Machine learning algorithms are...",
      "document_id": "550e8400-e29b-41d4-a716-446655440000",
      "document_filename": "ml_guide.pdf",
      "similarity": 0.92,
      "chunk_index": 5,
      "chunk_metadata": {
        "page": 3,
        "section": "Introduction"
      }
    }
  ],
  "total_results": 15,
  "search_time": 0.125,
  "query_embedding": [0.1, 0.2, 0.3, "..."]
}
```

### Find Similar Chunks
Find chunks similar to a specific chunk.

**Endpoint**: `POST /api/v1/search/similar`

**Request Body**:
```json
{
  "chunk_id": "550e8400-e29b-41d4-a716-446655440003",
  "profile_id": 1,
  "limit": 5,
  "similarity_threshold": 0.8
}
```

**Response**: Similar to semantic search response

## 🌐 WebSocket Events

### Connection
Connect to WebSocket for real-time chat.

**Endpoint**: `ws://localhost:8000/ws`

### Client to Server Events

#### Join Session
```json
{
  "type": "chat:join_session",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "profile_id": 1
  }
}
```

#### Send Message
```json
{
  "type": "chat:send_message",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "profile_id": 1,
    "message": "What is this document about?",
    "max_context_chunks": 5
  }
}
```

#### Typing Indicator
```json
{
  "type": "chat:typing",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "typing": true
  }
}
```

### Server to Client Events

#### Message Received
```json
{
  "type": "chat:message_received",
  "data": {
    "message_id": "550e8400-e29b-41d4-a716-446655440001",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "role": "user",
    "content": "What is this document about?",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### AI Response Streaming
```json
{
  "type": "chat:ai_streaming",
  "data": {
    "message_id": "550e8400-e29b-41d4-a716-446655440002",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "This document",
    "is_complete": false
  }
}
```

#### AI Response Complete
```json
{
  "type": "chat:ai_complete",
  "data": {
    "message_id": "550e8400-e29b-41d4-a716-446655440002",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "This document discusses machine learning...",
    "context_chunks": [...],
    "response_time": 2.5
  }
}
```

#### Typing Indicator
```json
{
  "type": "chat:typing_indicator",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_typing": true
  }
}
```

#### Session Created
```json
{
  "type": "chat:session_created",
  "data": {
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "profile_id": 1,
    "session_name": "New Chat"
  }
}
```

#### Error
```json
{
  "type": "chat:error",
  "data": {
    "error": "Session not found",
    "code": "SESSION_NOT_FOUND",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

## 🚨 Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Request validation failed | 400 |
| `UNAUTHORIZED` | Authentication required | 401 |
| `FORBIDDEN` | Access denied | 403 |
| `NOT_FOUND` | Resource not found | 404 |
| `PROFILE_NOT_FOUND` | Profile doesn't exist | 404 |
| `DOCUMENT_NOT_FOUND` | Document doesn't exist | 404 |
| `SESSION_NOT_FOUND` | Chat session doesn't exist | 404 |
| `PROCESSING_ERROR` | Document processing failed | 500 |
| `AI_PROVIDER_ERROR` | AI provider request failed | 500 |
| `DATABASE_ERROR` | Database operation failed | 500 |
| `INTERNAL_ERROR` | Internal server error | 500 |

## 📊 Rate Limiting

When enabled (`ENABLE_RATE_LIMITING=true`):
- **Default limit**: 100 requests per minute per IP
- **Headers**: 
  - `X-RateLimit-Limit`: Rate limit
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

## 📝 Examples

### Complete Chat Flow
```python
import requests
import websocket
import json

# 1. Create profile
profile = requests.post('http://localhost:8000/api/v1/profiles', json={
    'name': 'My Assistant',
    'description': 'Personal assistant',
    'prompt': 'You are a helpful assistant.',
    'provider': 'openai',
    'model': 'gpt-4o-mini'
}).json()

# 2. Upload document
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/v1/documents/upload',
        files={'file': f},
        data={'profile_id': profile['id']}
    )
document = response.json()

# 3. Create chat session
session = requests.post('http://localhost:8000/api/v1/chat/sessions', json={
    'profile_id': profile['id'],
    'session_name': 'Document Chat'
}).json()

# 4. Send message via WebSocket
def on_message(ws, message):
    data = json.loads(message)
    if data['type'] == 'chat:ai_complete':
        print(f"AI: {data['data']['content']}")

ws = websocket.WebSocketApp(
    'ws://localhost:8000/ws',
    on_message=on_message
)

# Join session and send message
ws.send(json.dumps({
    'type': 'chat:join_session',
    'data': {'session_id': session['id'], 'profile_id': profile['id']}
}))

ws.send(json.dumps({
    'type': 'chat:send_message',
    'data': {
        'session_id': session['id'],
        'profile_id': profile['id'],
        'message': 'What is this document about?'
    }
}))
```

## 🔧 Configuration

### AI Provider Settings
Configure available models in `backend/config/config.json`:

```json
{
  "ai_providers": {
    "openai": {
      "base_url": "https://api.openai.com/v1",
      "models": {
        "gpt-4o-mini": {
          "max_tokens": 4000,
          "temperature": 0.7,
          "top_p": 1.0,
          "frequency_penalty": 0.0,
          "presence_penalty": 0.0
        }
      }
    }
  }
}
```

### Environment Variables
See [Setup Guide](setup.md) for complete environment configuration.

---

For more information, check the [Setup Guide](setup.md) and [User Guide](user-guide.md).