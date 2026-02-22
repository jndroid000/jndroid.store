"""
Django Management Command to upload 5 sample Android apps
Usage: python manage.py upload_sample_apps
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from decimal import Decimal
from accounts.models import User
from categories.models import Category
from apps.models import App


class Command(BaseCommand):
    help = 'Upload 5 sample Android apps to JnDroid Store'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='appuploader',
            help='Username to upload apps as (default: appuploader)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force upload even if apps already exist'
        )

    def handle(self, *args, **options):
        username = options['username']
        force = options['force']

        self.stdout.write(self.style.SUCCESS('🚀 Starting sample apps upload...'))
        self.stdout.write('-' * 60)

        # Get or create user
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"✅ Using existing user: {user.username}")
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=username,
                email=f'{username}@jndroid.store',
                first_name='App',
                last_name='Developer',
                password='TestPassword123!'
            )
            self.stdout.write(f"✅ Created new user: {user.username}")

        self.stdout.write(f"   Email: {user.email}")
        self.stdout.write('-' * 60)

        # Ensure categories exist
        categories_data = {
            'games': {
                'name': 'Games',
                'icon': '🎮',
                'color': '#e74c3c',
                'order': 2,
            },
            'tools': {
                'name': 'Tools',
                'icon': '🛠️',
                'color': '#3498db',
                'order': 5,
            },
            'business': {
                'name': 'Business',
                'icon': '💼',
                'color': '#2ecc71',
                'order': 3,
            },
            'entertainment': {
                'name': 'Entertainment',
                'icon': '🎬',
                'color': '#9b59b6',
                'order': 4,
            },
            'productivity': {
                'name': 'Productivity',
                'icon': '📊',
                'color': '#f39c12',
                'order': 6,
            },
        }

        categories = {}
        for slug, data in categories_data.items():
            cat, created = Category.objects.get_or_create(slug=slug, defaults=data)
            categories[slug] = cat
            if created:
                self.stdout.write(f"✅ Created category: {cat.name}")

        self.stdout.write('-' * 60)
        self.stdout.write('\n📱 Uploading 5 sample apps...\n')

        # Sample apps data
        apps_data = [
            {
                'title': 'Game Master Pro',
                'short_description': 'Ultimate casual gaming experience',
                'description': 'A fast-paced, addictive game with amazing graphics and engaging gameplay. Compete with friends and climb the leaderboards.',
                'version': '1.0.0',
                'category_slug': 'games',
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
            },
            {
                'title': 'File Manager Plus',
                'short_description': 'Fast and powerful file management tool',
                'description': 'Organize your files efficiently with a modern interface. Features include cloud sync, compression, and secure deletion.',
                'version': '2.1.5',
                'category_slug': 'tools',
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
            },
            {
                'title': 'Invoice Maker Business',
                'short_description': 'Create professional invoices on the go',
                'description': 'Generate, send, and manage invoices from anywhere. Track payments, create estimates, and grow your business with ease.',
                'version': '3.2.1',
                'category_slug': 'business',
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
            },
            {
                'title': 'Movie Streaming Hub',
                'short_description': 'Watch movies and TV shows anywhere',
                'description': 'Stream thousands of movies and shows in HD and 4K. Download for offline viewing and enjoy entertainment wherever you are.',
                'version': '1.5.3',
                'category_slug': 'entertainment',
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
            },
            {
                'title': 'Productivity Timer',
                'short_description': 'Master time management and focus',
                'description': 'Use the Pomodoro technique to boost productivity. Track your tasks, set goals, and achieve more with effective time blocking.',
                'version': '4.0.2',
                'category_slug': 'productivity',
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
            },
        ]

        # Create apps
        created_count = 0
        skipped_count = 0

        for idx, app_data in enumerate(apps_data, 1):
            slug = slugify(app_data['title'])
            
            # Extract category
            category_slug = app_data.pop('category_slug')
            app_data['category'] = categories[category_slug]
            app_data['owner'] = user
            app_data['slug'] = slug
            app_data['is_published'] = True

            # Check if app exists
            if App.objects.filter(slug=slug).exists():
                if not force:
                    self.stdout.write(self.style.WARNING(
                        f"⚠️  App already exists: {app_data['title']}"
                    ))
                    skipped_count += 1
                    continue
                else:
                    App.objects.filter(slug=slug).delete()

            try:
                app = App.objects.create(**app_data)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"({idx}/5) ✅ {app.title} v{app.version}"
                ))
                self.stdout.write(f"       {app.category.icon} Category: {app.category.name}")
                self.stdout.write(f"       📊 Size: {app.size_mb}MB | Published: {app.is_published}")

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f"❌ Error creating '{app_data['title']}': {str(e)}"
                ))

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('📊 UPLOAD COMPLETE'))
        self.stdout.write('=' * 60)
        self.stdout.write(f"✅ Created: {created_count}")
        self.stdout.write(f"⚠️  Skipped: {skipped_count}")
        self.stdout.write(f"📱 Total User Apps: {App.objects.filter(owner=user).count()}")
        self.stdout.write('=' * 60)

        # Show apps list
        self.stdout.write('\n📋 Uploaded Apps:\n')
        for app in App.objects.filter(owner=user).order_by('-created_at'):
            self.stdout.write(f"  {app.category.icon} {app.title} v{app.version}")
            self.stdout.write(f"     URL: /apps/{app.slug}/")
            if app.download_link:
                self.stdout.write(f"     DL: {app.download_link[:50]}...")
