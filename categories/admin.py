from django.contrib import admin
from django.db.models import Count
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "slug", "get_app_count", "is_active")
    list_filter = ("is_active", "name")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "icon")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
    )
    
    readonly_fields = ("get_app_count",)
    
    def get_queryset(self, request):
        """Optimize queryset by annotating app count"""
        queryset = super().get_queryset(request)
        return queryset.annotate(app_count=Count("apps"))
    
    def get_app_count(self, obj):
        """Display the number of apps in this category"""
        return obj.app_count
    get_app_count.short_description = "Total Apps"
    get_app_count.admin_order_field = "app_count"
