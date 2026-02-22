#!/usr/bin/env python
"""
Script to upload 5 sample Android apps via HTTP API using Python requests
Usage: python upload_apps_api.py [BASE_URL] [USERNAME] [PASSWORD]
Example: python upload_apps_api.py http://localhost:8000 appuploader TestPassword123!
"""

import sys
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, Optional
import json


class AppUploader:
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(username, password)
        self.session.headers.update({
            'User-Agent': 'AndroidAppUploader/1.0'
        })
        self.upload_url = f"{self.base_url}/apps/upload/"
        
    def test_connection(self) -> bool:
        """Test connection to the server"""
        try:
            response = self.session.get(f"{self.base_url}/apps/", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    def upload_app(self, app_data: Dict) -> bool:
        """Upload a single app"""
        print(f"⏳ Uploading: {app_data['title']}")
        
        try:
            response = self.session.post(
                self.upload_url,
                data={
                    'title': app_data['title'],
                    'category': app_data['category'],
                    'version': app_data['version'],
                    'short_description': app_data['short_description'],
                    'description': app_data['description'],
                    'download_link': app_data.get('download_link', ''),
                    'developer_name': app_data.get('developer_name', 'JnDroid Developer'),
                    'developer_email': app_data.get('developer_email', 'dev@jndroid.store'),
                    'support_email': app_data.get('support_email', 'support@jndroid.store'),
                    'website_url': app_data.get('website_url', 'https://jndroid.store'),
                    'min_api_level': app_data.get('min_api_level', 21),
                    'target_api_level': app_data.get('target_api_level', 34),
                    'min_android_version': app_data.get('min_android_version', '5.0'),
                    'target_android_version': app_data.get('target_android_version', '14.0'),
                    'size_mb': app_data.get('size_mb', '15.5'),
                    'age_rating': app_data.get('age_rating', '3+'),
                    'is_free': 'on' if app_data.get('is_free', True) else '',
                    'has_iap': 'on' if app_data.get('has_iap', False) else '',
                    'is_original_content': 'on',
                    'is_published': 'on',
                    'price': app_data.get('price', ''),
                },
                timeout=30
            )
            
            if response.status_code in [200, 201, 302]:
                print(f"✅ Successfully uploaded: {app_data['title']}")
                return True
            else:
                print(f"❌ Failed ({response.status_code}): {app_data['title']}")
                print(f"   Response: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Error uploading '{app_data['title']}': {str(e)}")
            return False
    
    def run(self, apps_data: list) -> None:
        """Upload all apps"""
        print("=" * 60)
        print("📱 Android App Upload via HTTP API")
        print("=" * 60)
        print(f"Base URL: {self.base_url}")
        print(f"Username: {self.username}")
        print()
        
        # Test connection
        print("🔗 Testing connection...")
        if not self.test_connection():
            sys.exit(1)
        print("✅ Connection successful!\n")
        
        # Upload apps
        success_count = 0
        for idx, app in enumerate(apps_data, 1):
            if self.upload_app(app):
                success_count += 1
            print()
        
        # Summary
        print("=" * 60)
        print(f"✅ Upload Summary: {success_count}/{len(apps_data)} successful")
        print("=" * 60)
        print(f"\n📊 View apps at: {self.base_url}/apps/")
        print(f"💼 Your dashboard: {self.base_url}/apps/my-apps/")


def main():
    # Configuration
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    username = sys.argv[2] if len(sys.argv) > 2 else "appuploader"
    password = sys.argv[3] if len(sys.argv) > 3 else "TestPassword123!"
    
    # Apps data to upload
    apps_data = [
        {
            'title': 'Game Master Pro',
            'category': 'games',
            'version': '1.0.0',
            'short_description': 'Ultimate casual gaming experience',
            'description': 'A fast-paced, addictive game with amazing graphics and engaging gameplay. Compete with friends and climb the leaderboards.',
            'download_link': 'https://example.com/gamemaster.apk',
            'developer_name': 'GameStudio Inc',
            'developer_email': 'contact@gamestudio.dev',
            'size_mb': '45.50',
            'age_rating': '7+',
            'is_free': True,
            'has_iap': True,
        },
        {
            'title': 'File Manager Plus',
            'category': 'tools',
            'version': '2.1.5',
            'short_description': 'Fast and powerful file management tool',
            'description': 'Organize your files efficiently with a modern interface. Features include cloud sync, compression, and secure deletion.',
            'download_link': 'https://example.com/filemgr.apk',
            'developer_name': 'TechTools Labs',
            'developer_email': 'hello@techtools.io',
            'size_mb': '8.75',
            'age_rating': '3+',
            'is_free': True,
            'has_iap': False,
        },
        {
            'title': 'Invoice Maker Business',
            'category': 'business',
            'version': '3.2.1',
            'short_description': 'Create professional invoices on the go',
            'description': 'Generate, send, and manage invoices from anywhere. Track payments, create estimates, and grow your business with ease.',
            'download_link': 'https://example.com/invoice.apk',
            'developer_name': 'Business Apps Co',
            'developer_email': 'dev@bizapps.com',
            'size_mb': '12.30',
            'age_rating': '3+',
            'price': '4.99',
            'is_free': False,
            'has_iap': False,
        },
        {
            'title': 'Movie Streaming Hub',
            'category': 'entertainment',
            'version': '1.5.3',
            'short_description': 'Watch movies and TV shows anywhere',
            'description': 'Stream thousands of movies and shows in HD and 4K. Download for offline viewing and enjoy entertainment wherever you are.',
            'download_link': 'https://example.com/moviehub.apk',
            'developer_name': 'Entertainment Plus',
            'developer_email': 'contact@entplus.tv',
            'size_mb': '35.12',
            'age_rating': '12+',
            'is_free': True,
            'has_iap': True,
        },
        {
            'title': 'Productivity Timer',
            'category': 'productivity',
            'version': '4.0.2',
            'short_description': 'Master time management and focus',
            'description': 'Use the Pomodoro technique to boost productivity. Track your tasks, set goals, and achieve more with effective time blocking.',
            'download_link': 'https://example.com/prodtimer.apk',
            'developer_name': 'Flow Systems',
            'developer_email': 'team@flowsys.app',
            'size_mb': '6.45',
            'age_rating': '3+',
            'is_free': True,
            'has_iap': True,
        },
    ]
    
    # Run uploader
    uploader = AppUploader(base_url, username, password)
    uploader.run(apps_data)


if __name__ == '__main__':
    main()
