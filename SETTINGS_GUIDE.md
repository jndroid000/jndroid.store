# Django Settings Guide

This project uses a modular Django settings structure for managing configuration across different environments.

## Directory Structure

```
config/
├── settings/
│   ├── __init__.py        # Empty init file
│   ├── base.py            # Common settings for all environments
│   ├── development.py     # Development-specific settings
│   └── production.py      # Production-specific settings
├── wsgi.py
├── asgi.py
└── urls.py
```

## Environment Setup

### Development (Default)

Development uses the `development.py` settings file.

**Run locally:**
```bash
python manage.py runserver
```

**Features:**
- DEBUG = True
- SQLite database
- Console email backend (emails print to console)
- All hosts allowed
- Debug logging enabled

### Production

Production uses the `production.py` settings file.

**Enable production mode:**
```bash
# On Windows
set DJANGO_ENV=production
python manage.py runserver

# On Linux/Mac
export DJANGO_ENV=production
python manage.py runserver
```

**Features:**
- DEBUG = False
- SSL/HTTPS required
- PostgreSQL (recommended, configurable via env vars)
- SMTP email backend
- Restricted security settings
- Minimal logging

## Environment Variables

Create a `.env` file in the backend directory. See `.env.example` for all available options.

### Key Variables for Production:

```bash
DJANGO_ENV=production
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=jndroid.store,www.jndroid.store
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=jndroid_production
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

## Running Migrations

```bash
# Development
python manage.py migrate

# Production
export DJANGO_ENV=production
python manage.py migrate
```

## Creating Fixed Data or Admin Users

```bash
# Development
python manage.py createsuperuser

# Production
export DJANGO_ENV=production
python manage.py createsuperuser
```

## Settings Hierarchy

1. **base.py** - All common settings
   - INSTALLED_APPS
   - MIDDLEWARE
   - DATABASES (SQLite default)
   - EMAIL configuration
   - LOGGING
   - AUTHENTICATION settings

2. **development.py** - Inherits from base.py
   - DEBUG = True
   - EMAIL_BACKEND = console (prints to console)
   - ALLOWED_HOSTS = ['*']
   - Development tools

3. **production.py** - Inherits from base.py
   - DEBUG = False
   - EMAIL_BACKEND = SMTP
   - SSL/HTTPS security
   - Environment-based database configuration
   - Restricted hosts and security policies

## Email Configuration

### Development
- Emails print to console by default
- To save to files instead:
  1. Edit `config/settings/development.py`
  2. Uncomment the EmailBackend file configuration
  3. Emails will be saved to `sent_emails/` folder

### Production
- Uses Gmail SMTP by default
- Set `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` environment variables
- Or configure other email backends in `production.py`

## Database Configuration

### Development
- Uses SQLite (db.sqlite3)
- No configuration needed

### Production
- Default: SQLite (for quick deployments)
- Recommended: PostgreSQL
- Environment variables:
  - `DATABASE_ENGINE` - Database backend
  - `DATABASE_NAME` - Database name
  - `DATABASE_USER` - Database user
  - `DATABASE_PASSWORD` - Database password
  - `DATABASE_HOST` - Database host
  - `DATABASE_PORT` - Database port

## Security Notes for Production

1. **SECRET_KEY**: Generate a new one for production
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

2. **ALLOWED_HOSTS**: Set your domain names

3. **SSL/HTTPS**: 
   - Set `SECURE_SSL_REDIRECT = True`
   - All cookies are HTTPS-only
   - HSTS is enabled by default

4. **Email Credentials**: 
   - Store in environment variables
   - Never commit to version control

5. **Database Password**: 
   - Store in environment variables
   - Use strong passwords

## Deployment Checklist

- [ ] Set `DJANGO_ENV=production`
- [ ] Generate and set `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set up database (PostgreSQL recommended)
- [ ] Configure email credentials
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Use production WSGI server (Gunicorn, uWSGI, etc.)
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure firewall and security groups
- [ ] Set up log monitoring
- [ ] Configure backups for database

## Debugging

If you encounter import issues:

1. Make sure `config/settings/__init__.py` exists (empty file)
2. Check `DJANGO_SETTINGS_MODULE` environment variable
3. Verify settings file imports are correct

## Common Tasks

### Switch to Production
```bash
export DJANGO_ENV=production
```

### Check Which Settings Are Being Used
```bash
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)
>>> print(settings.EMAIL_BACKEND)
```

### Run Tests
```bash
# Development
python manage.py test

# Production
export DJANGO_ENV=production
python manage.py test
```
