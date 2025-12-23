from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import WasteProduct, Order

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(
        max_length=15, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +1234567890 or 1234567890'}),
        help_text="Phone number must be 10-15 digits, optionally starting with +"
    )
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=True)
    
    # Farmer specific fields
    farm_size = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        min_value=0.01,
        help_text="Farm size in acres (for farmers only)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    # Company specific fields
    company_name = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    registration_number = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user_type = kwargs.pop('user_type', None)
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        
        # Make farm_size required for farmers
        if self.user_type == 'farmer':
            self.fields['farm_size'].required = True
        # Make company fields required for companies
        elif self.user_type == 'company':
            self.fields['company_name'].required = True
            self.fields['registration_number'].required = True
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        import re
        if not re.match(r'^[+]?[0-9]{10,15}$', phone):
            raise ValidationError("Phone number must be 10-15 digits, optionally starting with +")
        return phone
    
    def clean_registration_number(self):
        registration_number = self.cleaned_data.get('registration_number')
        if self.user_type == 'company' and registration_number:
            import re
            if not re.match(r'^[A-Z0-9]{6,20}$', registration_number):
                raise ValidationError("Registration number must be 6-20 characters, alphanumeric uppercase only")
        return registration_number
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class WasteProductForm(forms.ModelForm):
    class Meta:
        model = WasteProduct
        fields = ['crop_name', 'quantity', 'price_per_ton', 'location', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'class': 'form-control'}),
            'price_per_ton': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'class': 'form-control'}),
            'crop_name': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'crop_name': 'Crop Type',
            'quantity': 'Quantity (tons)',
            'price_per_ton': 'Price per Ton (₹)',
            'location': 'Location',
            'description': 'Description',
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['quantity_ordered', 'notes']
        widgets = {
            'quantity_ordered': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0.01', 
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'Any additional notes or requirements...'
            }),
        }
        labels = {
            'quantity_ordered': 'Quantity (tons)',
            'notes': 'Additional Notes (Optional)',
        }
    
    def __init__(self, *args, **kwargs):
        self.waste_product = kwargs.pop('waste_product', None)
        super().__init__(*args, **kwargs)
        if self.waste_product:
            self.fields['quantity_ordered'].widget.attrs['max'] = str(self.waste_product.quantity)
    
    def clean_quantity_ordered(self):
        quantity = self.cleaned_data.get('quantity_ordered')
        if self.waste_product and quantity > self.waste_product.quantity:
            raise ValidationError(f"Quantity cannot exceed available stock ({self.waste_product.quantity} tons)")
        return quantity