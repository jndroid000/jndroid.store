from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from accounts.models import User
from apps.models import App
from apps.forms import AppUploadForm
from categories.models import Category
from reviews.models import Review


def home(request):
    return render(request, "home.html")

def support(request):
    """Support and community guidelines page"""
    return render(request, "support.html")

def community_guidelines(request):
    """Community guidelines page"""
    return render(request, "community_guidelines.html")

def report_bug(request):
    """Report a bug page"""
    return render(request, "report_bug.html")

def terms_of_service(request):
    """Terms of Service page"""
    return render(request, "terms_of_service.html")


# ============================================
# ADMIN DASHBOARD VIEWS
# ============================================

def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_staff


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard with statistics"""
    
    # Calculate stats
    total_apps = App.objects.count()
    published_apps = App.objects.filter(is_published=True).count()
    draft_apps = App.objects.filter(is_published=False).count()
    pending_apps = App.objects.filter(is_published=False).count()
    pending_deletions = App.objects.filter(is_pending_deletion=True).count()
    
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    total_downloads = App.objects.aggregate(total=Sum('downloads'))['total'] or 0
    total_reviews = Review.objects.count()
    avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    flagged_reviews = Review.objects.filter(is_flagged=True).count()
    
    # Recent activity
    recent_apps = App.objects.all().order_by('-created_at')[:5]
    recent_reviews = Review.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_apps': total_apps,
        'published_apps': published_apps,
        'draft_apps': draft_apps,
        'pending_apps': pending_apps,
        'pending_deletions': pending_deletions,
        'total_users': total_users,
        'active_users': active_users,
        'total_downloads': total_downloads,
        'total_reviews': total_reviews,
        'avg_rating': avg_rating,
        'flagged_reviews': flagged_reviews,
        'recent_apps': recent_apps,
        'recent_reviews': recent_reviews,
        'title': 'Admin Dashboard',
    }
    return render(request, 'admin/dashboard.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def apps_list(request):
    """Admin view for managing all apps with pagination and optimized queries"""
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()  # published or draft
    page = request.GET.get('page', 1)
    
    # Base queryset with optimized queries
    apps_qs = App.objects.select_related(
        "category", "owner"
    ).annotate(
        avg_rating=Avg("reviews__rating"),
        review_count=Count("reviews")
    ).order_by('-created_at')
    
    # Filter by status
    if status == "published":
        apps_qs = apps_qs.filter(is_published=True)
    elif status == "draft":
        apps_qs = apps_qs.filter(is_published=False)
    
    # Filter by search query
    if q:
        apps_qs = apps_qs.filter(
            Q(title__icontains=q) |
            Q(owner__username__icontains=q) |
            Q(owner__email__icontains=q) |
            Q(slug__icontains=q)
        )
    
    # Get stats with single aggregate query (fixes N+1 problem)
    stats = App.objects.aggregate(
        total_apps=Count('id'),
        published_count=Count('id', filter=Q(is_published=True)),
        draft_count=Count('id', filter=Q(is_published=False)),
        total_downloads=Sum('downloads') or 0,
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
        'apps': apps,
        'q': q,
        'status': status,
        **stats,  # Unpack stats into context
        'title': 'Admin - App Management',
    }
    return render(request, 'admin/apps_list.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def apps_pending(request):
    """List pending apps (draft apps) - redirect to apps_list with draft filter"""
    return redirect('admin_panel:apps_list') + '?status=draft'


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def app_detail(request, slug):
    """Admin detail view for a specific app with analytics and reviews"""
    app = get_object_or_404(
        App.objects.select_related("category", "owner").annotate(avg_rating=Avg("reviews__rating")),
        slug=slug
    )
    
    reviews = app.reviews.select_related("user").order_by('-created_at')
    app_versions = app.versions.all().order_by('-released_at')
    
    # Stats
    reviews_count = reviews.count()
    total_downloads = app.downloads
    
    context = {
        'app': app,
        'reviews': reviews,
        'reviews_count': reviews_count,
        'app_versions': app_versions,
        'total_downloads': total_downloads,
        'title': f'Admin - {app.title}',
    }
    return render(request, 'admin/apps_detail.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def apps_edit(request, slug):
    """Admin edit view for editing an app"""
    app = get_object_or_404(App, slug=slug)
    
    if request.method == 'POST':
        form = AppUploadForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, f"App '{app.title}' updated successfully!")
            return redirect('admin_panel:app_detail', slug=app.slug)
    else:
        form = AppUploadForm(instance=app)
    
    context = {
        'form': form,
        'app': app,
        'title': f'Edit - {app.title}',
        'is_edit': True,
    }
    return render(request, 'admin/apps_edit.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def users_list(request):
    """List all users"""
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users,
        'title': 'Users Management',
    }
    return render(request, 'admin/users_list.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def users_create(request):
    """Create new user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=True
            )
            messages.success(request, f'User {username} created successfully!')
            return redirect('admin_panel:users_list')
    
    context = {'title': 'Create User'}
    return render(request, 'admin/users_create.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def users_edit(request, pk):
    """Edit user details"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_staff = request.POST.get('is_staff') == 'on'
        user.save()
        
        messages.success(request, 'User updated successfully!')
        return redirect('admin_panel:users_list')
    
    context = {
        'user': user,
        'title': f'Edit {user.username}',
    }
    return render(request, 'admin/users_edit.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def categories_list(request):
    """List all categories"""
    categories = Category.objects.all().annotate(apps_count=Count('apps'))
    
    context = {
        'categories': categories,
        'title': 'Categories Management',
    }
    return render(request, 'admin/categories_list.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def categories_create(request):
    """Create new category"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if not name:
            messages.error(request, 'Category name is required!')
        else:
            if Category.objects.filter(name=name).exists():
                messages.error(request, 'Category already exists!')
            else:
                Category.objects.create(name=name, description=description)
                messages.success(request, f'Category "{name}" created successfully!')
        
        return redirect('admin_panel:categories_list')
    
    # GET request - show the list page with form
    categories = Category.objects.all().annotate(apps_count=Count('apps'))
    context = {
        'categories': categories,
        'title': 'Categories Management',
    }
    return render(request, 'admin/categories_list.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def categories_edit(request, pk):
    """Edit category"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.name = request.POST.get('name', category.name)
        category.description = request.POST.get('description', category.description)
        category.save()
        
        messages.success(request, 'Category updated successfully!')
        return redirect('admin_panel:categories_list')
    
    context = {
        'category': category,
        'title': f'Edit {category.name}',
    }
    return render(request, 'admin/categories_edit.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def categories_delete(request, pk):
    """Delete category"""
    category = get_object_or_404(Category, pk=pk)
    category_name = category.name
    category.delete()
    
    messages.success(request, f'Category "{category_name}" deleted successfully!')
    return redirect('admin_panel:categories_list')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def reviews_list(request):
    """List all reviews"""
    # Show all reviews that are not flagged or approved (pending review)
    reviews = Review.objects.filter(is_flagged=False).exclude(is_approved=True).select_related('user', 'app').order_by('-created_at')
    
    context = {
        'reviews': reviews,
        'title': 'Pending Reviews',
    }
    return render(request, 'admin/reviews_list.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def reviews_flagged(request):
    """List flagged reviews"""
    reviews = Review.objects.filter(is_flagged=True).select_related('user', 'app').order_by('-created_at')
    
    context = {
        'reviews': reviews,
        'title': 'Flagged Reviews',
    }
    return render(request, 'admin/reviews_flagged.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def reviews_approved(request):
    """List approved reviews"""
    reviews = Review.objects.filter(is_approved=True, is_flagged=False).select_related('user', 'app').order_by('-approved_at')
    
    context = {
        'reviews': reviews,
        'title': 'Approved Reviews',
    }
    return render(request, 'admin/reviews_approved.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def reviews_delete(request, pk):
    """Delete a review (hard delete from database)"""
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    messages.success(request, 'Review deleted permanently!')
    return redirect('admin_panel:reviews_list')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def reviews_flag(request, pk):
    """Flag a review for further review"""
    review = get_object_or_404(Review, pk=pk)
    review.is_flagged = True
    review.save()
    messages.success(request, 'Review flagged for moderation!')
    return redirect('admin_panel:reviews_list')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def reviews_approve(request, pk):
    """Approve a review"""
    from django.utils import timezone
    review = get_object_or_404(Review, pk=pk)
    review.is_approved = True
    review.is_flagged = False
    review.approved_at = timezone.now()
    review.save()
    messages.success(request, 'Review approved!')
    return redirect('admin_panel:reviews_list')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def analytics_overview(request):
    """Analytics overview"""
    context = {
        'title': 'Analytics Overview',
    }
    return render(request, 'admin/analytics_overview.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def analytics_reports(request):
    """Analytics reports"""
    context = {
        'title': 'Reports',
    }
    return render(request, 'admin/analytics_reports.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def settings(request):
    """Admin settings"""
    context = {
        'title': 'Settings',
    }
    return render(request, 'admin/settings.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def moderation(request):
    """Moderation settings"""
    context = {
        'title': 'Moderation Rules',
    }
    return render(request, 'admin/moderation.html', context)


# ============================================
# PENDING DELETIONS MANAGEMENT
# ============================================

@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def mark_app_for_deletion(request, slug):
    """Mark app for deletion (soft delete)"""
    app = get_object_or_404(App, slug=slug)
    app.is_pending_deletion = True
    app.save()
    messages.success(request, f'"{app.title}" marked for deletion. It will be permanently deleted after admin approval.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_panel:apps_list'))


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
def pending_deletions(request):
    """View apps pending deletion"""
    apps = App.objects.filter(is_pending_deletion=True).select_related('owner', 'category').order_by('-updated_at')
    
    context = {
        'apps': apps,
        'title': 'Pending Deletions',
    }
    return render(request, 'admin/pending_deletions.html', context)


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def approve_deletion(request, slug):
    """Permanently delete app (admin only)"""
    app = get_object_or_404(App, slug=slug)
    app_title = app.title
    app.delete()
    messages.success(request, f'App "{app_title}" has been permanently deleted.')
    return redirect('admin_panel:pending_deletions')


@login_required(login_url='accounts:login')
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def cancel_deletion(request, slug):
    """Cancel deletion (restore from pending)"""
    app = get_object_or_404(App, slug=slug, is_pending_deletion=True)
    app.is_pending_deletion = False
    app.save()
    messages.success(request, f'Deletion cancelled for "{app.title}".')
    return redirect('admin_panel:pending_deletions')


def submit_dmca_notice(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        copyrighted_work = request.POST.get('copyrighted_work')
        original_url = request.POST.get('original_url')
        copyright_holder = request.POST.get('copyright_holder')
        app_name = request.POST.get('app_name')
        infringing_url = request.POST.get('infringing_url')
        description = request.POST.get('description')
        damages = request.POST.get('damages')
        signature = request.POST.get('signature')

        try:
            # Send email to DMCA agent with detailed information
            subject = f"DMCA Takedown Notice from {name} - {app_name}"
            message = f"""
DMCA TAKEDOWN NOTICE

=== COMPLAINANT INFORMATION ===
Name: {name}
Email: {email}
Phone: {phone}
Address: {address}

=== COPYRIGHT INFORMATION ===
Description of Work: {copyrighted_work}
Original Work URL: {original_url if original_url else 'Not provided'}
Copyright Holder Status: {copyright_holder}

=== INFRINGING MATERIAL ===
App/Content Name: {app_name}
Infringing URL: {infringing_url}

=== INFRINGEMENT DETAILS ===
Description: {description}

Specific Infringing Content: {damages}

=== LEGAL DECLARATION ===
Digital Signature: {signature}

This notice was filed on: {request.POST.get('timestamp', 'See timestamp in email headers')}
"""
            send_mail(
                subject,
                message,
                'jndroid000@gmail.com',  # From email
                ['jndroid000@gmail.com', 'dmca@jndroid.com'],  # To emails
                fail_silently=False,
            )
            # Set flag in session to indicate successful submission
            request.session['dmca_submitted'] = True
            # Redirect to success page
            return redirect('dmca_success')
        except Exception as e:
            print(f"Error sending DMCA email: {str(e)}")
            # Still redirect to success page even if email fails
            request.session['dmca_submitted'] = True
            return redirect('dmca_success')

    return redirect('dmca_takedown')

def dmca_success(request):
    """DMCA success page - only accessible after form submission"""
    if not request.session.get('dmca_submitted'):
        # If not submitted through form, redirect to DMCA page
        return redirect('dmca_takedown')
    
    # Clear the session flag
    del request.session['dmca_submitted']
    
    return render(request, 'dmca_success.html')
