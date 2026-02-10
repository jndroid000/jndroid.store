#!/usr/bin/env python
"""
PostgreSQL Production Configuration Verification Script
Verifies all database connections and settings for production deployment
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_psycopg2_installed():
    """Test if psycopg2 is installed"""
    print("\n📦 Testing psycopg2 installation...")
    try:
        import psycopg2
        print(f"   ✓ psycopg2 is installed (version: {psycopg2.__version__})")
        return True
    except ImportError:
        print("   ✗ psycopg2 is NOT installed")
        print("   ⚠️  Run: pip install psycopg2-binary==2.9.9")
        return False


def test_postgres_connection():
    """Test direct PostgreSQL connection"""
    print("\n🔌 Testing PostgreSQL Connection...")
    
    try:
        import psycopg2
        
        # Load environment variables
        env_file = project_root / '.env.production'
        env_vars = {}
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        db_config = {
            'database': env_vars.get('DATABASE_NAME', 'jndroid_db'),
            'user': env_vars.get('DATABASE_USER', 'postgres'),
            'password': env_vars.get('DATABASE_PASSWORD', ''),
            'host': env_vars.get('DATABASE_HOST', 'localhost'),
            'port': env_vars.get('DATABASE_PORT', '5432'),
        }
        
        print(f"\n   Attempting connection with:")
        print(f"   - Database: {db_config['database']}")
        print(f"   - User: {db_config['user']}")
        print(f"   - Host: {db_config['host']}")
        print(f"   - Port: {db_config['port']}")
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        print(f"\n   ✓ PostgreSQL Connection Successful!")
        print(f"   Version: {db_version}")
        
        # Get database info
        cursor.execute("SELECT datname FROM pg_database WHERE datname = %s;", (db_config['database'],))
        if cursor.fetchone():
            print(f"   ✓ Database '{db_config['database']}' exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"\n   ✗ PostgreSQL Connection FAILED!")
        print(f"   Error: {str(e)}")
        print(f"\n   ⚠️  Troubleshooting:")
        print(f"      1. Check if PostgreSQL service is running")
        print(f"      2. Verify credentials in .env.production")
        print(f"      3. Check PostgreSQL host and port")
        return False


def test_django_settings():
    """Test Django settings with PostgreSQL"""
    print("\n⚙️  Testing Django Settings...")
    
    try:
        os.environ.setdefault('DJANGO_ENV', 'production')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
        
        import django
        django.setup()
        
        from django.conf import settings
        from django.db import connection
        
        print(f"   ✓ Django loaded successfully")
        
        # Check database backend
        if 'postgresql' in settings.DATABASES['default']['ENGINE']:
            print(f"   ✓ Using PostgreSQL backend")
        else:
            print(f"   ✗ Not using PostgreSQL backend: {settings.DATABASES['default']['ENGINE']}")
        
        # Check security settings
        if not settings.DEBUG:
            print(f"   ✓ DEBUG = False (production ready)")
        else:
            print(f"   ✗ DEBUG = True (NOT production ready)")
        
        # Test connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print(f"   ✓ Django database connection working")
        except Exception as e:
            print(f"   ✗ Django database connection failed: {str(e)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"\n   ✗ Django settings test FAILED!")
        print(f"   Error: {str(e)}")
        return False


def test_django_check():
    """Run Django system check"""
    print("\n✔️  Running Django System Check...")
    
    try:
        os.environ.setdefault('DJANGO_ENV', 'production')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
        
        import django
        django.setup()
        
        from django.core.management import execute_from_command_line
        
        # Run check command
        sys.argv = ['manage.py', 'check']
        try:
            execute_from_command_line(sys.argv)
            print(f"   ✓ All checks passed!")
            return True
        except SystemExit as e:
            if e.code == 0:
                print(f"   ✓ All checks passed!")
                return True
            else:
                print(f"   ✗ Checks failed with code: {e.code}")
                return False
        
    except Exception as e:
        print(f"\n   ✗ Django check FAILED!")
        print(f"   Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║   PostgreSQL Production Configuration Verification             ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    results = []
    
    # Run tests
    results.append(("psycopg2 Installation", test_psycopg2_installed()))
    results.append(("PostgreSQL Connection", test_postgres_connection()))
    results.append(("Django Settings", test_django_settings()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} | {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("="*70)
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✨ All tests passed! PostgreSQL is production-ready.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please fix before deployment.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
