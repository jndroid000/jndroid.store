from django.urls import path
from . import views
from .views_ledger import app_ledger_view, app_ledger_export, app_info_sheet

app_name = "apps"

urlpatterns = [
    path("", views.app_list, name="list"),
    path("upload/", views.app_upload, name="upload"),
    path("my-apps/", views.my_apps, name="my_apps"),
    path("ledger/", app_ledger_view, name="ledger"),
    path("ledger/export/", app_ledger_export, name="ledger_export"),
    path("info/<slug:slug>/", app_info_sheet, name="info_sheet"),
    path("<slug:slug>/", views.app_detail, name="detail"),
    path("<slug:slug>/edit/", views.app_edit, name="edit"),
    path("<slug:slug>/delete/", views.app_delete, name="delete"),
    path("<slug:slug>/download/", views.app_download, name="download"),
]
