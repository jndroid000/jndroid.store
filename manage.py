#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

# Load .env and .env.production files
def load_env_files():
    """Load environment variables from .env and .env.production files"""
    base_dir = Path(__file__).resolve().parent
    
    # First load .env (development defaults)
    env_file = base_dir / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
    
    # Then load .env.production (overrides .env in production)
    env_prod_file = base_dir / '.env.production'
    if env_prod_file.exists():
        with open(env_prod_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()  # Direct assignment to override

load_env_files()

def get_settings_module():
    """Determine which Django settings module to use"""
    # Check for explicit DJANGO_SETTINGS_MODULE (highest priority)
    if 'DJANGO_SETTINGS_MODULE' in os.environ:
        return os.environ['DJANGO_SETTINGS_MODULE']
    
    # Check DJANGO_ENV variable
    django_env = os.getenv('DJANGO_ENV', 'development').lower()
    
    # Check if .env.production exists (indicates production environment)
    base_dir = Path(__file__).resolve().parent
    env_prod_file = base_dir / '.env.production'
    
    if env_prod_file.exists() and django_env != 'development':
        return 'config.settings.production'
    
    # Default to development
    return 'config.settings.development'

def main():
    """Run administrative tasks."""
    settings_module = get_settings_module()
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
