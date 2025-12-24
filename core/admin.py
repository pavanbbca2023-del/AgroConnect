from django.contrib import admin
from .models import UserProfile, FarmerProfile, CompanyProfile, WasteProduct, Order, PriceBargain

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['user_profile', 'farm_size']
    search_fields = ['user_profile__user__username']

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'registration_number', 'user_profile']
    search_fields = ['company_name', 'registration_number']

@admin.register(WasteProduct)
class WasteProductAdmin(admin.ModelAdmin):
    list_display = ['crop_name', 'quantity', 'admin_price_per_ton', 'farmer', 'status', 'created_at']
    list_filter = ['crop_name', 'status', 'created_at']
    search_fields = ['farmer__user_profile__user__username']
    fields = ['farmer', 'crop_name', 'quantity', 'admin_price_per_ton', 'location', 'description', 'photo', 'status']
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'company', 'waste_product', 'quantity_ordered', 'company_price_per_ton', 'total_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['company__company_name']
    readonly_fields = ['total_price']

@admin.register(PriceBargain)
class PriceBargainAdmin(admin.ModelAdmin):
    list_display = ['waste_product', 'farmer_proposed_price', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['waste_product__crop_name']