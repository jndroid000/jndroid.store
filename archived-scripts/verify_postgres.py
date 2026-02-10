#!/usr/bin/env python
"""
PostgreSQL verification script
Verifies PostgreSQL database configuration and connectivity
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
django.setup()

from django.db import connection
from django.conf import settings

def verify_postgres():
    """Verify PostgreSQL configuration and connectivity"""
    print("=" * 60)
    print("POSTGRESQL VERIFICATION")
    print("=" * 60)
    
    # Get database configuration
    db_config = settings.DATABASES.get('default', {})
    
    print("\n[Database Configuration]")
    print("-" * 60)
    print(f"Engine: {db_config.get('ENGINE', 'Not configured')}")
    print(f"Name: {db_config.get('NAME', 'Not configured')}")
    print(f"User: {db_config.get('USER', 'Not configured')}")
    print(f"Host: {db_config.get('HOST', 'Not configured')}")
    print(f"Port: {db_config.get('PORT', 'Not configured')}")
    
    # Check if using PostgreSQL
    engine = db_config.get('ENGINE', '')
    is_postgres = 'postgres' in engine.lower()
    
    if is_postgres:
        print("\n✓ Using PostgreSQL")
    elif 'sqlite' in engine.lower():
        print("\n⚠ Using SQLite (Not PostgreSQL)")
        print("  To use PostgreSQL, update DATABASES in settings")
        return False
    else:
        print(f"\n⚠ Using {engine}")
    
    # Test connection
    print("\n[Connection Test]")
    print("-" * 60)
    try:
        with connection.cursor() as cursor:
            # Get PostgreSQL version if available
            if is_postgres:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                print(f"✓ PostgreSQL version: {version[0][:50]}...")
            
            # Test basic query
            cursor.execute("SELECT 1")
            print("✓ Connection successful")
            
            # Get database statistics
            if is_postgres:
                cursor.execute("""
                    SELECT datname, pg_size_pretty(pg_database_size(datname)) 
                    FROM pg_database 
                    WHERE datname = %s
                """, [db_config.get('NAME')])
                result = cursor.fetchone()
                if result:
                    print(f"✓ Database: {result[0]} ({result[1]})")
        
        print("\n✓ PostgreSQL verification: PASSED")
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        print("\nPossible solutions:")
        print("1. Ensure PostgreSQL server is running")
        print("2. Check database credentials in .env file")
        print("3. Verify DATABASE_URL or DATABASES settings")
        print("4. Ensure database user has proper permissions")
        return False
    
    # Additional checks if connected
    if is_postgres:
        print("\n[PostgreSQL Extensions]")
        print("-" * 60)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT extname FROM pg_extension;")
                extensions = cursor.fetchall()
                print(f"✓ Installed extensions: {len(extensions)}")
                for ext in extensions:
                    print(f"  - {ext[0]}")
        except Exception as e:
            print(f"⚠ Could not fetch extensions: {e}")

if __name__ == "__main__":
    success = verify_postgres()
    sys.exit(0 if success else 1)
