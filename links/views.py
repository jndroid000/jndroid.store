from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
import json
import csv
from datetime import datetime

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
