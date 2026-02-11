from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    """
    Category model for organizing apps.
    """
    ICON_CHOICES = [
        ("📱", "Mobile"),
        ("🎮", "Games"),
        ("📚", "Books & Reference"),
        ("🎵", "Music & Audio"),
        ("📹", "Video Players"),
        ("📷", "Photography"),
        ("🛒", "Shopping"),
        ("🍔", "Food & Drink"),
        ("🏋️", "Health & Fitness"),
        ("🏠", "Lifestyle"),
        ("📰", "News & Magazines"),
        ("🎨", "Art & Design"),
        ("🎓", "Education"),
        ("💼", "Business"),
        ("🛠️", "Tools"),
        ("⚙️", "Utilities"),
        ("🌐", "Communication"),
        ("🔒", "Security"),
        ("🎬", "Entertainment"),
        ("📊", "Productivity"),
        ("🚗", "Travel & Local"),
        ("⚽", "Sports"),
        ("🏥", "Medical"),
        ("👶", "Family"),
    ]
    
    name = models.CharField(
        max_length=120, 
        unique=True,
        help_text="Category name (e.g., Games, Business, Education)"
    )
    slug = models.SlugField(
        max_length=140, 
        unique=True,
        help_text="URL-friendly version of the category name"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of this category"
    )
    icon = models.CharField(
        max_length=10,
        choices=ICON_CHOICES,
        default="📱",
        help_text="Emoji or icon representing this category"
    )
    icon_class = models.CharField(
        max_length=60,
        blank=True,
        help_text="CSS class for icon (e.g., 'fas fa-gamepad')"
    )
    color = models.CharField(
        max_length=7,
        default="#3498db",
        help_text="Hex color for category (e.g., #3498db)"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order in listings"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is visible to users"
    )

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Categories"
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.icon} {self.name}"
    
    def save(self, *args, **kwargs):
        # Auto-generate slug from name if not provided
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
