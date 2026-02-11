from django.urls import path
from . import views

app_name = "categories"

urlpatterns = [
    # Web views
    path("", views.category_list, name="list"),
    path("<slug:slug>/", views.category_detail, name="detail"),
    
    # JSON API endpoints
    path("api/categories/", views.category_api, name="api_list"),
    path("api/<slug:slug>/apps/", views.category_apps_api, name="api_apps"),
]
