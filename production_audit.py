#!/usr/bin/env python
"""
Production Configuration Audit
Comprehensive check for all production-related issues
"""
import os
import sys
from pathlib import Path

os.environ['DJANGO_ENV'] = 'production'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

print("\n" + "="*80)
print("PRODUCTION CONFIGURATION AUDIT - JN APP STORE")
print("="*80 + "\n")

issues = []
warnings = []
success = []

# 1. Check SECRET_KEY
print("🔐 Security Checks:")
print("-" * 80)
try:
    from django.conf import settings
    
    secret_key = settings.SECRET_KEY
    
    if 'django-insecure' in secret_key:
        issues.append("⚠️  CRITICAL: SECRET_KEY contains 'django-insecure' - MUST change before production!")
        print(f"   ❌ SECRET_KEY is insecure (contains 'django-insecure')")
    elif len(secret_key) < 50:
        issues.append("⚠️  SECRET_KEY is too short")
        print(f"   ❌ SECRET_KEY is too short")
    else:
        success.append("✓ SECRET_KEY is properly configured")
        print(f"   ✅ SECRET_KEY looks good")
except Exception as e:
    issues.append(f"SECRET_KEY error: {str(e)}")
    print(f"   ❌ Error checking SECRET_KEY: {str(e)}")

# 2. Check DEBUG setting
try:
    if settings.DEBUG:
        issues.append("❌ DEBUG=True in production! Must be False!")
        print(f"   ❌ DEBUG = {settings.DEBUG} (MUST BE FALSE)")
    else:
        success.append("✓ DEBUG is False")
        print(f"   ✅ DEBUG = {settings.DEBUG}")
except Exception as e:
    issues.append(f"DEBUG error: {str(e)}")

# 3. Check ALLOWED_HOSTS
print("\n📍 Site Configuration:")
print("-" * 80)
try:
    allowed_hosts = settings.ALLOWED_HOSTS
    if not allowed_hosts or allowed_hosts == ['*']:
        warnings.append("⚠️  ALLOWED_HOSTS might be too permissive")
        print(f"   ⚠️  ALLOWED_HOSTS = {allowed_hosts}")
    else:
        print(f"   ✅ ALLOWED_HOSTS = {allowed_hosts}")
        success.append("✓ ALLOWED_HOSTS configured")
except Exception as e:
    issues.append(f"ALLOWED_HOSTS error: {str(e)}")

# 4. Check Database
print("\n🐘 Database Configuration:")
print("-" * 80)
try:
    db = settings.DATABASES['default']
    engine = db['ENGINE'].split('.')[-1]
    
    if 'postgresql' in db['ENGINE']:
        print(f"   ✅ Database Engine: PostgreSQL")
        print(f"   ✅ Database Name: {db['NAME']}")
        print(f"   ✅ Database Host: {db['HOST']}:{db['PORT']}")
        success.append("✓ PostgreSQL configured")
    else:
        issues.append(f"❌ Database is {engine}, not PostgreSQL!")
        print(f"   ❌ Database Engine: {engine} (should be postgresql)")
    
    if db.get('ATOMIC_REQUESTS'):
        print(f"   ✅ ATOMIC_REQUESTS = True")
        success.append("✓ ATOMIC_REQUESTS enabled")
    else:
        warnings.append("⚠️  ATOMIC_REQUESTS not enabled")
        
except Exception as e:
    issues.append(f"Database config error: {str(e)}")
    print(f"   ❌ Error: {str(e)}")

# 5. Check Security Settings
print("\n🔒 Security Headers:")
print("-" * 80)
security_checks = [
    ('SECURE_SSL_REDIRECT', True),
    ('SESSION_COOKIE_SECURE', True),
    ('CSRF_COOKIE_SECURE', True),
    ('SECURE_HSTS_SECONDS', None),  # Just check if exists
]

for check_name, expected in security_checks:
    try:
        value = getattr(settings, check_name, None)
        if value is None:
            issues.append(f"❌ {check_name} not set")
            print(f"   ❌ {check_name} = {value}")
        elif expected is not None and value != expected:
            issues.append(f"⚠️  {check_name} = {value} (expected {expected})")
            print(f"   ⚠️  {check_name} = {value}")
        else:
            print(f"   ✅ {check_name} = {value}")
            success.append(f"✓ {check_name} configured")
    except Exception as e:
        print(f"   ❌ {check_name} error: {str(e)}")

# 6. Check Email Configuration
print("\n📧 Email Configuration:")
print("-" * 80)
try:
    email_host = settings.EMAIL_HOST
    email_port = settings.EMAIL_PORT
    email_use_tls = settings.EMAIL_USE_TLS
    
    print(f"   ✅ EMAIL_HOST = {email_host}")
    print(f"   ✅ EMAIL_PORT = {email_port}")
    print(f"   ✅ EMAIL_USE_TLS = {email_use_tls}")
    success.append("✓ Email configured")
except Exception as e:
    print(f"   ⚠️  Error: {str(e)}")

# 7. Check Installed Apps
print("\n📦 Installed Applications:")
print("-" * 80)
try:
    apps = settings.INSTALLED_APPS
    required_apps = ['django.contrib.admin', 'accounts', 'apps', 'categories', 'reviews']
    
    for app in required_apps:
        if app in apps:
            print(f"   ✅ {app}")
        else:
            print(f"   ❌ {app} NOT installed")
            issues.append(f"Missing app: {app}")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# 8. Check Middleware
print("\n⚙️  Middleware:")
print("-" * 80)
try:
    middleware = settings.MIDDLEWARE
    
    if 'whitenoise.middleware.WhiteNoiseMiddleware' in middleware:
        print(f"   ✅ WhiteNoise middleware enabled")
        success.append("✓ WhiteNoise configured")
    else:
        print(f"   ⚠️  WhiteNoise middleware not found")
        warnings.append("⚠️  WhiteNoise not in middleware")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# 9. Check Logging Configuration
print("\n📝 Logging Configuration:")
print("-" * 80)
try:
    if 'LOGGING' in dir(settings):
        print(f"   ✅ Logging configured")
        success.append("✓ Logging configured")
    else:
        print(f"   ⚠️  No logging configured")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# 10. Check Static Files
print("\n📂 Static Files Configuration:")
print("-" * 80)
try:
    static_url = settings.STATIC_URL
    static_root = settings.STATIC_ROOT
    staticfiles_storage = settings.STATICFILES_STORAGE
    
    print(f"   ✅ STATIC_URL = {static_url}")
    print(f"   ✅ STATIC_ROOT = {static_root}")
    print(f"   ✅ Storage = {staticfiles_storage.split('.')[-1]}")
    success.append("✓ Static files configured")
except Exception as e:
    print(f"   ❌ Error: {str(e)}")

# SUMMARY
print("\n" + "="*80)
print("AUDIT SUMMARY")
print("="*80 + "\n")

print(f"✅ Passed: {len(success)}")
for item in success:
    print(f"   {item}")

if warnings:
    print(f"\n⚠️  Warnings: {len(warnings)}")
    for item in warnings:
        print(f"   {item}")

if issues:
    print(f"\n❌ Critical Issues: {len(issues)}")
    for item in issues:
        print(f"   {item}")

print("\n" + "="*80)
if not issues:
    print("✨ PRODUCTION READY ✨")
    print("\nHowever, make sure to:")
    print("  1. Generate a NEW SECRET_KEY (current one is development key)")
    print("  2. Set up HTTPS/SSL certificate")
    print("  3. Configure your domain properly")
    print("  4. Use Gunicorn + Nginx in production (not Django dev server)")
else:
    print("⚠️  FIX CRITICAL ISSUES BEFORE DEPLOYMENT")

print("="*80 + "\n")
