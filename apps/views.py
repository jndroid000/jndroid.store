from django.db.models import Avg, Q, Count, F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.views.decorators.http import require_http_methods

from .models import App
from .forms import AppUploadForm
from categories.models import Category


def is_staff(user):
    """Check if user is staff/admin"""
    return user.is_staff or user.is_superuser


def app_list(request):
    """Display list of published apps with pagination and filtering"""
    q = request.GET.get("q", "").strip()
    cat = request.GET.get("cat", "").strip()  # category slug
    page = request.GET.get('page', 1)

    # Base queryset with select_related for performance
    apps_qs = App.objects.filter(is_published=True).select_related(
        "category", "owner"
    ).annotate(
        review_count=Count("reviews")
    ).order_by("-created_at")

    # Get categories for sidebar
    categories = Category.objects.filter(is_active=True).order_by("name")

    # Apply category filter
    if cat:
        apps_qs = apps_qs.filter(category__slug=cat)

    # Apply search filter
    if q:
        apps_qs = apps_qs.filter(
            Q(title__icontains=q) |
            Q(short_description__icontains=q) |
            Q(description__icontains=q) |
            Q(version__icontains=q)
        )

    # Pagination (20 apps per page)
    paginator = Paginator(apps_qs, 20)
    try:
        apps = paginator.page(page)
    except PageNotAnInteger:
        apps = paginator.page(1)
    except EmptyPage:
        apps = paginator.page(paginator.num_pages)

    context = {
        "apps": apps,
        "categories": categories,
        "q": q,
        "cat": cat,
        "total_results": paginator.count,
    }
    return render(request, "apps/app_list.html", context)


def app_detail(request, slug):
    """Display detailed app page with reviews and related apps"""
    app = get_object_or_404(
        App.objects.select_related("category", "owner").annotate(
            review_count=Count("reviews")
        ),
        slug=slug,
        is_published=True,
    )
    
    reviews = app.reviews.select_related("user").order_by('-created_at')
    
    # Get related apps from same category (limit to 4)
    related_apps = App.objects.filter(
        category=app.category,
        is_published=True
    ).exclude(slug=slug)[:4]

    context = {
        "app": app,
        "reviews": reviews,
        "reviews_count": reviews.count(),
        "related_apps": related_apps,
    }
    return render(request, "apps/app_detail.html", context)


@require_http_methods(["GET"])
def app_download(request, slug):
    """Increment download count and redirect to download link"""
    app = get_object_or_404(App, slug=slug, is_published=True)

    # Check if download is available
    if not app.download_link and not app.apk_file:
        messages.error(request, 'Download link is not available for this app')
        return redirect('apps:detail', slug=slug)

    # Atomic increment - prevents race conditions
    with transaction.atomic():
        App.objects.filter(pk=app.pk).update(downloads=F('downloads') + 1)

    # Redirect to download link
    if app.download_link:
        return redirect(app.download_link)
    
    if app.apk_file:
        return redirect(app.apk_file.url)

    # Fallback (shouldn't reach here)
    return redirect('apps:detail', slug=slug)


@login_required(login_url='accounts:login')
@login_required(login_url='accounts:login')
def app_upload(request):
    """Upload a new app"""
    if request.method == 'POST':
        form = AppUploadForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.owner = request.user
            app.save()
            messages.success(request, f"App '{app.title}' uploaded successfully!")
            return redirect('apps:detail', slug=app.slug)
    else:
        form = AppUploadForm()
    
    context = {
        'form': form,
        'title': 'Upload New App',
    }
    return render(request, 'apps/app_upload.html', context)


@login_required(login_url='accounts:login')
def app_edit(request, slug):
    """Edit an existing app (only owner can edit)"""
    app = get_object_or_404(App, slug=slug)
    
    # Check if current user is the owner
    if app.owner != request.user:
        messages.error(request, 'You can only edit your own apps!')
        return redirect('apps:detail', slug=app.slug)
    
    if request.method == 'POST':
        form = AppUploadForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, f"App '{app.title}' updated successfully!")
            return redirect('apps:detail', slug=app.slug)
    else:
        form = AppUploadForm(instance=app)
    
    context = {
        'form': form,
        'title': 'Edit App',
        'app': app,
        'is_edit': True,
    }
    return render(request, 'apps/app_upload.html', context)


@login_required(login_url='accounts:login')
def my_apps(request):
    """View dashboard with all apps uploaded by the current user"""
    # Get user's apps with stats
    apps = App.objects.filter(owner=request.user).annotate(
        review_count=Count('reviews')
    ).order_by('-created_at')
    
    # Calculate total stats
    total_apps = apps.count()
    total_downloads = apps.aggregate(Sum('downloads'))['downloads__sum'] or 0
    published_apps = apps.filter(is_published=True).count()
    unpublished_apps = apps.filter(is_published=False).count()
    
    # Pagination (10 apps per page)
    page = request.GET.get('page', 1)
    paginator = Paginator(apps, 10)
    try:
        apps = paginator.page(page)
    except PageNotAnInteger:
        apps = paginator.page(1)
    except EmptyPage:
        apps = paginator.page(paginator.num_pages)
    
    context = {
        'apps': apps,
        'title': 'My Apps Dashboard',
        'total_apps': total_apps,
        'total_downloads': total_downloads,
        'published_apps': published_apps,
        'unpublished_apps': unpublished_apps,
    }
    return render(request, 'apps/my_apps.html', context)


@login_required(login_url='accounts:login')
def app_delete(request, slug):
    """Soft delete an app (only owner can delete)"""
    app = get_object_or_404(App, slug=slug)
    
    # Check if current user is the owner or staff
    if app.owner != request.user and not request.user.is_staff:
        messages.error(request, 'You can only delete your own apps!')
        return redirect('apps:detail', slug=app.slug)
    
    if request.method == 'POST':
        app.is_pending_deletion = True
        app.is_published = False
        app.save()
        messages.success(request, f"App '{app.title}' marked for deletion!")
        return redirect('apps:my_apps')
    
    context = {
        'app': app,
        'title': 'Delete App',
    }
    return render(request, 'apps/app_delete_confirm.html', context)
