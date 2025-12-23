from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/farmer/', views.register_farmer, name='register_farmer'),
    path('register/company/', views.register_company, name='register_company'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('waste/', views.WasteProductListView.as_view(), name='waste_list'),
    path('waste/<int:pk>/', views.WasteProductDetailView.as_view(), name='waste_detail'),
    path('waste/add/', views.WasteProductCreateView.as_view(), name='waste_add'),
    path('order/<int:waste_id>/', views.place_order, name='place_order'),
    path('order/<int:order_id>/<str:status>/', views.update_order_status, name='update_order_status'),
]