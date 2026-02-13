from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("email-verification-sent/", views.email_verification_sent, name="email-verification-sent"),
    path("confirm-email/<str:key>/", views.email_confirmation_view, name="email_confirmation"),
    path("resend-verification/", views.resend_verification_email, name="resend_verification"),
    path("profile/", views.profile_view, name="profile"),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),
    path("settings/", views.settings_view, name="settings"),
    
    # Account Deletion URLs
    path("delete-account/", views.delete_account_request_view, name="delete_account_request"),
    path("delete-account/verify-otp/", views.verify_delete_otp_view, name="verify_delete_otp"),
    path("delete-account/confirm/", views.confirm_delete_view, name="confirm_delete"),
    path("delete-account/cancel/", views.cancel_delete_account_view, name="cancel_delete"),
    
    # Password Reset URLs
    path("password-reset/", views.password_reset_view, name="password_reset"),
    path("password-reset/verify-otp/<str:email>/", views.password_reset_verify_otp_view, name="password_reset_verify_otp"),
    path("password-reset/new-password/<str:email>/", views.password_reset_new_password_view, name="password_reset_new_password"),
]
