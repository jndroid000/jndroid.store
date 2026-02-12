from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Display audit logs in Django admin"""
    list_display = ['admin_user', 'action', 'object_type', 'object_name', 'timestamp']
    list_filter = ['action', 'object_type', 'timestamp', 'admin_user']
    search_fields = ['object_name', 'admin_user__username', 'details']
    readonly_fields = ['admin_user', 'action', 'object_type', 'object_id', 'timestamp', 'ip_address', 'user_agent', 'details']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs (important for compliance)"""
        return False

