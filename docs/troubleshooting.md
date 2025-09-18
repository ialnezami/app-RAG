# 🔧 Troubleshooting Guide

## RAG Application Troubleshooting

This guide helps you diagnose and resolve common issues with your RAG application.

## 🚨 Emergency Quick Fixes

### Application Won't Start
```bash
# Check if Docker is running
docker version

# Check container status
docker-compose ps

# Restart all services
docker-compose down
docker-compose up -d --build

# Check logs
docker-compose logs --tail=50
```

### Database Connection Failed
```bash
# Check database health
docker exec apprag-db-1 pg_isready -U rag_user -d rag_db

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Frontend Not Loading
```bash
# Check frontend container
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend

# Check if port 3000 is available
lsof -ti:3000
```

## 🔍 Diagnostic Tools

### System Health Check
```bash
#!/bin/bash
# health-check.sh

echo "=== RAG Application Health Check ==="

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker: $(docker --version)"
else
    echo "❌ Docker: Not installed"
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose: $(docker-compose --version)"
else
    echo "❌ Docker Compose: Not installed"
fi

# Check containers
echo -e "\n=== Container Status ==="
docker-compose ps

# Check services
echo -e "\n=== Service Health ==="
curl -s http://localhost:8000/health | jq . || echo "❌ Backend health check failed"
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend accessible" || echo "❌ Frontend not accessible"

# Check database
docker exec apprag-db-1 pg_isready -U rag_user -d rag_db && echo "✅ Database ready" || echo "❌ Database not ready"

# Check disk space
echo -e "\n=== Disk Usage ==="
df -h

# Check memory
echo -e "\n=== Memory Usage ==="
free -h

echo -e "\n=== Docker Stats ==="
docker stats --no-stream
```

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

# View last 100 lines
docker-compose logs --tail=100 backend

# Filter logs by time
docker-compose logs --since="2024-01-01T00:00:00" backend
```

## 🐛 Common Issues and Solutions

### 1. Port Already in Use

**Problem**: `Error: Port 3000/8000 already in use`

**Symptoms**:
- Container fails to start
- "Port already allocated" error messages

**Solutions**:
```bash
# Find process using the port
lsof -ti:3000
lsof -ti:8000

# Kill the process
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Or change ports in .env file
FRONTEND_PORT=3001
BACKEND_PORT=8001
```

### 2. Database Connection Issues

**Problem**: `Cannot connect to database`

**Symptoms**:
- Backend fails to start
- "Connection refused" errors
- Database health check fails

**Solutions**:
```bash
# Check database container
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Check database credentials in .env
cat .env | grep POSTGRES

# Connect directly to database
docker exec -it apprag-db-1 psql -U rag_user -d rag_db

# Reset database if corrupted
docker-compose down
docker volume rm apprag_postgres_data
docker-compose up -d
```

### 3. File Upload Issues

**Problem**: `File upload fails or times out`

**Symptoms**:
- Upload progress stops
- "File too large" errors
- Upload timeout

**Solutions**:
```bash
# Check file size limits
grep MAX_FILE_SIZE .env

# Check allowed file types
grep ALLOWED_FILE_TYPES .env

# Check nginx upload limits (if using nginx)
grep client_max_body_size nginx/nginx.conf

# Check disk space
df -h

# Check upload directory permissions
docker exec apprag-backend-1 ls -la uploads/
```

### 4. AI Provider API Issues

**Problem**: `AI provider request failed`

**Symptoms**:
- Chat responses fail
- "API key invalid" errors
- "Rate limit exceeded"

**Solutions**:
```bash
# Check API keys
grep API_KEY .env

# Test API key manually
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# Check API provider status
# OpenAI: https://status.openai.com/
# Anthropic: https://status.anthropic.com/

# Check rate limits and quotas
# Review API provider dashboard

# Try different model
# Edit profile to use different model/provider
```

### 5. Document Processing Stuck

**Problem**: `Documents stuck in processing state`

**Symptoms**:
- Processing never completes
- No embeddings generated
- Search returns no results

**Solutions**:
```bash
# Check backend logs for errors
docker-compose logs backend | grep -i error

# Check document in database
docker exec -it apprag-db-1 psql -U rag_user -d rag_db -c "SELECT id, filename, processed FROM documents WHERE processed = false;"

# Manually reprocess document
docker exec -it apprag-backend-1 python cli.py documents reprocess DOCUMENT_ID

# Check file format support
file your-document.pdf

# Try with smaller document first
```

### 6. Memory Issues

**Problem**: `Out of memory errors`

**Symptoms**:
- Containers crashing
- Slow performance
- System becomes unresponsive

**Solutions**:
```bash
# Check memory usage
free -h
docker stats

# Reduce memory usage
# Edit docker-compose.yml to add memory limits:
services:
  backend:
    mem_limit: 1g
  frontend:
    mem_limit: 512m

# Optimize database settings
docker exec -it apprag-db-1 psql -U rag_user -d rag_db -c "SHOW shared_buffers;"

# Clear Docker system
docker system prune -a
```

### 7. Slow Performance

**Problem**: `Application running slowly`

**Symptoms**:
- Long response times
- Timeouts
- High CPU usage

**Solutions**:
```bash
# Check system resources
htop
docker stats

# Check database performance
docker exec -it apprag-db-1 psql -U rag_user -d rag_db -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Optimize database
docker exec -it apprag-backend-1 python cli.py db optimize

# Reduce context chunks in profiles
# Edit profile settings: max_context_chunks = 3

# Check network latency to AI providers
ping api.openai.com
```

### 8. SSL/HTTPS Issues

**Problem**: `SSL certificate errors`

**Symptoms**:
- Browser security warnings
- Certificate expired errors
- Mixed content warnings

**Solutions**:
```bash
# Check certificate validity
openssl x509 -in /path/to/cert.crt -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew

# Check nginx configuration
nginx -t

# Check certificate chain
openssl s_client -connect yourdomain.com:443 -showcerts
```

### 9. WebSocket Connection Issues

**Problem**: `Real-time chat not working`

**Symptoms**:
- Messages don't appear in real-time
- Connection keeps dropping
- WebSocket errors in console

**Solutions**:
```bash
# Check WebSocket endpoint
curl -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost:8000/ws

# Check nginx WebSocket configuration
grep -A 10 "location /ws" nginx/nginx.conf

# Check browser console for errors
# Open browser dev tools → Console

# Test with simple WebSocket client
# Use online WebSocket test tool
```

### 10. Search Not Working

**Problem**: `Search returns no results`

**Symptoms**:
- Empty search results
- "No embeddings found" errors
- Search takes too long

**Solutions**:
```bash
# Check if documents are processed
docker exec -it apprag-db-1 psql -U rag_user -d rag_db -c "SELECT COUNT(*) FROM document_chunks WHERE embedding IS NOT NULL;"

# Check embedding service
docker exec -it apprag-backend-1 python -c "from core.embeddings import get_embedding_generator; print(get_embedding_generator().test_connection())"

# Reprocess documents
docker exec -it apprag-backend-1 python cli.py documents reprocess-all

# Check similarity threshold
# Lower threshold in search (try 0.5 instead of 0.8)
```

## 🔧 Advanced Debugging

### Database Debugging
```sql
-- Connect to database
docker exec -it apprag-db-1 psql -U rag_user -d rag_db

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname = 'public';

-- Check running queries
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';

-- Check locks
SELECT 
    t.relname,
    l.locktype,
    page,
    virtualtransaction,
    pid,
    mode,
    granted
FROM pg_locks l, pg_stat_all_tables t
WHERE l.relation = t.relid
ORDER BY relation asc;

-- Check index usage
SELECT 
    indexrelname,
    idx_tup_read,
    idx_tup_fetch,
    idx_scan
FROM pg_stat_user_indexes;
```

### Backend Debugging
```python
# Add to backend for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test AI provider connection
python -c "
from core.ai_providers import get_provider_manager
pm = get_provider_manager()
print('Available providers:', pm.get_available_providers())
"

# Test database connection
python -c "
import asyncio
from core.database import check_db_health
print('DB Health:', asyncio.run(check_db_health()))
"

# Test embeddings
python -c "
import asyncio
from core.embeddings import get_embedding_generator
eg = get_embedding_generator()
result = asyncio.run(eg.generate_single_embedding('test'))
print('Embedding length:', len(result) if result else 'Failed')
"
```

### Frontend Debugging
```javascript
// Browser console debugging
// Check WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('WebSocket connected');
ws.onerror = (error) => console.error('WebSocket error:', error);

// Check API connectivity
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(data => console.log('API Health:', data))
  .catch(err => console.error('API Error:', err));

// Check local storage
console.log('Local storage:', localStorage);
```

## 📊 Performance Monitoring

### System Metrics
```bash
# CPU usage
top -p $(pgrep -d, -f docker)

# Memory usage by container
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Disk I/O
iostat -x 1

# Network usage
nethogs

# Database connections
docker exec -it apprag-db-1 psql -U rag_user -d rag_db -c "SELECT count(*) FROM pg_stat_activity;"
```

### Application Metrics
```bash
# API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Database query performance
docker exec -it apprag-db-1 psql -U rag_user -d rag_db -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# File upload performance
time curl -F "file=@test.pdf" -F "profile_id=1" http://localhost:8000/api/v1/documents/upload
```

## 🆘 Getting Help

### Information to Gather
Before seeking help, collect:

1. **System Information**:
   ```bash
   uname -a
   docker --version
   docker-compose --version
   ```

2. **Error Messages**:
   ```bash
   docker-compose logs --tail=100 > logs.txt
   ```

3. **Configuration**:
   ```bash
   cat .env | grep -v API_KEY > config.txt
   docker-compose ps > containers.txt
   ```

4. **Resource Usage**:
   ```bash
   free -h > memory.txt
   df -h > disk.txt
   docker stats --no-stream > docker-stats.txt
   ```

### Support Channels
- **Documentation**: Check setup.md, api.md, user-guide.md
- **Logs**: Review application logs for error messages
- **GitHub Issues**: Search existing issues for similar problems
- **Community Forums**: Ask questions with full error details

### Emergency Procedures

#### Complete System Reset
```bash
# WARNING: This will delete all data
docker-compose down -v
docker system prune -a
rm -rf uploads/*
docker-compose up -d --build
docker exec -it apprag-backend-1 python cli.py init-db
docker exec -it apprag-backend-1 python cli.py init-profiles
```

#### Rollback to Previous Version
```bash
git log --oneline -10  # Find previous commit
git checkout PREVIOUS_COMMIT_HASH
docker-compose down
docker-compose up -d --build
```

#### Data Recovery
```bash
# Restore from backup
docker exec -i apprag-db-1 psql -U rag_user -d rag_db < backup.sql

# Export current data
docker exec apprag-db-1 pg_dump -U rag_user rag_db > current_backup.sql
```

## 📝 Maintenance Tasks

### Daily Checks
- [ ] Check service health endpoints
- [ ] Review error logs
- [ ] Monitor disk space
- [ ] Check backup completion

### Weekly Tasks
- [ ] Update system packages
- [ ] Review performance metrics
- [ ] Clean up old log files
- [ ] Test backup restoration

### Monthly Tasks
- [ ] Update Docker images
- [ ] Review security settings
- [ ] Analyze database performance
- [ ] Update SSL certificates if needed

---

**Need More Help?** 🤔 Check the other documentation files or create a detailed issue report with the information gathered above.
