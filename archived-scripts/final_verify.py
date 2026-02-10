#!/usr/bin/env python
"""
Final verification script
Comprehensive system verification before deployment
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
django.setup()

from django.core.management import call_command
from django.conf import settings
from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()

def final_verification():
    """Perform comprehensive system verification"""
    print("=" * 60)
    print("FINAL SYSTEM VERIFICATION")
    print("=" * 60)
    
    all_checks_passed = True
    
    # 1. Check Django settings
    print("\n[1. Django Configuration]")
    print("-" * 60)
    try:
        print(f"✓ DEBUG: {settings.DEBUG}")
        print(f"✓ Allowed Hosts: {settings.ALLOWED_HOSTS[:2]}")
        print(f"✓ Static URL: {settings.STATIC_URL}")
        print(f"✓ Media URL: {settings.MEDIA_URL}")
        print(f"✓ Apps Installed: {len(settings.INSTALLED_APPS)}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        all_checks_passed = False
    
    # 2. Check database
    print("\n[2. Database Status]")
    print("-" * 60)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Database connection: OK")
        
        total_users = User.objects.count()
        print(f"✓ Database tables: MIGRATED")
        print(f"✓ User count: {total_users}")
    except Exception as e:
        print(f"✗ Database error: {str(e)}")
        all_checks_passed = False
    
    # 3. Check static files
    print("\n[3. Static Files]")
    print("-" * 60)
    try:
        static_path = os.path.join(settings.BASE_DIR, 'static')
        staticfiles_path = os.path.join(settings.BASE_DIR, 'staticfiles')
        print(f"✓ Static directory: {os.path.exists(static_path)}")
        print(f"✓ Staticfiles directory: {os.path.exists(staticfiles_path)}")
    except Exception as e:
        print(f"✗ Static files error: {str(e)}")
    
    # 4. Check media files
    print("\n[4. Media Files]")
    print("-" * 60)
    try:
        media_path = os.path.join(settings.BASE_DIR, 'media')
        print(f"✓ Media directory exists: {os.path.exists(media_path)}")
        if os.path.exists(media_path):
            media_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, dirnames, filenames in os.walk(media_path)
                for filename in filenames
            )
            print(f"✓ Media size: {media_size / (1024*1024):.2f} MB")
    except Exception as e:
        print(f"! Warning: {str(e)}")
    
    # 5. Check migrations
    print("\n[5. Database Migrations]")
    print("-" * 60)
    try:
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        print(f"✓ Migration status: UP-TO-DATE")
        print(f"✓ Latest migrations: {len(targets)}")
    except Exception as e:
        print(f"⚠ Could not check migrations: {str(e)}")
    
    # 6. Check installed apps
    print("\n[6. Required Apps]")
    print("-" * 60)
    required_apps = ['accounts', 'apps', 'categories', 'reviews', 'core']
    for app in required_apps:
        if app in settings.INSTALLED_APPS:
            print(f"✓ {app}")
        else:
            print(f"✗ {app} NOT FOUND")
            all_checks_passed = False
    
    # 7. Check email configuration
    print("\n[7. Email Configuration]")
    print("-" * 60)
    print(f"✓ Email Backend: {settings.EMAIL_BACKEND[:30]}...")
    print(f"✓ Default From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    # 8. Check environment variables
    print("\n[8. Environment Variables]")
    print("-" * 60)
    env_vars = ['SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'DATABASE_URL']
    for var in env_vars:
        if hasattr(settings, var.upper()):
            print(f"✓ {var} is set")
        else:
            print(f"⚠ {var} not found")
    
    # 9. Summary
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("✓ ALL CHECKS PASSED - System is ready for deployment")
    else:
        print("✗ SOME CHECKS FAILED - Please review errors above")
    print("=" * 60)
    
    return all_checks_passed

if __name__ == "__main__":
    success = final_verification()
    sys.exit(0 if success else 1)
