from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from .models import User, PasswordResetOTP, AccountDeletionOTP
from .forms import SignUpForm, LoginForm, ProfileUpdateForm
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)



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
            login(request, form.user, backend='django.contrib.auth.backends.ModelBackend')
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
            # Use get_or_create to avoid IntegrityError if it already exists
            try:
                email_address, created = EmailAddress.objects.get_or_create(
                    user=user,
                    email=user.email,
                    defaults={
                        'verified': False,
                        'primary': True
                    }
                )
                
                # If it already existed but wasn't primary, make it primary
                if not created and not email_address.primary:
                    # Delete other primary emails for this user
                    EmailAddress.objects.filter(user=user, primary=True).exclude(id=email_address.id).delete()
                    # Update this one to be primary
                    email_address.primary = True
                    email_address.verified = False
                    email_address.save()
                    
            except Exception as e:
                print(f"[ERROR] Failed to create EmailAddress during signup: {e}")
                messages.error(request, 'Account created but email setup failed. Please contact support.')
                return redirect('accounts:email-verification-sent')
            
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
                # Log error with full details for debugging
                logger.error(f"[SIGNUP EMAIL ERROR] Failed to send confirmation email to {user.email}: {str(e)}", exc_info=True)
                print(f"[ERROR] Error sending confirmation email: {e}")
            
            # Store referrer URL in session for post-verification redirect
            referrer = request.GET.get('next', request.POST.get('next'))
            if not referrer:
                # Try to get HTTP_REFERER if no next parameter
                http_referer = request.META.get('HTTP_REFERER', '')
                if http_referer and 'signup' not in http_referer:
                    referrer = http_referer
            
            if referrer:
                request.session['signup_referrer'] = referrer
            
            # Store email in session
            request.session['signup_email'] = user.email
            
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
    # Get email from session or find most recent unverified user
    email = request.session.get('signup_email')
    
    if not email:
        # Try to find the most recent unverified user
        try:
            unverified_user = User.objects.filter(is_active=False).order_by('-date_joined').first()
            if unverified_user:
                email = unverified_user.email
        except:
            pass
    
    context = {
        'title': 'Verify Your Email',
        'email': email,
    }
    return render(request, 'accounts/email_verification_sent.html', context)


@require_http_methods(["GET"])
def check_email_verification_status(request):
    """
    API endpoint to check if email has been verified
    Returns JSON with verification status and redirect URL
    """
    email = request.session.get('signup_email')
    
    if not email:
        return JsonResponse({
            'verified': False,
            'message': 'No email in session'
        })
    
    try:
        # Check if user exists and is active (verified)
        user = User.objects.get(email=email)
        
        if user.is_active and user.email_verified:
            # Email has been verified
            # Determine redirect URL
            redirect_url = request.session.pop('signup_referrer', None)
            
            # Clear email from session
            request.session.pop('signup_email', None)
            request.session.save()
            
            # If no referrer, default to profile
            if not redirect_url:
                redirect_url = '/accounts/profile/'
            
            return JsonResponse({
                'verified': True,
                'redirect_url': redirect_url,
                'message': 'Email verified successfully!'
            })
        else:
            return JsonResponse({
                'verified': False,
                'message': 'Email not yet verified'
            })
    
    except User.DoesNotExist:
        return JsonResponse({
            'verified': False,
            'message': 'User not found'
        })
    except Exception as e:
        return JsonResponse({
            'verified': False,
            'message': f'Error: {str(e)}'
        })


@require_http_methods(["GET"])
def email_confirmation_view(request, key):
    """
    Handle email verification via confirmation link
    User clicks link in email with verification key
    Redirects to profile after successful verification or shows error page
    """
    try:
        # Try to get and verify the confirmation
        try:
            confirmation = EmailConfirmationHMAC.from_key(key)
            print(f"[DEBUG] Confirmation key: {key}")
            print(f"[DEBUG] Confirmation object: {confirmation}")
        except Exception as e:
            print(f"[DEBUG] Error getting confirmation from key: {e}")
            confirmation = None
        
        if not confirmation:
            # Invalid or non-existent key
            print("[DEBUG] Confirmation is None/False - invalid key")
            context = {
                'title': 'Verification Failed',
                'error_type': 'invalid',
                'error_message': 'যাচাইকরণ লিঙ্কটি বৈধ নয় বা আর বিদ্যমান নেই।'
            }
            return render(request, 'accounts/email_verification_failure.html', context)
        
        # Get the email address object
        try:
            email_address = confirmation.email_address
            print(f"[DEBUG] Email address: {email_address}")
        except Exception as e:
            print(f"[DEBUG] Error getting email_address: {e}")
            raise
        
        # Check if already verified
        if email_address.verified:
            print(f"[DEBUG] Email already verified: {email_address.email}")
            # Already verified - just ensure user is logged in and redirect
            user = email_address.user
            
            # Auto-login the user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Store email in session
            request.session['signup_email'] = user.email
            request.session.save()
            
            messages.info(request, 'এই ইমেইল ইতিমধ্যে যাচাই করা হয়েছে এবং আপনার অ্যাকাউন্ট সক্রিয়।')
            
            # Redirect to email-verification-sent where polling will handle final redirect
            return redirect('accounts:email-verification-sent')
        
        # Verify the email address - handle duplicate email addresses first
        user = email_address.user
        
        # Delete any duplicate EmailAddress records with the same email (keep only this one)
        EmailAddress.objects.filter(email=email_address.email).exclude(id=email_address.id).delete()
        print(f"[DEBUG] Deleted duplicate EmailAddress records for: {email_address.email}")
        
        # Delete any other primary emails for this user
        EmailAddress.objects.filter(user=user, primary=True).exclude(id=email_address.id).delete()
        print(f"[DEBUG] Cleared other primary emails for user: {user.username}")
        
        # Now update this email as verified and primary using save()
        email_address.verified = True
        email_address.primary = True
        email_address.save()
        print(f"[DEBUG] Email verified and saved: {email_address.email}")
        
        # Mark user's email as verified in our User model
        user.email_verified = True
        
        # Activate the user account
        if not user.is_active:
            user.is_active = True
        
        user.save()
        print(f"[DEBUG] User activated: {user.username}")
        
        # Auto-login the user - refresh user object first
        user.refresh_from_db()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        print(f"[DEBUG] User logged in: {user.username}")
        
        # Store email and message in session so they persist through redirect
        request.session['signup_email'] = user.email
        request.session.save()
        
        # Show success message
        messages.success(request, '✓ ইমেইল যাচাইকরণ সফল! আপনার অ্যাকাউন্ট এখন সক্রিয়।')
        
        # Redirect to email-verification-sent page where polling will handle final redirect
        return redirect('accounts:email-verification-sent')
    
    except Exception as e:
        # Handle expired or invalid confirmations
        print(f"[ERROR] Email verification exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
        error_message = str(e).lower()
        
        if 'expired' in error_message or 'invalid' in error_message:
            error_type = 'expired'
            error_msg = 'যাচাইকরণ লিঙ্কের মেয়াদ শেষ হয়েছে। দয়া করে নতুন লিঙ্কের জন্য অনুরোধ করুন।'
        else:
            error_type = 'invalid'
            error_msg = f'যাচাইকরণ ব্যর্থ হয়েছে: {str(e)}'
        
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
        
        # Get or create EmailAddress - handle primary constraint
        email_address = None
        try:
            # Try to get existing EmailAddress for this user+email
            email_address = EmailAddress.objects.get(user=user, email=email)
        except EmailAddress.DoesNotExist:
            # Create new EmailAddress
            # Check if user already has a primary email
            has_primary = EmailAddress.objects.filter(user=user, primary=True).exists()
            
            email_address = EmailAddress.objects.create(
                user=user,
                email=email,
                verified=False,
                primary=not has_primary  # Only mark as primary if user doesn't have one
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
            logger.error(f"[RESEND EMAIL ERROR] Failed to resend confirmation email: {str(e)}", exc_info=True)
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
    from django.db.models import Count
    from django.utils import timezone
    from datetime import timedelta
    
    # Get favorites
    favorites = request.user.favorite_apps.all()[:6]
    total_favorites = request.user.favorite_apps.count()
    
    # Get download history (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_downloads = request.user.app_downloads.filter(
        downloaded_at__gte=thirty_days_ago
    ).select_related('app')[:10]
    total_downloads = request.user.app_downloads.count()
    
    # Get user reviews
    user_reviews = request.user.reviews.all()[:6]
    total_reviews = request.user.reviews.count()
    
    # Get login history (last login times)
    login_history = request.user.app_downloads.values(
        'downloaded_at'
    ).distinct()[:5] if request.user.app_downloads.exists() else []
    
    context = {
        'title': 'My Profile',
        'user': request.user,
        'favorites': favorites,
        'total_favorites': total_favorites,
        'recent_downloads': recent_downloads,
        'total_downloads': total_downloads,
        'user_reviews': user_reviews,
        'total_reviews': total_reviews,
        'last_login': request.user.last_login,
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


@login_required(login_url='accounts:login')
@require_http_methods(["GET", "POST"])
@csrf_protect
def settings_view(request):
    """Handle user settings"""
    
    if request.method == 'POST':
        # Handle settings updates
        notification_email = request.POST.get('notification_email') == 'on'
        notification_sms = request.POST.get('notification_sms') == 'on'
        
        # Update user preference
        user_profile = request.user.profile
        if hasattr(user_profile, 'notification_email'):
            user_profile.notification_email = notification_email
            user_profile.notification_sms = notification_sms
            user_profile.save()
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('accounts:settings')
    
    context = {
        'title': 'Settings',
        'user': request.user,
    }
    return render(request, 'accounts/settings.html', context)


# ==================== PASSWORD RESET VIEWS ====================

@require_http_methods(["GET", "POST"])
@csrf_protect
def password_reset_view(request):
    """Request password reset - user enters email"""
    from django.utils import timezone
    from datetime import timedelta
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'দয়া করে একটি ইমেইল ঠিকানা প্রদান করুন।')
            return render(request, 'accounts/password_reset.html')
        
        # Security check: If user is logged in, they can only reset for their own email
        if request.user.is_authenticated:
            if email != request.user.email:
                messages.error(request, 'আপনি আপনার সঠিক ইমেইল প্রদান করে নিজের অ্যাকাউন্টের পাসওয়ার্ড রিসেট করতে পারেন।')
                return render(request, 'accounts/password_reset.html')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate OTP
            otp = PasswordResetOTP.generate_otp()
            
            # Delete old OTP if exists and create new one
            PasswordResetOTP.objects.filter(user=user).delete()
            
            password_reset_otp = PasswordResetOTP.objects.create(
                user=user,
                otp=otp,
                expires_at=timezone.now() + timedelta(minutes=10),
                is_verified=False,
                attempts=0
            )
            
            # Send OTP via email
            try:
                subject = "আপনার পাসওয়ার্ড রিসেট কোড"
                
                email_context = {
                    'user': user,
                    'otp': otp,
                    'valid_time': '10 মিনিট'
                }
                
                html_message = render_to_string(
                    'accounts/email/password_reset_otp.html',
                    email_context
                )
                
                send_mail(
                    subject,
                    f'আপনার পাসওয়ার্ড রিসেট কোড: {otp}\n\nকোডটি 10 মিনিটের জন্য বৈধ।',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                messages.success(request, f'পাসওয়ার্ড রিসেট কোড {user.email} এ পাঠানো হয়েছে।')
                return redirect('accounts:password_reset_verify_otp', email=user.email)
            
            except Exception as e:
                logger.error(f"[PASSWORD RESET EMAIL ERROR] Failed to send OTP to {user.email}: {str(e)}", exc_info=True)
                print(f"Error sending OTP email: {e}")
                messages.error(request, 'ইমেইল পাঠানোর সময় সমস্যা হয়েছে। দয়া করে পরে চেষ্টা করুন।')
                return render(request, 'accounts/password_reset.html')
        
        except User.DoesNotExist:
            # Don't reveal if email exists or not (security)
            messages.info(request, 'যদি এই ইমেইলের সাথে একটি অ্যাকাউন্ট থাকে তবে একটি রিসেট কোড পাঠানো হয়েছে।')
            return render(request, 'accounts/password_reset.html')
    
    context = {'title': 'Reset Password'}
    return render(request, 'accounts/password_reset.html', context)


@require_http_methods(["GET", "POST"])
@csrf_protect
def password_reset_verify_otp_view(request, email):
    """Verify OTP for password reset"""
    from django.utils import timezone
    
    # Security check: If user is logged in, they can only reset for their own email
    if request.user.is_authenticated:
        if email != request.user.email:
            messages.error(request, 'আপনি শুধুমাত্র আপনার নিজের অ্যাকাউন্টের পাসওয়ার্ড পরিবর্তন করতে পারেন।')
            return redirect('accounts:profile')
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'অবৈধ ইমেইল ঠিকানা।')
        return redirect('accounts:password_reset')
    
    try:
        otp_record = user.password_reset_otp
    except PasswordResetOTP.DoesNotExist:
        messages.error(request, 'কোনো সক্রিয় পাসওয়ার্ড রিসেট রিকোয়েস্ট নেই। নতুন রিকোয়েস্ট শুরু করুন।')
        return redirect('accounts:password_reset')
    
    # Check if OTP is expired
    if otp_record.is_expired():
        otp_record.delete()
        messages.error(request, 'OTP এর মেয়াদ শেষ হয়েছে। একটি নতুন কোড পান।')
        return redirect('accounts:password_reset')
    
    # Check if locked due to too many attempts
    if otp_record.is_locked():
        messages.error(request, 'অনেক ব্যর্থ প্রচেষ্টা। পরে চেষ্টা করুন।')
        return redirect('accounts:password_reset')
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        
        if not entered_otp:
            messages.error(request, 'দয়া করে OTP কোড প্রবেশ করুন।')
            return render(request, 'accounts/password_reset_verify_otp.html', {'email': email})
        
        if entered_otp == otp_record.otp:
            # OTP verified
            otp_record.is_verified = True
            otp_record.save()
            messages.success(request, 'OTP যাচাই সফল! এখন আপনার নতুন পাসওয়ার্ড সেট করুন।')
            return redirect('accounts:password_reset_new_password', email=email)
        else:
            # Increment attempts
            otp_record.increment_attempts()
            remaining = otp_record.max_attempts - otp_record.attempts
            messages.error(request, f'ভুল OTP। অবশিষ্ট প্রচেষ্টা: {remaining}')
            return render(request, 'accounts/password_reset_verify_otp.html', {'email': email})
    
    context = {
        'title': 'Verify OTP',
        'email': email,
    }
    return render(request, 'accounts/password_reset_verify_otp.html', context)


@require_http_methods(["GET", "POST"])
@csrf_protect
def password_reset_new_password_view(request, email):
    """Set new password after OTP verification"""
    
    # Security check: If user is logged in, they can only reset for their own email
    if request.user.is_authenticated:
        if email != request.user.email:
            messages.error(request, 'আপনি শুধুমাত্র আপনার নিজের অ্যাকাউন্টের পাসওয়ার্ড পরিবর্তন করতে পারেন।')
            return redirect('accounts:profile')
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'অবৈধ ইমেইল ঠিকানা।')
        return redirect('accounts:password_reset')
    
    try:
        otp_record = user.password_reset_otp
    except PasswordResetOTP.DoesNotExist:
        messages.error(request, 'কোনো সক্রিয় পাসওয়ার্ড রিসেট রিকোয়েস্ট নেই।')
        return redirect('accounts:password_reset')
    
    # Check if OTP is verified
    if not otp_record.is_verified:
        messages.error(request, 'দয়া করে প্রথমে OTP যাচাই করুন।')
        return redirect('accounts:password_reset_verify_otp', email=email)
    
    # Check if OTP is expired
    if otp_record.is_expired():
        otp_record.delete()
        messages.error(request, 'OTP এর মেয়াদ শেষ হয়েছে।')
        return redirect('accounts:password_reset')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if not new_password or not confirm_password:
            messages.error(request, 'দয়া করে পাসওয়ার্ড প্রবেশ করুন।')
            return render(request, 'accounts/password_reset_new_password.html', {'email': email})
        
        if new_password != confirm_password:
            messages.error(request, 'পাসওয়ার্ড মিলছে না।')
            return render(request, 'accounts/password_reset_new_password.html', {'email': email})
        
        if len(new_password) < 8:
            messages.error(request, 'পাসওয়ার্ড কমপক্ষে 8 অক্ষর দীর্ঘ হতে হবে।')
            return render(request, 'accounts/password_reset_new_password.html', {'email': email})
        
        # Update password and delete OTP
        user.set_password(new_password)
        user.save()
        otp_record.delete()
        
        messages.success(request, 'পাসওয়ার্ড সফলভাবে পরিবর্তন হয়েছে! এখন লগইন করুন।')
        return redirect('accounts:login')
    
    context = {
        'title': 'Set New Password',
        'email': email,
    }
    return render(request, 'accounts/password_reset_new_password.html', context)


@login_required(login_url='accounts:login')
@login_required(login_url='accounts:login')
@require_http_methods(["GET", "POST"])
@csrf_protect
def delete_account_request_view(request):
    """Handle user account deletion request - initiate 3-day countdown"""
    user = request.user
    
    if request.method == 'POST':
        # Generate OTP
        otp = AccountDeletionOTP.generate_otp()
        expires_at = timezone.now() + timedelta(minutes=10)  # OTP expires in 10 minutes
        
        # Delete any existing OTP and create a new one
        AccountDeletionOTP.objects.filter(user=user).delete()
        
        deletion_otp = AccountDeletionOTP.objects.create(
            user=user,
            otp=otp,
            expires_at=expires_at,
            is_verified=False,
            attempts=0,
        )
        
        # Send OTP email
        try:
            email_context = {
                'username': user.username,
                'otp': otp,
                'expires_in': '10 minutes',
            }
            email_html = render_to_string('accounts/email/deletion_otp.html', email_context)
            send_mail(
                '🔐 Account Deletion Verification Code - JnDroid Store',
                f'Your OTP is: {otp}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=email_html,
                fail_silently=False,
            )
            messages.info(request, '📧 Verification code sent to your email. Please check your inbox.')
            return redirect('accounts:verify_delete_otp')
        except Exception as e:
            logger.error(f"Failed to send deletion OTP email to {user.email}: {str(e)}")
            messages.error(request, 'Failed to send verification code. Please try again.')
            return redirect('accounts:profile')
    
    context = {
        'title': 'Delete Account',
        'user': request.user,
    }
    return render(request, 'accounts/delete_account_request.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(["GET", "POST"])
@csrf_protect
def verify_delete_otp_view(request):
    """Handle OTP verification for account deletion"""
    user = request.user
    
    try:
        deletion_otp = AccountDeletionOTP.objects.get(user=user)
    except AccountDeletionOTP.DoesNotExist:
        messages.error(request, 'No deletion request found. Please start over.')
        return redirect('accounts:profile')
    
    # Check if OTP is already verified
    if deletion_otp.is_verified:
        messages.info(request, 'Your deletion request has already been verified.')
        return redirect('accounts:confirm_delete')
    
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        
        # Check if locked
        if deletion_otp.is_locked():
            messages.error(request, '❌ Too many attempts. Please request a new code.')
            deletion_otp.delete()
            return redirect('accounts:delete_account_request')
        
        # Check if expired
        if deletion_otp.is_expired():
            messages.error(request, '⏰ Verification code has expired. Please request a new one.')
            deletion_otp.delete()
            return redirect('accounts:delete_account_request')
        
        # Verify OTP
        if otp == deletion_otp.otp:
            deletion_otp.is_verified = True
            deletion_otp.save()
            
            messages.success(request, '✓ Verification successful!')
            return redirect('accounts:confirm_delete')
        else:
            deletion_otp.increment_attempts()
            remaining_attempts = deletion_otp.max_attempts - deletion_otp.attempts
            
            if remaining_attempts > 0:
                messages.error(request, f'❌ Incorrect code. {remaining_attempts} attempts remaining.')
            else:
                messages.error(request, '❌ Too many attempts. Please request a new code.')
                deletion_otp.delete()
                return redirect('accounts:delete_account_request')
            
            return redirect('accounts:verify_delete_otp')
    
    # Calculate OTP expiration time
    time_remaining = (deletion_otp.expires_at - timezone.now()).total_seconds()
    minutes_remaining = int(time_remaining / 60)
    
    context = {
        'title': 'Verify Deletion',
        'user': request.user,
        'minutes_remaining': max(0, minutes_remaining),
        'attempts_remaining': deletion_otp.max_attempts - deletion_otp.attempts,
    }
    return render(request, 'accounts/verify_delete_otp.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(["GET", "POST"])
@csrf_protect
def confirm_delete_view(request):
    """Show confirmation page with 3-day countdown before deletion"""
    user = request.user
    
    # Check if user already has a pending deletion
    if user.is_pending_deletion:
        # Delete from database
        user_id = user.id
        username = user.username
        email = user.email
        
        # Send final deletion email
        try:
            email_context = {
                'username': username,
                'date': timezone.now().strftime('%B %d, %Y at %H:%M %Z'),
            }
            email_html = render_to_string('accounts/email/account_deletion_confirmation.html', email_context)
            send_mail(
                '❌ Account Permanently Deleted - JnDroid Store',
                'Your account has been permanently deleted.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                html_message=email_html,
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send final deletion email: {str(e)}")
        
        # Delete user
        user.delete()
        logout(request)
        messages.success(request, '✓ Your account has been permanently deleted.')
        return redirect('home')
    
    # Check if OTP is verified
    try:
        deletion_otp = AccountDeletionOTP.objects.get(user=user)
        if not deletion_otp.is_verified:
            messages.error(request, 'Please verify your OTP first.')
            return redirect('accounts:verify_delete_otp')
    except AccountDeletionOTP.DoesNotExist:
        messages.error(request, 'No deletion request found.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        if action == 'confirm':
            # Set account as pending deletion
            deletion_time = timezone.now() + timedelta(days=3)
            user.is_pending_deletion = True
            user.deletion_requested_at = timezone.now()
            user.deletion_scheduled_at = deletion_time
            user.save()
            
            # Delete the OTP record
            deletion_otp.delete()
            
            # Send notification email
            try:
                email_context = {
                    'username': user.username,
                    'deletion_date': deletion_time.strftime('%B %d, %Y at %H:%M'),
                    'support_link': request.build_absolute_uri('/support/'),
                }
                email_html = render_to_string('accounts/email/deletion_scheduled.html', email_context)
                send_mail(
                    '⏳ Your Account Will Be Deleted in 3 Days - JnDroid Store',
                    'Your account deletion has been scheduled for 3 days from now.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=email_html,
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Failed to send deletion scheduled email: {str(e)}")
            
            messages.success(request, f'✓ Your account will be deleted on {deletion_time.strftime("%B %d, %Y")}. You can still login and cancel during the 3-day period.')
            return redirect('accounts:profile')
        
        elif action == 'cancel':
            deletion_otp.delete()
            messages.info(request, 'Account deletion cancelled.')
            return redirect('accounts:profile')
    
    # Calculate countdown
    countdown_days = 3
    
    context = {
        'title': 'Confirm Account Deletion',
        'user': request.user,
        'countdown_days': countdown_days,
        'deletion_date': timezone.now() + timedelta(days=3),
    }
    return render(request, 'accounts/confirm_delete.html', context)


@login_required(login_url='accounts:login')
@require_http_methods(["POST"])
@csrf_protect
def cancel_delete_account_view(request):
    """Cancel pending account deletion"""
    user = request.user
    
    if user.is_pending_deletion:
        user.is_pending_deletion = False
        user.deletion_requested_at = None
        user.deletion_scheduled_at = None
        user.save()
        
        # Clean up any remaining OTP records
        AccountDeletionOTP.objects.filter(user=user).delete()
        
        # Send cancellation email
        try:
            email_context = {
                'username': user.username,
            }
            email_html = render_to_string('accounts/email/deletion_cancelled.html', email_context)
            send_mail(
                '✓ Your Account Deletion Has Been Cancelled - JnDroid Store',
                'Your account deletion has been cancelled.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=email_html,
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send deletion cancellation email: {str(e)}")
        
        messages.success(request, '✓ Your account deletion has been cancelled. Your account is now active.')
    else:
        messages.info(request, 'No active deletion request found.')
    
    return redirect('accounts:profile')


def delete_account_view(request):
    """Permanently delete user account (called by management command)"""
    user = request.user
    username = user.username
    email = user.email
    
    # Send deletion confirmation email
    try:
        email_context = {
            'username': username,
            'date': timezone.now().strftime('%B %d, %Y at %H:%M %Z'),
        }
        email_html = render_to_string('accounts/email/account_deletion_confirmation.html', email_context)
        send_mail(
            '❌ Account Deleted - JnDroid Store',
            'Your account has been permanently deleted.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            html_message=email_html,
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Failed to send deletion email to {email}: {str(e)}")
    
    # Delete user account
    user.delete()
    
    # Logout
    logout(request)
    
    messages.success(request, '✓ Your account has been permanently deleted. All your data has been removed.')
    return redirect('home')
