from django.contrib import admin
from .models import LinkCategory, Link, LinkClick


@admin.register(LinkCategory)
class LinkCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category_type', 'order')
    list_filter = ('category_type', 'user')
    search_fields = ('name', 'user__username')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'url', 'click_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'user', 'created_at')
    search_fields = ('title', 'user__username', 'url')
    readonly_fields = ('click_count', 'created_at', 'updated_at')
    ordering = ('user', 'order')


@admin.register(LinkClick)
class LinkClickAdmin(admin.ModelAdmin):
    list_display = ('link', 'ip_address', 'clicked_at')
    list_filter = ('link', 'clicked_at')
    search_fields = ('link__title', 'ip_address')
    readonly_fields = ('link', 'ip_address', 'user_agent', 'clicked_at')
