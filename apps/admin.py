from django.contrib import admin
from .models import App, AppVersion

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "platform", "version", "is_published", "downloads", "created_at")
    list_filter = ("platform", "is_published", "category")
    search_fields = ("title", "slug", "version")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ("app", "version_number", "size_mb", "is_active", "released_at")
    list_filter = ("app", "is_active", "released_at")
    search_fields = ("app__title", "version_number")
    ordering = ("-released_at",)
