# API Documentation

## Base URL

- Development: `http://localhost:8000`
- Production: `https://your-domain.com/api`

## Authentication

Currently, authentication is optional. Set `ENABLE_AUTH=true` in environment variables to enable JWT authentication.

## Endpoints

### Health & Status

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-12-01T10:00:00Z"
}
```

#### GET /status
System status with detailed information.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "ai_providers": {
    "openai": "available",
    "anthropic": "available"
  },
  "version": "1.0.0"
}
```

### Profiles

#### GET /api/v1/profiles
List all available profiles.

**Response:**
```json
[
  {
    "id": 1,
    "name": "General Assistant",
    "description": "General purpose Q&A assistant",
    "provider": "openai",
    "model": "gpt-4o-mini",
    "settings": {
      "max_context_chunks": 5,
      "chunk_size": 1000,
      "chunk_overlap": 200
    },
    "created_at": "2023-12-01T10:00:00Z"
  }
]
```

#### GET /api/v1/profiles/{id}
Get profile by ID.

**Parameters:**
- `id` (path): Profile ID

**Response:**
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
  "created_at": "2023-12-01T10:00:00Z"
}
```

#### POST /api/v1/profiles
Create a new profile.

**Request Body:**
```json
{
  "name": "Custom Assistant",
  "description": "Custom AI assistant",
  "prompt": "You are a custom assistant...",
  "provider": "openai",
  "model": "gpt-4o-mini",
  "settings": {
    "max_context_chunks": 5,
    "chunk_size": 1000,
    "chunk_overlap": 200
  }
}
```

#### PUT /api/v1/profiles/{id}
Update an existing profile.

**Parameters:**
- `id` (path): Profile ID

**Request Body:** Same as POST

#### DELETE /api/v1/profiles/{id}
Delete a profile.

**Parameters:**
- `id` (path): Profile ID

### Documents

#### GET /api/v1/documents
List documents for a profile.

**Query Parameters:**
- `profile_id` (optional): Filter by profile ID
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**
```json
[
  {
    "id": "uuid-here",
    "filename": "document.pdf",
    "original_filename": "My Document.pdf",
    "file_size": 1024000,
    "mime_type": "application/pdf",
    "upload_date": "2023-12-01T10:00:00Z",
    "processed": true,
    "profile_id": 1,
    "metadata": {
      "pages": 10,
      "word_count": 2500
    }
  }
]
```

#### GET /api/v1/documents/{id}
Get document details.

**Parameters:**
- `id` (path): Document UUID

#### POST /api/v1/documents/upload
Upload a new document.

**Request:** Multipart form data
- `file`: The document file
- `profile_id`: Target profile ID

**Response:**
```json
{
  "id": "uuid-here",
  "filename": "document.pdf",
  "status": "uploaded",
  "message": "Document uploaded successfully"
}
```

#### POST /api/v1/documents/process
Process an uploaded document.

**Request Body:**
```json
{
  "document_id": "uuid-here",
  "profile_id": 1
}
```

#### DELETE /api/v1/documents/{id}
Delete a document.

**Parameters:**
- `id` (path): Document UUID

### Chat

#### GET /api/v1/chat/sessions
List chat sessions.

**Query Parameters:**
- `profile_id` (optional): Filter by profile ID
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

#### POST /api/v1/chat/sessions
Create a new chat session.

**Request Body:**
```json
{
  "profile_id": 1,
  "session_name": "My Chat Session"
}
```

#### GET /api/v1/chat/sessions/{id}
Get session messages.

**Parameters:**
- `id` (path): Session UUID

**Response:**
```json
{
  "id": "session-uuid",
  "session_name": "My Chat Session",
  "profile_id": 1,
  "messages": [
    {
      "id": "message-uuid",
      "role": "user",
      "content": "Hello, how are you?",
      "timestamp": "2023-12-01T10:00:00Z"
    },
    {
      "id": "message-uuid-2",
      "role": "assistant",
      "content": "I'm doing well, thank you!",
      "context_chunks": [],
      "timestamp": "2023-12-01T10:00:05Z"
    }
  ],
  "created_at": "2023-12-01T10:00:00Z"
}
```

#### POST /api/v1/chat/query
Send a chat message.

**Request Body:**
```json
{
  "session_id": "session-uuid",
  "message": "What is the main topic of the uploaded documents?",
  "profile_id": 1
}
```

**Response:**
```json
{
  "id": "message-uuid",
  "role": "assistant",
  "content": "Based on the uploaded documents...",
  "context_chunks": [
    {
      "id": "chunk-uuid",
      "content": "Relevant text excerpt...",
      "document_id": "doc-uuid",
      "similarity": 0.85
    }
  ],
  "timestamp": "2023-12-01T10:00:00Z"
}
```

#### DELETE /api/v1/chat/sessions/{id}
Delete a chat session.

**Parameters:**
- `id` (path): Session UUID

### Search

#### POST /api/v1/search
Perform semantic search.

**Request Body:**
```json
{
  "query": "machine learning algorithms",
  "profile_id": 1,
  "limit": 10
}
```

**Response:**
```json
[
  {
    "id": "chunk-uuid",
    "content": "Machine learning algorithms are...",
    "document_id": "doc-uuid",
    "similarity": 0.92,
    "metadata": {
      "chunk_index": 5,
      "page": 3
    }
  }
]
```

#### POST /api/v1/search/similar
Find similar chunks to a given text.

**Request Body:**
```json
{
  "text": "Sample text to find similar content",
  "profile_id": 1,
  "limit": 5
}
```

### Configuration

#### GET /api/v1/config/providers
Get available AI providers.

**Response:**
```json
{
  "openai": {
    "name": "OpenAI",
    "models": ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]
  },
  "anthropic": {
    "name": "Anthropic",
    "models": ["claude-3-sonnet", "claude-3-haiku"]
  }
}
```

#### GET /api/v1/config/models
Get available models for a provider.

**Query Parameters:**
- `provider`: AI provider name

## WebSocket Events

Connect to: `ws://localhost:8000/ws`

### Client to Server Events

#### chat:join_session
Join a chat session.
```json
{
  "session_id": "session-uuid"
}
```

#### chat:send_message
Send a message.
```json
{
  "session_id": "session-uuid",
  "message": "Hello, how are you?",
  "profile_id": 1
}
```

#### chat:typing
Send typing indicator.
```json
{
  "session_id": "session-uuid",
  "typing": true
}
```

### Server to Client Events

#### chat:message_received
New message received.
```json
{
  "id": "message-uuid",
  "role": "assistant",
  "content": "Response content...",
  "context_chunks": [],
  "timestamp": "2023-12-01T10:00:00Z"
}
```

#### chat:typing_indicator
User typing indicator.
```json
{
  "session_id": "session-uuid",
  "user_id": "user-uuid",
  "typing": true
}
```

#### chat:session_created
New session created.
```json
{
  "id": "session-uuid",
  "session_name": "My Chat Session",
  "profile_id": 1
}
```

#### chat:error
Error occurred.
```json
{
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": "Additional error details"
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Request validation failed
- `NOT_FOUND`: Resource not found
- `UNAUTHORIZED`: Authentication required
- `FORBIDDEN`: Access denied
- `RATE_LIMITED`: Too many requests
- `AI_PROVIDER_ERROR`: AI provider unavailable
- `DATABASE_ERROR`: Database operation failed
- `FILE_PROCESSING_ERROR`: Document processing failed
