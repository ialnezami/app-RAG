# Setup Instructions

## Prerequisites

- Docker and Docker Compose
- Git
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag-fullstack
   ```

2. **Copy environment template**
   ```bash
   cp .env.example .env
   ```

3. **Edit environment variables**
   ```bash
   nano .env
   ```
   
   Add your API keys:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GOOGLE_API_KEY`: Your Google API key (optional)
   - `ANTHROPIC_API_KEY`: Your Anthropic API key (optional)

4. **Start the development environment**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
   ```

5. **Initialize the database**
   ```bash
   docker exec -it rag-fullstack-backend-1 python cli.py init-db
   docker exec -it rag-fullstack-backend-1 python cli.py init-profiles
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Development Commands

### Start services
```bash
# All services
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Specific services
docker-compose up db backend
```

### View logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Execute CLI commands
```bash
docker exec -it rag-fullstack-backend-1 python cli.py <command>
```

### Database access
```bash
docker exec -it rag-fullstack-db-1 psql -U rag_user -d rag_db
```

### Run tests
```bash
docker exec -it rag-fullstack-backend-1 pytest
```

## Production Deployment

1. **Use production compose file**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

2. **Setup SSL certificates** (recommended)
   - Use Let's Encrypt or your certificate provider
   - Update nginx configuration with your domain

3. **Set production environment variables**
   ```bash
   export ENVIRONMENT=production
   export SECRET_KEY="your-production-secret"
   ```

4. **Initialize production database**
   ```bash
   docker exec -it rag-fullstack-backend-1 python cli.py init-db
   docker exec -it rag-fullstack-backend-1 python cli.py init-profiles
   ```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in `.env` file
2. **API key errors**: Verify API keys are correctly set
3. **Database connection**: Check if PostgreSQL container is running
4. **Build failures**: Clear Docker cache: `docker system prune -a`

### Health Checks

- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000/health
- Database: `docker exec -it rag-fullstack-db-1 pg_isready`

### Logs

- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`
- Database logs: `docker-compose logs db`
