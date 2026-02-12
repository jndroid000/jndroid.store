from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse


class LinkCategory(models.Model):
    """Categories for organizing links"""
    CATEGORY_CHOICES = [
        ('social', 'Social Media'),
        ('portfolio', 'Portfolio'),
        ('download', 'Download Links'),
        ('resource', 'Resources'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='link_categories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    icon = models.CharField(max_length=50, blank=True, help_text='Font Awesome icon class (e.g., fa-github)')
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ('user', 'slug')
        ordering = ['order', 'name']
        verbose_name_plural = 'Link Categories'
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Link(models.Model):
    """User links management"""
    ICON_CHOICES = [
        ('fa-link', 'Generic Link'),
        ('fa-github', 'GitHub'),
        ('fa-twitter', 'Twitter'),
        ('fa-facebook', 'Facebook'),
        ('fa-instagram', 'Instagram'),
        ('fa-linkedin', 'LinkedIn'),
        ('fa-youtube', 'YouTube'),
        ('fa-globe', 'Website'),
        ('fa-envelope', 'Email'),
        ('fa-download', 'Download'),
        ('fa-code', 'Code'),
        ('fa-book', 'Documentation'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='links')
    category = models.ForeignKey(LinkCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='links')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    url = models.URLField()
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='fa-link')
    
    # Analytics
    click_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Ordering
    order = models.PositiveIntegerField(default=0)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def get_icon_class(self):
        """Get Font Awesome icon class"""
        return f"fas {self.icon}"
    
    def get_absolute_url(self):
        """Get the click redirect URL for this link"""
        return reverse('links:redirect', kwargs={'link_id': self.id})


class LinkClick(models.Model):
    """Track link clicks for analytics"""
    link = models.ForeignKey(Link, on_delete=models.CASCADE, related_name='clicks')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['link', 'clicked_at']),
        ]
    
    def __str__(self):
        return f"{self.link.title} - {self.clicked_at}"
