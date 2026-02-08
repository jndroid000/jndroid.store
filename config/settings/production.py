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

# ALLOWED_HOSTS is inherited from base.py and configured via DJANGO_ALLOWED_HOSTS env variable

# ==================== SECURITY HEADERS ====================
# Use this if behind a reverse proxy (nginx/Apache)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_TRUSTED_ORIGINS = [h.strip() for h in os.getenv('CSRF_TRUSTED_ORIGINS', 'https://jndroid.store,https://www.jndroid.store').split(',') if h.strip()]

# HTTPS only
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True



# ==================== EMAIL BACKEND (Production) ====================
# SMTP configured via environment variables

# ==================== DATABASE (Production) ====================
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DATABASE_NAME', 'jndroid_production'),
        'USER': os.getenv('DATABASE_USER', 'postgres'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
        'CONN_MAX_AGE': 600,
    }
}

# ==================== CACHING (Production) ====================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# ==================== STATIC & MEDIA FILES (Production) ====================
# Run before deployment: python manage.py collectstatic --noinput
STATICFILES_DIRS = []

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

# ==================== ADMIN ====================
ADMINS = [
    ('JN Admin', os.getenv('ADMIN_EMAIL', 'admin@jndroid.store')),
]
MANAGERS = ADMINS

# ==================== SECURITY ====================
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
