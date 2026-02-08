from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class SignUpForm(forms.ModelForm):
    """Form for user registration with password validation"""
    
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'required': 'required',
        }),
        help_text='At least 8 characters'
    )
    
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': 'required',
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
                'required': 'required',
            }),
        }
    
    def clean_username(self):
        """Check if username already exists"""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists')
        return username
    
    def clean_email(self):
        """Check if email already exists"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email
    
    def clean_password1(self):
        """Validate password strength"""
        password1 = self.cleaned_data.get('password1')
        
        if len(password1) < 8:
            raise forms.ValidationError('Password must be at least 8 characters')
        
        # Check for common patterns
        if password1.isdigit():
            raise forms.ValidationError('Password cannot be entirely numeric')
        
        return password1
    
    def clean(self):
        """Check if passwords match"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Passwords do not match')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save user with hashed password"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        
        if commit:
            user.save()
        
        return user


class LoginForm(forms.Form):
    """Form for user login with authentication"""
    
    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or email',
            'required': 'required',
            'autofocus': 'autofocus',
        })
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'required': 'required',
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )
    
    def clean(self):
        """Authenticate user"""
        from django.contrib.auth.hashers import check_password
        
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        
        self.user = None
        self.unverified_email = None
        
        if username and password:
            # First, try to find user by username or email
            user = None
            try:
                # Try username first
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                try:
                    # Try email
                    user = User.objects.get(email=username)
                except User.DoesNotExist:
                    # User doesn't exist
                    raise forms.ValidationError('Invalid username/email or password')
            
            # Now check password
            if user and check_password(password, user.password):
                # Password is correct
                # Check if email is verified (is_active)
                if not user.is_active:
                    # Email is not verified - store email for modal display
                    self.unverified_email = user.email
                    raise forms.ValidationError('UNVERIFIED_EMAIL')
                
                # User is verified, set authenticated user
                self.user = user
            else:
                # Password is incorrect
                raise forms.ValidationError('Invalid username/email or password')
        
        return cleaned_data



class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'avatar']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number',
                'type': 'tel',
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }
    
    def clean_email(self):
        """Check if email is unique (except current user)"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is already in use')
        return email
