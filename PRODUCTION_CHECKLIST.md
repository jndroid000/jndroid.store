# Production Deployment Checklist - jndroid.store

## ✅ Pre-Deployment Checklist

### Local Computer (Windows)

- [ ] Open `.env.production.template` file
- [ ] Run: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- [ ] Copy the SECRET_KEY output
- [ ] Generate Gmail App Password from https://myaccount.google.com/apppasswords
- [ ] Save these credentials securely
- [ ] Open Notepad and prepare `.env.production` content with:
  - [ ] SECRET_KEY (generated above)
  - [ ] DATABASE_PASSWORD (PostgreSQL password)
  - [ ] EMAIL_HOST_PASSWORD (Gmail App Password)
  - [ ] ALLOWED_HOSTS (your VPS IP)
- [ ] Run: `git add . && git commit -m "Production ready" && git push`

---

### VPS Server (Linux)

- [ ] SSH into VPS: `ssh root@your-vps-ip`
- [ ] Create PostgreSQL database:
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
- [ ] Verify database created: `sudo -u postgres psql -l | grep jndroid_db`

---

### FileZilla Upload

- [ ] Open FileZilla
- [ ] Connect to VPS via SFTP
- [ ] Create new file with `.env.production` content
- [ ] Navigate to `/var/www/jndroid.store/backend/`
- [ ] Upload `.env.production` file
- [ ] Verify file uploaded: `ls -la /var/www/jndroid.store/backend/.env.production`
- [ ] Set correct permissions: 
  ```bash
  chmod 600 /var/www/jndroid.store/backend/.env.production
  ```

---

### VPS Deployment

- [ ] SSH into VPS
- [ ] Navigate: `cd /var/www/jndroid.store/backend`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Pull latest code: `git pull origin main`
- [ ] Install packages: `pip install -r requirements.txt`
- [ ] Run migrations: `python manage.py migrate --noinput`
- [ ] Collect static: `python manage.py collectstatic --noinput`
- [ ] Verify setup: `python archived-scripts/final_verify.py`
- [ ] Check audit: `python archived-scripts/production_audit.py`

---

### Gunicorn & Nginx Setup

- [ ] Copy Gunicorn service: `sudo cp gunicorn.service /etc/systemd/system/`
- [ ] Reload systemd: `sudo systemctl daemon-reload`
- [ ] Enable Gunicorn: `sudo systemctl enable gunicorn`
- [ ] Start Gunicorn: `sudo systemctl start gunicorn`
- [ ] Check status: `sudo systemctl status gunicorn`
- [ ] Copy Nginx config: `sudo cp nginx.conf /etc/nginx/sites-available/jndroid-store`
- [ ] Enable site: `sudo ln -s /etc/nginx/sites-available/jndroid-store /etc/nginx/sites-enabled/`
- [ ] Test Nginx: `sudo nginx -t`
- [ ] Restart Nginx: `sudo systemctl restart nginx`

---

### SSL Certificate (Let's Encrypt)

- [ ] Install Certbot: `sudo apt install certbot python3-certbot-nginx`
- [ ] Generate certificate:
  ```bash
  sudo certbot certonly --webroot -w /var/www/letsencrypt \
      -d jndroid.store \
      -d www.jndroid.store \
      --email jndroid000@gmail.com \
      --agree-tos \
      --no-eff-email
  ```
- [ ] Update Nginx for HTTPS (uncomment in nginx.conf)
- [ ] Reload Nginx: `sudo systemctl reload nginx`
- [ ] Test SSL: `https://jndroid.store` in browser

---

### Final Verification

- [ ] Visit `https://jndroid.store` in browser
- [ ] Verify no SSL errors
- [ ] Check admin panel: `https://jndroid.store/admin`
- [ ] Verify email verification works
- [ ] Run final audit: `python archived-scripts/production_audit.py`
- [ ] Check logs: `tail -f /var/log/gunicorn/error.log`

---

## Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| 502 Bad Gateway | Check Gunicorn: `systemctl status gunicorn` |
| Static files not loading | Run `python manage.py collectstatic --noinput` |
| Database connection error | Verify PostgreSQL: `sudo systemctl status postgresql` |
| Permission denied | Fix: `sudo chown -R www-data:www-data /var/www/jndroid.store` |
| Email not sending | Check credentials in `.env.production` |

---

## Important Files Location

```
/var/www/jndroid.store/backend/
├── .env.production          ← Configuration (upload via FileZilla)
├── manage.py
├── requirements.txt
├── deploy.sh
├── gunicorn.service
├── nginx.conf
├── staticfiles/             ← Generated after collectstatic
├── media/                   ← User uploads
└── archived-scripts/        ← Utility scripts
```

---

## Useful Commands

```bash
# Check Django settings
python manage.py check

# Create superuser
python manage.py createsuperuser

# View migrations
python manage.py showmigrations

# Backup database
pg_dump -U jndroid_user -d jndroid_db > backup.sql

# Restore database
psql -U jndroid_user -d jndroid_db < backup.sql

# Restart services
sudo systemctl restart gunicorn nginx postgresql

# View logs
tail -f /var/log/gunicorn/error.log
tail -f /var/log/nginx/error.log
```

---

**Status: When you complete all checks above, your app is PRODUCTION READY! 🚀**
