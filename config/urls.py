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
from django.views.generic import TemplateView
from core import views

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
    path('links/', include('links.urls')),  # Link management
    path('reviews/', include('reviews.urls')),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('dmca-takedown/', TemplateView.as_view(template_name='dmca_takedown.html'), name='dmca_takedown'),
    path('dmca-takedown/submit/', views.submit_dmca_notice, name='submit_dmca_notice'),
    path('dmca-success/', views.dmca_success, name='dmca_success'),
]
from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
