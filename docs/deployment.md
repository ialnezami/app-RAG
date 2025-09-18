# 🚀 Deployment Guide

## Production Deployment Guide

This guide covers deploying the RAG application to production environments with proper security, performance, and reliability configurations.

## 📋 Pre-Deployment Checklist

### Infrastructure Requirements
- [ ] **Server**: Minimum 4 CPU cores, 16GB RAM, 100GB storage
- [ ] **Docker**: Version 20.0 or higher installed
- [ ] **Docker Compose**: Version 2.0 or higher
- [ ] **Domain**: Registered domain with DNS configured
- [ ] **SSL Certificate**: Valid SSL certificate for HTTPS
- [ ] **Backup Strategy**: Database backup solution in place
- [ ] **Monitoring**: System monitoring tools configured

### Security Requirements
- [ ] **Firewall**: Properly configured firewall rules
- [ ] **API Keys**: Production API keys obtained
- [ ] **Secrets**: All secrets properly secured
- [ ] **Updates**: System and dependencies updated
- [ ] **Access Control**: SSH keys and user access configured

## 🔧 Production Configuration

### Environment Variables
Create a production `.env` file with secure values:

```bash
# Database Configuration
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=rag_production
POSTGRES_USER=rag_prod_user
POSTGRES_PASSWORD=STRONG_RANDOM_PASSWORD_HERE

# API Keys (Production)
OPENAI_API_KEY=sk-prod-your-openai-key-here
GOOGLE_API_KEY=AI-prod-your-google-key-here
ANTHROPIC_API_KEY=sk-ant-prod-your-anthropic-key-here

# Application Configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
SECRET_KEY=STRONG_RANDOM_SECRET_KEY_64_CHARS_OR_MORE
ENVIRONMENT=production

# Security Settings
ENABLE_AUTH=true
ENABLE_RATE_LIMITING=true
LOG_LEVEL=WARNING

# File Upload Settings
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_FILE_TYPES=pdf,docx,txt,md

# AI Provider Settings
DEFAULT_EMBEDDING_PROVIDER=openai
DEFAULT_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# Production Settings
DEBUG=false
RELOAD=false
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# SSL and Security
SSL_REDIRECT=true
SECURE_COOKIES=true
HSTS_MAX_AGE=31536000
```

### Docker Compose Production
Use the production Docker Compose configuration:

```bash
# Start production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Nginx Configuration
Update `nginx/nginx.conf` for production:

```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=1r/s;
    
    # Upstream servers
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;
        
        # SSL Configuration
        ssl_certificate /etc/ssl/certs/yourdomain.crt;
        ssl_certificate_key /etc/ssl/private/yourdomain.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # Client max body size (for file uploads)
        client_max_body_size 50M;
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Backend API
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # File uploads
        location /api/v1/documents/upload {
            limit_req zone=upload burst=5 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_request_buffering off;
        }
        
        # WebSocket
        location /ws {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 86400;
        }
        
        # Health checks
        location /health {
            proxy_pass http://backend;
            access_log off;
        }
        
        # Static files caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## 🔐 SSL Certificate Setup

### Using Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (add to crontab)
0 12 * * * /usr/bin/certbot renew --quiet
```

### Using Custom Certificate
1. Place certificate files in appropriate directories
2. Update Nginx configuration with correct paths
3. Set proper file permissions (600 for private key)

## 🗄️ Database Configuration

### Production Database Settings
```bash
# Connect to database container
docker exec -it apprag-db-1 psql -U rag_prod_user -d rag_production

# Create additional indexes for performance
CREATE INDEX CONCURRENTLY idx_documents_profile_processed ON documents(profile_id, processed);
CREATE INDEX CONCURRENTLY idx_chat_sessions_profile_updated ON chat_sessions(profile_id, updated_at DESC);
CREATE INDEX CONCURRENTLY idx_chat_messages_session_role ON chat_messages(session_id, role);

# Configure PostgreSQL settings
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

# Restart database
SELECT pg_reload_conf();
```

### Database Backup Strategy
```bash
#!/bin/bash
# backup-database.sh

BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="rag_backup_${DATE}.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
docker exec apprag-db-1 pg_dump -U rag_prod_user -d rag_production > "$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Keep only last 30 days of backups
find $BACKUP_DIR -name "rag_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

Set up automated backups:
```bash
# Add to crontab
0 2 * * * /path/to/backup-database.sh
```

## 📊 Monitoring and Logging

### Application Monitoring
Create `docker-compose.monitoring.yml`:

```yaml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin_password_change_me
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  prometheus_data:
  grafana_data:
```

### Log Management
Configure centralized logging:

```yaml
# Add to main docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
  frontend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Health Check Script
Create `health-check.sh`:

```bash
#!/bin/bash
# health-check.sh

BACKEND_URL="https://yourdomain.com/health"
FRONTEND_URL="https://yourdomain.com"

# Check backend health
if curl -f -s $BACKEND_URL > /dev/null; then
    echo "Backend: OK"
else
    echo "Backend: FAILED"
    # Send alert (email, Slack, etc.)
fi

# Check frontend
if curl -f -s $FRONTEND_URL > /dev/null; then
    echo "Frontend: OK"
else
    echo "Frontend: FAILED"
    # Send alert
fi

# Check database
if docker exec apprag-db-1 pg_isready -U rag_prod_user -d rag_production > /dev/null; then
    echo "Database: OK"
else
    echo "Database: FAILED"
    # Send alert
fi
```

## 🚀 Deployment Process

### Initial Deployment
```bash
# 1. Clone repository on server
git clone <repository-url> /opt/rag-app
cd /opt/rag-app

# 2. Set up environment
cp .env.example .env
# Edit .env with production values

# 3. Set up SSL certificates
# (Follow SSL setup instructions above)

# 4. Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# 5. Initialize database
docker exec -it apprag-backend-1 python cli.py init-db
docker exec -it apprag-backend-1 python cli.py init-profiles

# 6. Verify deployment
curl https://yourdomain.com/health
```

### Updates and Maintenance
```bash
#!/bin/bash
# deploy-update.sh

cd /opt/rag-app

# 1. Pull latest changes
git pull origin main

# 2. Backup database
./backup-database.sh

# 3. Build and restart services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Run any database migrations
docker exec -it apprag-backend-1 python cli.py migrate

# 5. Verify deployment
sleep 30
curl -f https://yourdomain.com/health || echo "Deployment verification failed"
```

### Rollback Process
```bash
#!/bin/bash
# rollback.sh

cd /opt/rag-app

# 1. Get previous commit
PREVIOUS_COMMIT=$(git log --oneline -n 2 | tail -n 1 | cut -d' ' -f1)

# 2. Rollback code
git checkout $PREVIOUS_COMMIT

# 3. Restore database backup if needed
# docker exec -i apprag-db-1 psql -U rag_prod_user -d rag_production < backup.sql

# 4. Restart services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

echo "Rolled back to commit: $PREVIOUS_COMMIT"
```

## 🔧 Performance Optimization

### Database Optimization
```sql
-- Analyze query performance
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;

-- Update table statistics
ANALYZE documents;
ANALYZE document_chunks;
ANALYZE chat_sessions;
ANALYZE chat_messages;

-- Vacuum tables
VACUUM ANALYZE documents;
VACUUM ANALYZE document_chunks;
```

### Application Tuning
```bash
# Backend optimization
# Edit backend/main.py to add:
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000
)

# Database connection pooling
export DATABASE_POOL_SIZE=20
export DATABASE_MAX_OVERFLOW=30
```

### Caching Strategy
```nginx
# Add to nginx.conf
location /api/v1/profiles {
    proxy_cache_valid 200 5m;
    proxy_cache_key $request_uri;
    proxy_pass http://backend;
}
```

## 🛡️ Security Hardening

### System Security
```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Configure firewall
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh
```

### Application Security
```bash
# Set secure file permissions
chmod 600 .env
chmod 600 ssl/private/*
chmod 644 ssl/certs/*

# Regular security updates
docker-compose pull
docker-compose up -d --build
```

### Monitoring Security
```bash
# Install fail2ban
sudo apt-get install fail2ban

# Configure fail2ban for nginx
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
# Edit jail.local to enable nginx protection
```

## 📈 Scaling Considerations

### Horizontal Scaling
- **Load Balancer**: Use nginx or cloud load balancer
- **Multiple Backend Instances**: Scale backend containers
- **Database Replication**: Set up read replicas
- **File Storage**: Use object storage (S3, etc.)

### Vertical Scaling
- **CPU**: Monitor and upgrade as needed
- **Memory**: Increase for better performance
- **Storage**: SSD for database, object storage for files

### Cloud Deployment
- **AWS**: ECS, RDS, S3, CloudFront
- **Google Cloud**: Cloud Run, Cloud SQL, Cloud Storage
- **Azure**: Container Instances, Azure Database, Blob Storage

## 🚨 Troubleshooting

### Common Production Issues

#### High Memory Usage
```bash
# Check container memory usage
docker stats

# Optimize database connections
# Reduce worker processes if needed
```

#### Slow API Responses
```bash
# Check database performance
docker exec -it apprag-db-1 psql -U rag_prod_user -d rag_production -c "SELECT * FROM pg_stat_activity;"

# Check for long-running queries
# Optimize database indexes
```

#### SSL Certificate Issues
```bash
# Check certificate expiration
openssl x509 -in /etc/ssl/certs/yourdomain.crt -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew --dry-run
```

## 📞 Production Support

### Emergency Contacts
- **System Administrator**: [contact info]
- **Database Administrator**: [contact info]
- **DevOps Team**: [contact info]

### Monitoring Alerts
Set up alerts for:
- Service downtime
- High resource usage
- Database connection issues
- SSL certificate expiration
- Failed backups

### Maintenance Windows
- **Scheduled Maintenance**: First Sunday of each month, 2-4 AM
- **Emergency Maintenance**: As needed with 2-hour notice
- **Updates**: Weekly security updates, monthly feature updates

---

**Production Deployment Complete!** 🎉 Your RAG application is now running securely in production.
