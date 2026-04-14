from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Trang công khai
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # GIS
    path('stores/', views.store_locator, name='store_locator'),
    path('tracking/', views.order_tracking, name='order_tracking'),

    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Giỏ hàng
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('api/cart-items/', views.cart_items_api, name='cart_items_api'),

    # Admin Dashboard
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Admin — Products
    path('admin-dashboard/products/', views.admin_products, name='admin_products'),
    path('admin-dashboard/products/add/', views.admin_product_create, name='admin_product_create'),
    path('admin-dashboard/products/<int:product_id>/edit/', views.admin_product_edit, name='admin_product_edit'),
    path('admin-dashboard/products/<int:product_id>/delete/', views.admin_product_delete, name='admin_product_delete'),

    # Admin — Orders
    path('admin-dashboard/orders/', views.admin_orders, name='admin_orders'),
    path('admin-dashboard/orders/<int:order_id>/', views.admin_order_update, name='admin_order_update'),
    path('admin-dashboard/orders/<int:order_id>/delete/', views.admin_order_delete, name='admin_order_delete'),

    # Admin — Stores
    path('admin-dashboard/stores/', views.admin_stores, name='admin_stores'),
    path('admin-dashboard/stores/add/', views.admin_store_create, name='admin_store_create'),
    path('admin-dashboard/stores/<int:store_id>/edit/', views.admin_store_edit, name='admin_store_edit'),
    path('admin-dashboard/stores/<int:store_id>/delete/', views.admin_store_delete, name='admin_store_delete'),

]