from django import forms
from django.core.exceptions import ValidationError
from .models import App, AppVersion
import os


class AppUploadForm(forms.ModelForm):
    """Form for uploading a new app with comprehensive validation"""
    
    # File size limits (in bytes)
    MAX_APK_SIZE = 500 * 1024 * 1024  # 500 MB
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    # Allowed file extensions
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    ALLOWED_APP_EXTENSIONS = {'.apk', '.exe', '.ipa'}
    
    def __init__(self, *args, user=None, **kwargs):
        """Initialize form with user for conditional field disabling"""
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Pre-fill developer info from user profile if user is provided
        if user:
            # Get full name from user profile
            full_name = user.get_full_name() or user.username
            
            # Pre-fill developer info
            self.fields['developer_name'].initial = full_name
            self.fields['developer_email'].initial = user.email
            self.fields['support_email'].initial = user.email
            
            # If user is not superuser, disable developer info fields
            if not user.is_superuser:
                self.fields['developer_name'].widget.attrs['disabled'] = True
                self.fields['developer_name'].widget.attrs['readonly'] = True
                self.fields['developer_email'].widget.attrs['disabled'] = True
                self.fields['developer_email'].widget.attrs['readonly'] = True
                self.fields['support_email'].widget.attrs['disabled'] = True
                self.fields['support_email'].widget.attrs['readonly'] = True
                
                # Add help text explaining why fields are disabled
                self.fields['developer_name'].help_text = "Read-only (account info). Contact admin to change."
                self.fields['developer_email'].help_text = "Read-only (account email). Contact admin to change."
                self.fields['support_email'].help_text = "Read-only (account email). Contact admin to change."
            else:
                # For superusers, add help text showing these can be edited
                self.fields['developer_name'].help_text = "Editable (superuser access)"
                self.fields['developer_email'].help_text = "Editable (superuser access)"
                self.fields['support_email'].help_text = "Editable (superuser access)"
    
    def clean_cover_image(self):
        """Validate cover image file size and format"""
        cover_image = self.cleaned_data.get('cover_image')
        if cover_image:
            # Check file size
            if cover_image.size > self.MAX_IMAGE_SIZE:
                raise ValidationError(
                    f"Image file is too large. Maximum size is 10 MB. "
                    f"Your file is {cover_image.size / (1024 * 1024):.2f} MB."
                )
            
            # Check file extension
            ext = os.path.splitext(cover_image.name)[1].lower()
            if ext not in self.ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError(
                    f"Image format '{ext}' is not allowed. "
                    f"Please use JPG, PNG, GIF, or WebP."
                )
        return cover_image
    
    def clean_apk_file(self):
        """Validate APK/app file size and format"""
        apk_file = self.cleaned_data.get('apk_file')
        if apk_file:
            # Check file size
            if apk_file.size > self.MAX_APK_SIZE:
                raise ValidationError(
                    f"App file is too large. Maximum size is 500 MB. "
                    f"Your file is {apk_file.size / (1024 * 1024):.2f} MB."
                )
            
            # Check file extension
            ext = os.path.splitext(apk_file.name)[1].lower()
            if ext not in self.ALLOWED_APP_EXTENSIONS:
                raise ValidationError(
                    f"File format '{ext}' is not allowed. "
                    f"Please use APK, EXE, or IPA."
                )
        return apk_file
    
    def clean(self):
        """Validate that at least one download option is provided"""
        cleaned_data = super().clean()
        apk_file = cleaned_data.get('apk_file')
        download_link = cleaned_data.get('download_link')
        
        if not apk_file and not download_link:
            raise ValidationError(
                "Please provide either an APK file upload or an external download link."
            )
        
        # Validate price for paid apps
        is_free = cleaned_data.get('is_free')
        price = cleaned_data.get('price')
        
        if not is_free and not price:
            raise ValidationError(
                "Please enter a price for paid apps."
            )
        
        if is_free and price:
            cleaned_data['price'] = None  # Clear price for free apps
        
        # Restore disabled developer fields from initial values for non-superusers
        if self.user and not self.user.is_superuser:
            cleaned_data['developer_name'] = self.user.get_full_name() or self.user.username
            cleaned_data['developer_email'] = self.user.email
            cleaned_data['support_email'] = self.user.email
        
        return cleaned_data
    
    class Meta:
        model = App
        fields = [
            'title',
            'slug',
            'category',
            'short_description',
            'description',
            'version',
            'size_mb',
            'min_api_level',
            'target_api_level',
            'min_android_version',
            'target_android_version',
            'cover_image',
            'apk_file',
            'download_link',
            'file_hash',
            'developer_name',
            'developer_email',
            'support_email',
            'website_url',
            'privacy_policy_url',
            'terms_url',
            'age_rating',
            'is_free',
            'price',
            'has_iap',
            'source_url',
            'store_name',
            'store_email',
            'is_published',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'App Name',
                'required': 'required',
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'app-slug-name',
                'required': 'required',
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required',
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description (max 220 characters)',
                'rows': 2,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Detailed description of your app',
                'rows': 5,
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1.0.0',
            }),
            'size_mb': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Size in MB',
                'step': '0.01',
            }),
            'min_api_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum API level (e.g., 21)',
            }),
            'target_api_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Target API level (e.g., 35)',
            }),
            'min_android_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 5.0 (Lollipop)',
            }),
            'target_android_version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 15.0 (VanillaIceCream)',
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'apk_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.apk,.exe,.ipa',
            }),
            'download_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://drive.google.com/... (optional)',
            }),
            'file_hash': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SHA256 hash (optional)',
            }),
            'developer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your company/developer name',
            }),
            'developer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'developer@example.com',
            }),
            'support_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'support@example.com',
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.example.com',
            }),
            'privacy_policy_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/privacy',
            }),
            'terms_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/terms',
            }),
            'age_rating': forms.Select(attrs={
                'class': 'form-control',
            }),
            'is_free': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '9.99',
                'step': '0.01',
            }),
            'has_iap': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'source_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/... (optional)',
            }),
            'store_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Google Play, App Store, GitHub',
            }),
            'store_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@yourstore.com',
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class AppVersionForm(forms.ModelForm):
    """Form for adding app versions"""
    
    class Meta:
        model = AppVersion
        fields = [
            'version_number',
            'description',
            'size_mb',
            'apk_file',
            'download_link',
            'is_active',
        ]
        widgets = {
            'version_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1.0.1',
                'required': 'required',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'What changed in this version?',
                'rows': 3,
            }),
            'size_mb': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Size in MB',
                'step': '0.01',
            }),
            'apk_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.apk,.exe,.ipa',
            }),
            'download_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://...',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
