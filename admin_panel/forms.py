from django import forms
from core.models import Product, Category


class ProductForm(forms.ModelForm):
    """Form for creating/editing products"""
    class Meta:
        model = Product
        fields = ['name', 'slug', 'category', 'price', 'description', 'image', 
                  'weight', 'rating', 'is_featured', 'is_special', 'is_available', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'admin-input'}),
            'slug': forms.TextInput(attrs={'class': 'admin-input'}),
            'category': forms.Select(attrs={'class': 'admin-select'}),
            'price': forms.NumberInput(attrs={'class': 'admin-input', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 4}),
            'weight': forms.TextInput(attrs={'class': 'admin-input', 'placeholder': 'e.g., 500gm'}),
            'rating': forms.NumberInput(attrs={'class': 'admin-input', 'step': '0.1', 'min': '0', 'max': '5'}),
            'stock': forms.NumberInput(attrs={'class': 'admin-input', 'min': '0'}),
        }


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories"""
    class Meta:
        model = Category
        fields = ['name', 'slug', 'image', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'admin-input'}),
            'slug': forms.TextInput(attrs={'class': 'admin-input'}),
            'description': forms.Textarea(attrs={'class': 'admin-textarea', 'rows': 3}),
        }
