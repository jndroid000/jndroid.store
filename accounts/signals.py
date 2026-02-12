"""
Django signals for accounts app
Handles email verification, account activation, etc.
"""
from django.dispatch import receiver
from allauth.account.signals import email_confirmed
from django.contrib.auth import login
from django.http import HttpRequest


@receiver(email_confirmed)
def email_confirmed_handler(sender, request, email_address, **kwargs):
    """
    Handle email confirmation - auto-login user and activate account
    """
    user = email_address.user
    
    # Mark email as verified
    email_address.verified = True
    email_address.save()
    
    # Activate user account
    user.is_active = True
    user.save()
    
    # Auto-login user if request is available
    if request:
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
