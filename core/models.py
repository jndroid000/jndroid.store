from django.db import models
from django.conf import settings
from django.utils import timezone


class AuditLog(models.Model):
    """Track all administrative actions for security and auditing"""
    
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('deactivate', 'Deactivated'),
        ('activate', 'Activated'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('flag', 'Flagged'),
        ('unflag', 'Unflagged'),
        ('export', 'Exported'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('permission_change', 'Permission Changed'),
        ('other', 'Other'),
    ]
    
    OBJECT_TYPE_CHOICES = [
        ('user', 'User'),
        ('app', 'App'),
        ('category', 'Category'),
        ('review', 'Review'),
        ('link', 'Link'),
        ('settings', 'Settings'),
        ('content', 'Content'),
    ]
    
    # Who did the action
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions',
        help_text="The admin/staff who performed the action"
    )
    
    # What action was done
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text="Type of action performed"
    )
    
    # What object was affected
    object_type = models.CharField(
        max_length=20,
        choices=OBJECT_TYPE_CHOICES,
        help_text="Type of object affected"
    )
    object_id = models.IntegerField(
        help_text="ID of the object affected"
    )
    object_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name/identifier of the affected object"
    )
    
    # What changed
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Details of what was changed (optional)"
    )
    
    # When it happened
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the action was performed"
    )
    
    # IP and User Agent for security
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of the admin"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Browser/client information"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['admin_user', '-timestamp']),
            models.Index(fields=['object_type', 'object_id']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.action} {self.object_type} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    @classmethod
    def log_action(cls, admin_user, action, object_type, object_id, object_name="", details=None, ip_address="", user_agent=""):
        """Helper method to create an audit log entry"""
        return cls.objects.create(
            admin_user=admin_user,
            action=action,
            object_type=object_type,
            object_id=object_id,
            object_name=object_name,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
