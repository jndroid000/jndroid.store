from django.conf import settings
from django.db import models
from categories.models import Category
from django.core.validators import MinValueValidator, MaxValueValidator

class App(models.Model):
    AGE_RATING_CHOICES = [
        ("3+", "3+ years"),
        ("7+", "7+ years"),
        ("12+", "12+ years"),
        ("16+", "16+ years"),
        ("18+", "18+ years"),
    ]

    # ==================== Basic Information ====================
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="apps",
        help_text="User who uploaded this app"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="apps",
        help_text="Category this app belongs to"
    )
    
    title = models.CharField(
        max_length=180,
        help_text="App name/title"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL-friendly version of the title"
    )
    short_description = models.CharField(
        max_length=220,
        blank=True,
        help_text="Brief description (1 line)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the app"
    )

    # ==================== Android Version Requirements ====================
    version = models.CharField(
        max_length=40,
        blank=True,
        help_text="Current app version (e.g., 1.0.0)"
    )
    size_mb = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text="APK size in megabytes"
    )
    min_api_level = models.IntegerField(
        default=21,
        help_text="Minimum Android API level required (21 = Android 5.0 Lollipop)"
    )
    target_api_level = models.IntegerField(
        default=35,
        help_text="Target Android API level (35 = Android 15 VanillaIceCream)"
    )
    
    # ==================== Android Details ====================
    min_android_version = models.CharField(
        max_length=10,
        default="5.0",
        help_text="Minimum Android version (e.g., 5.0, 6.0, 7.0)"
    )
    target_android_version = models.CharField(
        max_length=10,
        default="15.0",
        help_text="Target Android version (e.g., 13.0, 14.0, 15.0)"
    )

    # ==================== Media ====================
    cover_image = models.ImageField(
        upload_to="app_covers/",
        blank=True,
        null=True,
        help_text="App cover/thumbnail image"
    )
    
    # ==================== Download Options ====================
    apk_file = models.FileField(
        upload_to="apks/",
        blank=True,
        null=True,
        help_text="Direct APK file for download"
    )
    download_link = models.URLField(
        blank=True,
        help_text="External download link (Google Drive, etc)"
    )
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA256 hash of APK for verification"
    )
    
    # ==================== Developer Information ====================
    developer_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Developer/Publisher name"
    )
    developer_email = models.EmailField(
        blank=True,
        help_text="Developer email"
    )
    support_email = models.EmailField(
        blank=True,
        help_text="Support/Contact email"
    )
    website_url = models.URLField(
        blank=True,
        help_text="Developer website"
    )
    
    # ==================== Store Information ====================
    store_name = models.CharField(
        max_length=100,
        blank=True,
        default="JN App Store",
        help_text="Store name (for credits)"
    )
    store_email = models.EmailField(
        blank=True,
        help_text="Store contact email"
    )
    
    # ==================== Legal & Compliance ====================
    privacy_policy_url = models.URLField(
        blank=True,
        help_text="Privacy policy URL"
    )
    terms_url = models.URLField(
        blank=True,
        help_text="Terms of service URL"
    )

    # ==================== Monetization ====================
    is_free = models.BooleanField(
        default=True,
        help_text="Is this app free?"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Price in USD (if not free)"
    )
    has_iap = models.BooleanField(
        default=False,
        help_text="Has in-app purchases?"
    )
    
    # ==================== Content Classification ====================
    age_rating = models.CharField(
        max_length=10,
        choices=AGE_RATING_CHOICES,
        default="3+",
        help_text="Appropriate age rating"
    )
    
    # ==================== Metrics & Analytics ====================
    downloads = models.PositiveIntegerField(
        default=0,
        help_text="Total download count"
    )
    install_count = models.PositiveIntegerField(
        default=0,
        help_text="Estimated install count"
    )
    avg_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Average user rating (0-5)"
    )
    total_ratings = models.PositiveIntegerField(
        default=0,
        help_text="Total number of ratings"
    )
    
    # ==================== Source & Attribution ====================
    source_url = models.URLField(
        blank=True,
        help_text="Original source/home page of the app"
    )

    # ==================== Status ====================
    is_published = models.BooleanField(
        default=True,
        help_text="Is this app published/visible?"
    )
    is_pending_deletion = models.BooleanField(
        default=False,
        help_text="Marked for deletion?"
    )

    # ==================== Timestamps ====================
    release_date = models.DateField(
        auto_now_add=False,
        default='2026-01-29',
        help_text="Date when app was first published"
    )
    last_update_date = models.DateField(
        auto_now=True,
        help_text="Date of last update"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this listing was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last modified"
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "App"
        verbose_name_plural = "Apps"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['created_at']),
            models.Index(fields=['avg_rating']),
            models.Index(fields=['-downloads']),
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        return f"{self.title} (v{self.version})"
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('apps:detail', kwargs={'slug': self.slug})


class AppVersion(models.Model):
    """
    Track different versions of an app
    """
    app = models.ForeignKey(
        App,
        on_delete=models.CASCADE,
        related_name="versions",
        help_text="App this version belongs to"
    )
    version_number = models.CharField(
        max_length=40,
        help_text="Version number (e.g., 1.0.1)"
    )
    description = models.TextField(
        blank=True,
        help_text="What's new in this version"
    )
    size_mb = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="App size in megabytes"
    )
    download_link = models.URLField(
        blank=True,
        help_text="Download link for this version"
    )
    file_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA256 hash"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this version available for download?"
    )
    released_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Release date and time"
    )

    class Meta:
        ordering = ["-released_at"]
        verbose_name_plural = "App Versions"
        unique_together = ["app", "version_number"]

    def __str__(self):
        return f"{self.app.title} v{self.version_number}"
