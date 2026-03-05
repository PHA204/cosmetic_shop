from django.contrib import admin
from .models import Store, Product, Order, OrderItem

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone', 'latitude', 'longitude']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'phone', 'status', 'created_at']
    list_filter = ['status']
    inlines = [OrderItemInline]