from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with email verification status"""
    list_display = ['username', 'email', 'is_active', 'email_verified', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'email_verified', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone', 'avatar', 'email_verified')
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']

