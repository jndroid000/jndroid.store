"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from core.views import home, support, community_guidelines, report_bug, terms_of_service

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('support/', support, name='support'),
    path('community-guidelines/', community_guidelines, name='community_guidelines'),
    path('report-bug/', report_bug, name='report_bug'),
    path('terms-of-service/', terms_of_service, name='terms_of_service'),

    path('admin-panel/', include('core.urls')),  # Admin dashboard
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.account.urls')),  # django-allauth email verification
    path('categories/', include('categories.urls')),
    path('apps/', include('apps.urls')),
    path('reviews/', include('reviews.urls')),
]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
