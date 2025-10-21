# Production Deployment Guide

This guide covers deploying the Amida AI Assistant to production.

## Pre-Deployment Checklist

- [ ] All OAuth credentials configured
- [ ] Strong SECRET_KEY generated
- [ ] Database backup strategy in place
- [ ] HTTPS/SSL certificates obtained
- [ ] Domain names configured
- [ ] Environment variables secured
- [ ] Monitoring set up
- [ ] Backup strategy implemented

## Environment Setup

### 1. Generate Secure Secret Key

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use this value for `SECRET_KEY` in production.

### 2. Production Environment Variables

Create a `.env.production` file:

```bash
# Application
SECRET_KEY=your-strong-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/amida_db
FRONTEND_URL=https://your-domain.com

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://your-domain.com/api/auth/google/callback

# Slack
SLACK_CLIENT_ID=your-client-id
SLACK_CLIENT_SECRET=your-client-secret
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_REDIRECT_URI=https://your-domain.com/api/auth/slack/callback
SLACK_BOT_TOKEN=xoxb-your-bot-token

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=your-deployment
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Database Migration to PostgreSQL

### 1. Install PostgreSQL

```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql
```

### 2. Create Database

```bash
sudo -u postgres psql
CREATE DATABASE amida_db;
CREATE USER amida_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE amida_db TO amida_user;
\q
```

### 3. Update Dependencies

Add to `requirements.txt`:
```
psycopg2-binary==2.9.9
```

### 4. Update DATABASE_URL

```bash
DATABASE_URL=postgresql://amida_user:strong_password@localhost/amida_db
```

## Backend Deployment

### Option 1: Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t amida-backend .
docker run -p 8000:8000 --env-file .env.production amida-backend
```

### Option 2: Systemd Service

**Create service file:** `/etc/systemd/system/amida-backend.service`

```ini
[Unit]
Description=Amida AI Assistant Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/amida/backend
Environment="PATH=/var/www/amida/venv/bin"
EnvironmentFile=/var/www/amida/backend/.env.production
ExecStart=/var/www/amida/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable amida-backend
sudo systemctl start amida-backend
sudo systemctl status amida-backend
```

### Option 3: Cloud Platforms

#### AWS EC2

1. Launch EC2 instance (t3.medium or larger)
2. Install dependencies
3. Set up nginx as reverse proxy
4. Configure SSL with Let's Encrypt
5. Use systemd service

#### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/amida-backend
gcloud run deploy amida-backend \
  --image gcr.io/PROJECT_ID/amida-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars="$(cat .env.production)"
```

#### Heroku

```bash
# Create app
heroku create amida-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
# ... set all other env vars

# Deploy
git push heroku main
```

## Frontend Deployment

### Build for Production

```bash
cd frontend
npm run build
```

This creates a `dist` folder with optimized static files.

### Option 1: Vercel

```bash
npm install -g vercel
vercel --prod
```

### Option 2: Netlify

```bash
npm install -g netlify-cli
netlify deploy --prod --dir=dist
```

### Option 3: Nginx Static Hosting

**Nginx config:** `/etc/nginx/sites-available/amida-frontend`

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /var/www/amida/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 4: AWS S3 + CloudFront

```bash
# Sync to S3
aws s3 sync dist/ s3://your-bucket-name/

# Set up CloudFront distribution pointing to S3 bucket
```

## Nginx Reverse Proxy Configuration

**Full config with SSL:**

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Frontend
    location / {
        root /var/www/amida/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support (if needed)
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## SSL/HTTPS Setup with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## Database Backup

### Automated PostgreSQL Backups

**Backup script:** `/opt/scripts/backup-amida-db.sh`

```bash
#!/bin/bash
BACKUP_DIR="/backups/amida"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/amida_db_$TIMESTAMP.sql"

# Create backup
pg_dump -U amida_user amida_db > $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

**Cron job:**
```bash
# Run daily at 2 AM
0 2 * * * /opt/scripts/backup-amida-db.sh
```

## Monitoring

### 1. Application Monitoring

**Using Sentry:**

```bash
pip install sentry-sdk
```

**Add to main.py:**
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### 2. Server Monitoring

**Using Prometheus + Grafana:**

```bash
# Install Prometheus
# Install Grafana
# Configure dashboards for:
# - CPU/Memory usage
# - Request rate
# - Error rate
# - Response time
```

### 3. Log Aggregation

**Using ELK Stack or CloudWatch:**

Configure application to send logs to centralized logging.

## Scaling

### Horizontal Scaling

**Using Docker Compose:**

```yaml
version: '3.8'
services:
  backend:
    image: amida-backend
    replicas: 3
    environment:
      - DATABASE_URL=postgresql://...
    depends_on:
      - db
  
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  nginx:
    image: nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Load Balancing

**Nginx load balancer config:**

```nginx
upstream backend {
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

## Security Hardening

### 1. Firewall Rules

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

### 2. Rate Limiting

Add to nginx config:
```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api {
    limit_req zone=api burst=20;
    proxy_pass http://localhost:8000;
}
```

### 3. Security Headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000" always;
```

## Performance Optimization

### 1. Database Indexing

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_activity_logs_user_id ON activity_logs(user_id);
CREATE INDEX idx_activity_logs_timestamp ON activity_logs(timestamp);
CREATE INDEX idx_cost_tracking_user_id ON cost_tracking(user_id);
```

### 2. Caching

**Using Redis:**

```bash
pip install redis
```

**Cache configuration:**
```python
import redis
cache = redis.Redis(host='localhost', port=6379, db=0)
```

### 3. CDN for Static Assets

Use CloudFlare, AWS CloudFront, or similar for:
- Frontend static files
- Images
- CSS/JS bundles

## Monitoring Checklist

- [ ] Server metrics (CPU, RAM, Disk)
- [ ] Application metrics (requests, errors, latency)
- [ ] Database metrics (connections, queries, slow queries)
- [ ] API rate limits
- [ ] SSL certificate expiration
- [ ] Backup success/failure
- [ ] Cost tracking (Azure OpenAI usage)

## Rollback Strategy

1. **Tag releases:**
   ```bash
   git tag -a v1.0.0 -m "Release 1.0.0"
   git push origin v1.0.0
   ```

2. **Keep previous version:**
   ```bash
   # Before deploying new version
   cp -r /var/www/amida /var/www/amida-backup
   ```

3. **Quick rollback:**
   ```bash
   # Stop current version
   sudo systemctl stop amida-backend
   
   # Restore backup
   rm -rf /var/www/amida
   mv /var/www/amida-backup /var/www/amida
   
   # Start service
   sudo systemctl start amida-backend
   ```

## Post-Deployment Testing

```bash
# Health check
curl https://your-domain.com/api/health

# Test authentication
curl https://your-domain.com/api/auth/status

# Check SSL
curl -I https://your-domain.com

# Test email (requires auth token)
curl -X POST https://your-domain.com/api/assistant/email-summary \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days": 1, "source": "portal"}'
```

## Support & Maintenance

### Regular Tasks

- **Daily:** Check logs for errors
- **Weekly:** Review cost tracking, update dependencies
- **Monthly:** Review security patches, database optimization
- **Quarterly:** Load testing, disaster recovery testing

---

Your Amida AI Assistant is production-ready! 🚀
