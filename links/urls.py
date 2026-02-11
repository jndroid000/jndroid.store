from django.urls import path
from . import views

app_name = 'links'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.link_dashboard, name='dashboard'),
    path('all/', views.view_all_links, name='all_links'),
    path('active/', views.view_active_links, name='active_links'),
    
    # CRUD operations
    path('create/', views.link_create, name='create'),
    path('<int:link_id>/edit/', views.link_edit, name='edit'),
    path('<int:link_id>/delete/', views.link_delete, name='delete'),
    
    # Export functionality
    path('export/json/', views.export_links_json, name='export_json'),
    path('export/csv/', views.export_links_csv, name='export_csv'),
    
    # Public profiles
    path('@<str:username>/', views.public_link_profile, name='public_profile'),
    path('go/<int:link_id>/', views.link_redirect, name='redirect'),
]
