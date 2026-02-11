from django.contrib import admin
from .models import App, AppVersion

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "platform", "version", "is_published", "avg_rating", "downloads", "created_at")
    list_filter = ("platform", "is_published", "category", "is_free", "age_rating")
    search_fields = ("title", "slug", "developer_name", "developer_email")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("downloads", "created_at", "updated_at", "release_date")
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("title", "slug", "short_description", "description", "category", "owner")
        }),
        ("Media", {
            "fields": ("cover_image",)
        }),
        ("Platform & Version", {
            "fields": ("platform", "version", "size_mb", "min_api_level", "target_api_level")
        }),
        ("Download Options", {
            "fields": ("apk_file", "download_link", "file_hash")
        }),
        ("Developer Information", {
            "fields": ("developer_name", "developer_email", "support_email", "website_url")
        }),
        ("Legal & Compliance", {
            "fields": ("privacy_policy_url", "terms_url", "age_rating")
        }),
        ("Monetization", {
            "fields": ("is_free", "price", "has_iap")
        }),
        ("Metrics & Analytics", {
            "fields": ("downloads", "install_count", "avg_rating", "total_ratings")
        }),
        ("Content & Attribution", {
            "fields": ("source_url", "store_name", "store_email")
        }),
        ("Status & Dates", {
            "fields": ("is_published", "is_pending_deletion", "release_date", "created_at", "updated_at")
        }),
    )


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ("app", "version_number", "size_mb", "is_active", "released_at")
    list_filter = ("app", "is_active", "released_at")
    search_fields = ("app__title", "version_number")
    ordering = ("-released_at",)
