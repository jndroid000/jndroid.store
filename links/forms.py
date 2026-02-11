from django import forms
from .models import Link, LinkCategory


class LinkCategoryForm(forms.ModelForm):
    class Meta:
        model = LinkCategory
        fields = ['name', 'category_type', 'icon', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'category_type': forms.Select(attrs={'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., fa-github'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ['title', 'description', 'url', 'category', 'icon', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Link title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'icon': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
