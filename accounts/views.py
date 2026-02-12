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
from .models import User, PasswordResetOTP
from .forms import SignUpForm, LoginForm, ProfileUpdateForm
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
            # Already verified - show success page
            context = {
                'title': 'Email Already Verified',
                'email': email_address.email,
                'already_verified': True,
            }
            messages.info(request, 'এই ইমেইল ইতিমধ্যে যাচাই করা হয়েছে এবং আপনার অ্যাকাউন্ট সক্রিয়।')
            return render(request, 'accounts/email_verification_success.html', context)
        
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
        
        # Show success page with redirect info
        context = {
            'title': 'Email Verified',
            'email': user.email,
        }
        messages.success(request, '✓ ইমেইল যাচাইকরণ সফল! আপনার অ্যাকাউন্ট এখন সক্রিয়।')
        return render(request, 'accounts/email_verification_success.html', context)
    
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

