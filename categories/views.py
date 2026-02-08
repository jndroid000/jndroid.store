from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Category
from apps.models import App


def category_list(request):
    categories = (
        Category.objects.filter(is_active=True)
        .annotate(app_count=Count("apps"))
        .order_by("name")
    )
    return render(request, "categories/category_list.html", {"categories": categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    apps = App.objects.filter(is_published=True, category=category).select_related("owner", "category")
    return render(request, "categories/category_detail.html", {"category": category, "apps": apps})
