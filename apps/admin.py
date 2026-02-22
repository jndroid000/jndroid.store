from django.contrib import admin
from django.db.models import Count, Avg
from .models import (
    App, AppVersion, AppScreenshot, CopyrightClaim, 
    CopyrightInfringementReport, CopyrightDisputeResolution, CopyrightVerificationToken
)


class AppScreenshotInline(admin.TabularInline):
    model = AppScreenshot
    extra = 3
    fields = ('image', 'caption', 'order')
    ordering = ('order',)


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    inlines = [AppScreenshotInline]
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


@admin.register(AppScreenshot)
class AppScreenshotAdmin(admin.ModelAdmin):
    list_display = ('app', 'order', 'caption', 'created_at')
    list_filter = ('app', 'created_at')
    search_fields = ('app__title', 'caption')
    ordering = ('app', 'order')
    
    fieldsets = (
        (None, {
            'fields': ('app', 'image')
        }),
        ('Details', {
            'fields': ('caption', 'order')
        }),
        ('Info', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)


@admin.register(CopyrightClaim)
class CopyrightClaimAdmin(admin.ModelAdmin):
    """Admin interface for managing DMCA and copyright claims"""
    list_display = (
        "app",
        "get_claim_type_display",
        "status",
        "claimant_name",
        "submitted_at",
        "reviewed_at",
    )
    list_filter = (
        "claim_type",
        "status",
        "submitted_at",
        "reviewed_at",
    )
    search_fields = (
        "app__title",
        "claimant_name",
        "claimant_email",
        "description",
    )
    readonly_fields = (
        "submitted_at",
        "reviewed_at",
        "resolved_at",
    )
    
    fieldsets = (
        ("Claim Information", {
            "fields": ("app", "claim_type", "status")
        }),
        ("Claimant Details", {
            "fields": ("claimant_name", "claimant_email", "claimant_address")
        }),
        ("Description", {
            "fields": ("description", "reason", "evidence_url")
        }),
        ("Admin Review", {
            "fields": ("admin_notes", "action_taken")
        }),
        ("Timestamps", {
            "fields": ("submitted_at", "reviewed_at", "resolved_at"),
            "classes": ("collapse",)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make certain fields read-only after submission"""
        if obj:
            return self.readonly_fields + ("app", "claim_type", "claimant_name", "claimant_email", "claimant_address", "description", "reason", "evidence_url")
        return self.readonly_fields


@admin.register(CopyrightInfringementReport)
class CopyrightInfringementReportAdmin(admin.ModelAdmin):
    """Admin for managing copyright infringement reports"""
    list_display = (
        "app",
        "title",
        "reporter_name",
        "status",
        "submitted_at",
    )
    list_filter = (
        "status",
        "submitted_at",
    )
    search_fields = (
        "app__title",
        "reporter_name",
        "reporter_email",
        "title",
    )
    readonly_fields = (
        "submitted_at",
        "reviewed_at",
        "resolved_at",
    )
    
    fieldsets = (
        ("App Information", {
            "fields": ("app",)
        }),
        ("Reporter Details", {
            "fields": ("reporter_name", "reporter_email")
        }),
        ("Report Details", {
            "fields": ("title", "description", "evidence_description")
        }),
        ("Original Work", {
            "fields": ("original_app_name", "original_app_url")
        }),
        ("Review", {
            "fields": ("status", "admin_notes")
        }),
        ("Timestamps", {
            "fields": ("submitted_at", "reviewed_at", "resolved_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(CopyrightDisputeResolution)
class CopyrightDisputeResolutionAdmin(admin.ModelAdmin):
    """Admin for managing copyright disputes"""
    list_display = (
        "app",
        "resolution_status",
        "assigned_to",
        "created_at",
    )
    list_filter = (
        "resolution_status",
        "created_at",
        "assigned_to",
    )
    search_fields = (
        "app__title",
        "description",
        "resolution_terms",
    )
    readonly_fields = (
        "created_at",
        "resolved_at",
    )
    
    fieldsets = (
        ("Dispute Information", {
            "fields": ("app", "copyright_claim", "description")
        }),
        ("Resolution", {
            "fields": ("resolution_status", "resolution_terms", "last_communication")
        }),
        ("Administration", {
            "fields": ("assigned_to",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "resolved_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(CopyrightVerificationToken)
class CopyrightVerificationTokenAdmin(admin.ModelAdmin):
    """Admin for managing copyright verification tokens"""
    list_display = (
        "app",
        "email",
        "is_verified",
        "created_at",
        "expires_at",
    )
    list_filter = (
        "is_verified",
        "created_at",
        "expires_at",
    )
    search_fields = (
        "app__title",
        "email",
        "token",
    )
    readonly_fields = (
        "token",
        "created_at",
        "verified_at",
    )
    
    fieldsets = (
        ("Token Information", {
            "fields": ("app", "token", "email")
        }),
        ("Verification", {
            "fields": ("is_verified", "attempts")
        }),
        ("Timestamps", {
            "fields": ("created_at", "verified_at", "expires_at"),
            "classes": ("collapse",)
        }),
    )
