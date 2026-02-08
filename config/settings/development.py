"""
Development Django settings for JN App Store.
Only for local development - not for production.
"""

from .base import *

# ==================== DEBUG & SECURITY ====================
DEBUG = True
SECRET_KEY = 'django-insecure-sc3-+u47j_1outnsvye&wzuet6cyjh=r-ne=)5x3jmx9%!%mu5'
ALLOWED_HOSTS = ['*']  # Allow all hosts in development

# Disable CSRF for development
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# ==================== DEVELOPMENT TOOLS ====================

# ==================== EMAIL BACKEND (Development) ====================
# Emails print to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ==================== DATABASE (Development) ====================
# SQLite (inherited from base.py)

# ==================== LOGGING (Development) ====================
LOGGING['loggers']['django']['level'] = 'INFO'
LOGGING['loggers']['apps']['level'] = 'INFO'
LOGGING['loggers']['accounts']['level'] = 'INFO'
