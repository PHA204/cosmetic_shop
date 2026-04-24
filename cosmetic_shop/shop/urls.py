from django.urls import path
from . import views
from django.views.defaults import page_not_found
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

    path('about/', views.about, name='about'),
 
    # MoMo payment
    path('payment/momo/<int:order_id>/', views.momo_payment, name='momo_payment'),
    path('payment/momo/<int:order_id>/confirm/', views.momo_confirm, name='momo_confirm'),
 
    # Admin — Báo cáo doanh thu
    path('admin-dashboard/revenue/', views.admin_revenue, name='admin_revenue'),
    
    # Admin — Shippers
    path('admin-dashboard/shippers/', views.admin_shippers, name='admin_shippers'),
    path('admin-dashboard/shippers/add/', views.admin_shipper_create, name='admin_shipper_create'),
    path('admin-dashboard/shippers/<int:shipper_id>/', views.admin_shipper_detail, name='admin_shipper_detail'),
    path('admin-dashboard/shippers/<int:shipper_id>/edit/', views.admin_shipper_edit, name='admin_shipper_edit'),
    path('admin-dashboard/shippers/<int:shipper_id>/delete/', views.admin_shipper_delete, name='admin_shipper_delete'),
    path('admin-dashboard/orders/<int:order_id>/assign-shipper/', views.admin_assign_shipper, name='admin_assign_shipper'),

     # Search API (gợi ý)
    path('api/search-suggest/', views.search_ajax, name='search_suggest'),
 
    # Admin — Categories
    path('admin-dashboard/categories/', views.admin_categories, name='admin_categories'),
    path('admin-dashboard/categories/add/', views.admin_category_create, name='admin_category_create'),
    path('admin-dashboard/categories/<int:category_id>/edit/', views.admin_category_edit, name='admin_category_edit'),
    path('admin-dashboard/categories/<int:category_id>/delete/', views.admin_category_delete, name='admin_category_delete'),
    
    # 404
    
]