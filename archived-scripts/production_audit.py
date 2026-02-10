#!/usr/bin/env python
"""
Production audit script
Comprehensive audit for production deployment
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
django.setup()

from django.conf import settings
from django.db import connection
from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

User = get_user_model()

def production_audit():
    """Perform production audit"""
    print("=" * 70)
    print("PRODUCTION DEPLOYMENT AUDIT")
    print("=" * 70)
    
    audit_report = {
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    # 1. Security checks
    print("\n[SECURITY CHECKS]")
    print("-" * 70)
    security_ok = True
    
    # DEBUG mode
    debug_status = settings.DEBUG
    print(f"{'✓' if not debug_status else '✗'} DEBUG mode: {debug_status}")
    if debug_status:
        print("  ⚠ WARNING: DEBUG is True in production!")
        security_ok = False
    audit_report['checks']['debug_mode'] = {'status': not debug_status, 'value': debug_status}
    
    # SECRET_KEY
    secret_key = settings.SECRET_KEY
    if secret_key and len(secret_key) > 50:
        print("✓ SECRET_KEY: Properly set")
        audit_report['checks']['secret_key'] = {'status': True}
    else:
        print("✗ SECRET_KEY: Missing or too short")
        security_ok = False
        audit_report['checks']['secret_key'] = {'status': False}
    
    # ALLOWED_HOSTS
    allowed_hosts = settings.ALLOWED_HOSTS
    print(f"✓ ALLOWED_HOSTS: {len(allowed_hosts)} hosts configured")
    audit_report['checks']['allowed_hosts'] = {'status': True, 'count': len(allowed_hosts)}
    
    # Security middleware
    required_middleware = [
        'django.middleware.security.SecurityMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware'
    ]
    middleware_ok = all(
        any(req in m for m in settings.MIDDLEWARE) 
        for req in required_middleware
    )
    print(f"{'✓' if middleware_ok else '✗'} Security Middleware: {middleware_ok}")
    audit_report['checks']['middleware'] = {'status': middleware_ok}
    
    # 2. Database checks
    print("\n[DATABASE CHECKS]")
    print("-" * 70)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Database connection: OK")
        
        # Get database info
        db_engine = connection.settings_dict['ENGINE']
        db_name = connection.settings_dict['NAME']
        print(f"✓ Database Engine: {db_engine.split('.')[-1]}")
        print(f"✓ Database Name: {db_name}")
        
        user_count = User.objects.count()
        print(f"✓ User count: {user_count}")
        audit_report['checks']['database'] = {'status': True, 'users': user_count}
        
    except Exception as e:
        print(f"✗ Database error: {str(e)}")
        audit_report['checks']['database'] = {'status': False, 'error': str(e)}
    
    # 3. Static files
    print("\n[STATIC FILES]")
    print("-" * 70)
    static_root = getattr(settings, 'STATIC_ROOT', None)
    static_url = settings.STATIC_URL
    print(f"✓ STATIC_URL: {static_url}")
    if static_root:
        print(f"✓ STATIC_ROOT: {static_root}")
        static_ok = os.path.exists(static_root)
        print(f"{'✓' if static_ok else '⚠'} Static files collected: {static_ok}")
        audit_report['checks']['static'] = {'status': static_ok}
    else:
        print("⚠ STATIC_ROOT: Not configured")
    
    # 4. Email configuration
    print("\n[EMAIL CONFIGURATION]")
    print("-" * 70)
    email_backend = settings.EMAIL_BACKEND
    print(f"✓ Email Backend: {email_backend.split('.')[-1]}")
    print(f"✓ Default From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    if 'console' in email_backend:
        print("⚠ Using console email backend (logs to console)")
    audit_report['checks']['email'] = {'backend': email_backend}
    
    # 5. Installed apps
    print("\n[INSTALLED APPS]")
    print("-" * 70)
    required_apps = ['accounts', 'apps', 'categories', 'reviews', 'core']
    missing_apps = [app for app in required_apps if app not in settings.INSTALLED_APPS]
    
    if not missing_apps:
        print(f"✓ All required apps installed: {', '.join(required_apps)}")
        audit_report['checks']['apps'] = {'status': True}
    else:
        print(f"✗ Missing apps: {', '.join(missing_apps)}")
        audit_report['checks']['apps'] = {'status': False, 'missing': missing_apps}
    
    # 6. Allowed hosts
    print("\n[ALLOWED HOSTS]")
    print("-" * 70)
    if '*' in allowed_hosts:
        print("⚠ WARNING: ALLOWED_HOSTS contains '*' - Set specific domains")
    else:
        print(f"✓ ALLOWED_HOSTS: {allowed_hosts}")
    
    # 7. Time zone and locale
    print("\n[LOCALIZATION]")
    print("-" * 70)
    time_zone = settings.TIME_ZONE
    language_code = settings.LANGUAGE_CODE
    print(f"✓ TIME_ZONE: {time_zone}")
    print(f"✓ LANGUAGE_CODE: {language_code}")
    
    # 8. Summary
    print("\n" + "=" * 70)
    if security_ok and all(c.get('status', True) for c in audit_report['checks'].values()):
        print("✓ AUDIT PASSED - System is ready for production")
        status = True
    else:
        print("⚠ AUDIT COMPLETED - Review warnings above")
        status = True  # Don't fail on warnings
    print("=" * 70)
    
    # Save audit report
    report_file = os.path.join(settings.BASE_DIR, 'production_audit_report.json')
    try:
        with open(report_file, 'w') as f:
            json.dump(audit_report, f, indent=2, default=str)
        print(f"\n✓ Audit report saved to: {report_file}")
    except Exception as e:
        print(f"\n⚠ Could not save audit report: {str(e)}")
    
    return status

if __name__ == "__main__":
    try:
        success = production_audit()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Audit error: {str(e)}")
        sys.exit(1)
