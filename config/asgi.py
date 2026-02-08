"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Use environment variable to select settings
environment = os.getenv('DJANGO_ENV', 'development')

if environment == 'production':
    settings_module = 'config.settings.production'
else:
    settings_module = 'config.settings.development'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

application = get_asgi_application()
