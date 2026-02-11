from django.conf import settings
from django.db import models
from categories.models import Category

class App(models.Model):
    PLATFORM_CHOICES = [
        ("android", "Android"),
        ("windows", "Windows"),
        ("ios", "iOS"),
        ("web", "Web"),
    ]
    
    AGE_RATING_CHOICES = [
        ("3+", "3+ years"),
        ("7+", "7+ years"),
        ("12+", "12+ years"),
        ("16+", "16+ years"),
        ("18+", "18+ years"),
    ]

    # Basic Info
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="apps")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="apps")
    
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.CharField(max_length=220, blank=True)
    description = models.TextField(blank=True)

    # Platform & Version
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default="android")
    version = models.CharField(max_length=40, blank=True)
    size_mb = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    # Android-specific (Optional)
    min_api_level = models.IntegerField(default=21, help_text="Minimum Android API level")
    target_api_level = models.IntegerField(default=35, help_text="Target Android API level")

    # Media
    cover_image = models.ImageField(upload_to="app_covers/", blank=True, null=True)
    
    # Download Options
    apk_file = models.FileField(upload_to="apks/", blank=True, null=True, help_text="Direct APK file")
    download_link = models.URLField(blank=True, help_text="External download link (Google Drive, etc)")
    file_hash = models.CharField(max_length=64, blank=True, help_text="SHA256 hash of APK for verification")
    
    # Developer Information
    developer_name = models.CharField(max_length=120, blank=True, help_text="Developer/Publisher name")
    developer_email = models.EmailField(blank=True, help_text="Developer email")
    support_email = models.EmailField(blank=True, help_text="Support/Contact email")
    website_url = models.URLField(blank=True, help_text="Developer website")
    
    # Legacy fields (for backward compatibility)
    store_name = models.CharField(max_length=100, blank=True, default="JN App Store")
    store_email = models.EmailField(blank=True)
    
    # Legal & Compliance
    privacy_policy_url = models.URLField(blank=True, help_text="Privacy policy URL")
    terms_url = models.URLField(blank=True, help_text="Terms of service URL")

    # Monetization
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price in USD (if not free)")
    has_iap = models.BooleanField(default=False, help_text="Has in-app purchases")
    
    # Content Classification
    age_rating = models.CharField(max_length=10, choices=AGE_RATING_CHOICES, default="3+")
    
    # Metrics & Analytics
    downloads = models.PositiveIntegerField(default=0)
    install_count = models.PositiveIntegerField(default=0, help_text="Estimated install count")
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, help_text="Average user rating (0-5)")
    total_ratings = models.PositiveIntegerField(default=0, help_text="Total number of ratings")
    
    # Source & Attribution
    source_url = models.URLField(blank=True, help_text="Original source/home page of the app")

    # Status
    is_published = models.BooleanField(default=True)
    is_pending_deletion = models.BooleanField(default=False)

    # Timestamps
    release_date = models.DateField(auto_now_add=False, default='2026-01-29', help_text="Date when app was first published")
    last_update_date = models.DateField(auto_now=True, help_text="Date of last update")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['platform']),
            models.Index(fields=['created_at']),
            models.Index(fields=['avg_rating']),
            models.Index(fields=['-downloads']),
        ]

    def __str__(self):
        return self.title
    
    def get_rating_display(self):
        """Return formatted rating (e.g., '4.5 out of 5')"""
        if self.total_ratings == 0:
            return "No ratings yet"
        return f"{self.avg_rating:.1f}/5.0 ({self.total_ratings} ratings)"


class AppVersion(models.Model):
    """Store version history for apps"""
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name="versions")
    version_number = models.CharField(max_length=40)
    description = models.TextField(blank=True)
    size_mb = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    apk_file = models.FileField(upload_to="apks/", blank=True, null=True)
    download_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    released_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-released_at"]
        unique_together = ("app", "version_number")

    def __str__(self):
        return f"{self.app.title} - v{self.version_number}"
