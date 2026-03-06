from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Trang chính
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
    path('api/cart-items/', views.get_cart_items, name='get_cart_items'),
    path('checkout/', views.checkout, name='checkout'),
]