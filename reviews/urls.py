from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("add/<slug:app_slug>/", views.add_review, name="add"),
]
