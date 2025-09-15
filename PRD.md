# 📄 Product Requirements Document (PRD)
## Full-Stack RAG (Retrieval-Augmented Generation) Application

**Project:** Full-Stack Customizable RAG Service with Web UI  
**Owner:** Development Team  
**Version:** 2.0  
**Date:** September 2025  

---

## 1. Executive Summary

A complete full-stack RAG application featuring a **React.js frontend**, **FastAPI backend**, **PostgreSQL with pgvector**, and **multi-provider AI support**. The system provides document ingestion, semantic search, and AI-powered question answering through both web UI and CLI interfaces.

### Key Features
- 🎨 **Modern React.js Web UI** with real-time chat interface
- 🚀 **FastAPI Backend** with async processing and WebSocket support
- 🗄️ **PostgreSQL + pgvector** for document storage and semantic search
- 🤖 **Multi-AI Provider Support** (OpenAI, Gemini, Claude, custom endpoints)
- 📁 **Document Management** with chunking and metadata
- 🔧 **CLI Tools** for setup, ingestion, and management
- 🐳 **Docker Compose** deployment with development and production configs

---

## 2. Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React.js UI   │    │  FastAPI Backend│    │ PostgreSQL +    │
│                 │◄──►│                 │◄──►│ pgvector        │
│ - Chat Interface│    │ - API Endpoints │    │                 │
│ - Doc Management│    │ - WebSocket     │    │ - Documents     │
│ - Config UI     │    │ - AI Integration│    │ - Embeddings    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   AI Providers  │
                       │                 │
                       │ - OpenAI        │
                       │ - Google Gemini │
                       │ - Anthropic     │
                       │ - Custom APIs   │
                       └─────────────────┘
```

---

## 3. Technical Stack

### Frontend
- **Framework:** React.js 18+ with TypeScript
- **Styling:** Tailwind CSS + Headless UI
- **State Management:** Zustand or Redux Toolkit
- **HTTP Client:** Axios
- **WebSocket:** Socket.IO client
- **Build Tool:** Vite
- **UI Components:** Custom components + Lucide React icons

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Async Support:** asyncio, asyncpg
- **WebSocket:** FastAPI WebSocket + Socket.IO
- **Authentication:** JWT tokens (optional)
- **File Processing:** PyPDF2, python-docx, markdown
- **Embeddings:** OpenAI embeddings, sentence-transformers
- **CLI:** Click framework

### Database
- **Primary:** PostgreSQL 15+
- **Vector Extension:** pgvector
- **Connection Pool:** asyncpg
- **Migrations:** Alembic (optional)

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Reverse Proxy:** Nginx (production)
- **Environment:** Development & Production configs
- **Storage:** Docker volumes for persistence

---

## 4. Project Structure

```
rag-fullstack/
├── docker-compose.yml              # Main compose file
├── docker-compose.dev.yml          # Development overrides
├── docker-compose.prod.yml         # Production overrides
├── .env.example                    # Environment template
├── .env                           # Environment variables (gitignored)
├── nginx/
│   └── nginx.conf                 # Nginx configuration
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                    # FastAPI application
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py            # App settings
│   │   └── config.json            # AI providers & profiles
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── documents.py       # Document management
│   │   │   ├── chat.py           # Chat endpoints
│   │   │   ├── profiles.py       # Profile management
│   │   │   └── health.py         # Health checks
│   │   └── websocket/
│   │       ├── __init__.py
│   │       └── chat.py           # WebSocket chat handler
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py           # DB connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── ai_providers.py      # AI provider abstractions
│   │   ├── embeddings.py        # Embedding generation
│   │   ├── chunking.py          # Text chunking logic
│   │   └── retrieval.py         # Vector search logic
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py              # CLI entry point
│   │   ├── commands/
│   │   │   ├── __init__.py
│   │   │   ├── init.py          # Database initialization
│   │   │   ├── ingest.py        # Document ingestion
│   │   │   ├── profiles.py      # Profile management
│   │   │   └── reset.py         # Data reset commands
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── file_processing.py
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_cli.py
│       └── test_ai_providers.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── index.html
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Footer.tsx
│   │   │   ├── Chat/
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   └── TypingIndicator.tsx
│   │   │   ├── Documents/
│   │   │   │   ├── DocumentList.tsx
│   │   │   │   ├── DocumentUpload.tsx
│   │   │   │   └── DocumentViewer.tsx
│   │   │   ├── Profiles/
│   │   │   │   ├── ProfileList.tsx
│   │   │   │   ├── ProfileEditor.tsx
│   │   │   │   └── ProfileSelector.tsx
│   │   │   └── Common/
│   │   │       ├── Button.tsx
│   │   │       ├── Input.tsx
│   │   │       ├── Modal.tsx
│   │   │       └── Loading.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Chat.tsx
│   │   │   ├── Documents.tsx
│   │   │   ├── Profiles.tsx
│   │   │   └── Settings.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useApi.ts
│   │   │   └── useLocalStorage.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── websocket.ts
│   │   │   └── types.ts
│   │   ├── store/
│   │   │   ├── index.ts
│   │   │   ├── chatStore.ts
│   │   │   ├── documentStore.ts
│   │   │   └── profileStore.ts
│   │   ├── styles/
│   │   │   └── globals.css
│   │   └── utils/
│   │       ├── constants.ts
│   │       ├── formatters.ts
│   │       └── validators.ts
│   └── nginx.conf                 # Nginx config for frontend
├── database/
│   ├── init.sql                   # Database initialization
│   └── migrations/                # SQL migration files
└── docs/
    ├── setup.md                   # Setup instructions
    ├── api.md                     # API documentation
    ├── deployment.md              # Deployment guide
    └── development.md             # Development guide
```

---

## 5. Configuration System

### 5.1 Environment Variables (.env)

```bash
# Database
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=secure_password

# API Keys
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...
ANTHROPIC_API_KEY=sk-ant-...

# Application
BACKEND_PORT=8000
FRONTEND_PORT=3000
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development

# Optional Features
ENABLE_AUTH=false
ENABLE_RATE_LIMITING=true
LOG_LEVEL=INFO
```

### 5.2 AI Providers Configuration (config.json)

```json
{
  "ai_providers": {
    "openai": {
      "base_url": "https://api.openai.com/v1",
      "models": {
        "gpt-4o-mini": {
          "max_tokens": 4000,
          "temperature": 0.7
        },
        "gpt-4": {
          "max_tokens": 8000,
          "temperature": 0.7
        }
      }
    },
    "gemini": {
      "base_url": "https://generativelanguage.googleapis.com/v1beta",
      "models": {
        "gemini-1.5-pro": {
          "max_tokens": 4000,
          "temperature": 0.7
        }
      }
    },
    "anthropic": {
      "base_url": "https://api.anthropic.com/v1",
      "models": {
        "claude-3-sonnet": {
          "max_tokens": 4000,
          "temperature": 0.7
        }
      }
    },
    "custom": {
      "base_url": "http://localhost:11434/v1",
      "models": {
        "llama3": {
          "max_tokens": 2000,
          "temperature": 0.7
        }
      }
    }
  },
  "profiles": [
    {
      "id": 1,
      "name": "General Assistant",
      "description": "General purpose Q&A assistant",
      "prompt": "You are a helpful assistant. Use the following context to answer questions accurately.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "settings": {
        "max_context_chunks": 5,
        "chunk_size": 1000,
        "chunk_overlap": 200
      }
    },
    {
      "id": 2,
      "name": "Technical Expert",
      "description": "Technical documentation assistant",
      "prompt": "You are a technical expert. Provide detailed, accurate answers based on the documentation context.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
      "provider": "anthropic",
      "model": "claude-3-sonnet",
      "settings": {
        "max_context_chunks": 8,
        "chunk_size": 1500,
        "chunk_overlap": 300
      }
    }
  ],
  "embedding": {
    "provider": "openai",
    "model": "text-embedding-3-small",
    "dimensions": 1536
  }
}
```

---

## 6. Database Schema

### 6.1 Core Tables

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Profiles table
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    prompt TEXT NOT NULL,
    provider VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    mime_type VARCHAR(100),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    profile_id INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
    metadata JSONB DEFAULT '{}'
);

-- Document chunks table
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    profile_id INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
    session_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    context_chunks JSONB DEFAULT '[]',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_document_chunks_profile ON document_chunks(profile_id);
CREATE INDEX idx_documents_profile ON documents(profile_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_sessions_profile ON chat_sessions(profile_id);
```

---

## 7. API Endpoints

### 7.1 REST API

```
# Health & Status
GET    /health                     # Health check
GET    /status                     # System status

# Profiles
GET    /api/v1/profiles           # List all profiles
GET    /api/v1/profiles/{id}      # Get profile by ID
POST   /api/v1/profiles           # Create new profile
PUT    /api/v1/profiles/{id}      # Update profile
DELETE /api/v1/profiles/{id}      # Delete profile

# Documents
GET    /api/v1/documents          # List documents
GET    /api/v1/documents/{id}     # Get document details
POST   /api/v1/documents/upload   # Upload document
DELETE /api/v1/documents/{id}     # Delete document
POST   /api/v1/documents/process  # Process uploaded document

# Chat
GET    /api/v1/chat/sessions      # List chat sessions
POST   /api/v1/chat/sessions      # Create new session
GET    /api/v1/chat/sessions/{id} # Get session messages
POST   /api/v1/chat/query         # Send chat message
DELETE /api/v1/chat/sessions/{id} # Delete session

# Search
POST   /api/v1/search             # Semantic search
POST   /api/v1/search/similar     # Find similar chunks

# Configuration
GET    /api/v1/config/providers   # Get available providers
GET    /api/v1/config/models      # Get available models
```

### 7.2 WebSocket Events

```
# Client to Server
chat:join_session        # Join chat session
chat:send_message        # Send message
chat:typing              # Typing indicator

# Server to Client
chat:message_received    # New message
chat:typing_indicator    # User typing
chat:session_created     # New session created
chat:error              # Error message
```

---

## 8. CLI Commands

### 8.1 Installation & Setup

```bash
# Initialize database
python cli.py init-db

# Create default profiles
python cli.py init-profiles

# Check system status
python cli.py status
```

### 8.2 Profile Management

```bash
# List profiles
python cli.py profiles list

# Create profile
python cli.py profiles create "Technical Expert" --provider anthropic --model claude-3-sonnet

# Update profile
python cli.py profiles update 1 --prompt "New prompt here"

# Delete profile
python cli.py profiles delete 2
```

### 8.3 Document Management

```bash
# Ingest single file
python cli.py ingest 1 document.pdf

# Ingest folder
python cli.py ingest-folder 1 ./documents/ --recursive

# List documents
python cli.py documents list --profile 1

# Delete document
python cli.py documents delete doc-uuid-here

# Reset profile data
python cli.py reset-profile 1

# Reset all data
python cli.py reset-all
```

### 8.4 Configuration

```bash
# Validate config
python cli.py config validate

# Test AI providers
python cli.py config test-providers

# Update provider settings
python cli.py config update-provider openai --base-url "https://custom.openai.com/v1"
```

---

## 9. Docker Configuration

### 9.1 docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./backend:/app
      - uploaded_files:/app/uploads
    ports:
      - "${BACKEND_PORT}:8000"
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "${FRONTEND_PORT}:3000"
    environment:
      - VITE_API_BASE_URL=http://localhost:${BACKEND_PORT}
      - VITE_WS_URL=ws://localhost:${BACKEND_PORT}
    command: npm run dev -- --host 0.0.0.0

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - frontend
      - backend
    profiles:
      - production

volumes:
  postgres_data:
  uploaded_files:
```

---

## 10. Development Workflow

### 10.1 Initial Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd rag-fullstack

# 2. Copy environment template
cp .env.example .env

# 3. Edit .env with your API keys and settings
nano .env

# 4. Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# 5. Initialize database and profiles
docker exec -it rag-fullstack-backend-1 python cli.py init-db
docker exec -it rag-fullstack-backend-1 python cli.py init-profiles

# 6. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 10.2 Development Commands

```bash
# Start development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Start specific services
docker-compose up db backend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute CLI commands
docker exec -it rag-fullstack-backend-1 python cli.py <command>

# Database access
docker exec -it rag-fullstack-db-1 psql -U rag_user -d rag_db

# Run tests
docker exec -it rag-fullstack-backend-1 pytest
```

---

## 11. Production Deployment

### 11.1 Production Setup

```bash
# 1. Use production compose file
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 2. Setup SSL certificates (recommended)
# Use Let's Encrypt or your certificate provider

# 3. Configure reverse proxy (nginx)
# Update nginx.conf with your domain

# 4. Set production environment variables
export ENVIRONMENT=production
export SECRET_KEY="your-production-secret"

# 5. Initialize production database
docker exec -it rag-fullstack-backend-1 python cli.py init-db
docker exec -it rag-fullstack-backend-1 python cli.py init-profiles
```

### 11.2 Production Security

- Use strong passwords and secrets
- Enable HTTPS with SSL certificates
- Implement rate limiting
- Use environment-specific API keys
- Regular security updates
- Database backups
- Log monitoring

---

## 12. UI/UX Design

### 12.1 Main Interface Components

1. **Header Navigation**
   - Logo and app name
   - Profile selector dropdown
   - Settings/admin access
   - Connection status indicator

2. **Sidebar**
   - Chat sessions list
   - Document management
   - Profile management
   - System status

3. **Main Chat Interface**
   - Message history with timestamps
   - Message input with file upload
   - Typing indicators
   - Context source citations
   - Response streaming

4. **Document Management**
   - Drag-and-drop upload
   - Document list with metadata
   - Processing status
   - Delete/reprocess options

5. **Profile Configuration**
   - Profile creation/editing
   - Prompt templates
   - AI provider selection
   - Advanced settings

### 12.2 Responsive Design

- Mobile-first approach
- Tablet and desktop optimized
- Collapsible sidebar
- Touch-friendly interactions
- Progressive web app features

---

## 13. Testing Strategy

### 13.1 Backend Testing

```bash
# Unit tests
pytest tests/test_ai_providers.py
pytest tests/test_embeddings.py
pytest tests/test_chunking.py

# Integration tests
pytest tests/test_api.py
pytest tests/test_cli.py

# End-to-end tests
pytest tests/test_e2e.py
```

### 13.2 Frontend Testing

```bash
# Unit tests with Vitest
npm run test

# Component tests
npm run test:components

# E2E tests with Playwright
npm run test:e2e
```

---

## 14. Monitoring & Logging

### 14.1 Application Metrics

- API response times
- Database query performance
- AI provider latency
- WebSocket connection stats
- File upload/processing times

### 14.2 Health Checks

- Database connectivity
- AI provider availability
- Vector search performance
- Memory and CPU usage
- Disk space monitoring

---

## 15. Future Enhancements

### Phase 2 Features
- User authentication and authorization
- Multi-tenant support
- Advanced document preprocessing
- Custom embedding models
- API rate limiting and quotas

### Phase 3 Features
- Mobile applications
- Advanced analytics dashboard
- A/B testing for prompts
- Integration with external systems
- Enterprise SSO support

---

## 16. Success Metrics

### Technical KPIs
- API response time < 2 seconds
- 99.9% uptime
- Vector search recall > 0.85
- File processing < 1 minute per MB

### User Experience KPIs
- Chat response time < 5 seconds
- Document upload success rate > 95%
- User session duration
- Feature adoption rates

---

## 17. Risk Assessment

### Technical Risks
- AI provider API limits/costs
- Database performance at scale
- WebSocket connection stability
- File storage requirements

### Mitigation Strategies
- Implement caching layers
- Provider fallback mechanisms
- Connection retry logic
- Storage cleanup policies

---

## 18. Deliverables Checklist

### Core Components
- [ ] Docker Compose configuration
- [ ] PostgreSQL with pgvector setup
- [ ] FastAPI backend with all endpoints
- [ ] React.js frontend with modern UI
- [ ] CLI tools for management
- [ ] Configuration system
- [ ] Documentation

### Quality Assurance
- [ ] Unit test coverage > 80%
- [ ] Integration tests
- [ ] Security review
- [ ] Performance testing
- [ ] Code review process

### Documentation
- [ ] Setup instructions
- [ ] API documentation
- [ ] User guide
- [ ] Deployment guide
- [ ] Troubleshooting guide

---

This comprehensive PRD provides all the specifications needed to develop a production-ready, full-stack RAG application with modern architecture, excellent user experience, and enterprise-grade features.