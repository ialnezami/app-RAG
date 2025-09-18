# 🚀 Setup Guide

## Full-Stack RAG Application Setup

This guide will help you set up the RAG (Retrieval-Augmented Generation) application on your local machine or production environment.

## 📋 Prerequisites

### System Requirements
- **Operating System**: macOS, Linux, or Windows with WSL2
- **Docker**: Version 20.0 or higher
- **Docker Compose**: Version 2.0 or higher
- **Git**: Latest version
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: At least 10GB free space

### Required API Keys
You'll need at least one of the following API keys:
- **OpenAI API Key** (Recommended): For GPT models and embeddings
- **Google API Key**: For Gemini models
- **Anthropic API Key**: For Claude models

## 🛠️ Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd app\ RAG
```

### 2. Environment Configuration
```bash
# Copy the environment template
cp .env.example .env

# Edit the environment file
nano .env
```

**Required Environment Variables:**
```bash
# Database Configuration
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=secure_password_change_in_production

# API Keys (At least one required)
OPENAI_API_KEY=sk-your-openai-key-here
GOOGLE_API_KEY=AI-your-google-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Application Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development

# Optional Features
ENABLE_AUTH=false
ENABLE_RATE_LIMITING=true
LOG_LEVEL=INFO

# File Upload Settings
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=pdf,docx,txt,md

# AI Provider Settings
DEFAULT_EMBEDDING_PROVIDER=openai
DEFAULT_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# Development Settings
DEBUG=true
RELOAD=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Start the Application

#### Development Environment
```bash
# Start all services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Or start in detached mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

#### Production Environment
```bash
# Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 4. Initialize the Database
```bash
# Initialize database tables
docker exec -it apprag-backend-1 python cli.py init-db

# Create default AI profiles
docker exec -it apprag-backend-1 python cli.py init-profiles

# Check system status
docker exec -it apprag-backend-1 python cli.py status
```

### 5. Verify Installation
```bash
# Check if all services are running
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test frontend (should return HTML)
curl http://localhost:3000
```

## 🌐 Access the Application

Once setup is complete, you can access:

- **Frontend Web UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (if needed for direct access)

## 📁 First-Time Usage

### 1. Create Your First Profile
```bash
# Via CLI
docker exec -it apprag-backend-1 python cli.py profiles create "My Assistant" --provider openai --model gpt-4o-mini

# Or use the web interface at http://localhost:3000/profiles
```

### 2. Upload Documents
```bash
# Via CLI
docker exec -it apprag-backend-1 python cli.py ingest 1 /path/to/document.pdf

# Or use the web interface at http://localhost:3000/documents
```

### 3. Start Chatting
- Navigate to http://localhost:3000/chat
- Select your profile
- Ask questions about your uploaded documents

## 🔧 Configuration Options

### AI Provider Configuration
Edit `backend/config/config.json` to customize AI providers and models:

```json
{
  "ai_providers": {
    "openai": {
      "base_url": "https://api.openai.com/v1",
      "models": {
        "gpt-4o-mini": {
          "max_tokens": 4000,
          "temperature": 0.7
        }
      }
    }
  }
}
```

### Database Configuration
The application uses PostgreSQL with pgvector extension for vector similarity search. Database settings are configured via environment variables.

### File Upload Limits
- **Max file size**: 10MB (configurable via `MAX_FILE_SIZE`)
- **Supported formats**: PDF, DOCX, TXT, MD
- **Storage**: Files are stored in Docker volumes

## 🔍 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Kill processes using the ports
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Or change ports in .env file
FRONTEND_PORT=3001
BACKEND_PORT=8001
```

#### Docker Issues
```bash
# Restart Docker
docker-compose down
docker-compose up --build

# Clean Docker system
docker system prune -a
```

#### Database Connection Issues
```bash
# Check database health
docker exec -it apprag-db-1 pg_isready -U rag_user -d rag_db

# View database logs
docker-compose logs db
```

#### API Key Issues
- Verify API keys are correctly set in `.env`
- Check API key permissions and quotas
- Test API keys with provider's official tools

### Log Analysis
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f backend
```

## 🔒 Security Considerations

### Development
- Default passwords are used for development
- Debug mode is enabled
- CORS is permissive

### Production
- Change all default passwords
- Set strong `SECRET_KEY`
- Configure proper CORS origins
- Enable HTTPS with SSL certificates
- Set `ENVIRONMENT=production`
- Disable debug mode (`DEBUG=false`)

## 📞 Support

### Getting Help
- Check the [Troubleshooting Guide](troubleshooting.md)
- Review the [API Documentation](api.md)
- Check Docker logs for error messages
- Ensure all prerequisites are met

### Common Commands
```bash
# Restart services
docker-compose restart

# Update application
git pull
docker-compose build --no-cache
docker-compose up -d

# Backup database
docker exec apprag-db-1 pg_dump -U rag_user rag_db > backup.sql

# Reset application data
docker exec -it apprag-backend-1 python cli.py reset-all
```

## ✅ Next Steps

After successful setup:
1. Read the [User Guide](user-guide.md)
2. Explore the [API Documentation](api.md)
3. Check the [Development Guide](development.md) if you plan to modify the code
4. Review the [Deployment Guide](deployment.md) for production deployment

---

**Setup Complete!** 🎉 Your RAG application is now ready to use.