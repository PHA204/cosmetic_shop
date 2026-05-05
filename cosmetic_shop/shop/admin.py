from django.contrib import admin
from .models import Store, Product, Order, OrderItem, AboutPage, AboutValue, AboutGallery

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone', 'latitude', 'longitude']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'description']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'phone', 'status', 'created_at']
    list_filter = ['status']
    inlines = [OrderItemInline]


class AboutValueInline(admin.TabularInline):
    model = AboutValue
    extra = 1
    fields = ['icon', 'title', 'description', 'order']

class AboutGalleryInline(admin.TabularInline):
    model = AboutGallery
    extra = 1
    fields = ['image', 'caption', 'order']

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    list_display = ['id', 'hero_title', 'updated_at']
    inlines = [AboutValueInline, AboutGalleryInline]
    fieldsets = (
        ('Hero Section', {
            'fields': ('hero_label', 'hero_title', 'hero_text', 'hero_image')
        }),
        ('Thống kê', {
            'fields': ('branches_text', 'customers_text', 'products_text', 'rating_text')
        }),
        ('Câu chuyện', {
            'fields': ('story_label', 'story_title', 'story_year', 'story_year_label', 'story_image', 'story_text_1', 'story_text_2')
        }),
        ('Stats badges', {
            'fields': ('authentic_text', 'return_text', 'support_text')
        }),
        ('Giá trị cốt lõi', {
            'fields': ('values_label', 'values_title')
        }),
        ('CTA', {
            'fields': ('cta_title', 'cta_text')
        }),
    )