import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agroconnect.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import UserProfile, FarmerProfile, CompanyProfile

print("=== Database Check ===")
print(f"Users: {User.objects.count()}")
print(f"UserProfiles: {UserProfile.objects.count()}")
print(f"FarmerProfiles: {FarmerProfile.objects.count()}")
print(f"CompanyProfiles: {CompanyProfile.objects.count()}")

print("\n=== User Details ===")
for user in User.objects.all():
    print(f"User: {user.username} - {user.email}")
    try:
        profile = user.userprofile
        print(f"  Profile: {profile.role} - {profile.phone}")
        if profile.role == 'farmer':
            farmer = profile.farmerprofile
            print(f"  Farmer: {farmer.farm_size} acres")
        elif profile.role == 'company':
            company = profile.companyprofile
            print(f"  Company: {company.company_name} - {company.registration_number}")
    except:
        print("  No profile found")
    print()