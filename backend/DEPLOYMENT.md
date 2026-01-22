# DEPLOYMENT.md

# Production Deployment Guide

This guide covers deploying the Billing Software backend to production.

## Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and merged
- [ ] Security settings configured
- [ ] Database backups in place
- [ ] Environment variables set
- [ ] HTTPS certificate obtained
- [ ] Email service configured
- [ ] Monitoring set up

## Environment Setup

### Production .env Configuration

```env
# Django
DEBUG=False
SECRET_KEY=your-strong-secret-key-here-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=billing_production
DB_USER=postgres_user
DB_PASSWORD=strong_password_here
DB_HOST=your-database-server.com
DB_PORT=5432

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password-here

# API
API_PAGINATION_SIZE=20
API_THROTTLE_RATE=100/hour

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/billing/django.log
```

## Deployment Methods

### Option 1: Using Gunicorn + Nginx

#### 1. Install Dependencies

```bash
pip install gunicorn whitenoise
```

#### 2. Create Systemd Service File

Create `/etc/systemd/system/billing-api.service`:

```ini
[Unit]
Description=Billing API Gunicorn Service
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/billing-software/backend
Environment="PATH=/opt/billing-software/backend/venv/bin"
EnvironmentFile=/opt/billing-software/backend/.env
ExecStart=/opt/billing-software/backend/venv/bin/gunicorn \
    --workers=4 \
    --worker-class=uvicorn.workers.UvicornWorker \
    --bind=127.0.0.1:8000 \
    --timeout=120 \
    --access-logfile=/var/log/billing/access.log \
    --error-logfile=/var/log/billing/error.log \
    core.wsgi:application

Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable billing-api
sudo systemctl start billing-api
sudo systemctl status billing-api
```

#### 3. Nginx Configuration

Create `/etc/nginx/sites-available/billing`:

```nginx
upstream billing_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;

    # Logging
    access_log /var/log/nginx/billing_access.log;
    error_log /var/log/nginx/billing_error.log;

    # Static files
    location /static/ {
        alias /opt/billing-software/backend/staticfiles/;
        expires 30d;
    }

    # Media files
    location /media/ {
        alias /opt/billing-software/backend/media/;
    }

    # API requests
    location / {
        proxy_pass http://billing_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/billing /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Using Docker

#### Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "core.wsgi:application"]
```

#### Create docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py collectstatic --noinput &&
             gunicorn --bind 0.0.0.0:8000 --workers 4 core.wsgi:application"
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DB_HOST=db
      - DB_PORT=5432
    depends_on:
      - db
    restart: always
    volumes:
      - ./logs:/app/logs
      - ./media:/app/media

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./staticfiles:/app/staticfiles:ro
      - ./media:/app/media:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - web
    restart: always

volumes:
  postgres_data:
```

Deploy:

```bash
docker-compose up -d
docker-compose logs -f
```

## SSL Certificate Setup

### Using Let's Encrypt (Certbot)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal
sudo certbot renew --dry-run
```

## Database Setup

### PostgreSQL Installation

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb billing_production

# Create user
sudo -u postgres createuser -P postgres_user

# Set permissions
sudo -u postgres psql -c "ALTER ROLE postgres_user CREATEDB;"
```

### Backup Strategy

```bash
# Daily backup script (backup.sh)
#!/bin/bash
BACKUP_DIR="/backups/billing"
DB_NAME="billing_production"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

Add to crontab:

```bash
0 2 * * * /opt/billing-software/backup.sh
```

## Monitoring and Logging

### Log Rotation

Create `/etc/logrotate.d/billing`:

```
/var/log/billing/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload billing-api > /dev/null 2>&1 || true
    endscript
}
```

### Monitoring with Prometheus + Grafana

Install prometheus-client:

```bash
pip install prometheus-client
```

Add metrics middleware to settings.py:

```python
INSTALLED_APPS = [
    ...
    'django_prometheus',
    ...
]

MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    ...
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
```

### Health Check Endpoint

Add to urls.py:

```python
path('health/', lambda request: JsonResponse({'status': 'ok'}), name='health-check'),
```

## Post-Deployment Steps

1. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

3. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

4. **Verify Installation**
   ```bash
   python manage.py check --deploy
   ```

5. **Test Email Configuration**
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
   ```

## Troubleshooting

### 502 Bad Gateway

1. Check gunicorn is running:
   ```bash
   systemctl status billing-api
   ```

2. Check logs:
   ```bash
   tail -f /var/log/billing/error.log
   ```

### Database Connection Issues

```bash
# Test connection
psql -h your-database-server.com -U postgres_user -d billing_production

# Check Django connection
python manage.py dbshell
```

### Static Files Not Loading

```bash
# Recollect static files
python manage.py collectstatic --clear --noinput

# Check permissions
ls -la staticfiles/
```

## Scaling Considerations

### Horizontal Scaling

1. Use load balancer (HAProxy, AWS ALB)
2. Multiple gunicorn workers per server
3. Multiple server instances
4. Shared database (PostgreSQL)
5. Redis for caching/sessions

### Database Scaling

1. Read replicas for read-heavy operations
2. Connection pooling (PgBouncer)
3. Regular VACUUM and ANALYZE
4. Index optimization

## Security Hardening

1. Keep dependencies updated
2. Regular security audits
3. Implement rate limiting
4. Monitor suspicious activity
5. Use WAF (Web Application Firewall)
6. Regular backups and restore testing
7. Principle of least privilege

## Disaster Recovery

### Backup Verification

```bash
# Test restore monthly
pg_restore -d test_db backup.sql.gz
```

### RTO and RPO

- RTO (Recovery Time Objective): < 1 hour
- RPO (Recovery Point Objective): < 1 day (daily backups)

### Failover Procedure

1. Verify backup integrity
2. Restore to backup server
3. Update DNS/load balancer
4. Monitor application
5. Communicate status

