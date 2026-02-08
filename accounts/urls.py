from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("email-verification-sent/", views.email_verification_sent, name="email-verification-sent"),
    path("confirm-email/<str:key>/", views.email_confirmation_view, name="email_confirmation"),
    path("profile/", views.profile_view, name="profile"),
    path("edit-profile/", views.edit_profile_view, name="edit_profile"),
]
