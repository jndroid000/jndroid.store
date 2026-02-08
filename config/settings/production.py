"""
Production Django settings for JN App Store.
Secure settings for live deployment.
"""

import os
from .base import *

# ==================== DEBUG & SECURITY ====================
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY', '')

# Ensure SECRET_KEY is set in production
if not SECRET_KEY or SECRET_KEY == 'change-me-in-production-please':
    raise ValueError(
        '🚨 CRITICAL: SECRET_KEY environment variable must be set in production!\n'
        'Generate a new one with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"\n'
        'Then set it as an environment variable: export SECRET_KEY=<generated-key>'
    )

# Set allowed hosts from environment variable
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', 'jndroid.store,www.jndroid.store').split(',') if h.strip()]

# ==================== SECURITY HEADERS ====================
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [h.strip() for h in os.getenv('CSRF_TRUSTED_ORIGINS', 'https://jndroid.store,https://www.jndroid.store').split(',') if h.strip()]

# HTTPS only
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Security middleware settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
}

# ==================== EMAIL BACKEND (Production) ====================
# Use SMTP for production (Gmail configured in base.py)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Note: EMAIL_HOST_USER and EMAIL_HOST_PASSWORD should be set via environment variables
# export EMAIL_HOST_USER=your-email@gmail.com
# export EMAIL_HOST_PASSWORD=your-app-password

# ==================== DATABASE (Production) ====================
# Example PostgreSQL configuration (recommended for production)
# If using PostgreSQL, also update BASE_DIR/requirements.txt to include psycopg2
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DATABASE_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('DATABASE_USER', ''),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST': os.getenv('DATABASE_HOST', ''),
        'PORT': os.getenv('DATABASE_PORT', ''),
    }
}

# ==================== CACHING (Production) ====================
# Use Redis or in-memory cache for production
CACHES = {
    'default': {
        'BACKEND': os.getenv(
            'CACHE_BACKEND',
            'django.core.cache.backends.locmem.LocMemCache'
        ),
        'LOCATION': os.getenv('CACHE_LOCATION', 'unique-snowflake'),
    }
}

# ==================== STATIC & MEDIA FILES (Production) ====================
# IMPORTANT: Run this before deployment:
# python manage.py collectstatic --noinput
#
# STATIC_ROOT is inherited from base.py (set to 'staticfiles' directory)
STATICFILES_DIRS = []  # Clear development static paths

# For serving static files with a web server (nginx/apache):
# - Set up web server to serve /static/ from the STATIC_ROOT directory
# - Or use a CDN service like AWS S3, Cloudinary, etc.
#
# For CDN deployment (AWS S3, Cloudinary, etc.), uncomment and configure:
# AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

# ==================== LOGGING (Production) ====================
# Production logging - remove console output, keep file logging only
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['django']['handlers'] = ['file']  # Remove console

LOGGING['loggers']['django.request']['level'] = 'ERROR'
LOGGING['loggers']['django.request']['handlers'] = ['error_file']  # Remove console

LOGGING['loggers']['django.security']['level'] = 'WARNING'
LOGGING['loggers']['django.security']['handlers'] = ['security_file']  # Remove console

LOGGING['loggers']['apps']['level'] = 'INFO'
LOGGING['loggers']['apps']['handlers'] = ['file']  # Remove console

LOGGING['loggers']['accounts']['level'] = 'INFO'
LOGGING['loggers']['accounts']['handlers'] = ['file']  # Remove console

LOGGING['root']['handlers'] = ['file']  # Remove console from root

# ==================== PERFORMANCE ====================
# Disable SQL query logging in production
LOGGING['loggers'].pop('django.db.backends', None)

# ==================== ADMIN & MAINTENANCE ====================
ADMINS = [
    ('JN Admin', os.getenv('ADMIN_EMAIL', 'admin@jndroid.store')),
]

# These are sent to admins when errors occur
MANAGERS = ADMINS

# ==================== EMAIL ERROR REPORTING ====================
# Send 500 error emails to admins (set EMAIL correctly above)
SEND_BROKEN_LINK_EMAILS = True

# ==================== ADDITIONAL SECURITY SETTINGS ====================
# Prevent framing of the site (clickjacking protection)
X_FRAME_OPTIONS = 'DENY'

# Referrer Policy
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Permissions Policy (formerly Feature Policy)
PERMISSIONS_POLICY = {
    'geolocation': [],
    'microphone': [],
    'camera': [],
}

# ==================== ADDITIONAL PRODUCTION SETTINGS ====================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
