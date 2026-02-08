from django.urls import path
from core import views

app_name = "admin_panel"

urlpatterns = [
    # Dashboard
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # Apps Management
    path("apps/", views.apps_list, name="apps_list"),
    path("apps/pending/", views.apps_pending, name="apps_pending"),
    path("apps/<slug:slug>/", views.app_detail, name="app_detail"),
    path("apps/<slug:slug>/edit/", views.apps_edit, name="apps_edit"),
    
    # Users Management
    path("users/", views.users_list, name="users_list"),
    path("users/create/", views.users_create, name="users_create"),
    path("users/<int:pk>/edit/", views.users_edit, name="users_edit"),
    
    # Categories Management
    path("categories/", views.categories_list, name="categories_list"),
    path("categories/create/", views.categories_create, name="categories_create"),
    path("categories/<int:pk>/edit/", views.categories_edit, name="categories_edit"),
    path("categories/<int:pk>/delete/", views.categories_delete, name="categories_delete"),
    
    # Reviews Management
    path("reviews/", views.reviews_list, name="reviews_list"),
    path("reviews/flagged/", views.reviews_flagged, name="reviews_flagged"),
    path("reviews/approved/", views.reviews_approved, name="reviews_approved"),
    path("reviews/<int:pk>/delete/", views.reviews_delete, name="reviews_delete"),
    path("reviews/<int:pk>/flag/", views.reviews_flag, name="reviews_flag"),
    path("reviews/<int:pk>/approve/", views.reviews_approve, name="reviews_approve"),
    
    # Analytics
    path("analytics/", views.analytics_overview, name="analytics_overview"),
    path("analytics/reports/", views.analytics_reports, name="analytics_reports"),
    
    # Settings
    path("settings/", views.settings, name="settings"),
    path("moderation/", views.moderation, name="moderation"),
    
    # Pending Deletions
    path("pending-deletions/", views.pending_deletions, name="pending_deletions"),
    path("apps/<slug:slug>/mark-for-deletion/", views.mark_app_for_deletion, name="mark_app_for_deletion"),
    path("apps/<slug:slug>/approve-deletion/", views.approve_deletion, name="approve_deletion"),
    path("apps/<slug:slug>/cancel-deletion/", views.cancel_deletion, name="cancel_deletion"),
]

