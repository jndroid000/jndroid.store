from django.contrib import admin
from django.db.models import Count, Avg
from .models import App, AppVersion

@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "version",
        "get_rating_display",
        "get_downloads",
        "is_published",
        "created_at"
    )
    list_filter = (
        "is_published",
        "category",
        "is_free",
        "age_rating",
        "created_at"
    )
    search_fields = (
        "title",
        "slug",
        "developer_name",
        "developer_email",
        "category__name"
    )
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = (
        "downloads",
        "created_at",
        "updated_at",
        "release_date",
        "get_total_reviews"
    )
    
    fieldsets = (
        ("📱 Basic Information", {
            "fields": ("title", "slug", "category", "owner", "short_description", "description")
        }),
        ("🖼️ Media", {
            "fields": ("cover_image",)
        }),
        ("🤖 Android Version Requirements", {
            "fields": ("version", "size_mb", "min_api_level", "target_api_level", "min_android_version", "target_android_version")
        }),
        ("⬇️ Download Options", {
            "fields": ("apk_file", "download_link", "file_hash")
        }),
        ("👨‍💼 Developer Information", {
            "fields": ("developer_name", "developer_email", "support_email", "website_url")
        }),
        ("🏪 Store Information", {
            "fields": ("store_name", "store_email")
        }),
        ("⚖️ Legal & Compliance", {
            "fields": ("privacy_policy_url", "terms_url", "age_rating")
        }),
        ("💰 Monetization", {
            "fields": ("is_free", "price", "has_iap")
        }),
        ("📊 Metrics & Analytics", {
            "fields": ("downloads", "install_count", "avg_rating", "total_ratings", "get_total_reviews")
        }),
        ("🔗 Content & Attribution", {
            "fields": ("source_url",)
        }),
        ("✅ Status & Dates", {
            "fields": ("is_published", "is_pending_deletion", "release_date", "created_at", "updated_at")
        }),
    )
    
    actions = ["publish_apps", "unpublish_apps", "mark_for_deletion"]
    
    def get_queryset(self, request):
        """Optimize queryset"""
        queryset = super().get_queryset(request)
        return queryset.select_related("category", "owner")
    
    def get_rating_display(self, obj):
        """Display rating with star emoji"""
        if obj.total_ratings == 0:
            return "No ratings"
        return f"⭐ {obj.avg_rating:.1f} ({obj.total_ratings})"
    get_rating_display.short_description = "Rating"
    get_rating_display.admin_order_field = "avg_rating"
    
    def get_downloads(self, obj):
        """Format downloads nicely"""
        return f"📥 {obj.downloads:,}"
    get_downloads.short_description = "Downloads"
    get_downloads.admin_order_field = "downloads"
    
    def get_total_reviews(self, obj):
        """Get total reviews from related reviews"""
        from reviews.models import Review
        count = Review.objects.filter(app=obj).count()
        return count
    get_total_reviews.short_description = "Total Reviews"
    
    @admin.action(description="✅ Publish selected apps")
    def publish_apps(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(request, f"{updated} app(s) published.")
    
    @admin.action(description="❌ Unpublish selected apps")
    def unpublish_apps(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"{updated} app(s) unpublished.")
    
    @admin.action(description="🗑️ Mark selected for deletion")
    def mark_for_deletion(self, request, queryset):
        updated = queryset.update(is_pending_deletion=True)
        self.message_user(request, f"{updated} app(s) marked for deletion.")


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = (
        "app",
        "version_number",
        "size_mb",
        "is_active",
        "released_at"
    )
    list_filter = (
        "app",
        "is_active",
        "released_at"
    )
    search_fields = (
        "app__title",
        "version_number"
    )
    readonly_fields = ("released_at",)
    ordering = ("-released_at",)
    
    fieldsets = (
        ("📱 Version Info", {
            "fields": ("app", "version_number")
        }),
        ("📝 Details", {
            "fields": ("description", "size_mb")
        }),
        ("⬇️ Download", {
            "fields": ("download_link", "file_hash")
        }),
        ("✅ Status", {
            "fields": ("is_active", "released_at")
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset"""
        queryset = super().get_queryset(request)
        return queryset.select_related("app")
    
