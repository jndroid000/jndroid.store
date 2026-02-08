from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from .models import User
from .forms import SignUpForm, LoginForm, ProfileUpdateForm


@require_http_methods(["GET", "POST"])
@csrf_protect
def login_view(request):
    """Handle user login with form validation"""
    
    # Redirect authenticated users
    if request.user.is_authenticated:
        return redirect('home')
    
    unverified_email = None
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # User is authenticated in form.clean()
            login(request, form.user)
            messages.success(request, 'Login successful!')
            
            # Redirect to next page or home
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            # Check if form has unverified email
            if hasattr(form, 'unverified_email') and form.unverified_email:
                unverified_email = form.unverified_email
    else:
        form = LoginForm()
    
    context = {
        'form': form,
        'title': 'Login',
        'unverified_email': unverified_email,
    }
    return render(request, 'accounts/login.html', context)


@require_http_methods(["GET", "POST"])
@csrf_protect
def signup_view(request):
    """Handle user registration with email verification"""
    
    # Redirect authenticated users
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Disable account until email is verified
            user.save()
            
            # Create EmailAddress record for django-allauth
            email_address = EmailAddress.objects.create(
                user=user,
                email=user.email,
                verified=False,
                primary=True
            )
            
            # Send verification email manually
            try:
                confirmation = EmailConfirmationHMAC(email_address)
                activate_url = request.build_absolute_uri(
                    f'/accounts/confirm-email/{confirmation.key}/'
                )
                
                # Render email template
                email_context = {
                    'user': user,
                    'activate_url': activate_url,
                    'email': user.email,
                }
                
                subject = f"{settings.ACCOUNT_EMAIL_SUBJECT_PREFIX}ইমেইল যাচাইকরণ"
                
                # Send HTML email
                html_message = render_to_string(
                    'account/email/email_confirmation_message.html',
                    email_context
                )
                
                send_mail(
                    subject,
                    f'আপনার অ্যাকাউন্ট যাচাই করতে এই লিঙ্ক ভিজিট করুন: {activate_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                # Log error but don't fail signup
                print(f"Error sending confirmation email: {e}")
            
            messages.success(
                request,
                f'Account created! Please check your email at {user.email} to verify your account. '
                'The verification link will expire in 7 days.'
            )
            return redirect('accounts:email-verification-sent')
    else:
        form = SignUpForm()
    
    context = {
        'form': form,
        'title': 'Sign Up',
    }
    return render(request, 'accounts/signup.html', context)


@require_http_methods(["GET"])
def email_verification_sent(request):
    """Show message after sending verification email"""
    context = {
        'title': 'Verify Your Email',
    }
    return render(request, 'accounts/email_verification_sent.html', context)


@require_http_methods(["GET"])
def email_confirmation_view(request, key):
    """
    Handle email verification via confirmation link
    User clicks link in email with verification key
    """
    try:
        # Try to get and verify the confirmation
        confirmation = EmailConfirmationHMAC.from_key(key)
        
        if not confirmation:
            # Invalid or non-existent key
            context = {
                'title': 'Verification Failed',
                'error_type': 'invalid',
                'error_message': 'যাচাইকরণ লিঙ্কটি বৈধ নয় বা আর বিদ্যমান নেই।'
            }
            return render(request, 'accounts/email_verification_failure.html', context)
        
        # Get the email address object
        email_address = confirmation.email_address
        
        # Check if already verified
        if email_address.verified:
            context = {
                'title': 'Already Verified',
                'error_type': 'already_verified',
                'error_message': 'এই ইমেইল ইতিমধ্যে যাচাই করা হয়েছে।',
                'email': email_address.email
            }
            return render(request, 'accounts/email_verification_success.html', context)
        
        # Verify the email address
        email_address.verified = True
        email_address.primary = True
        email_address.save()
        
        # Activate the user account
        user = email_address.user
        if not user.is_active:
            user.is_active = True
            user.save()
        
        # Auto-login the user
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        
        # Show success page
        context = {
            'title': 'Email Verified',
            'email': user.email,
            'next_url': request.GET.get('next') or 'accounts:profile'
        }
        messages.success(request, 'ইমেইল যাচাইকরণ সফল হয়েছে! আপনি এখন লগইন করেছেন।')
        return render(request, 'accounts/email_verification_success.html', context)
    
    except Exception as e:
        # Handle expired or invalid confirmations
        print(f"Email verification error: {e}")
        error_message = str(e).lower()
        
        if 'expired' in error_message or 'invalid' in error_message:
            error_type = 'expired'
            error_msg = 'যাচাইকরণ লিঙ্কের মেয়াদ শেষ হয়েছে। দয়া করে নতুন লিঙ্কের জন্য অনুরোধ করুন।'
        else:
            error_type = 'invalid'
            error_msg = 'যাচাইকরণ ব্যর্থ হয়েছে। দয়া করে আবার চেষ্টা করুন বা সাহায্য যোগাযোগ করুন।'
        
        context = {
            'title': 'Verification Failed',
            'error_type': error_type,
            'error_message': error_msg
        }
        return render(request, 'accounts/email_verification_failure.html', context)


@require_http_methods(["GET"])
@csrf_protect
def resend_verification_email(request):
    """Resend verification email to unverified users"""
    email = request.GET.get('email', '').strip()
    
    if not email:
        messages.error(request, 'ইমেইল ঠিকানা প্রদান করা হয়নি।')
        return redirect('accounts:login')
    
    try:
        user = User.objects.get(email=email)
        
        # If already verified, redirect to login
        if user.is_active:
            messages.info(request, 'এই ইমেইল ইতিমধ্যে যাচাই করা হয়েছে। আপনি এখন লগইন করতে পারেন।')
            return redirect('accounts:login')
        
        # Get or create EmailAddress
        email_address, created = EmailAddress.objects.get_or_create(
            user=user,
            email=email,
            defaults={'verified': False, 'primary': True}
        )
        
        # Send verification email
        try:
            confirmation = EmailConfirmationHMAC(email_address)
            activate_url = request.build_absolute_uri(
                f'/accounts/confirm-email/{confirmation.key}/'
            )
            
            email_context = {
                'user': user,
                'activate_url': activate_url,
                'email': user.email,
            }
            
            subject = f"{settings.ACCOUNT_EMAIL_SUBJECT_PREFIX}ইমেইল যাচাইকরণ (পুনরায় পাঠানো)"
            
            html_message = render_to_string(
                'account/email/email_confirmation_message.html',
                email_context
            )
            
            send_mail(
                subject,
                f'আপনার অ্যাকাউন্ট যাচাই করতে এই লিঙ্ক ভিজিট করুন: {activate_url}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(
                request,
                f'যাচাইকরণ ইমেইল {user.email} এ পাঠানো হয়েছে। '
                'দয়া করে আপনার ইনবক্স চেক করুন।'
            )
        except Exception as e:
            print(f"Error resending email: {e}")
            messages.error(request, 'ইমেইল পাঠানোর সময় সমস্যা হয়েছে। দয়া করে পরে চেষ্টা করুন।')
        
        return redirect('accounts:email-verification-sent')
    
    except User.DoesNotExist:
        messages.error(request, 'এই ইমেইল দিয়ে কোনো অ্যাকাউন্ট নেই।')
        return redirect('accounts:login')


@require_http_methods(["POST"])
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')


@login_required(login_url='accounts:login')
@require_http_methods(["GET"])
def profile_view(request):
    """Handle user profile viewing"""
    from django.db.models import Avg, Sum, Count
    
    # Get developer stats
    user_apps = request.user.apps.all()
    total_downloads = user_apps.aggregate(total=Sum('downloads'))['total'] or 0
    avg_rating = user_apps.aggregate(avg=Avg('reviews__rating'))['avg']
    total_reviews = sum(app.reviews.count() for app in user_apps)
    
    context = {
        'title': 'My Profile',
        'user': request.user,
        'user_apps': user_apps,
        'total_downloads': total_downloads,
        'avg_rating': avg_rating or 0.0,
        'total_reviews': total_reviews,
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(["GET", "POST"])
@csrf_protect
def edit_profile_view(request):
    """Handle user profile editing"""
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    context = {
        'form': form,
        'title': 'Edit Profile',
    }
    return render(request, 'accounts/edit_profile.html', context)
