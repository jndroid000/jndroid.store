from django.db.models import Avg, Q, Count, F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.utils import timezone

from .models import App, CopyrightClaim, CopyrightInfringementReport, AppScreenshot
from .forms import AppUploadForm, AppTakedownRequestForm, CopyrightInfringementReportForm
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
    return render(request, "apps/app_list_new.html", context)


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
def app_upload(request):
    """Upload a new app - authenticated users only"""
    if request.method == 'POST':
        form = AppUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    app = form.save(commit=False)
                    app.owner = request.user
                    app.save()
                    
                    # Handle screenshot uploads
                    screenshots = request.FILES.getlist('screenshots')
                    for i, screenshot in enumerate(screenshots):
                        if screenshot:
                            AppScreenshot.objects.create(
                                app=app,
                                image=screenshot,
                                order=i,
                            )
                    
                    messages.success(
                        request,
                        f"✅ Success! '{app.title}' has been uploaded to JnDroid Store.",
                        extra_tags='success'
                    )
                return redirect('apps:detail', slug=app.slug)
            except Exception as e:
                messages.error(
                    request,
                    f"❌ Error saving app: {str(e)}. Please try again.",
                    extra_tags='error'
                )
        else:
            # Show form validation errors
            messages.error(
                request,
                "⚠️ Please fix the errors below and try again.",
                extra_tags='error'
            )
            # Also show detailed field errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"  • {error}", extra_tags='error')
    else:
        form = AppUploadForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Upload New App',
        'is_upload': True,
        'is_superuser': request.user.is_superuser,
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
        form = AppUploadForm(request.POST, request.FILES, instance=app, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    messages.success(
                        request,
                        f"✅ App '{app.title}' updated successfully!",
                        extra_tags='success'
                    )
                    return redirect('apps:detail', slug=app.slug)
            except Exception as e:
                messages.error(
                    request,
                    f"❌ Error saving app: {str(e)}. Please try again.",
                    extra_tags='error'
                )
        else:
            # Show form validation errors
            messages.error(
                request,
                "⚠️ Please fix the errors below and try again.",
                extra_tags='error'
            )
            # Also show detailed field errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"  • {error}", extra_tags='error')
    else:
        form = AppUploadForm(instance=app, user=request.user)
    
    context = {
        'form': form,
        'title': f'Edit {app.title}',
        'app': app,
        'is_edit': True,
        'is_superuser': request.user.is_superuser,
    }
    return render(request, 'apps/app_edit.html', context)


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


# ==================== PWA API ENDPOINTS ====================

@cache_page(60 * 30)  # Cache for 30 minutes
@require_http_methods(["GET"])
def popular_apps_api(request):
    """
    API endpoint for Service Worker to fetch popular apps for offline caching.
    Returns top 20 popular apps with minimal data.
    """
    try:
        # Get top apps by download count
        popular_apps = App.objects.filter(
            is_published=True
        ).select_related(
            'category', 'owner'
        ).annotate(
            review_count=Count('reviews')
        ).order_by('-downloads')[:20]
        
        apps_data = []
        for app in popular_apps:
            app_dict = {
                'id': app.id,
                'slug': app.slug,
                'title': app.title,
                'short_description': app.short_description,
                'version': app.version,
                'downloads': app.downloads,
                'rating': float(app.avg_rating or 0),
                'category': app.category.name if app.category else 'Unknown',
            }
            
            # Add cover image if available
            if app.cover_image:
                app_dict['cover_image'] = request.build_absolute_uri(app.cover_image.url)
            
            apps_data.append(app_dict)
        
        return JsonResponse({
            'success': True,
            'count': len(apps_data),
            'apps': apps_data,
            'timestamp': timezone.now().isoformat(),
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


# ==================== COPYRIGHT & TAKEDOWN ====================

@login_required(login_url='accounts:login')
def app_takedown_request(request, slug):
    """
    Allow app owners to request takedown of their own apps.
    This creates a CopyrightClaim with type 'owner_request'
    """
    app = get_object_or_404(App, slug=slug)
    
    # Verify user is the owner
    if app.owner != request.user:
        messages.error(request, 'You can only request takedown of your own apps!')
        return redirect('apps:detail', slug=app.slug)
    
    # Check if takedown already requested
    if app.takedown_requested:
        messages.warning(request, f"Takedown for '{app.title}' is already requested and pending review.")
        return redirect('apps:detail', slug=app.slug)
    
    if request.method == 'POST':
        form = AppTakedownRequestForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create CopyrightClaim for owner-requested takedown
                    claim = CopyrightClaim.objects.create(
                        app=app,
                        claim_type='owner_request',
                        claimant_name=request.user.get_full_name() or request.user.username,
                        claimant_email=request.user.email,
                        description=f"Owner takedown request for: {app.title}",
                        reason=form.cleaned_data['detailed_reason'],
                        status='pending',
                    )
                    
                    # Mark app as takedown requested
                    app.takedown_requested = True
                    app.takedown_reason = form.cleaned_data['detailed_reason']
                    app.takedown_requested_at = timezone.now()
                    app.save()
                    
                    messages.success(
                        request,
                        f"✅ Takedown request submitted! Your app '{app.title}' will be reviewed for removal within 24-48 hours.",
                        extra_tags='success'
                    )
                    return redirect('apps:detail', slug=app.slug)
            except Exception as e:
                messages.error(
                    request,
                    f"❌ Error submitting takedown request: {str(e)}",
                    extra_tags='error'
                )
    else:
        form = AppTakedownRequestForm()
    
    context = {
        'app': app,
        'form': form,
        'title': 'Request App Takedown',
    }
    return render(request, 'apps/app_takedown_request.html', context)


@login_required(login_url='accounts:login')
def app_copyright_status(request, slug):
    """
    Show copyright status and claims for an app
    (only visible to app owner)
    """
    app = get_object_or_404(App, slug=slug)
    
    # Verify user is the owner or staff
    if app.owner != request.user and not request.user.is_staff:
        messages.error(request, 'You can only view copyright status of your own apps!')
        return redirect('apps:detail', slug=app.slug)
    
    # Get all claims related to this app
    claims = CopyrightClaim.objects.filter(app=app).order_by('-submitted_at')
    
    # Get pending claims count
    pending_claims = claims.filter(status='pending').count()
    approved_claims = claims.filter(status='approved').count()
    
    context = {
        'app': app,
        'claims': claims,
        'pending_claims': pending_claims,
        'approved_claims': approved_claims,
        'title': f'Copyright Status - {app.title}',
    }
    return render(request, 'apps/app_copyright_status.html', context)


# ==================== COPYRIGHT INFRINGEMENT REPORTING ====================

@require_http_methods(["GET", "POST"])
def app_report_infringement(request, slug):
    """
    Allow users to report copyright infringement for an app
    """
    app = get_object_or_404(App, slug=slug, is_published=True)
    
    if request.method == 'POST':
        form = CopyrightInfringementReportForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    report = form.save(commit=False)
                    report.app = app
                    report.status = 'submitted'
                    report.save()
                    
                    # Update app's infringement report count
                    app.copyright_infringement_count = F('copyright_infringement_count') + 1
                    app.has_infringement_report = True
                    app.save(update_fields=['copyright_infringement_count', 'has_infringement_report'])
                    
                    messages.success(
                        request,
                        "✅ Thank you! Your infringement report has been submitted. Our team will review it within 24-48 hours.",
                        extra_tags='success'
                    )
                    return redirect('apps:detail', slug=app.slug)
            except Exception as e:
                messages.error(
                    request,
                    f"❌ Error submitting report: {str(e)}",
                    extra_tags='error'
                )
    else:
        form = CopyrightInfringementReportForm()
    
    context = {
        'app': app,
        'form': form,
        'title': f'Report Infringement - {app.title}',
    }
    return render(request, 'apps/app_report_infringement.html', context)


def app_copyright_check(request, slug):
    """
    Show copyright verification status for an app (public view)
    """
    app = get_object_or_404(App, slug=slug, is_published=True)
    
    context = {
        'app': app,
        'title': f'Copyright Information - {app.title}',
    }
    return render(request, 'apps/app_copyright_check.html', context)


@require_http_methods(["GET"])
def search_api(request):
    """
    রিয়েলটাইম API সার্চ এন্ডপয়েন্ট
    GET /api/search/?q=query
    
    JSON রেসপন্স রিটার্ন করে:
    {
        "success": bool,
        "query": string,
        "count": int,
        "apps": [
            {
                "id": int,
                "title": string,
                "slug": string,
                "icon": string (image URL),
                "short_description": string,
                "category": string,
                "rating": float,
                "download_count": int
            }
        ]
    }
    """
    query = request.GET.get('q', '').strip()
    
    # মিনিমাম ১ ক্যারেক্টার প্রয়োজন
    if not query or len(query) < 1:
        return JsonResponse({
            'success': False,
            'query': query,
            'count': 0,
            'apps': [],
            'message': 'কমপক্ষে ১ ক্যারেক্টার টাইপ করুন'
        })
    
    # সার্চ করো টাইটেল, ডেস্ক্রিপশন, ক্যাটাগরিতে
    apps = App.objects.filter(
        is_published=True
    ).filter(
        Q(title__icontains=query) |
        Q(short_description__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query)
    ).select_related('category').order_by('-downloads')[:10]  # ম্যাক্স ১০ রেজাল্ট
    
    # JSON ফরম্যাটে রেসপন্স প্রিপেয়ার করো
    results = []
    for app in apps:
        results.append({
            'id': app.id,
            'title': app.title,
            'slug': app.slug,
            'icon': app.cover_image.url if app.cover_image else '/static/images/default-app-icon.png',
            'short_description': app.short_description[:100] if app.short_description else '',
            'category': app.category.name if app.category else 'অন্যান্য',
            'rating': round(app.avg_rating or 0, 1),
            'download_count': app.downloads or 0,
        })
    
    return JsonResponse({
        'success': True,
        'query': query,
        'count': len(results),
        'apps': results
    })
