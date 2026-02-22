#!/usr/bin/env python
"""
Script to bulk upload 5 sample Android apps to JnDroid Store
Usage: python manage.py shell < upload_sample_apps.py
"""

import os
import json
from decimal import Decimal
from django.core.files.base import ContentFile
from django.utils.text import slugify
from accounts.models import User
from categories.models import Category
from apps.models import App


def create_sample_apps():
    """Create and upload 5 sample Android apps"""
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='appuploader',
        defaults={
            'email': 'developer@jndroid.store',
            'first_name': 'App',
            'last_name': 'Developer',
            'is_staff': False,
        }
    )
    
    if created:
        user.set_password('TestPassword123!')
        user.save()
        print(f"✅ Created user: {user.username}")
    else:
        print(f"✅ Using existing user: {user.username}")
    
    # Get categories
    games_cat, _ = Category.objects.get_or_create(
        slug='games',
        defaults={
            'name': 'Games',
            'icon': '🎮',
            'color': '#e74c3c',
            'order': 2,
            'is_active': True,
        }
    )
    
    tools_cat, _ = Category.objects.get_or_create(
        slug='tools',
        defaults={
            'name': 'Tools',
            'icon': '🛠️',
            'color': '#3498db',
            'order': 5,
            'is_active': True,
        }
    )
    
    business_cat, _ = Category.objects.get_or_create(
        slug='business',
        defaults={
            'name': 'Business',
            'icon': '💼',
            'color': '#2ecc71',
            'order': 3,
            'is_active': True,
        }
    )
    
    entertainment_cat, _ = Category.objects.get_or_create(
        slug='entertainment',
        defaults={
            'name': 'Entertainment',
            'icon': '🎬',
            'color': '#9b59b6',
            'order': 4,
            'is_active': True,
        }
    )
    
    productivity_cat, _ = Category.objects.get_or_create(
        slug='productivity',
        defaults={
            'name': 'Productivity',
            'icon': '📊',
            'color': '#f39c12',
            'order': 6,
            'is_active': True,
        }
    )
    
    # Sample app data
    apps_data = [
        {
            'title': 'Game Master Pro',
            'short_description': 'Ultimate casual gaming experience',
            'description': 'A fast-paced, addictive game with amazing graphics and engaging gameplay. Compete with friends and climb the leaderboards.',
            'version': '1.0.0',
            'category': games_cat,
            'size_mb': Decimal('45.50'),
            'min_api_level': 21,
            'target_api_level': 34,
            'min_android_version': '5.0',
            'target_android_version': '14.0',
            'developer_name': 'GameStudio Inc',
            'developer_email': 'contact@gamestudio.dev',
            'support_email': 'support@gamestudio.dev',
            'website_url': 'https://gamestudio.dev',
            'is_free': True,
            'has_iap': True,
            'age_rating': '7+',
            'download_link': 'https://example.com/gamemaster.apk',
            'source_url': 'https://gamestudio.dev/master',
            'is_published': True,
        },
        {
            'title': 'File Manager Plus',
            'short_description': 'Fast and powerful file management tool',
            'description': 'Organize your files efficiently with a modern interface. Features include cloud sync, compression, and secure deletion.',
            'version': '2.1.5',
            'category': tools_cat,
            'size_mb': Decimal('8.75'),
            'min_api_level': 24,
            'target_api_level': 34,
            'min_android_version': '7.0',
            'target_android_version': '14.0',
            'developer_name': 'TechTools Labs',
            'developer_email': 'hello@techtools.io',
            'support_email': 'support@techtools.io',
            'website_url': 'https://techtools.io',
            'is_free': True,
            'has_iap': False,
            'age_rating': '3+',
            'download_link': 'https://example.com/filemgr.apk',
            'source_url': 'https://techtools.io/files',
            'is_published': True,
        },
        {
            'title': 'Invoice Maker Business',
            'short_description': 'Create professional invoices on the go',
            'description': 'Generate, send, and manage invoices from anywhere. Track payments, create estimates, and grow your business with ease.',
            'version': '3.2.1',
            'category': business_cat,
            'size_mb': Decimal('12.30'),
            'min_api_level': 21,
            'target_api_level': 34,
            'min_android_version': '5.0',
            'target_android_version': '14.0',
            'developer_name': 'Business Apps Co',
            'developer_email': 'dev@bizapps.com',
            'support_email': 'support@bizapps.com',
            'website_url': 'https://bizapps.com',
            'is_free': False,
            'price': Decimal('4.99'),
            'has_iap': False,
            'age_rating': '3+',
            'download_link': 'https://example.com/invoice.apk',
            'source_url': 'https://bizapps.com/invoice',
            'is_published': True,
        },
        {
            'title': 'Movie Streaming Hub',
            'short_description': 'Watch movies and TV shows anywhere',
            'description': 'Stream thousands of movies and shows in HD and 4K. Download for offline viewing and enjoy entertainment wherever you are.',
            'version': '1.5.3',
            'category': entertainment_cat,
            'size_mb': Decimal('35.12'),
            'min_api_level': 21,
            'target_api_level': 34,
            'min_android_version': '5.0',
            'target_android_version': '14.0',
            'developer_name': 'Entertainment Plus',
            'developer_email': 'contact@entplus.tv',
            'support_email': 'help@entplus.tv',
            'website_url': 'https://entplus.tv',
            'is_free': True,
            'has_iap': True,
            'age_rating': '12+',
            'download_link': 'https://example.com/moviehub.apk',
            'source_url': 'https://entplus.tv/hub',
            'is_published': True,
        },
        {
            'title': 'Productivity Timer',
            'short_description': 'Master time management and focus',
            'description': 'Use the Pomodoro technique to boost productivity. Track your tasks, set goals, and achieve more with effective time blocking.',
            'version': '4.0.2',
            'category': productivity_cat,
            'size_mb': Decimal('6.45'),
            'min_api_level': 26,
            'target_api_level': 34,
            'min_android_version': '8.0',
            'target_android_version': '14.0',
            'developer_name': 'Flow Systems',
            'developer_email': 'team@flowsys.app',
            'support_email': 'support@flowsys.app',
            'website_url': 'https://flowsys.app',
            'is_free': True,
            'has_iap': True,
            'age_rating': '3+',
            'download_link': 'https://example.com/prodtimer.apk',
            'source_url': 'https://flowsys.app/timer',
            'is_published': True,
        },
    ]
    
    # Create apps
    created_count = 0
    for app_data in apps_data:
        slug = slugify(app_data['title'])
        
        # Check if app already exists
        if App.objects.filter(slug=slug).exists():
            print(f"⚠️  App '{app_data['title']}' already exists. Skipping...")
            continue
        
        try:
            app = App.objects.create(
                owner=user,
                slug=slug,
                **app_data
            )
            created_count += 1
            print(f"✅ Created app: {app.title} (v{app.version})")
            print(f"   • Category: {app.category.name}")
            print(f"   • Download Link: {app.download_link}")
            print(f"   • Published: {app.is_published}")
            print()
            
        except Exception as e:
            print(f"❌ Error creating '{app_data['title']}': {str(e)}")
            print()
    
    # Summary
    total_apps = App.objects.filter(owner=user).count()
    print("\n" + "="*60)
    print("📊 UPLOAD SUMMARY")
    print("="*60)
    print(f"User: {user.get_full_name()} ({user.email})")
    print(f"Apps Created: {created_count}")
    print(f"Total User Apps: {total_apps}")
    print(f"Categories: {Category.objects.filter(is_active=True).count()}")
    print("="*60)
    
    # Show all apps
    print("\n📱 All Apps by this user:")
    for app in App.objects.filter(owner=user).order_by('-created_at'):
        print(f"  • {app.title} v{app.version} ({app.category.icon} {app.category.name})")
        if app.apk_file:
            print(f"    - APK File: {app.apk_file.name}")
        if app.download_link:
            print(f"    - Download: {app.download_link}")
        print(f"    - Slug: {app.slug}")
        print()


if __name__ == '__main__':
    create_sample_apps()
