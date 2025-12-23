from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView
from .models import UserProfile, FarmerProfile, CompanyProfile, WasteProduct, Order
from .forms import UserRegistrationForm, WasteProductForm, OrderForm

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

def home(request):
    return render(request, 'core/home.html')
def register_farmer(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, user_type='farmer')

        if form.is_valid():
            from django.db import transaction
            try:
                with transaction.atomic():
                    user = form.save()

                    profile = UserProfile.objects.create(
                        user=user,
                        role='farmer',
                        phone=form.cleaned_data['phone'],
                        address=form.cleaned_data['address']
                    )

                    FarmerProfile.objects.create(
                        user_profile=profile,
                        farm_size=form.cleaned_data['farm_size']
                    )

                    login(request, user)
                    messages.success(request, "Farmer registered successfully!")
                    return redirect('dashboard')

            except Exception as e:
                messages.error(request, f"Registration failed: {e}")

        else:
            # 🔥 THIS WAS MISSING
            print("FORM ERRORS:", form.errors)
            messages.error(request, "Please correct the errors below.")

    else:
        form = UserRegistrationForm(user_type='farmer')

    # 🔥 THIS RETURN IS MANDATORY
    return render(request, 'registration/register_farmer.html', {'form': form})

def register_company(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, user_type='company')
        if form.is_valid():
            try:
                from django.db import transaction
                with transaction.atomic():
                    user = form.save()
                    profile = UserProfile.objects.create(
                        user=user,
                        role='company',
                        phone=form.cleaned_data['phone'],
                        address=form.cleaned_data['address']
                    )
                    CompanyProfile.objects.create(
                        user_profile=profile,
                        company_name=form.cleaned_data['company_name'],
                        registration_number=form.cleaned_data['registration_number']
                    )
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    messages.success(request, 'Registration successful! Welcome to AgroConnect.')
                    return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm(user_type='company')
    return render(request, 'registration/register_company.html', {'form': form})

@login_required
def dashboard(request):
    try:
        profile = request.user.userprofile
        if profile.role == 'farmer':
            try:
                farmer_profile = profile.farmerprofile
                waste_products = WasteProduct.objects.filter(farmer=farmer_profile)
                orders = Order.objects.filter(waste_product__farmer=farmer_profile)
                return render(request, 'core/farmer_dashboard.html', {
                    'waste_products': waste_products,
                    'orders': orders
                })
            except FarmerProfile.DoesNotExist:
                messages.error(request, 'Farmer profile not found. Please contact admin.')
                return redirect('home')
        elif profile.role == 'company':
            try:
                company_profile = profile.companyprofile
                orders = Order.objects.filter(company=company_profile)
                return render(request, 'core/company_dashboard.html', {
                    'orders': orders
                })
            except CompanyProfile.DoesNotExist:
                messages.error(request, 'Company profile not found. Please contact admin.')
                return redirect('home')
        else:
            messages.error(request, 'Invalid user role. Please contact admin.')
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found. Please register again or contact admin.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('home')

class WasteProductListView(LoginRequiredMixin, ListView):
    model = WasteProduct
    template_name = 'core/waste_list.html'
    context_object_name = 'waste_products'
    
    def get_queryset(self):
        queryset = WasteProduct.objects.filter(status='available')
        crop_type = self.request.GET.get('crop_type')
        if crop_type:
            queryset = queryset.filter(crop_name=crop_type)
        return queryset

class WasteProductDetailView(LoginRequiredMixin, DetailView):
    model = WasteProduct
    template_name = 'core/waste_detail.html'

class WasteProductCreateView(LoginRequiredMixin, CreateView):
    model = WasteProduct
    form_class = WasteProductForm
    template_name = 'core/waste_form.html'
    success_url = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'farmer':
            raise PermissionDenied('Only farmers can create waste products.')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.farmer = self.request.user.userprofile.farmerprofile
        return super().form_valid(form)

@login_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def place_order(request, waste_id):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'company':
        raise PermissionDenied('Only companies can place orders.')
    
    try:
        waste_id = int(waste_id)
    except (ValueError, TypeError):
        messages.error(request, 'Invalid waste product ID.')
        return redirect('dashboard')
    
    waste_product = get_object_or_404(WasteProduct, id=waste_id, status='available')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity_ordered']
            if quantity <= waste_product.quantity:
                order = form.save(commit=False)
                order.company = request.user.userprofile.companyprofile
                order.waste_product = waste_product
                order.total_price = quantity * waste_product.price_per_ton
                order.save()
                
                waste_product.status = 'reserved'
                waste_product.save()
                
                messages.success(request, 'Order placed successfully!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Quantity exceeds available stock.')
    else:
        form = OrderForm()
    
    return render(request, 'core/place_order.html', {
        'form': form,
        'waste_product': waste_product
    })

@login_required
@csrf_protect
def update_order_status(request, order_id, status):
    try:
        order_id = int(order_id)
    except (ValueError, TypeError):
        messages.error(request, 'Invalid order ID.')
        return redirect('dashboard')
    
    order = get_object_or_404(Order, id=order_id)
    
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'farmer':
        raise PermissionDenied('Only farmers can update order status.')
    
    if order.waste_product.farmer.user_profile.user != request.user:
        raise PermissionDenied('You can only update orders for your own products.')
    
    order.status = status
    order.save()
    
    if status == 'accepted':
        order.waste_product.status = 'sold'
        order.waste_product.save()
    elif status == 'rejected':
        order.waste_product.status = 'available'
        order.waste_product.save()
    
    messages.success(request, f'Order {status} successfully!')
    return redirect('dashboard')