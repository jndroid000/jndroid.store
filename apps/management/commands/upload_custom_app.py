#!/usr/bin/env python
"""
Universal App Upload Script for JnDroid Store
Usage: python manage.py upload_custom_app --name="WhatsApp" --app-version="2.24.10" --category="communication" --size="50.5"
"""

from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from accounts.models import User
from categories.models import Category
from apps.models import App
from django.utils.text import slugify


class Command(BaseCommand):
    help = 'Upload any custom app to JnDroid Store'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='App name')
        parser.add_argument('--app-version', type=str, default='1.0.0', help='App version')
        parser.add_argument('--category', type=str, default='tools', help='Category slug')
        parser.add_argument('--size', type=float, default=50.0, help='Size in MB')
        parser.add_argument('--description', type=str, default='', help='Short description')
        parser.add_argument('--download-link', type=str, default='', help='Download link')
        parser.add_argument('--developer', type=str, default='Developer', help='Developer name')
        parser.add_argument('--email', type=str, default='dev@example.com', help='Developer email')
        parser.add_argument('--website', type=str, default='', help='Website URL')
        parser.add_argument('--is-free', type=bool, default=True, help='Is free app')
        parser.add_argument('--min-api', type=int, default=21, help='Minimum API level')
        parser.add_argument('--target-api', type=int, default=35, help='Target API level')
        parser.add_argument('--min-version', type=str, default='5.0', help='Minimum Android version')
        parser.add_argument('--target-version', type=str, default='15.0', help='Target Android version')
        parser.add_argument('--age-rating', type=str, default='3+', help='Age rating')
        parser.add_argument('--publish', type=bool, default=True, help='Publish immediately')

    def handle(self, *args, **options):
        app_name = options['name']
        version = options['app_version']
        category_slug = options['category']
        size = Decimal(str(options['size']))
        description = options['description'] or f'Fast and powerful {app_name}'
        download_link = options['download_link']
        developer_name = options['developer']
        developer_email = options['email']
        website_url = options['website']
        is_free = options['is_free']
        min_api = options['min_api']
        target_api = options['target_api']
        min_version = options['min_version']
        target_version = options['target_version']
        age_rating = options['age_rating']
        is_published = options['publish']

        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS(f"📤 UPLOADING: {app_name.upper()}"))
        self.stdout.write("="*70 + "\n")
        
        try:
            # Step 1: Get or create developer
            self.stdout.write(f"👤 Creating developer account for '{developer_name}'...")
            username = slugify(developer_name.lower())[:30]
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': developer_email,
                    'first_name': app_name,
                    'last_name': 'Team',
                    'is_staff': False,
                }
            )
            if created:
                user.set_password('AutoGenPassword123!')
                user.save()
            self.stdout.write(self.style.SUCCESS(f"   ✅ Developer: {user.username}"))
            
            # Step 2: Get or create category
            self.stdout.write(f"\n📂 Setting up category '{category_slug}'...")
            try:
                category = Category.objects.get(slug=category_slug)
            except Category.DoesNotExist:
                raise CommandError(f"Category '{category_slug}' does not exist. Available categories: tools, games, communication, business, entertainment, productivity")
            self.stdout.write(self.style.SUCCESS(f"   ✅ Category: {category.icon} {category.name}"))
            
            # Step 3: Create or update app
            slug = slugify(app_name)
            self.stdout.write(f"\n📦 Creating app entry (slug: {slug})...")
            
            try:
                app = App.objects.get(slug=slug)
                self.stdout.write(self.style.WARNING(f"   ⚠️  App already exists, updating..."))
                is_new = False
            except App.DoesNotExist:
                app = App()
                is_new = True
            
            # Set all details
            app.owner = user
            app.title = app_name
            app.slug = slug
            app.category = category
            app.short_description = description[:220]
            app.description = description
            app.version = version
            app.size_mb = size
            app.min_api_level = min_api
            app.target_api_level = target_api
            app.min_android_version = min_version
            app.target_android_version = target_version
            app.developer_name = developer_name
            app.developer_email = developer_email
            app.support_email = developer_email
            app.website_url = website_url if website_url else ''
            app.is_free = is_free
            app.age_rating = age_rating
            app.is_published = is_published
            app.content_ownership_type = 'informational'
            app.copyright_statement = f'{app_name} is available on JnDroid Store for informational purposes.'
            app.copyright_license_type = 'proprietary'
            app.is_original_content = True
            
            if download_link:
                app.download_link = download_link
            
            app.save()
            
            if is_new:
                self.stdout.write(self.style.SUCCESS(f"   ✅ Created app (ID: {app.id})"))
            else:
                self.stdout.write(self.style.SUCCESS(f"   ✅ Updated app (ID: {app.id})"))
            
            # Step 4: Summary
            self.stdout.write("\n" + "="*70)
            self.stdout.write(self.style.SUCCESS("✨ UPLOAD COMPLETE"))
            self.stdout.write("="*70)
            self.stdout.write(f"📱 App Name:        {app.title}")
            self.stdout.write(f"📌 Version:         {app.version}")
            self.stdout.write(f"📂 Category:        {app.category.icon} {app.category.name}")
            self.stdout.write(f"📦 Size:            {app.size_mb} MB")
            self.stdout.write(f"👤 Developer:       {app.developer_name} ({app.developer_email})")
            self.stdout.write(f"🤖 Min API:         {app.min_api_level} ({app.min_android_version})")
            self.stdout.write(f"🎯 Target API:      {app.target_api_level} ({app.target_android_version})")
            self.stdout.write(f"🆓 Free:            {'Yes' if app.is_free else 'No'}")
            self.stdout.write(f"📊 Status:          {'Published ✓' if app.is_published else 'Draft'}")
            self.stdout.write(f"🔗 URL:             /apps/{app.slug}/")
            if app.download_link:
                self.stdout.write(f"⬇️  Download:        {app.download_link}")
            self.stdout.write("="*70)
            self.stdout.write(self.style.SUCCESS(f"\n🎉 {app_name} is now available on your store!\n"))
            
        except CommandError as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error: {str(e)}\n"))
            raise
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Unexpected error: {str(e)}\n"))
            raise
