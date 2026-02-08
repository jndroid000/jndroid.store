from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("app", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("app__title", "user__username")
