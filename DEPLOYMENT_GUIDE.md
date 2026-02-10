# VPS Deployment Guide - jndroid.store Backend

## Complete Production Deployment Steps

### Prerequisites
- Ubuntu 20.04 LTS or higher
- Root or sudo access
- Domain name (optional but recommended)
- PostgreSQL database setup

---

## Step 1: Server Setup (First Time Only)

### Update System
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3.10 python3.10-venv python3.10-dev
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx
sudo apt install -y git curl wget
```

### Create Application User
```bash
sudo useradd -m -s /bin/bash appuser
sudo usermod -aG sudo appuser
sudo su - appuser
```

### Clone Repository
```bash
cd /var/www
git clone https://github.com/yourusername/jndroid.store.git
cd jndroid.store/backend
```

---

## Step 2: Django Setup

### Create Virtual Environment
```bash
python3.10 -m venv venv
source venv/bin/activate
```

### Install Requirements
```bash
cp deploy.sh /tmp/
chmod +x /tmp/deploy.sh
/tmp/deploy.sh
```

Or manually:
```bash
pip install --upgrade pip
pip install Django==6.0.2
pip install -r requirements.txt
```

### Configure Environment Variables
```bash
cp .env.example .env
nano .env  # Edit with your settings
```

**Required .env variables:**
```
DEBUG=False
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-ip-address
DATABASE_URL=postgresql://dbuser:dbpassword@localhost:5432/jndroid_db
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Create PostgreSQL Database
```bash
sudo -u postgres psql
CREATE DATABASE jndroid_db;
CREATE USER jndroid_user WITH PASSWORD 'strong_password';
ALTER ROLE jndroid_user SET client_encoding TO 'utf8';
ALTER ROLE jndroid_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE jndroid_user SET default_transaction_deferrable TO on;
ALTER ROLE jndroid_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE jndroid_db TO jndroid_user;
\q
```

### Run Migrations
```bash
source venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py createsuperuser --noinput \
    --username admin \
    --email admin@yourdomain.com
```

---

## Step 3: Gunicorn Setup

### Create Log Directory
```bash
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
sudo chmod 755 /var/log/gunicorn
```

### Install Gunicorn Service
```bash
sudo cp gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

### Check Gunicorn Socket
```bash
ls -la /var/www/jndroid.store/backend/gunicorn.sock
```

---

## Step 4: Nginx Configuration

### Setup Nginx
```bash
# Copy config
sudo cp nginx.conf /etc/nginx/sites-available/jndroid-store
sudo ln -s /etc/nginx/sites-available/jndroid-store /etc/nginx/sites-enabled/

# Edit domain name
sudo nano /etc/nginx/sites-available/jndroid-store
# Replace: yourdomain.com with your actual domain

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## Step 5: SSL Certificate (Let's Encrypt)

### Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Generate Certificate
```bash
sudo certbot certonly --webroot -w /var/www/letsencrypt \
    -d yourdomain.com \
    -d www.yourdomain.com \
    --email admin@yourdomain.com \
    --agree-tos \
    --no-eff-email
```

### Enable HTTPS in Nginx
```bash
# Uncomment HTTPS section in nginx.conf
sudo nano /etc/nginx/sites-available/jndroid-store

# Uncomment the HTTPS server block and update domain names
sudo nginx -t
sudo systemctl restart nginx
```

### Auto-Renew Certificate
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## Step 6: Firewall Setup (UFW)

```bash
sudo ufw enable
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw status
```

---

## Step 7: Monitoring & Logs

### Check Application Logs
```bash
# Django logs
tail -f /var/log/gunicorn/error.log

# Nginx logs
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### Monitor Services
```bash
# Check Gunicorn status
systemctl status gunicorn

# Check Nginx status
systemctl status nginx

# Check PostgreSQL status
systemctl status postgresql
```

### Restart Services if Needed
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
sudo systemctl restart postgresql
```

---

## Step 8: Backup Strategy

### Daily Database Backup
```bash
# Create backup script
sudo nano /usr/local/bin/backup-db.sh
```

**Script content:**
```bash
#!/bin/bash
BACKUP_DIR="/backups/jndroid"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U jndroid_user -d jndroid_db > $BACKUP_DIR/db_$DATE.sql
gzip $BACKUP_DIR/db_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/db_$DATE.sql.gz"
```

### Add to Crontab
```bash
sudo chmod +x /usr/local/bin/backup-db.sh
sudo crontab -e
# Add: 2 2 * * * /usr/local/bin/backup-db.sh
```

---

## Troubleshooting

### 502 Bad Gateway Error
```bash
# Check Gunicorn socket
ls -la /var/www/jndroid.store/backend/gunicorn.sock

# Check Gunicorn service
systemctl status gunicorn
tail -f /var/log/gunicorn/error.log
```

### Static Files Not Loading
```bash
# Recollect static files
cd /var/www/jndroid.store/backend
source venv/bin/activate
python manage.py collectstatic --noinput
```

### Database Connection Error
```bash
# Test database
source venv/bin/activate
python manage.py dbshell

# Check PostgreSQL is running
systemctl status postgresql
```

### Permission Denied Errors
```bash
# Fix permissions
sudo chown -R www-data:www-data /var/www/jndroid.store/backend
sudo chmod -R 755 /var/www/jndroid.store/backend
```

---

## Performance Optimization

### Increase Gunicorn Workers
Edit `/etc/systemd/system/gunicorn.service`:
```
--workers 8  # Increase based on CPU cores (Cores * 2 + 1)
```

### Enable Caching
Edit `config/settings/production.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### Database Connection Pooling
```bash
pip install psycopg2-pool
```

---

## Useful Commands

```bash
# Check deployment status
python archived-scripts/production_audit.py

# View all users
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.all()

# Clear cache
python manage.py clear_cache

# Create superuser
python manage.py createsuperuser

# Dump database
pg_dump -U jndroid_user -d jndroid_db > backup.sql

# Restore database
psql -U jndroid_user -d jndroid_db < backup.sql
```

---

## Final Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] All requirements installed
- [ ] PostgreSQL database created
- [ ] `.env` file configured
- [ ] Migrations run successfully
- [ ] Static files collected
- [ ] Gunicorn running (systemd)
- [ ] Nginx configured
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Domain pointing to server
- [ ] Admin panel accessible
- [ ] Email verification working
- [ ] Database backups scheduled

---

## Support

If you encounter issues:
1. Check logs: `/var/log/gunicorn/error.log`
2. Test config: `python manage.py check`
3. Verify database: `python manage.py dbshell`
4. Run audit: `python archived-scripts/production_audit.py`

Good luck! 🚀
