from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Trang công khai
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    
    # Tính năng GIS
    path('stores/', views.store_locator, name='store_locator'),
    path('tracking/', views.order_tracking, name='order_tracking'),
    
    # Đăng nhập / Đăng ký
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Giỏ hàng
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/products/', views.admin_products, name='admin_products'),
    path('admin-dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('admin-dashboard/orders/<int:order_id>/', views.admin_order_update, name='admin_order_update'),
    path('admin-dashboard/stores/', views.admin_stores, name='admin_stores'),
]