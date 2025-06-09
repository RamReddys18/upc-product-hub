
from django import forms
from .models import Product, ProductAttribute, Category, Size

class ProductForm(forms.ModelForm):
    # Custom size field that allows adding new sizes
    custom_size = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter new size if not in dropdown'})
    )
    
    # Custom category field that allows adding new categories
    custom_category = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter new category if not in dropdown'})
    )
    
    class Meta:
        model = Product
        fields = ['name', 'upc', 'ean', 'brand_name', 'description', 'size', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'upc': forms.TextInput(attrs={'class': 'form-control', 'style': 'text-transform: uppercase;'}),
            'ean': forms.TextInput(attrs={'class': 'form-control', 'style': 'text-transform: uppercase;'}),
            'brand_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'size': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['size'].queryset = Size.objects.all()
        self.fields['category'].queryset = Category.objects.all()
        
        # Make size and category not required since we have custom fields
        self.fields['size'].required = False
        self.fields['category'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        size = cleaned_data.get('size')
        custom_size = cleaned_data.get('custom_size')
        category = cleaned_data.get('category')
        custom_category = cleaned_data.get('custom_category')
        
        # Handle custom size
        if custom_size and not size:
            size_obj, created = Size.objects.get_or_create(name=custom_size.strip())
            cleaned_data['size'] = size_obj
        elif not size and not custom_size:
            raise forms.ValidationError("Please select a size or enter a custom size.")
        
        # Handle custom category
        if custom_category and not category:
            category_obj, created = Category.objects.get_or_create(name=custom_category.strip())
            cleaned_data['category'] = category_obj
        elif not category and not custom_category:
            raise forms.ValidationError("Please select a category or enter a custom category.")
        
        return cleaned_data

class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ['key', 'value']
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Country of Origin'}),
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., United States'}),
        }

# Formset for handling multiple attributes
ProductAttributeFormSet = forms.inlineformset_factory(
    Product, 
    ProductAttribute, 
    form=ProductAttributeForm,
    extra=1,
    can_delete=True
)

class ReviewForm(forms.Form):
    ACTION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.RadioSelect)
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        help_text="Required only when rejecting a product"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')
        
        if action == 'reject' and not rejection_reason:
            raise forms.ValidationError("Rejection reason is required when rejecting a product.")
        
        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }
