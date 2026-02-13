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
    
    # Password Reset URLs
    path("password-reset/", views.password_reset_view, name="password_reset"),
    path("password-reset/verify-otp/<str:email>/", views.password_reset_verify_otp_view, name="password_reset_verify_otp"),
    path("password-reset/new-password/<str:email>/", views.password_reset_new_password_view, name="password_reset_new_password"),
]
