# 🤖 Full-Stack RAG Application

A complete full-stack RAG (Retrieval-Augmented Generation) application featuring a modern React.js frontend, FastAPI backend, PostgreSQL with pgvector, and multi-provider AI support.

## 🚀 Features

- 🎨 **Modern React.js Web UI** with real-time chat interface
- 🚀 **FastAPI Backend** with async processing and WebSocket support
- 🗄️ **PostgreSQL + pgvector** for document storage and semantic search
- 🤖 **Multi-AI Provider Support** (OpenAI, Gemini, Claude, custom endpoints)
- 📁 **Document Management** with chunking and metadata
- 🔧 **CLI Tools** for setup, ingestion, and management
- 🐳 **Docker Compose** deployment with development and production configs

## 🏗️ Architecture

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

## 🛠️ Tech Stack

### Frontend
- **Framework:** React.js 18+ with TypeScript
- **Styling:** Tailwind CSS + Headless UI
- **State Management:** Zustand or Redux Toolkit
- **HTTP Client:** Axios
- **WebSocket:** Socket.IO client
- **Build Tool:** Vite

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Async Support:** asyncio, asyncpg
- **WebSocket:** FastAPI WebSocket + Socket.IO
- **File Processing:** PyPDF2, python-docx, markdown
- **Embeddings:** OpenAI embeddings, sentence-transformers
- **CLI:** Click framework

### Database
- **Primary:** PostgreSQL 15+
- **Vector Extension:** pgvector
- **Connection Pool:** asyncpg

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **Reverse Proxy:** Nginx (production)
- **Storage:** Docker volumes for persistence

## 📁 Project Structure

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
│   ├── config/                    # Configuration files
│   ├── api/                       # API routes and WebSocket
│   ├── core/                      # Core business logic
│   ├── cli/                       # CLI tools
│   └── tests/                     # Test files
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── src/                       # React source code
│   └── public/                    # Static assets
├── database/
│   ├── init.sql                   # Database initialization
│   └── migrations/                # SQL migration files
└── docs/                          # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag-fullstack
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Start the development environment**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
   ```

4. **Initialize the database and profiles**
   ```bash
   docker exec -it rag-fullstack-backend-1 python cli.py init-db
   docker exec -it rag-fullstack-backend-1 python cli.py init-profiles
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📋 Development Status

This project is currently in **development phase**. See [TASK_MANAGER.md](./TASK_MANAGER.md) for detailed development progress and task tracking.

### Current Status
- ✅ Project initialization and structure setup
- 🔄 Backend development in progress
- ⏳ Frontend development pending
- ⏳ Testing and documentation pending

## 🔧 CLI Commands

The application includes comprehensive CLI tools for management:

```bash
# Database initialization
python cli.py init-db
python cli.py init-profiles

# Profile management
python cli.py profiles list
python cli.py profiles create "Technical Expert" --provider anthropic --model claude-3-sonnet

# Document ingestion
python cli.py ingest 1 document.pdf
python cli.py ingest-folder 1 ./documents/ --recursive

# System management
python cli.py status
python cli.py config validate
```

## 📚 Documentation

- [Product Requirements Document](./PRD.md) - Complete project specifications
- [Task Manager](./TASK_MANAGER.md) - Development progress and task tracking
- [Setup Guide](./docs/setup.md) - Detailed setup instructions (coming soon)
- [API Documentation](./docs/api.md) - API reference (coming soon)
- [Deployment Guide](./docs/deployment.md) - Production deployment (coming soon)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the task manager for development status

---

**Status:** 🚧 Under Active Development  
**Last Updated:** $(date)  
**Version:** 2.0
