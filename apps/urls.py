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
    path("api/popular-apps/", views.popular_apps_api, name="popular_apps_api"),
    path("api/search/", views.search_api, name="search_api"),
    path("<slug:slug>/", views.app_detail, name="detail"),
    path("<slug:slug>/edit/", views.app_edit, name="edit"),
    path("<slug:slug>/delete/", views.app_delete, name="delete"),
    path("<slug:slug>/download/", views.app_download, name="download"),
    path("<slug:slug>/takedown-request/", views.app_takedown_request, name="takedown_request"),
    path("<slug:slug>/copyright-status/", views.app_copyright_status, name="copyright_status"),
    path("<slug:slug>/report-infringement/", views.app_report_infringement, name="report_infringement"),
    path("<slug:slug>/copyright-check/", views.app_copyright_check, name="copyright_check"),
]

