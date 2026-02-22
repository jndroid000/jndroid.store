"""
Management command to upload Telegram app
Usage: python manage.py upload_telegram_app
"""

from decimal import Decimal
from django.core.management.base import BaseCommand
from accounts.models import User
from categories.models import Category
from apps.models import App


class Command(BaseCommand):
    help = 'Upload Telegram app to JnDroid Store'

    def handle(self, *args, **options):
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("🚀 TELEGRAM APP UPLOAD"))
        self.stdout.write("="*60 + "\n")
        
        # Step 1: Get or create developer user
        self.stdout.write("📝 Step 1: Setting up developer account...")
        user, created = User.objects.get_or_create(
            username='telegramdeveloper',
            defaults={
                'email': 'telegram@jndroid.store',
                'first_name': 'Telegram',
                'last_name': 'Team',
                'is_staff': False,
            }
        )
        
        if created:
            user.set_password('TelegramApp123!')
            user.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Created developer: {user.username}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Using existing developer: {user.username}"))
        
        # Step 2: Get or create Communication category
        self.stdout.write("\n📁 Step 2: Setting up category...")
        category, created = Category.objects.get_or_create(
            slug='communication',
            defaults={
                'name': 'Communication',
                'icon': '💬',
                'color': '#0088cc',
                'order': 7,
                'is_active': True,
            }
        )
        self.stdout.write(self.style.SUCCESS(f"✅ Category ready: {category.name} {category.icon}"))
        
        # Step 3: Check if Telegram already exists
        self.stdout.write("\n🔍 Step 3: Checking for existing Telegram app...")
        slug = 'telegram-messenger'
        
        try:
            existing_app = App.objects.get(slug=slug)
            self.stdout.write(self.style.WARNING(f"⚠️  Telegram app already exists (ID: {existing_app.id})"))
            self.stdout.write("   Updating existing app...")
            app = existing_app
            is_new = False
        except App.DoesNotExist:
            self.stdout.write("📦 Creating new Telegram app entry...")
            app = App()
            is_new = True
        
        # Step 4: Set app details
        self.stdout.write("\n📋 Step 4: Setting app details...")
        
        app.owner = user
        app.title = 'Telegram'
        app.slug = slug
        app.category = category
        app.short_description = 'Fast and secure messaging app with cloud sync'
        app.description = '''Telegram is a messaging app focused on speed and security. It's super fast, simple, and free. You can send messages, photos, videos and audio files of any type to anyone, anytime, anywhere.

Features:
• Cloud-based: Instantly access your messages from multiple devices
• Fast: Telegram is the fastest messaging app on the market
• Simple: The interface is clean and intuitive
• Secure: Telegram uses end-to-end encrypted Secret Chats
• Powerful: You can send files up to 2GB in size
• Open: Telegram's code is open and available for review
• Free: Telegram will always be free. No ads, ever.

Contact:
🌐 Website: telegram.org
📧 Support: support@telegram.org
💬 Community: t.me/telegram'''
        
        app.version = '10.13.3'
        app.size_mb = Decimal('90.25')
        app.min_api_level = 24
        app.target_api_level = 35
        app.min_android_version = '7.0'
        app.target_android_version = '15.0'
        
        # Developer info
        app.developer_name = 'Telegram FZ-LLC'
        app.developer_email = 'support@telegram.org'
        app.support_email = 'support@telegram.org'
        app.website_url = 'https://telegram.org'
        app.source_url = 'https://github.com/DrKLO/Telegram'
        app.privacy_policy_url = 'https://telegram.org/privacy'
        app.terms_url = 'https://telegram.org/tos'
        app.store_name = 'JnDroid Store'
        app.store_email = 'apps@jndroid.store'
        
        # Monetization
        app.is_free = True
        app.price = None
        app.has_iap = False
        app.age_rating = '3+'
        
        # Download options
        app.download_link = 'https://telegram.org/dl/android'
        
        # Copyright info
        app.content_ownership_type = 'informational'
        app.copyright_statement = 'Telegram is an open-source messaging application available on jndroid.store for informational purposes and accessibility.'
        app.copyright_license_type = 'proprietary'
        app.copyright_notice_required = False
        app.is_original_content = True
        app.play_store_link = 'https://play.google.com/store/apps/details?id=org.telegram.messenger'
        app.developer_website = 'https://telegram.org'
        
        # Publishing
        app.is_published = True
        
        # Save
        app.save()
        
        if is_new:
            self.stdout.write(self.style.SUCCESS(f"✅ Created new Telegram app (ID: {app.id})"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Updated existing Telegram app (ID: {app.id})"))
        
        # Step 5: Print summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📊 UPLOAD SUMMARY"))
        self.stdout.write("="*60)
        self.stdout.write(f"✅ App Name:         {app.title}")
        self.stdout.write(f"✅ Version:          {app.version}")
        self.stdout.write(f"✅ Category:         {app.category.icon} {app.category.name}")
        self.stdout.write(f"✅ Size:             {app.size_mb} MB")
        self.stdout.write(f"✅ Developer:        {app.developer_name}")
        self.stdout.write(f"✅ Download Link:    {app.download_link}")
        self.stdout.write(f"✅ Official Link:    {app.play_store_link}")
        self.stdout.write(f"✅ Status:           {'Published ✓' if app.is_published else 'Draft'}")
        self.stdout.write(f"✅ Created At:       {app.created_at}")
        self.stdout.write(f"✅ Updated At:       {app.updated_at}")
        self.stdout.write(f"✅ App URL:          /apps/{app.slug}/")
        self.stdout.write("="*60)
        
        self.stdout.write(self.style.SUCCESS("\n🎉 SUCCESS! Telegram app is now available on your store!"))
        self.stdout.write(f"📱 View at: http://localhost:8000/apps/{app.slug}/\n")
