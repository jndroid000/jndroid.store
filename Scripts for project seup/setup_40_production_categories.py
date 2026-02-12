#!/usr/bin/env python
"""
Production-Level Categories Setup - 40 Complete Categories
All categories with full production details, descriptions, colors, icons
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from categories.models import Category

# 40 PRODUCTION-LEVEL CATEGORIES
PRODUCTION_CATEGORIES = [
    {
        "name": "Games",
        "slug": "games",
        "icon": "🎮",
        "icon_class": "fas fa-gamepad",
        "color": "#e74c3c",
        "description": "Explore action games, puzzles, strategy games, RPGs, and casual games. Unlimited entertainment tested for quality and security.",
        "order": 1,
    },
    {
        "name": "Business",
        "slug": "business",
        "icon": "💼",
        "icon_class": "fas fa-briefcase",
        "color": "#3498db",
        "description": "Professional tools for entrepreneurs and corporate teams. Manage finance, projects, and grow your business efficiently.",
        "order": 2,
    },
    {
        "name": "Education",
        "slug": "education",
        "icon": "🎓",
        "icon_class": "fas fa-graduation-cap",
        "color": "#27ae60",
        "description": "Learn new skills with online courses, tutorials, and educational content. Improve knowledge in any field you desire.",
        "order": 3,
    },
    {
        "name": "Health & Fitness",
        "slug": "health-fitness",
        "icon": "🏋️",
        "icon_class": "fas fa-heartbeat",
        "color": "#f39c12",
        "description": "Track workouts, nutrition, and wellness. Personal training apps, meditation guides, and fitness tracking tools.",
        "order": 4,
    },
    {
        "name": "Social Media",
        "slug": "social-media",
        "icon": "📱",
        "icon_class": "fas fa-share-alt",
        "color": "#9b59b6",
        "description": "Connect with friends and family through social networking apps. Share moments, chat, and build communities.",
        "order": 5,
    },
    {
        "name": "Productivity",
        "slug": "productivity",
        "icon": "📊",
        "icon_class": "fas fa-chart-line",
        "color": "#1abc9c",
        "description": "Organize tasks, manage projects, and boost productivity. Note-taking apps, calendars, and to-do list managers.",
        "order": 6,
    },
    {
        "name": "Entertainment",
        "slug": "entertainment",
        "icon": "🎬",
        "icon_class": "fas fa-film",
        "color": "#e67e22",
        "description": "Stream movies, TV shows, and entertainment content. Watch anytime, anywhere with premium quality.",
        "order": 7,
    },
    {
        "name": "Utilities",
        "slug": "utilities",
        "icon": "🛠️",
        "icon_class": "fas fa-tools",
        "color": "#95a5a6",
        "description": "Essential tools and system utilities. File managers, cleaners, optimizers, and system maintenance applications.",
        "order": 8,
    },
    {
        "name": "Shopping",
        "slug": "shopping",
        "icon": "🛒",
        "icon_class": "fas fa-shopping-cart",
        "color": "#c0392b",
        "description": "Shop online for everything you need. Compare prices, find deals, and get the best shopping experience.",
        "order": 9,
    },
    {
        "name": "Food & Drink",
        "slug": "food-drink",
        "icon": "🍔",
        "icon_class": "fas fa-utensils",
        "color": "#d35400",
        "description": "Order food, find recipes, and discover restaurants. Delivery apps and cooking guides at your fingertips.",
        "order": 10,
    },
    {
        "name": "Travel & Local",
        "slug": "travel-local",
        "icon": "✈️",
        "icon_class": "fas fa-plane",
        "color": "#16a085",
        "description": "Book flights, hotels, and explore local attractions. Travel guides and maps for adventurous journeys.",
        "order": 11,
    },
    {
        "name": "Photography",
        "slug": "photography",
        "icon": "📷",
        "icon_class": "fas fa-camera",
        "color": "#8e44ad",
        "description": "Edit photos, apply filters, and create stunning images. Professional photography tools and effects.",
        "order": 12,
    },
    {
        "name": "Music & Audio",
        "slug": "music-audio",
        "icon": "🎵",
        "icon_class": "fas fa-music",
        "color": "#2980b9",
        "description": "Stream music, create playlists, and discover artists. High-quality audio and exclusive content.",
        "order": 13,
    },
    {
        "name": "Books & Reference",
        "slug": "books-reference",
        "icon": "📚",
        "icon_class": "fas fa-book",
        "color": "#34495e",
        "description": "Read ebooks, digital books, and reference materials. Access knowledge from any device anytime.",
        "order": 14,
    },
    {
        "name": "News & Magazines",
        "slug": "news-magazines",
        "icon": "📰",
        "icon_class": "fas fa-newspaper",
        "color": "#7f8c8d",
        "description": "Stay updated with breaking news and trending stories. Personalized news feeds and magazine subscriptions.",
        "order": 15,
    },
    {
        "name": "Sports",
        "slug": "sports",
        "icon": "⚽",
        "icon_class": "fas fa-football-ball",
        "color": "#e74c3c",
        "description": "Follow your favorite teams and athletes. Live scores, updates, and sports analysis at your fingertips.",
        "order": 16,
    },
    {
        "name": "Communication",
        "slug": "communication",
        "icon": "💬",
        "icon_class": "fas fa-comments",
        "color": "#3498db",
        "description": "Messaging apps, voice calls, and video conferencing. Stay in touch with seamless communication tools.",
        "order": 17,
    },
    {
        "name": "Video Players",
        "slug": "video-players",
        "icon": "🎥",
        "icon_class": "fas fa-video",
        "color": "#e67e22",
        "description": "Play videos in all formats. Fast, reliable video playback with advanced features and subtitles.",
        "order": 18,
    },
    {
        "name": "Maps & Navigation",
        "slug": "maps-navigation",
        "icon": "🗺️",
        "icon_class": "fas fa-map",
        "color": "#27ae60",
        "description": "Navigate with GPS, find locations, and get directions. Real-time traffic and offline map support.",
        "order": 19,
    },
    {
        "name": "Finance",
        "slug": "finance",
        "icon": "💰",
        "icon_class": "fas fa-money-bill-wave",
        "color": "#27ae60",
        "description": "Manage finances, track investments, and plan budgets. Banking apps and financial analysis tools.",
        "order": 20,
    },
    {
        "name": "Messaging",
        "slug": "messaging",
        "icon": "✉️",
        "icon_class": "fas fa-envelope",
        "color": "#9b59b6",
        "description": "Send messages, share media, and create group chats. Encrypted messaging for privacy and security.",
        "order": 21,
    },
    {
        "name": "Lifestyle",
        "slug": "lifestyle",
        "icon": "🌟",
        "icon_class": "fas fa-star",
        "color": "#f39c12",
        "description": "Explore fashion, beauty, and wellness. Apps for lifestyle enhancement and personal development.",
        "order": 22,
    },
    {
        "name": "Art & Design",
        "slug": "art-design",
        "icon": "🎨",
        "icon_class": "fas fa-palette",
        "color": "#e74c3c",
        "description": "Create artwork, design graphics, and edit images. Professional design tools for artists and creators.",
        "order": 23,
    },
    {
        "name": "Medical",
        "slug": "medical",
        "icon": "⚕️",
        "icon_class": "fas fa-stethoscope",
        "color": "#e74c3c",
        "description": "Healthcare advice, medical records, and telemedicine services. Connect with doctors and health professionals.",
        "order": 24,
    },
    {
        "name": "Parenting & Kids",
        "slug": "parenting-kids",
        "icon": "👶",
        "icon_class": "fas fa-child",
        "color": "#f39c12",
        "description": "Educational games, parenting tips, and kid-friendly content. Safe apps designed for children and parents.",
        "order": 25,
    },
    {
        "name": "Weather",
        "slug": "weather",
        "icon": "🌤️",
        "icon_class": "fas fa-cloud-sun",
        "color": "#3498db",
        "description": "Real-time weather forecasts, alerts, and climate data. Plan your day with accurate weather information.",
        "order": 26,
    },
    {
        "name": "Dating & Romance",
        "slug": "dating-romance",
        "icon": "❤️",
        "icon_class": "fas fa-heart",
        "color": "#e74c3c",
        "description": "Meet new people and find your perfect match. Safe dating apps for meaningful connections.",
        "order": 27,
    },
    {
        "name": "Pets & Animals",
        "slug": "pets-animals",
        "icon": "🐕",
        "icon_class": "fas fa-paw",
        "color": "#d35400",
        "description": "Pet care tips, veterinary services, and pet communities. Connect with pet lovers everywhere.",
        "order": 28,
    },
    {
        "name": "DIY & Crafts",
        "slug": "diy-crafts",
        "icon": "🧵",
        "icon_class": "fas fa-hammer",
        "color": "#8e44ad",
        "description": "DIY tutorials, craft ideas, and creative projects. Learn to make something amazing at home.",
        "order": 29,
    },
    {
        "name": "Home & Garden",
        "slug": "home-garden",
        "icon": "🏡",
        "icon_class": "fas fa-home",
        "color": "#27ae60",
        "description": "Interior design, gardening tips, and home improvement. Transform your home with expert advice.",
        "order": 30,
    },
    {
        "name": "Podcasts",
        "slug": "podcasts",
        "icon": "🎙️",
        "icon_class": "fas fa-microphone",
        "color": "#2980b9",
        "description": "Listen to podcasts on any topic. Discover shows, subscribe, and enjoy premium audio content.",
        "order": 31,
    },
    {
        "name": "Audiobooks",
        "slug": "audiobooks",
        "icon": "🎧",
        "icon_class": "fas fa-headphones",
        "color": "#16a085",
        "description": "Listen to books narrated by professionals. Thousands of audiobooks from your favorite authors.",
        "order": 32,
    },
    {
        "name": "Comics",
        "slug": "comics",
        "icon": "💭",
        "icon_class": "fas fa-book-open",
        "color": "#c0392b",
        "description": "Read digital comics and graphic novels. New releases and classic series in high quality.",
        "order": 33,
    },
    {
        "name": "Anime & Manga",
        "slug": "anime-manga",
        "icon": "🎆",
        "icon_class": "fas fa-image",
        "color": "#9b59b6",
        "description": "Stream anime and read manga. Latest episodes and chapters with subtitles and translations.",
        "order": 34,
    },
    {
        "name": "Streaming Services",
        "slug": "streaming-services",
        "icon": "📡",
        "icon_class": "fas fa-broadcast-tower",
        "color": "#e67e22",
        "description": "Watch movies, series, and exclusive content. Premium streaming with 4K quality and offline viewing.",
        "order": 35,
    },
    {
        "name": "Security & Privacy",
        "slug": "security-privacy",
        "icon": "🔒",
        "icon_class": "fas fa-lock",
        "color": "#c0392b",
        "description": "VPN, password managers, and antivirus tools. Protect your data and privacy online effectively.",
        "order": 36,
    },
    {
        "name": "Cloud Storage",
        "slug": "cloud-storage",
        "icon": "☁️",
        "icon_class": "fas fa-cloud-upload-alt",
        "color": "#3498db",
        "description": "Store, sync, and share files securely. Access your documents from any device anytime.",
        "order": 37,
    },
    {
        "name": "Programming & Dev",
        "slug": "programming-dev",
        "icon": "💻",
        "icon_class": "fas fa-code",
        "color": "#2c3e50",
        "description": "Learn coding, develop apps, and share code. IDEs, compilers, and development tools for programmers.",
        "order": 38,
    },
    {
        "name": "Fitness Tracking",
        "slug": "fitness-tracking",
        "icon": "⌚",
        "icon_class": "fas fa-check-circle",
        "color": "#f39c12",
        "description": "Track workouts, calories, and daily activity. Wearable integration and personalized fitness plans.",
        "order": 39,
    },
    {
        "name": "Emergency & Safety",
        "slug": "emergency-safety",
        "icon": "🚨",
        "icon_class": "fas fa-exclamation-triangle",
        "color": "#e74c3c",
        "description": "Emergency alerts, safety apps, and disaster preparedness. Stay safe with real-time information.",
        "order": 40,
    },
]

print("🚀 CREATING 40 PRODUCTION-LEVEL CATEGORIES\n")
print("=" * 80)

created_count = 0
updated_count = 0
error_count = 0

for data in PRODUCTION_CATEGORIES:
    try:
        category, created = Category.objects.update_or_create(
            name=data["name"],
            defaults={
                "slug": data["slug"],
                "icon": data["icon"],
                "icon_class": data.get("icon_class", ""),
                "color": data["color"],
                "description": data["description"],
                "order": data["order"],
                "is_active": True,
            }
        )
        
        if created:
            status = "✅ CREATED"
            created_count += 1
        else:
            status = "🔄 UPDATED"
            updated_count += 1
        
        print(f"{status} | Order {data['order']:2d} | {category.icon} {category.name:22s} | {category.color}")
        
    except Exception as e:
        error_count += 1
        print(f"❌ ERROR   | {data['name']:25s} | {str(e)[:50]}")

print("=" * 80)
print(f"\n📊 FINAL SUMMARY:")
print(f"   ✅ Created:        {created_count} categories")
print(f"   🔄 Updated:        {updated_count} categories")
print(f"   ❌ Errors:         {error_count}")
print(f"   📈 Total in DB:    {Category.objects.count()}")
print(f"   🟢 Active:         {Category.objects.filter(is_active=True).count()}")

print(f"\n✨ PRODUCTION SETUP COMPLETE!")
print(f"   All 40 categories ready for production use")
print(f"   Django Admin:      /admin/ → Categories")
print(f"   Web Frontend:      /categories/ (List)")
print(f"   Web Frontend:      /categories/{{slug}}/ (Detail)")
print(f"   JSON API:          /categories/api/categories/")
print(f"   JSON API:          /categories/api/{{slug}}/apps/")
