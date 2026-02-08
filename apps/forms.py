from django import forms
from .models import App, AppVersion


class AppUploadForm(forms.ModelForm):
    """Form for uploading a new app"""
    
    class Meta:
        model = App
        fields = [
            'title',
            'slug',
            'category',
            'platform',
            'short_description',
            'description',
            'version',
            'size_mb',
            'cover_image',
            'apk_file',
            'download_link',
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
            'platform': forms.Select(attrs={
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
