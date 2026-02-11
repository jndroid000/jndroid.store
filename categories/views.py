from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Category
from apps.models import App


def category_list(request):
    """
    Display all active categories with app counts
    """
    categories = (
        Category.objects
        .filter(is_active=True)
        .annotate(app_count=Count("apps", filter=Q(apps__is_published=True)))
        .order_by("order", "name")
    )
    
    context = {
        "categories": categories,
        "total_categories": categories.count(),
    }
    return render(request, "categories/category_list.html", context)


def category_detail(request, slug):
    """
    Display a specific category and all its published apps
    """
    category = get_object_or_404(
        Category.objects.annotate(app_count=Count("apps", filter=Q(apps__is_published=True))),
        slug=slug,
        is_active=True
    )
    
    apps = (
        App.objects
        .filter(is_published=True, category=category)
        .select_related("owner", "category")
        .order_by("-downloads", "-avg_rating")
    )
    
    context = {
        "category": category,
        "apps": apps,
        "total_apps": apps.count(),
    }
    return render(request, "categories/category_detail.html", context)


@require_http_methods(["GET"])
def category_api(request):
    """
    JSON API endpoint for categories
    """
    categories = (
        Category.objects
        .filter(is_active=True)
        .annotate(app_count=Count("apps", filter=Q(apps__is_published=True)))
        .values("id", "name", "slug", "icon", "color", "app_count")
        .order_by("order", "name")
    )
    
    return JsonResponse({
        "status": "success",
        "total": len(list(categories)),
        "categories": list(categories),
    })


@require_http_methods(["GET"])
def category_apps_api(request, slug):
    """
    JSON API endpoint for apps in a specific category
    """
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    apps = (
        App.objects
        .filter(is_published=True, category=category)
        .select_related("category")
        .values(
            "id", "slug", "title", "platform", "version",
            "avg_rating", "total_ratings", "downloads",
            "size_mb", "is_free", "price"
        )
        .order_by("-downloads")
    )
    
    return JsonResponse({
        "status": "success",
        "category": {
            "name": category.name,
            "slug": category.slug,
            "icon": category.icon,
        },
        "total_apps": len(list(apps)),
        "apps": list(apps),
    })
