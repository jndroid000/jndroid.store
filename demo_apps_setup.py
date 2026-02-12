from apps.models import App
from categories.models import Category
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

# Get or create user
user, created = User.objects.get_or_create(
    username="demo_developer",
    defaults={
        "email": "demo@appstore.local",
        "first_name": "Demo",
        "last_name": "Developer",
        "is_staff": True,
    }
)
if created:
    print("✓ Created demo user")

# Create categories
social_cat, created = Category.objects.get_or_create(
    name="Social",
    defaults={"icon": "👥", "color": "#3498db", "description": "Social apps", "is_active": True}
)
comm_cat, created = Category.objects.get_or_create(
    name="Communication",
    defaults={"icon": "💬", "color": "#2ecc71", "description": "Communication apps", "is_active": True}
)
ent_cat, created = Category.objects.get_or_create(
    name="Entertainment",
    defaults={"icon": "🎵", "color": "#e74c3c", "description": "Entertainment apps", "is_active": True}
)

# Create demo apps
with transaction.atomic():
    # Facebook
    facebook, created = App.objects.get_or_create(
        slug="facebook",
        defaults={
            "title": "Facebook",
            "owner": user,
            "category": social_cat,
            "version": "373.0",
            "size_mb": 142.5,
            "min_android_version": "7.0",
            "target_android_version": "15.0",
            "min_api_level": 24,
            "target_api_level": 35,
            "developer_name": "Meta Platforms, Inc.",
            "is_free": True,
            "downloads": 10000000,
            "avg_rating": 4.3,
            "is_published": True,
        }
    )
    print(f"✓ Facebook - {facebook.title}" if created else f"⊙ Facebook - Already exists")

    # WhatsApp
    whatsapp, created = App.objects.get_or_create(
        slug="whatsapp",
        defaults={
            "title": "WhatsApp",
            "owner": user,
            "category": comm_cat,
            "version": "23.26.74",
            "size_mb": 89.2,
            "min_android_version": "8.0",
            "target_android_version": "15.0",
            "min_api_level": 26,
            "target_api_level": 35,
            "developer_name": "WhatsApp LLC",
            "is_free": True,
            "downloads": 5000000,
            "avg_rating": 4.5,
            "is_published": True,
        }
    )
    print(f"✓ WhatsApp - {whatsapp.title}" if created else f"⊙ WhatsApp - Already exists")

    # TikTok
    tiktok, created = App.objects.get_or_create(
        slug="tiktok",
        defaults={
            "title": "TikTok",
            "owner": user,
            "category": ent_cat,
            "version": "37.4.0",
            "size_mb": 156.8,
            "min_android_version": "8.0",
            "target_android_version": "15.0",
            "min_api_level": 26,
            "target_api_level": 35,
            "developer_name": "TikTok Pte. Ltd.",
            "is_free": True,
            "downloads": 3000000,
            "avg_rating": 4.4,
            "is_published": True,
        }
    )
    print(f"✓ TikTok - {tiktok.title}" if created else f"⊙ TikTok - Already exists")

print()
print("=" * 60)
print("✅ Production-Ready App Detail Pages Created!")
print("=" * 60)
print()
print("📱 View the demo apps at:")
print("   http://127.0.0.1:8000/apps/facebook/")
print("   http://127.0.0.1:8000/apps/whatsapp/")
print("   http://127.0.0.1:8000/apps/tiktok/")
print()
print("✨ Features:")
print("   ✓ External CSS styling (static/css/app_detail.css)")
print("   ✓ Play Store-like design")
print("   ✓ Android version requirements display")
print("   ✓ Professional layout optimized for all devices")
print("   ✓ Responsive design")
print("   ✓ User reviews section")
print()
