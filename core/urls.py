from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .auth_views import ConcurrentLoginView
from .middleware import get_active_sessions_api, terminate_session_api

urlpatterns = [
    path('', views.home, name='home'),
    path('register/farmer/', views.register_farmer, name='register_farmer'),
    path('register/company/', views.register_company, name='register_company'),
    path('login/', ConcurrentLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('waste/', views.WasteProductListView.as_view(), name='waste_list'),
    path('waste/<int:pk>/', views.WasteProductDetailView.as_view(), name='waste_detail'),
    path('waste/add/', views.WasteProductCreateView.as_view(), name='waste_add'),
    path('order/<int:waste_id>/', views.place_order, name='place_order'),
    path('order/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
    
    # Profile Management
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Admin Price Management
    path('price-management/view/', views.admin_view_prices, name='admin_view_prices'),
    
    # Bargaining System
    path('bargain/create/<int:waste_id>/', views.create_bargain, name='create_bargain'),
    path('bargains/', views.admin_bargains, name='admin_bargains'),
    path('bargain/<int:bargain_id>/respond/', views.respond_bargain, name='respond_bargain'),
    
    # Admin Order Management
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('admin-order/<int:order_id>/approve/', views.admin_approve_order, name='admin_approve_order'),
    path('admin/orders/<int:order_id>/complete/', views.admin_complete_order, name='admin_complete_order'),
    path('order-summary/', views.order_summary, name='order_summary'),
    
    # Session Management APIs
    path('api/sessions/', get_active_sessions_api, name='api_active_sessions'),
    path('api/sessions/terminate/', terminate_session_api, name='api_terminate_session'),
]