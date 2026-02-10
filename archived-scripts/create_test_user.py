#!/usr/bin/env python
"""
Create test user script
Creates a test user for development and testing
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
django.setup()

from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

def create_test_user():
    """Create a test user"""
    print("=" * 60)
    print("CREATE TEST USER")
    print("=" * 60)
    
    test_data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'TestPassword123!@#',
        'first_name': 'Test',
        'last_name': 'User',
    }
    
    try:
        # Check if user already exists
        if User.objects.filter(username=test_data['username']).exists():
            print(f"✓ User '{test_data['username']}' already exists")
            user = User.objects.get(username=test_data['username'])
            print(f"  - ID: {user.id}")
            print(f"  - Email: {user.email}")
            print(f"  - Is Active: {user.is_active}")
            return user
        
        # Create new user
        user = User.objects.create_user(
            username=test_data['username'],
            email=test_data['email'],
            password=test_data['password'],
            first_name=test_data['first_name'],
            last_name=test_data['last_name'],
        )
        
        # Mark email as verified (if email_verified field exists)
        if hasattr(user, 'email_verified'):
            user.email_verified = True
            user.save()
        
        print(f"✓ Test user created successfully")
        print(f"  - Username: {user.username}")
        print(f"  - Email: {user.email}")
        print(f"  - Password: {test_data['password']}")
        print(f"  - ID: {user.id}")
        
        # Create additional test users
        print("\nCreating additional test users...")
        additional_users = [
            {'username': 'admin', 'email': 'admin@example.com'},
            {'username': 'testuser2', 'email': 'testuser2@example.com'},
            {'username': 'developer', 'email': 'developer@example.com'},
        ]
        
        for data in additional_users:
            if not User.objects.filter(username=data['username']).exists():
                user = User.objects.create_user(
                    username=data['username'],
                    email=data['email'],
                    password='TestPassword123!@#'
                )
                if hasattr(user, 'email_verified'):
                    user.email_verified = True
                    user.save()
                print(f"✓ Created user: {data['username']}")
            else:
                print(f"✓ User already exists: {data['username']}")
        
        print(f"\n✓ Total users: {User.objects.count()}")
        return True
        
    except IntegrityError as e:
        print(f"✗ Error: User already exists")
        print(f"✗ Details: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Error creating test user")
        print(f"✗ Details: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_test_user()
    sys.exit(0 if success else 1)
