# VPS Production Setup Guide - jndroid.store

## Step 1: VPS-এ PostgreSQL ডাটাবেস সেটআপ করুন

```bash
# VPS-এ SSH দিয়ে লগইন করুন এবং এই কমান্ডগুলি চালান:

sudo -u postgres psql

# PostgreSQL শেলে এই কমান্ডগুলি চালান:
CREATE DATABASE jndroid_db;
CREATE USER jndroid_user WITH PASSWORD 'YOUR_STRONG_PASSWORD_HERE';
ALTER ROLE jndroid_user SET client_encoding TO 'utf8';
ALTER ROLE jndroid_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE jndroid_user SET default_transaction_deferrable TO on;
ALTER ROLE jndroid_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE jndroid_db TO jndroid_user;
\q
```

**গুরুত্বপূর্ণ:** 
- `YOUR_STRONG_PASSWORD_HERE` একটি শক্তিশালী পাসওয়ার্ড দিয়ে রিপ্লেস করুন
- এই পাসওয়ার্ড মনে রাখুন - আপনাকে `.env.production` ফাইলে রাখতে হবে

---

## Step 2: Django SECRET_KEY জেনারেট করুন

আপনার লোকাল কম্পিউটারে (গুরুত্বপূর্ণ):

```bash
cd c:\Users\juhan\Desktop\jndroid.store\backend
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

এটি একটি দীর্ঘ র্যান্ডম স্ট্রিং প্রিন্ট করবে। এই স্ট্রিংটি কপি করুন এবং নিরাপদে রাখুন।

---

## Step 3: Gmail App Password জেনারেট করুন

ইমেইল সেটআপের জন্য:

1. Google Account এ যান: https://myaccount.google.com
2. Security ট্যাব ক্লিক করুন
3. 2-Step Verification চালু করুন (যদি না করা হয়)
4. App passwords জেনারেট করুন (https://myaccount.google.com/apppasswords)
5. Gmail সিলেক্ট করুন এবং Windows PC বেছে নিন
6. একটি 16-ক্যারেক্টার পাসওয়ার্ড পাবেন - এটি কপি করুন

---

## Step 4: `.env.production` ফাইল তৈরি করুন

FileZilla ব্যবহার করে VPS-এ এই কন্টেন্ট দিয়ে একটি ফাইল তৈরি করুন:

**ফাইল নাম:** `.env.production`
**অবস্থান:** `/var/www/jndroid.store/backend/.env.production`

### নিচের কন্টেন্ট ব্যবহার করুন (মূল্যবান পরিবর্তন করে):

```
# ==================== ENVIRONMENT SELECTION ====================
DJANGO_ENV=production

# ==================== DJANGO SETTINGS ====================
SECRET_KEY=<আপনার-জেনারেট-করা-SECRET_KEY-এখানে-পেস্ট-করুন>

# ==================== SECURITY ====================
DEBUG=False
ALLOWED_HOSTS=jndroid.store,www.jndroid.store,<আপনার-VPS-IP-এখানে>

# CSRF settings
CSRF_TRUSTED_ORIGINS=https://jndroid.store,https://www.jndroid.store

# ==================== DATABASE CONFIGURATION (PostgreSQL) ====================
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=jndroid_db
DATABASE_USER=jndroid_user
DATABASE_PASSWORD=<আপনার-PostgreSQL-পাসওয়ার্ড-এখানে>
DATABASE_HOST=localhost
DATABASE_PORT=5432

# ==================== EMAIL CONFIGURATION ====================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=jndroid000@gmail.com
EMAIL_HOST_PASSWORD=<আপনার-Gmail-App-Password-এখানে>
DEFAULT_FROM_EMAIL=jndroid000@gmail.com
ADMIN_EMAIL=jndroid000@gmail.com

# ==================== CACHING ====================
CACHE_BACKEND=django.core.cache.backends.locmem.LocMemCache
CACHE_LOCATION=unique-snowflake

# ==================== STATIC & MEDIA FILES ====================
STATIC_URL=/static/
STATIC_ROOT=/var/www/jndroid.store/backend/staticfiles
MEDIA_URL=/media/
MEDIA_ROOT=/var/www/jndroid.store/backend/media

# ==================== GUNICORN SETTINGS ====================
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120

# ==================== LOGGING ====================
LOG_LEVEL=INFO
```

---

## Step 5: FileZilla দিয়ে আপলোড করুন

1. **FileZilla খুলুন**
2. **Site Manager** ক্লিক করুন
3. আপনার VPS এর বিস্তারিত দিন:
   - Host: আপনার VPS IP অথবা ডোমেইন
   - Protocol: SFTP
   - Port: 22
   - Username: root
   - Password: আপনার VPS পাসওয়ার্ড
4. **Connect** ক্লিক করুন
5. বাম দিকে নেভিগেট করুন: `.env.production` ফাইল যা আপনি তৈরি করেছেন
6. ডান দিকে নেভিগেট করুন: `/var/www/jndroid.store/backend/`
7. ফাইল ড্র্যাগ করে আপলোড করুন

---

## Step 6: VPS-এ Migration চালান

SSH দিয়ে VPS-এ লগইন করে:

```bash
cd /var/www/jndroid.store/backend
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python archived-scripts/final_verify.py
```

---

## পূর্ণাঙ্গ মূল্যবান তালিকা যা পরিবর্তন করতে হবে:

| ফিল্ড | পুরনো | নতুন |
|------|--------|------|
| `SECRET_KEY` | `django-insecure-...` | `আপনার-জেনারেট-করা-KEY` |
| `DATABASE_PASSWORD` | `CHANGE_THIS...` | `PostgreSQL-পাসওয়ার্ড` |
| `EMAIL_HOST_USER` | `your-email@gmail.com` | `jndroid000@gmail.com` |
| `EMAIL_HOST_PASSWORD` | `your-app-password` | `Gmail-App-Password` |
| `ALLOWED_HOSTS` | `yourvpsip.xx.xxx.xx` | `আপনার-VPS-IP` |

---

## সমস্যা সমাধান

### Error: "No such file or directory: .env.production"
- ফাইলটি আপনলোড হয়েছে কিনা চেক করুন
- অনুমতি চেক করুন: `ls -la /var/www/jndroid.store/backend/.env.production`

### Error: "FATAL: role 'jndroid_user' does not exist"
- PostgreSQL ডাটাবেস সেটআপ করেননি
- Step 1 পুনরাবৃত্তি করুন

### Error: "password authentication failed"
- DATABASE_PASSWORD সঠিকভাবে দিয়েছেন কিনা চেক করুন
- PostgreSQL-এ যে পাসওয়ার্ড দিয়েছেন সেটাই ব্যবহার করুন

---

## সফলতার চিহ্ন

যখন `python manage.py migrate --noinput` সফল হয়, আপনি দেখবেন:
```
Operations to perform:
  Apply all migrations: ...
Running migrations:
  Applying accounts.0001_initial... OK
  ...
✓ All migrations applied successfully
```

**তারপর আপনার অ্যাপ উৎপাদনের জন্য সম্পূর্ণ প্রস্তুত!** 🚀
