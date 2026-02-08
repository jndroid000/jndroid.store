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

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="apps")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="apps")

    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    short_description = models.CharField(max_length=220, blank=True)
    description = models.TextField(blank=True)

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES, default="android")
    version = models.CharField(max_length=40, blank=True)
    size_mb = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    cover_image = models.ImageField(upload_to="app_covers/", blank=True, null=True)
    apk_file = models.FileField(upload_to="apks/", blank=True, null=True)  # optional
    download_link = models.URLField(blank=True)  # external link (drive/pixeldrain)
    store_name = models.CharField(max_length=100, blank=True, default="JN App Store")  # e.g., Google Play, App Store
    store_email = models.EmailField(blank=True)  # store/developer email

    is_published = models.BooleanField(default=True)
    is_pending_deletion = models.BooleanField(default=False)
    downloads = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


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
