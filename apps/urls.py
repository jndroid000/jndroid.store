from django.urls import path
from . import views

app_name = "apps"

urlpatterns = [
    path("", views.app_list, name="list"),
    path("upload/", views.app_upload, name="upload"),
    path("my-apps/", views.my_apps, name="my_apps"),
    path("<slug:slug>/", views.app_detail, name="detail"),
    path("<slug:slug>/edit/", views.app_edit, name="edit"),
    path("<slug:slug>/download/", views.app_download, name="download"),
]
