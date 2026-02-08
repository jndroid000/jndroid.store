"""
Production Django settings for JN App Store.
Secure settings for live deployment.
"""

import os
from .base import *

# ==================== DEBUG & SECURITY ====================
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production-please')

# Set allowed hosts from environment variable
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# ==================== SECURITY HEADERS ====================
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

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
# In production, use a static file service (AWS S3, Cloudinary, etc.)
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Uncomment and configure for S3 or other CDN
# AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
# AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

# ==================== LOGGING (Production) ====================
# Production logging is more restrictive - only log warnings and errors
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['django.request']['level'] = 'ERROR'
LOGGING['loggers']['django.security']['level'] = 'WARNING'
LOGGING['loggers']['apps']['level'] = 'INFO'
LOGGING['loggers']['accounts']['level'] = 'INFO'

# ==================== PERFORMANCE ====================
# Disable SQL query logging in production
LOGGING['loggers'].pop('django.db.backends', None)

# ==================== ADMIN & MAINTENANCE ====================
ADMINS = [
    ('Admin Name', os.getenv('ADMIN_EMAIL', 'admin@example.com')),
]

# These are sent to admins when errors occur
MANAGERS = ADMINS

# ==================== ADDITIONAL PRODUCTION SETTINGS ====================
# Data to include in error emails
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
