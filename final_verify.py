#!/usr/bin/env python
"""
Final PostgreSQL Production Setup Verification
"""
import os
import sys
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

print(f"\n{BLUE}{'='*70}")
print("FINAL POSTGRESQL PRODUCTION SETUP VERIFICATION")
print(f"{'='*70}{RESET}\n")

os.environ.setdefault('DJANGO_ENV', 'production')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
os.environ.setdefault('DATABASE_PASSWORD', '522475')

tests_passed = 0
tests_failed = 0

# Test 1: psycopg2
print(f"{BLUE}1. Testing psycopg2 installation...{RESET}")
try:
    import psycopg2
    print(f"   {GREEN}✓{RESET} psycopg2 version {psycopg2.__version__} installed")
    tests_passed += 1
except ImportError:
    print(f"   {RED}✗{RESET} psycopg2 NOT installed")
    tests_failed += 1

# Test 2: PostgreSQL Connection
print(f"\n{BLUE}2. Testing PostgreSQL connection...{RESET}")
try:
    import psycopg2
    conn = psycopg2.connect(
        dbname='jndroid_db',
        user='postgres',
        password='522475',
        host='localhost',
        port='5432'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"   {GREEN}✓{RESET} Connected to jndroid_db")
    print(f"   {GREEN}✓{RESET} PostgreSQL version: {version.split(',')[0]}")
    cursor.close()
    conn.close()
    tests_passed += 1
except Exception as e:
    print(f"   {RED}✗{RESET} Connection failed: {str(e)}")
    tests_failed += 1

# Test 3: Django Configuration
print(f"\n{BLUE}3. Testing Django configuration...{RESET}")
try:
    import django
    django.setup()
    from django.conf import settings
    print(f"   {GREEN}✓{RESET} Django loaded successfully")
    print(f"   {GREEN}✓{RESET} DEBUG = {settings.DEBUG}")
    print(f"   {GREEN}✓{RESET} Database Engine: {settings.DATABASES['default']['ENGINE'].split('.')[-1]}")
    tests_passed += 1
except Exception as e:
    print(f"   {RED}✗{RESET} Django configuration failed: {str(e)}")
    tests_failed += 1

# Test 4: Database Connection via Django
print(f"\n{BLUE}4. Testing Django database connection...{RESET}")
try:
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    cursor.close()
    print(f"   {GREEN}✓{RESET} Django database connection working")
    tests_passed += 1
except Exception as e:
    print(f"   {RED}✗{RESET} Database connection failed: {str(e)}")
    tests_failed += 1

# Test 5: Models
print(f"\n{BLUE}5. Testing Django models...{RESET}")
try:
    from accounts.models import User
    from apps.models import App, AppVersion
    from categories.models import Category
    from reviews.models import Review
    print(f"   {GREEN}✓{RESET} All models loaded successfully")
    print(f"   {GREEN}✓{RESET} User model: accounts.User")
    print(f"   {GREEN}✓{RESET} App model: apps.App")
    print(f"   {GREEN}✓{RESET} Category model: categories.Category")
    print(f"   {GREEN}✓{RESET} Review model: reviews.Review")
    tests_passed += 1
except Exception as e:
    print(f"   {RED}✗{RESET} Models loading failed: {str(e)}")
    tests_failed += 1

# Summary
print(f"\n{BLUE}{'='*70}")
print("SUMMARY")
print(f"{'='*70}{RESET}")
print(f"{GREEN}✓ PASSED: {tests_passed}{RESET}")
print(f"{RED}✗ FAILED: {tests_failed}{RESET}")

if tests_failed == 0:
    print(f"\n{GREEN}✅ ALL TESTS PASSED!{RESET}")
    print(f"\n{BLUE}Your PostgreSQL production setup is ready for deployment!{RESET}")
    print(f"\nNext steps:")
    print(f"  1. python manage.py migrate")
    print(f"  2. python manage.py createsuperuser")
    print(f"  3. python manage.py collectstatic --noinput")
    print()
    sys.exit(0)
else:
    print(f"\n{RED}❌ SOME TESTS FAILED!{RESET}")
    print(f"Please fix the above errors before deployment.")
    print()
    sys.exit(1)
