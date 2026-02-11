from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Avg, Count
from django.core.paginator import Paginator
from .models import App
from categories.models import Category
from reviews.models import Review


@login_required
def app_ledger_view(request):
    """
    Comprehensive app ledger view showing all app information
    with sidebar statistics and filtering
    """
    
    # Get all apps for current user
    apps = App.objects.filter(owner=request.user).select_related('category')
    
    # Apply filters
    platform = request.GET.get('platform', '')
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-created_at')
    search = request.GET.get('search', '')
    
    # Filter by platform
    if platform:
        apps = apps.filter(platform=platform)
    
    # Filter by category
    if category:
        apps = apps.filter(category__slug=category)
    
    # Filter by status
    if status == 'published':
        apps = apps.filter(is_published=True)
    elif status == 'draft':
        apps = apps.filter(is_published=False)
    elif status == 'pending_deletion':
        apps = apps.filter(is_pending_deletion=True)
    
    # Search filter
    if search:
        apps = apps.filter(
            Q(title__icontains=search) |
            Q(slug__icontains=search) |
            Q(developer_name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Sort
    apps = apps.order_by(sort_by)
    
    # Calculate sidebar statistics
    total_apps = App.objects.filter(owner=request.user).count()
    published_apps = App.objects.filter(owner=request.user, is_published=True).count()
    draft_apps = App.objects.filter(owner=request.user, is_published=False).count()
    pending_delete = App.objects.filter(owner=request.user, is_pending_deletion=True).count()
    
    # Aggregate stats
    stats = App.objects.filter(owner=request.user).aggregate(
        total_downloads=Sum('downloads'),
        total_installs=Sum('install_count'),
        avg_rating=Avg('avg_rating'),
        total_revenue=Sum('price', filter=Q(is_free=False))
    )
    
    # Platform distribution
    platform_dist = App.objects.filter(owner=request.user).values('platform').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Category distribution
    category_dist = App.objects.filter(owner=request.user).values(
        'category__name'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Monetization insights
    free_apps = App.objects.filter(owner=request.user, is_free=True).count()
    paid_apps = App.objects.filter(owner=request.user, is_free=False).count()
    apps_with_iap = App.objects.filter(owner=request.user, has_iap=True).count()
    
    # Get all categories for filter dropdown
    categories = Category.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(apps, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get detailed info for paginated apps
    app_details = []
    for app in page_obj.object_list:
        reviews = Review.objects.filter(app=app).aggregate(
            count=Count('id'),
            avg_rating=Avg('rating')
        )
        
        app_details.append({
            'app': app,
            'review_count': reviews['count'] or 0,
            'review_rating': reviews['avg_rating'] or 0,
        })
    
    context = {
        'page_obj': page_obj,
        'app_details': app_details,
        'total_apps': total_apps,
        'published_apps': published_apps,
        'draft_apps': draft_apps,
        'pending_delete': pending_delete,
        'stats': stats,
        'platform_dist': platform_dist,
        'category_dist': category_dist,
        'free_apps': free_apps,
        'paid_apps': paid_apps,
        'apps_with_iap': apps_with_iap,
        'categories': categories,
        'current_platform': platform,
        'current_category': category,
        'current_status': status,
        'current_sort': sort_by,
        'search_query': search,
    }
    
    return render(request, 'apps/ledger_view.html', context)


@login_required
def app_ledger_export(request):
    """
    Export app ledger as JSON or CSV
    """
    import json
    from django.http import JsonResponse, HttpResponse
    from csv import writer
    
    format_type = request.GET.get('format', 'json')
    
    apps = App.objects.filter(owner=request.user).select_related('category').values(
        'id', 'title', 'slug', 'platform', 'version', 'downloads', 
        'install_count', 'avg_rating', 'total_ratings', 'is_free', 'price',
        'developer_name', 'is_published', 'created_at', 'updated_at'
    )
    
    if format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="app_ledger.csv"'
        
        csv_writer = writer(response)
        csv_writer.writerow([
            'App ID', 'Title', 'Slug', 'Platform', 'Version', 'Downloads',
            'Installs', 'Rating', 'Total Ratings', 'Free?', 'Price',
            'Developer', 'Published', 'Created', 'Updated'
        ])
        
        for app in apps:
            csv_writer.writerow([
                app['id'],
                app['title'],
                app['slug'],
                app['platform'],
                app['version'],
                app['downloads'],
                app['install_count'],
                app['avg_rating'],
                app['total_ratings'],
                'Yes' if app['is_free'] else 'No',
                app['price'] or 'N/A',
                app['developer_name'],
                'Yes' if app['is_published'] else 'No',
                app['created_at'].strftime('%Y-%m-%d %H:%M'),
                app['updated_at'].strftime('%Y-%m-%d %H:%M'),
            ])
        
        return response
    
    else:  # JSON
        app_list = list(apps)
        return JsonResponse({
            'total': len(app_list),
            'apps': app_list,
            'developer': request.user.get_full_name() or request.user.username,
        }, safe=False)


@login_required
def app_info_sheet(request, slug):
    """
    Detailed information sheet for a single app
    Shows all app metadata in organized cards
    """
    try:
        app = App.objects.get(slug=slug, owner=request.user)
    except App.DoesNotExist:
        from django.http import Http404
        raise Http404("App not found or you don't have permission to view it")
    
    context = {
        'app': app,
    }
    
    return render(request, 'apps/app_info_sheet.html', context)
