from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    email_verified = models.BooleanField(default=False, help_text="Email address verified")
    
    # Account deletion fields
    is_pending_deletion = models.BooleanField(default=False, help_text="Account is pending deletion")
    deletion_requested_at = models.DateTimeField(null=True, blank=True, help_text="When deletion was requested")
    deletion_scheduled_at = models.DateTimeField(null=True, blank=True, help_text="When account will be deleted (3 days after request)")
    
    class Meta:
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['email_verified']),
            models.Index(fields=['is_pending_deletion']),
        ]

    def __str__(self):
        return self.username
    
    def get_deletion_countdown_days(self):
        """Get remaining days before account deletion"""
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.is_pending_deletion or not self.deletion_scheduled_at:
            return None
        
        remaining = self.deletion_scheduled_at - timezone.now()
        if remaining.total_seconds() <= 0:
            return 0
        
        return remaining.days
    
    def get_deletion_countdown_hours(self):
        """Get remaining hours before account deletion"""
        from django.utils import timezone
        
        if not self.is_pending_deletion or not self.deletion_scheduled_at:
            return None
        
        remaining = self.deletion_scheduled_at - timezone.now()
        if remaining.total_seconds() <= 0:
            return 0
        
        return int(remaining.total_seconds() // 3600)


class PasswordResetOTP(models.Model):
    """Model to store OTP for password reset"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='password_reset_otp')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)

    class Meta:
        verbose_name = "Password Reset OTP"
        verbose_name_plural = "Password Reset OTPs"

    def __str__(self):
        return f"OTP for {self.user.username}"

    @staticmethod
    def generate_otp():
        """Generate a 6-digit random OTP"""
        return ''.join(random.choices(string.digits, k=6))

    def is_expired(self):
        """Check if OTP has expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def is_locked(self):
        """Check if user has exceeded max attempts"""
        return self.attempts >= self.max_attempts

    def increment_attempts(self):
        """Increment failed attempt counter"""
        self.attempts += 1
        self.save()


class AccountDeletionOTP(models.Model):
    """Model to store OTP for account deletion verification"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='deletion_otp')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=5)

    class Meta:
        verbose_name = "Account Deletion OTP"
        verbose_name_plural = "Account Deletion OTPs"

    def __str__(self):
        return f"Deletion OTP for {self.user.username}"

    @staticmethod
    def generate_otp():
        """Generate a 6-digit random OTP"""
        return ''.join(random.choices(string.digits, k=6))

    def is_expired(self):
        """Check if OTP has expired"""
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def is_locked(self):
        """Check if user has exceeded max attempts"""
        return self.attempts >= self.max_attempts

    def increment_attempts(self):
        """Increment failed attempt counter"""
        self.attempts += 1
        self.save()
