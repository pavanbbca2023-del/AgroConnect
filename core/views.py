from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import UserProfile, FarmerProfile, CompanyProfile, WasteProduct, Order, PriceBargain
from .forms import UserRegistrationForm, WasteProductForm, OrderForm, ProfileUpdateForm
import logging

logger = logging.getLogger(__name__)

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

                    # Enhanced login with session tracking
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    
                    # Log successful registration
                    logger.info(f"New farmer registered: {user.username}")
                    
                    messages.success(request, "Farmer registered successfully!")
                    return redirect('dashboard')

            except Exception as e:
                logger.error(f"Farmer registration failed for {form.cleaned_data.get('username', 'unknown')}: {e}")
                messages.error(request, f"Registration failed: {e}")

        else:
            logger.warning(f"Farmer registration form errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")

    else:
        form = UserRegistrationForm(user_type='farmer')

    return render(request, 'registration/register_farmer.html', {'form': form})

def register_company(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, user_type='company')
        if form.is_valid():
            try:
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
                    
                    # Enhanced login with session tracking
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    
                    # Log successful registration
                    logger.info(f"New company registered: {user.username} - {form.cleaned_data['company_name']}")
                    
                    messages.success(request, 'Registration successful! Welcome to AgroConnect.')
                    return redirect('dashboard')
            except Exception as e:
                logger.error(f"Company registration failed for {form.cleaned_data.get('username', 'unknown')}: {e}")
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            logger.warning(f"Company registration form errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegistrationForm(user_type='company')
    return render(request, 'registration/register_company.html', {'form': form})

@login_required
def dashboard(request):
    # Check if user is superuser for admin dashboard
    if request.user.is_superuser:
        return admin_dashboard(request)
    
    # Check if user has a profile
    if not hasattr(request.user, 'userprofile'):
        messages.error(request, 'User profile not found. Please register again or contact admin.')
        return redirect('home')
    
    try:
        profile = request.user.userprofile
        if profile.role == 'farmer':
            try:
                farmer_profile = profile.farmerprofile
                waste_products = WasteProduct.objects.filter(farmer=farmer_profile)
                orders = Order.objects.filter(waste_product__farmer=farmer_profile).order_by('-created_at')
                bargains = PriceBargain.objects.filter(waste_product__farmer=farmer_profile)
                
                # Get current market prices set by admin
                from django.db.models import Max
                market_prices = WasteProduct.objects.values('crop_name').annotate(
                    latest_price=Max('admin_price_per_ton')
                ).filter(latest_price__gt=0)
                
                return render(request, 'core/farmer_dashboard.html', {
                    'waste_products': waste_products,
                    'orders': orders,
                    'bargains': bargains,
                    'market_prices': market_prices,
                    'crop_choices': WasteProduct.CROP_CHOICES
                })
            except FarmerProfile.DoesNotExist:
                messages.error(request, 'Farmer profile not found. Please contact admin.')
                return redirect('home')
        elif profile.role == 'company':
            try:
                from django.db.models import Sum, Avg, Count
                company_profile = profile.companyprofile
                orders = Order.objects.filter(company=company_profile)
                
                # Get aggregated waste data for company dashboard
                aggregated_waste = WasteProduct.objects.filter(status='available').exclude(crop_name='corn').values('crop_name').annotate(
                    total_quantity=Sum('quantity'),
                    avg_price=Avg('admin_price_per_ton')
                ).order_by('crop_name')
                
                return render(request, 'core/company_dashboard.html', {
                    'orders': orders,
                    'aggregated_waste': aggregated_waste
                })
            except CompanyProfile.DoesNotExist:
                messages.error(request, 'Company profile not found. Please contact admin.')
                return redirect('home')
        else:
            messages.error(request, 'Invalid user role. Please contact admin.')
            return redirect('home')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('home')

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        raise PermissionDenied('Admin access required.')
    
    stats = {
        'total_users': User.objects.count(),
        'total_farmers': FarmerProfile.objects.count(),
        'total_companies': CompanyProfile.objects.count(),
        'total_orders': Order.objects.count(),
    }
    
    recent_orders = Order.objects.select_related('company__user_profile__user').order_by('-created_at')[:5]
    recent_waste = WasteProduct.objects.select_related('farmer__user_profile__user').order_by('-created_at')[:5]
    pending_bargains = PriceBargain.objects.filter(status='pending').select_related('waste_product__farmer__user_profile__user')[:5]
    
    return render(request, 'core/admin_dashboard.html', {
        'stats': stats,
        'recent_orders': recent_orders,
        'recent_waste': recent_waste,
        'pending_bargains': pending_bargains,
    })

class WasteProductListView(LoginRequiredMixin, ListView):
    model = WasteProduct
    template_name = 'core/waste_list.html'
    context_object_name = 'waste_products'
    
    def get_queryset(self):
        from django.db.models import Sum, Avg, Count
        
        crop_type = self.request.GET.get('crop_type')
        
        if crop_type == 'corn':
            # Redirect corn requests to main page
            from django.shortcuts import redirect
            return redirect('waste_list')
        
        if crop_type:
            # Show individual products for specific crop type
            queryset = WasteProduct.objects.filter(status='available', crop_name=crop_type).exclude(crop_name='corn')
            return queryset
        else:
            # Show aggregated data by crop type
            queryset = WasteProduct.objects.filter(status='available').exclude(crop_name='corn')
            
            # Aggregate by crop type
            aggregated_data = queryset.values('crop_name').annotate(
                total_quantity=Sum('quantity'),
                avg_price=Avg('admin_price_per_ton'),
                total_value=Sum('quantity') * Avg('admin_price_per_ton')
            ).order_by('crop_name')
            
            return aggregated_data
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        crop_type = self.request.GET.get('crop_type')
        context['is_aggregated'] = not crop_type
        context['selected_crop'] = crop_type
        return context

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
        # Admin will set the price later
        form.instance.admin_price_per_ton = 0.01  # Default minimal price
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
                order.total_price = quantity * form.cleaned_data['company_price_per_ton']
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
    
    if order.status != 'sent_to_farmer':
        messages.error(request, 'This order is not available for response.')
        return redirect('dashboard')
    
    if status == 'accepted':
        order.status = 'accepted_by_farmer'
        order.waste_product.status = 'reserved'
        order.save()
        order.waste_product.save()
        messages.success(request, 'Order accepted! Waiting for final admin approval.')
    elif status == 'rejected':
        order.status = 'rejected_by_farmer'
        order.waste_product.status = 'available'
        order.save()
        order.waste_product.save()
        messages.success(request, 'Order rejected!')
    
    return redirect('dashboard')

@login_required
def profile(request):
    # Admin users don't have UserProfile, redirect to admin dashboard
    if request.user.is_superuser:
        messages.info(request, 'Admin users can access admin dashboard directly.')
        return redirect('dashboard')
    
    try:
        user_profile = request.user.userprofile
        context = {'user_profile': user_profile}
        
        if user_profile.role == 'farmer':
            context['farmer_profile'] = user_profile.farmerprofile
        elif user_profile.role == 'company':
            context['company_profile'] = user_profile.companyprofile
            
        return render(request, 'core/profile.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('dashboard')

@login_required
def edit_profile(request):
    # Admin users don't have UserProfile, redirect to admin dashboard
    if request.user.is_superuser:
        messages.info(request, 'Admin users can access admin dashboard directly.')
        return redirect('dashboard')
    
    try:
        user_profile = request.user.userprofile
        
        if request.method == 'POST':
            form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile, user=request.user)
            if form.is_valid():
                with transaction.atomic():
                    # Update User model fields
                    user = request.user
                    user.first_name = form.cleaned_data['first_name']
                    user.last_name = form.cleaned_data['last_name']
                    user.email = form.cleaned_data['email']
                    user.save()
                    
                    # Update UserProfile
                    form.save()
                    
                    # Update role-specific profile
                    if user_profile.role == 'farmer' and hasattr(user_profile, 'farmerprofile'):
                        farmer_profile = user_profile.farmerprofile
                        farmer_profile.farm_size = form.cleaned_data['farm_size']
                        farmer_profile.save()
                    elif user_profile.role == 'company' and hasattr(user_profile, 'companyprofile'):
                        company_profile = user_profile.companyprofile
                        company_profile.company_name = form.cleaned_data['company_name']
                        company_profile.save()
                    
                    messages.success(request, 'Profile updated successfully!')
                    return redirect('profile')
        else:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
            
            if user_profile.role == 'farmer' and hasattr(user_profile, 'farmerprofile'):
                initial_data['farm_size'] = user_profile.farmerprofile.farm_size
            elif user_profile.role == 'company' and hasattr(user_profile, 'companyprofile'):
                initial_data['company_name'] = user_profile.companyprofile.company_name
                
            form = ProfileUpdateForm(instance=user_profile, user=request.user, initial=initial_data)
        
        return render(request, 'core/edit_profile.html', {'form': form})
    except UserProfile.DoesNotExist:
        messages.error(request, 'Profile not found.')
        return redirect('dashboard')

@login_required
def admin_view_prices(request):
    if not request.user.is_superuser:
        raise PermissionDenied('Admin access required.')
    
    waste_products = WasteProduct.objects.select_related('farmer__user_profile__user').order_by('-created_at')
    
    # Filter by crop type if specified
    crop_filter = request.GET.get('crop')
    if crop_filter:
        waste_products = waste_products.filter(crop_name=crop_filter)
    
    # Filter by status if specified
    status_filter = request.GET.get('status')
    if status_filter:
        waste_products = waste_products.filter(status=status_filter)
    
    # Calculate summary statistics
    total_products = waste_products.count()
    available_products = waste_products.filter(status='available').count()
    total_quantity = sum(float(w.quantity) for w in waste_products)
    total_value = sum(float(w.total_value) for w in waste_products)
    
    context = {
        'waste_products': waste_products,
        'crop_choices': WasteProduct.CROP_CHOICES,
        'status_choices': WasteProduct.STATUS_CHOICES,
        'current_crop': crop_filter,
        'current_status': status_filter,
        'total_products': total_products,
        'available_products': available_products,
        'total_quantity': total_quantity,
        'total_value': total_value,
    }
    
    return render(request, 'core/admin_view_prices.html', context)

@login_required
def create_bargain(request, waste_id):
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'farmer':
        raise PermissionDenied('Only farmers can create bargains.')
    
    waste_product = get_object_or_404(WasteProduct, id=waste_id, farmer__user_profile__user=request.user)
    
    if request.method == 'POST':
        proposed_price = request.POST.get('proposed_price')
        message = request.POST.get('message')
        
        if proposed_price and message:
            PriceBargain.objects.create(
                waste_product=waste_product,
                farmer_proposed_price=proposed_price,
                farmer_message=message
            )
            messages.success(request, 'Bargain request sent to admin!')
            return redirect('dashboard')
    
    return render(request, 'core/create_bargain.html', {'waste_product': waste_product})

@login_required
def admin_bargains(request):
    if not request.user.is_superuser:
        raise PermissionDenied('Admin access required.')
    
    bargains = PriceBargain.objects.select_related('waste_product__farmer__user_profile__user').order_by('-created_at')
    return render(request, 'core/admin_bargains.html', {'bargains': bargains})

@login_required
def admin_orders(request):
    if not request.user.is_superuser:
        raise PermissionDenied('Admin access required.')
    
    orders = Order.objects.select_related('company__user_profile__user', 'waste_product__farmer__user_profile__user').order_by('-created_at')
    
    # Filter by status if specified
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    return render(request, 'core/admin_orders.html', {'orders': orders})

@login_required
def admin_approve_order(request, order_id):
    if not request.user.is_superuser:
        raise PermissionDenied('Admin access required.')
    
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        
        if action == 'send_to_farmer' and order.status == 'pending_admin':
            order.status = 'sent_to_farmer'
            order.admin_notes = admin_notes
            order.save()
            messages.success(request, 'Order sent to farmer for review!')
        elif action == 'final_approve' and order.status == 'accepted_by_farmer':
            order.status = 'approved_by_admin'
            order.admin_notes = admin_notes
            order.save()
            messages.success(request, 'Order finally approved for company!')
        elif action == 'reject':
            order.status = 'rejected_by_farmer'
            order.admin_notes = admin_notes
            order.save()
            messages.success(request, 'Order rejected!')
        
        return redirect('admin_orders')
    
    return render(request, 'core/admin_approve_order.html', {'order': order})

@login_required
def respond_bargain(request, bargain_id):
    if not request.user.is_superuser:
        raise PermissionDenied('Admin access required.')
    
    bargain = get_object_or_404(PriceBargain, id=bargain_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_message = request.POST.get('admin_message', '')
        
        if action == 'accept':
            bargain.status = 'accepted'
            bargain.admin_message = admin_message
            bargain.waste_product.admin_price_per_ton = bargain.farmer_proposed_price
            bargain.waste_product.save()
            bargain.save()
            messages.success(request, 'Bargain accepted and price updated!')
        elif action == 'reject':
            bargain.status = 'rejected'
            bargain.admin_message = admin_message
            bargain.save()
            messages.success(request, 'Bargain rejected!')
        elif action == 'counter':
            counter_price = request.POST.get('counter_price')
            if counter_price:
                bargain.admin_counter_price = counter_price
                bargain.admin_message = admin_message
                bargain.save()
                messages.success(request, 'Counter offer sent!')
        
        return redirect('admin_bargains')
    
    return render(request, 'core/respond_bargain.html', {'bargain': bargain})

@login_required
@require_http_methods(["POST"])
def admin_complete_order(request, order_id):
    if not request.user.is_superuser:
        raise PermissionDenied('Admin access required.')
    
    try:
        order = get_object_or_404(Order, id=order_id)
        if order.status == 'accepted':
            order.status = 'completed'
            order.save()
            return JsonResponse({'success': True, 'message': 'Order marked as completed'})
        else:
            return JsonResponse({'success': False, 'message': 'Order cannot be completed'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
def order_summary(request):
    if not request.user.is_superuser:
        raise PermissionDenied('Admin access required.')
    
    # Get order counts by status
    pending_count = Order.objects.filter(status='pending_admin').count()
    sent_to_farmer_count = Order.objects.filter(status='sent_to_farmer').count()
    accepted_by_farmer_count = Order.objects.filter(status='accepted_by_farmer').count()
    completed_count = Order.objects.filter(status='completed').count()
    
    # Get pending orders for quick action
    pending_orders = Order.objects.filter(status__in=['pending_admin', 'accepted_by_farmer']).select_related(
        'company__user_profile__user', 'waste_product'
    ).order_by('-created_at')[:5]
    
    # Calculate order values
    from django.db.models import Sum
    total_value = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    completed_value = Order.objects.filter(status='completed').aggregate(Sum('total_price'))['total_price__sum'] or 0
    pending_value = Order.objects.filter(status__in=['pending_admin', 'sent_to_farmer', 'accepted_by_farmer']).aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    context = {
        'pending_count': pending_count,
        'sent_to_farmer_count': sent_to_farmer_count,
        'accepted_by_farmer_count': accepted_by_farmer_count,
        'completed_count': completed_count,
        'pending_orders': pending_orders,
        'total_value': total_value,
        'completed_value': completed_value,
        'pending_value': pending_value,
    }
    
    return render(request, 'core/order_summary.html', context)