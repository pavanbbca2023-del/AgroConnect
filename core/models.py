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
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
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
    admin_price_per_ton = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price set by admin for farmers"
    )
    farmer_price_per_ton = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price set by farmer (can bargain from admin price)",
        null=True,
        blank=True
    )
    location = models.CharField(max_length=200, help_text="Location where waste is available")
    description = models.TextField()
    photo = models.ImageField(upload_to='waste_photos/', blank=True, null=True)
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
    def effective_price(self):
        return self.farmer_price_per_ton or self.admin_price_per_ton
    
    @property
    def total_value(self):
        return self.quantity * self.effective_price

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending_admin', 'Pending Admin Review'),
        ('sent_to_farmer', 'Sent to Farmer'),
        ('accepted_by_farmer', 'Accepted by Farmer'),
        ('rejected_by_farmer', 'Rejected by Farmer'),
        ('approved_by_admin', 'Final Admin Approval'),
        ('completed', 'Completed'),
    ]
    
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='orders')
    waste_product = models.ForeignKey(WasteProduct, on_delete=models.CASCADE, related_name='orders')
    quantity_ordered = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    company_price_per_ton = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price offered by company"
    )
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_admin')
    notes = models.TextField(blank=True, help_text="Additional notes from company")
    admin_notes = models.TextField(blank=True, help_text="Admin's notes")
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
                self.total_price = self.quantity_ordered * self.company_price_per_ton
            super().save(*args, **kwargs)

class PriceBargain(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    waste_product = models.ForeignKey(WasteProduct, on_delete=models.CASCADE, related_name='bargains')
    farmer_proposed_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Price proposed by farmer"
    )
    admin_counter_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Counter price by admin",
        null=True,
        blank=True
    )
    farmer_message = models.TextField(help_text="Farmer's bargaining message")
    admin_message = models.TextField(blank=True, help_text="Admin's response message")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bargain #{self.id} - {self.waste_product.crop_name} - {self.get_status_display()}"