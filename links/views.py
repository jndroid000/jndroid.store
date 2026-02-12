from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Count, Q
from django.http import JsonResponse, HttpResponse
import json
import csv
from datetime import datetime

from accounts.models import User
from .models import Link, LinkCategory, LinkClick
from .forms import LinkForm, LinkCategoryForm


@login_required(login_url='accounts:login')
def link_dashboard(request):
    """User's link management dashboard"""
    categories = LinkCategory.objects.filter(user=request.user)
    links = Link.objects.filter(user=request.user).select_related('category')
    
    # Statistics
    total_links = links.count()
    total_clicks = LinkClick.objects.filter(link__user=request.user).count()
    
    context = {
        'categories': categories,
        'links': links,
        'total_links': total_links,
        'total_clicks': total_clicks,
        'title': 'Link Management Dashboard',
    }
    return render(request, 'links/dashboard.html', context)


@login_required(login_url='accounts:login')
def link_create(request):
    """Create a new link"""
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.user = request.user
            link.save()
            messages.success(request, f"Link '{link.title}' created successfully!")
            return redirect('links:dashboard')
    else:
        form = LinkForm()
        # Filter categories to current user only
        form.fields['category'].queryset = LinkCategory.objects.filter(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create Link',
    }
    return render(request, 'links/link_form.html', context)


@login_required(login_url='accounts:login')
def link_edit(request, link_id):
    """Edit an existing link"""
    link = get_object_or_404(Link, id=link_id, user=request.user)
    
    if request.method == 'POST':
        form = LinkForm(request.POST, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, f"Link '{link.title}' updated successfully!")
            return redirect('links:dashboard')
    else:
        form = LinkForm(instance=link)
        form.fields['category'].queryset = LinkCategory.objects.filter(user=request.user)
    
    context = {
        'form': form,
        'link': link,
        'title': 'Edit Link',
    }
    return render(request, 'links/link_form.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
def link_delete(request, link_id):
    """Delete a link"""
    link = get_object_or_404(Link, id=link_id, user=request.user)
    title = link.title
    link.delete()
    messages.success(request, f"Link '{title}' deleted successfully!")
    return redirect('links:dashboard')


def public_link_profile(request, username):
    """Public profile with user's all active links"""
    user = get_object_or_404(User, username=username)
    categories = LinkCategory.objects.filter(user=user)
    links = Link.objects.filter(user=user, is_active=True).select_related('category')
    
    context = {
        'profile_user': user,
        'categories': categories,
        'links': links,
        'title': f"{user.get_full_name or user.username}'s Links",
    }
    return render(request, 'links/public_profile.html', context)


@require_http_methods(["GET"])
def link_redirect(request, link_id):
    """Track and redirect to link"""
    link = get_object_or_404(Link, id=link_id, is_active=True)
    
    # Track click
    LinkClick.objects.create(
        link=link,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # Increment counter
    link.click_count += 1
    link.save(update_fields=['click_count'])
    
    return redirect(link.url)


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required(login_url='accounts:login')
def view_all_links(request):
    """View ALL user's links (active and inactive)"""
    links = Link.objects.filter(user=request.user).select_related('category').order_by('-created_at')
    
    # Count stats
    total_links = links.count()
    active_links = links.filter(is_active=True).count()
    inactive_links = links.filter(is_active=False).count()
    
    context = {
        'links': links,
        'total_links': total_links,
        'active_links': active_links,
        'inactive_links': inactive_links,
    }
    return render(request, 'links/all_links_list.html', context)


@login_required(login_url='accounts:login')
def view_active_links(request):
    """View all active user's links"""
    links = Link.objects.filter(user=request.user, is_active=True).select_related('category').order_by('-created_at')
    
    context = {
        'links': links,
        'total_active_links': links.count(),
    }
    return render(request, 'links/active_links_list.html', context)


@login_required(login_url='accounts:login')
def export_links_json(request):
    """Export all active user's links as JSON file"""
    links = Link.objects.filter(user=request.user, is_active=True).select_related('category').values(
        'id',
        'title',
        'description',
        'url',
        'icon',
        'click_count',
        'category__name',
        'created_at',
        'updated_at'
    )
    
    # Convert to list and prepare data
    links_data = list(links)
    
    # Prepare response
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"links_backup_{timestamp}.json"
    
    response = HttpResponse(
        json.dumps(links_data, indent=2, default=str),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    messages.success(request, f"Exported {len(links_data)} active links to JSON!")
    return response


@login_required(login_url='accounts:login')
def export_links_csv(request):
    """Export all active user's links as CSV file"""
    links = Link.objects.filter(user=request.user, is_active=True).select_related('category')
    
    # Create CSV response
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"links_backup_{timestamp}.csv"
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Write CSV header
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Title', 'Description', 'URL', 'Category', 'Icon', 'Clicks', 'Created', 'Updated'
    ])
    
    # Write data rows
    for link in links:
        writer.writerow([
            link.id,
            link.title,
            link.description,
            link.url,
            link.category.name if link.category else '',
            link.icon,
            link.click_count,
            link.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            link.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    messages.success(request, f"Exported {links.count()} active links to CSV!")
    return response

# ==================== ADMIN VIEWS ====================

@staff_member_required(login_url='accounts:login')
def admin_links_overview(request):
    """Admin dashboard overview for links analytics"""
    # Get statistics
    total_links = Link.objects.count()
    total_clicks = LinkClick.objects.count()
    total_categories = LinkCategory.objects.count()
    
    # Get active users with links
    users_with_links = User.objects.filter(links__isnull=False).distinct().count()
    
    # Most popular links (top 10)
    popular_links = Link.objects.filter(is_active=True).select_related('user', 'category').order_by('-click_count')[:10]
    
    # Recent links
    recent_links = Link.objects.select_related('user', 'category').order_by('-created_at')[:10]
    
    # Top link creators (users with most links)
    top_creators = User.objects.annotate(
        link_count=Count('links')
    ).filter(link_count__gt=0).order_by('-link_count')[:10]
    
    context = {
        'total_links': total_links,
        'total_clicks': total_clicks,
        'total_categories': total_categories,
        'users_with_links': users_with_links,
        'popular_links': popular_links,
        'recent_links': recent_links,
        'top_creators': top_creators,
        'title': 'Link Management Analytics',
    }
    return render(request, 'admin/links_overview.html', context)


@staff_member_required(login_url='accounts:login')
def admin_links_list(request):
    """Admin view all links with moderation controls"""
    # Get filter parameters
    search = request.GET.get('search', '')
    is_active = request.GET.get('is_active', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Start with all links
    links = Link.objects.select_related('user', 'category')
    
    # Apply filters
    if search:
        links = links.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) | 
            Q(user__username__icontains=search) |
            Q(url__icontains=search)
        )
    
    if is_active:
        links = links.filter(is_active=is_active.lower() == 'true')
    
    # Apply sorting
    valid_sorts = ['-created_at', 'created_at', '-click_count', 'click_count', 'title', '-title']
    if sort_by not in valid_sorts:
        sort_by = '-created_at'
    links = links.order_by(sort_by)
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(links, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_links': links.count(),
        'search': search,
        'is_active': is_active,
        'sort_by': sort_by,
        'title': 'Link Management',
    }
    return render(request, 'admin/links_list.html', context)


@staff_member_required(login_url='accounts:login')
@require_http_methods(["POST"])
def admin_link_toggle_status(request, link_id):
    """Admin toggle link active/inactive status"""
    link = get_object_or_404(Link, id=link_id)
    link.is_active = not link.is_active
    link.save()
    
    status = "activated" if link.is_active else "deactivated"
    messages.success(request, f"Link '{link.title}' {status} successfully!")
    return redirect('admin_panel:links_list')


@staff_member_required(login_url='accounts:login')
@require_http_methods(["POST"])
def admin_link_delete(request, link_id):
    """Admin delete user's link"""
    link = get_object_or_404(Link, id=link_id)
    title = link.title
    username = link.user.username
    link.delete()
    
    messages.success(request, f"Link '{title}' (from @{username}) deleted successfully!")
    return redirect('admin_panel:links_list')


@staff_member_required(login_url='accounts:login')
def admin_link_analytics(request):
    """Detailed link analytics and statistics"""
    # Top 20 most clicked links
    most_clicked = Link.objects.filter(is_active=True).order_by('-click_count')[:20]
    
    # Recent clicks
    recent_clicks = LinkClick.objects.select_related('link', 'link__user').order_by('-clicked_at')[:30]
    
    # Total statistics
    total_clicks = LinkClick.objects.count()
    total_links = Link.objects.count()
    
    # Links by category with calculated width percentage
    links_by_category = LinkCategory.objects.annotate(
        total=Count('links')
    ).order_by('-total')[:10]
    
    # Calculate width percentage for each category
    max_count = max([c.total for c in links_by_category], default=1)
    for category in links_by_category:
        category.width_percent = min(int((category.total / max_count) * 100), 100)
    
    # Average clicks per link
    avg_clicks = total_links > 0 and (total_clicks / total_links) or 0
    
    context = {
        'most_clicked': most_clicked,
        'recent_clicks': recent_clicks,
        'total_clicks': total_clicks,
        'total_links': total_links,
        'avg_clicks': f"{avg_clicks:.1f}",
        'links_by_category': links_by_category,
        'title': 'Link Analytics',
    }
    return render(request, 'admin/links_analytics.html', context)