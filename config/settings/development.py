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
# Installed apps for development only
if DEBUG:
    INSTALLED_APPS += [
        # 'debug_toolbar',  # Uncomment if you install django-debug-toolbar
    ]
    
    MIDDLEWARE += [
        # 'debug_toolbar.middleware.DebugToolbarMiddleware',  # Uncomment if you install django-debug-toolbar
    ]

# Allow internal IPs for debug toolbar
INTERNAL_IPS = [
    'localhost',
    '127.0.0.1',
]

# ==================== EMAIL BACKEND (Development) ====================
# Use console email backend for development - emails print to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Optional: Use file backend to save emails to files
# EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
# EMAIL_FILE_PATH = BASE_DIR / 'sent_emails'

# ==================== DATABASE (Development) ====================
# SQLite is fine for development
# To use PostgreSQL in development, uncomment below and install psycopg2
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'jndroid_dev',
#         'USER': 'postgres',
#         'PASSWORD': 'password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }

# ==================== LOGGING (Development) ====================
LOGGING['loggers']['django']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'
LOGGING['loggers']['accounts']['level'] = 'DEBUG'

# Print all SQL queries to console in development
# Uncomment if you want to see all database queries
# LOGGING['loggers']['django.db.backends'] = {
#     'handlers': ['console'],
#     'level': 'DEBUG',
#     'propagate': False,
# }
