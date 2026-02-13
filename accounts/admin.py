from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AccountDeletionOTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin with email verification status and account deletion tracking"""
    list_display = ['username', 'email', 'is_active', 'email_verified', 'is_pending_deletion', 'date_joined']
    list_filter = ['is_active', 'email_verified', 'is_pending_deletion', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone', 'avatar', 'email_verified')
        }),
        ('Account Deletion', {
            'fields': ('is_pending_deletion', 'deletion_requested_at', 'deletion_scheduled_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login', 'deletion_requested_at', 'deletion_scheduled_at']


@admin.register(AccountDeletionOTP)
class AccountDeletionOTPAdmin(admin.ModelAdmin):
    """Admin for managing account deletion OTP requests"""
    list_display = ['user', 'is_verified', 'attempts', 'created_at', 'expires_at']
    list_filter = ['is_verified', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'otp']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'otp')
        }),
        ('Verification Status', {
            'fields': ('is_verified', 'attempts', 'max_attempts')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at')
        }),
    )
