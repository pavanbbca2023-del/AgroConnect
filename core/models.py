from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('company', 'Company'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(
            regex=r'^[+]?[0-9]{10,15}$',
            message='Phone number must be 10-15 digits, optionally starting with +'
        )]
    )
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

class FarmerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    farm_size = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text="Farm size in acres"
    )
    
    def __str__(self):
        return f"Farmer: {self.user_profile.user.get_full_name() or self.user_profile.user.username}"

class CompanyProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    registration_number = models.CharField(
        max_length=50, 
        unique=True,
        db_index=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]{6,20}$',
            message='Registration number must be 6-20 characters, alphanumeric uppercase only'
        )]
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['registration_number'],
                name='unique_company_registration'
            )
        ]
    
    def __str__(self):
        return self.company_name

class WasteProduct(models.Model):
    CROP_CHOICES = [
        ('rice', 'Rice Residue'),
        ('corn', 'Corn Residue'),
        ('wheat', 'Wheat Residue'),
        ('sugarcane', 'Sugarcane Residue'),
        ('cotton', 'Cotton Residue'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('reserved', 'Reserved'),
    ]
    
    farmer = models.ForeignKey(FarmerProfile, on_delete=models.CASCADE, related_name='waste_products')
    crop_name = models.CharField(max_length=20, choices=CROP_CHOICES)
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text="Quantity in tons"
    )
    price_per_ton = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    location = models.CharField(max_length=200, help_text="Location where waste is available")
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_crop_name_display()} - {self.quantity} tons by {self.farmer}"
    
    def get_absolute_url(self):
        return reverse('waste_detail', kwargs={'pk': self.pk})
    
    @property
    def total_value(self):
        return self.quantity * self.price_per_ton

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='orders')
    waste_product = models.ForeignKey(WasteProduct, on_delete=models.CASCADE, related_name='orders')
    quantity_ordered = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, help_text="Additional notes from company")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.company.company_name} - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        from django.db import transaction
        with transaction.atomic():
            if not self.total_price:
                self.total_price = self.quantity_ordered * self.waste_product.price_per_ton
            super().save(*args, **kwargs)