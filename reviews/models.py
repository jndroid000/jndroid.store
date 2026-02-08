from django.conf import settings
from django.db import models
from apps.models import App

class Review(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")

    rating = models.PositiveSmallIntegerField(default=5)  # 1..5
    comment = models.TextField(blank=True)
    
    # Status fields
    is_approved = models.BooleanField(default=False)  # Auto-approved on app page
    is_flagged = models.BooleanField(default=False)   # Flagged for review
    
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("app", "user")  # one review per user per app

    def __str__(self):
        return f"{self.app.title} - {self.user.username} ({self.rating})"
