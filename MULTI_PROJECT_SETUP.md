# VPS Multiple Projects Setup Guide

## দুটি প্রজেক্ট একসাথে চালানো (jks-bd.org + jndroid.store)

---

## Step 1: Gunicorn Service Setup

### jndroid.store এর জন্য নতুন service:

```bash
# Service file কপি করুন
sudo cp /var/www/jndroid.store/gunicorn_jndroid.service /etc/systemd/system/

# Log directory তৈরি করুন
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn

# Systemd reload করুন
sudo systemctl daemon-reload

# Service enable এবং start করুন
sudo systemctl enable gunicorn_jndroid
sudo systemctl start gunicorn_jndroid
sudo systemctl status gunicorn_jndroid
```

### পুরনো jks service (যদি থাকে):

```bash
# এটি আলাদা থাকবে - যেমন gunicorn.service
sudo systemctl status gunicorn

# দুটোই চেক করুন:
sudo systemctl status gunicorn
sudo systemctl status gunicorn_jndroid
```

---

## Step 2: Nginx Setup

### উভয় প্রজেক্টের Nginx config সেটআপ:

```bash
# jndroid.store এর জন্য নতুন config
sudo cp /var/www/jndroid.store/nginx_jndroid.conf /etc/nginx/sites-available/jndroid-store

# jks এর জন্য পুরনো config (যা আছে):
# /etc/nginx/sites-available/jks-bd.org (অথবা যা নাম আছে)

# উভয় সাইট enable করুন
sudo ln -s /etc/nginx/sites-available/jndroid-store /etc/nginx/sites-enabled/
# sudo ln -s /etc/nginx/sites-available/jks-bd.org /etc/nginx/sites-enabled/  (যদি enable না থাকে)

# Nginx test করুন
sudo nginx -t

# Nginx restart করুন
sudo systemctl restart nginx
```

---

## Step 3: SSL Certificate Setup

### দুটি ডোমেইনের জন্য SSL:

```bash
# jndroid.store এর জন্য:
sudo certbot certonly --webroot -w /var/www/letsencrypt \
    -d jndroid.store \
    -d www.jndroid.store \
    --email jndroid000@gmail.com \
    --agree-tos \
    --no-eff-email

# jks-bd.org এর জন্য (যদি আগে না করা হয়):
sudo certbot certonly --webroot -w /var/www/letsencrypt \
    -d jks-bd.org \
    -d www.jks-bd.org \
    --email your-email@jks-bd.org \
    --agree-tos \
    --no-eff-email
```

---

## Step 4: Nginx HTTPS Configuration

### jndroid.store nginx config update করুন:

```bash
sudo nano /etc/nginx/sites-available/jndroid-store

# নিচের HTTPS section uncomment করুন এবং যোগ করুন:
```

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name jndroid.store www.jndroid.store;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name jndroid.store www.jndroid.store;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/jndroid.store/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/jndroid.store/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    location / {
        proxy_pass http://gunicorn_jndroid;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_redirect off;
        proxy_buffering off;
    }

    location /static/ {
        alias /var/www/jndroid.store/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /var/www/jndroid.store/media/;
        expires 7d;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

---

## Step 5: Update Django Settings for HTTPS

### production.py enable করুন:

```bash
# Local computer-এ:
# config/settings/production.py খুলুন

# এই লাইনগুলি change করুন:
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

Git-এ commit এবং push করুন, তারপর VPS-তে pull করুন।

---

## Step 6: PostgreSQL Multi-Database (Optional)

যদি আলাদা database চান:

```bash
sudo -u postgres psql

-- jndroid.store database
CREATE DATABASE jndroid_db;
CREATE USER jndroid_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE jndroid_db TO jndroid_user;

-- jks database (যদি আলাদা থাকে)
-- CREATE DATABASE jks_db;
-- CREATE USER jks_user WITH PASSWORD 'password';
-- GRANT ALL PRIVILEGES ON DATABASE jks_db TO jks_user;

\q
```

---

## Step 7: Verification

### উভয় service চেক করুন:

```bash
# Services
sudo systemctl status gunicorn
sudo systemctl status gunicorn_jndroid

# Nginx
sudo systemctl status nginx

# Logs
tail -f /var/log/gunicorn/error.log  # jks
tail -f /var/log/gunicorn/jndroid_error.log  # jndroid

# Access both sites
curl http://jks-bd.org
curl http://jndroid.store
```

---

## Step 8: Firewall Rules

```bash
sudo ufw allow 22/tcp       # SSH
sudo ufw allow 80/tcp       # HTTP
sudo ufw allow 443/tcp      # HTTPS
sudo ufw status
```

---

## Troubleshooting

### যদি gunicorn socket না থাকে:

```bash
# Check socket
ls -la /var/www/jndroid.store/gunicorn.sock

# Restart service
sudo systemctl restart gunicorn_jndroid
```

### যদি nginx error হয়:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### যদি SSL error হয়:

```bash
# Certificate check
sudo certbot certificates

# Renew
sudo certbot renew --dry-run
```

---

## ফাইল ম্যাপিং

```
VPS Structure:
/var/www/
├── jks-bd.org/                  (পুরানো প্রজেক্ট)
│   ├── venv/
│   └── ...
└── jndroid.store/               (নতুন প্রজেক্ট)
    ├── venv/
    ├── config/
    ├── manage.py
    ├── gunicorn_jndroid.service
    ├── nginx_jndroid.conf
    └── ...

/etc/systemd/system/
├── gunicorn.service             (jks এর জন্য)
└── gunicorn_jndroid.service     (jndroid এর জন্য)

/etc/nginx/sites-available/
├── jks-bd.org                   (jks এর জন্য)
└── jndroid-store                (jndroid এর জন্য)

/etc/nginx/sites-enabled/
├── jks-bd.org                   (symlink)
└── jndroid-store                (symlink)
```

---

## Summary

```bash
# একটি command-এ সব:

# 1. Services setup
sudo cp /var/www/jndroid.store/gunicorn_jndroid.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn_jndroid
sudo systemctl start gunicorn_jndroid

# 2. Nginx setup
sudo cp /var/www/jndroid.store/nginx_jndroid.conf /etc/nginx/sites-available/jndroid-store
sudo ln -s /etc/nginx/sites-available/jndroid-store /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 3. SSL
sudo certbot certonly --webroot -w /var/www/letsencrypt \
    -d jndroid.store -d www.jndroid.store

# 4. Verify
sudo systemctl status gunicorn gunicorn_jndroid nginx
```

---

**এখন VPS-এ উপরের steps অনুসরণ করুন!** 🚀
