# Production Settings Issues - Identified & Fixed

## Issues Found

### 1. **Hardcoded Email Password ❌ FIXED**
- **Problem**: Email password was hardcoded with a default value
- **Risk**: Security vulnerability if committed to version control
- **Fix**: Changed to require environment variable, no default fallback
- **Before**: `EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'cbsv rvqu truu yjzt')`
- **After**: `EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')`

### 2. **Wrong Timezone ❌ FIXED**
- **Problem**: Set to 'UTC' instead of local timezone (Asia/Dhaka)
- **Impact**: All timestamps in database will be in UTC causing confusion
- **Fix**: Changed to 'Asia/Dhaka'
- **Before**: `TIME_ZONE = 'UTC'`
- **After**: `TIME_ZONE = 'Asia/Dhaka'`

### 3. **Generic Email Prefix ❌ FIXED**
- **Problem**: Email subject prefix was '[My Project]' instead of project name
- **Fix**: Changed to '[JN App Store]'
- **Before**: `ACCOUNT_EMAIL_SUBJECT_PREFIX = '[My Project] '`
- **After**: `ACCOUNT_EMAIL_SUBJECT_PREFIX = '[JN App Store] '`

### 4. **ALLOWED_HOSTS Parsing Issue ❌ FIXED**
- **Problem**: `.split(',')` creates empty strings: `['localhost', '127.0.0.1', '']`
- **Risk**: Django may not properly validate hosts
- **Fix**: Filter out empty strings and strip whitespace
- **Before**: `ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')`
- **After**: `ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'jndroid.store,www.jndroid.store').split(',') if h.strip()]`

### 5. **CSRF_TRUSTED_ORIGINS Parsing Issue ❌ FIXED**
- **Problem**: Empty default results in list with empty string: `['']`
- **Risk**: CSRF protection might not work correctly
- **Fix**: Filter empty strings and set sensible defaults
- **Before**: `CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')`
- **After**: `CSRF_TRUSTED_ORIGINS = [h.strip() for h in os.getenv('CSRF_TRUSTED_ORIGINS', 'https://jndroid.store,https://www.jndroid.store').split(',') if h.strip()]`

### 6. **Console Logging in Production ❌ FIXED**
- **Problem**: Production logs included console output (unbuffered, noisy)
- **Impact**: Slow performance, poor log management
- **Fix**: Removed console handlers from production logging
- **Before**: `'handlers': ['console', 'file']`
- **After**: `'handlers': ['file']` (file logging only)

### 7. **Static Files Misconfiguration ❌ FIXED**
- **Problem**: `STATICFILES_DIRS` was inherited in production causing conflicts with `STATIC_ROOT`
- **Risk**: Static file collection (`collectstatic`) might fail or collect wrong files
- **Fix**: Clear `STATICFILES_DIRS = []` in production
- **Note**: Must run `python manage.py collectstatic --noinput` before deployment

### 8. **Missing SECRET_KEY Validation ❌ FIXED**
- **Problem**: No validation that SECRET_KEY is actually set
- **Risk**: App starts with weak/default secret key
- **Fix**: Added explicit check that raises error if SECRET_KEY not properly set
- **Code**: 
  ```python
  if not SECRET_KEY or SECRET_KEY == 'change-me-in-production-please':
      raise ValueError('🚨 CRITICAL: SECRET_KEY environment variable must be set...')
  ```

### 9. **Default Admin Email Wrong ❌ FIXED**
- **Problem**: Default was 'admin@example.com'
- **Fix**: Changed to 'admin@jndroid.store'
- **Impact**: Error emails go to the right admin

### 10. **Weak Security Headers ❌ FIXED**
- **Missing**: X-Frame-Options, Referrer-Policy, Permissions-Policy
- **Fix**: Added:
  ```python
  X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking
  SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
  PERMISSIONS_POLICY = {'geolocation': [], 'microphone': [], 'camera': []}
  ```

## Production Checklist

Before deploying to production:

- [ ] Generate new SECRET_KEY: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- [ ] Set environment variable: `export SECRET_KEY=<your-key>`
- [ ] Set DJANGO_ENV: `export DJANGO_ENV=production`
- [ ] Create `.env` file or set all environment variables:
  - `SECRET_KEY` (required - will error if not set)
  - `ALLOWED_HOSTS=jndroid.store,www.jndroid.store`
  - `CSRF_TRUSTED_ORIGINS=https://jndroid.store,https://www.jndroid.store`
  - `EMAIL_HOST_USER` (Gmail address)
  - `EMAIL_HOST_PASSWORD` (Gmail app password)
  - `ADMIN_EMAIL` (where to send errors)
  - Database credentials if using PostgreSQL
  - Cache backend settings if using Redis

- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] **Collect static files**: `python manage.py collectstatic --noinput`
- [ ] Test with Django check: `python manage.py check --deploy`
- [ ] Set up web server (nginx/Apache) to:
  - Serve `/static/` from `staticfiles/` directory
  - Proxy requests to Django app
  - Enable HTTPS/SSL
  - Set security headers
- [ ] Configure backups for database
- [ ] Set up log monitoring
- [ ] Test email delivery
- [ ] Run through security checklist

## Environment Variables Template

```bash
# Production environment
DJANGO_ENV=production

# Security (REQUIRED - must generate new one)
SECRET_KEY=<generate-with-command-above>

# Hosts
ALLOWED_HOSTS=jndroid.store,www.jndroid.store
CSRF_TRUSTED_ORIGINS=https://jndroid.store,https://www.jndroid.store

# Email (Gmail)
EMAIL_HOST_USER=jndroid000@gmail.com
EMAIL_HOST_PASSWORD=<your-app-password>

# Admin
ADMIN_EMAIL=admin@jndroid.store

# Database (if using PostgreSQL)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=jndroid_production
DATABASE_USER=postgres
DATABASE_PASSWORD=<strong-password>
DATABASE_HOST=db.example.com
DATABASE_PORT=5432

# Caching (if using Redis)
CACHE_BACKEND=django.core.cache.backends.redis.RedisCache
CACHE_LOCATION=redis://cache.example.com:6379/1
```

## Testing Production Settings Locally

To test production settings before deployment:

```bash
export DJANGO_ENV=production
export SECRET_KEY=test-key-12345
python manage.py check --deploy
```

This will show any configuration issues without needing to deploy.

## Important Notes

1. **Always generate a new SECRET_KEY** for production - never use the development one
2. **Email password is not optional** - must be set via environment variable
3. **Static files must be collected** before deployment - `python manage.py collectstatic`
4. **Use HTTPS only** - `SECURE_SSL_REDIRECT = True` is enabled
5. **All cookies are secure** - set to HTTPS only: `SESSION_COOKIE_SECURE = True`, `CSRF_COOKIE_SECURE = True`
6. **HSTS enabled for 1 year** - browsers will force HTTPS
7. **Logs go to files only** - no console output in production (check `logs/` directory)

## If Production Breaks

1. Check environment variables are all set
2. Run `python manage.py check --deploy` for detailed errors
3. Check log files in `logs/` directory
4. Make sure database is accessible
5. Ensure static files are collected
6. Verify email credentials work
