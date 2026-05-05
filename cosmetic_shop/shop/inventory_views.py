from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import models
from .models import Store, Product, StoreProduct

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_inventory(request):
    """Danh sách chi nhánh và tổng tồn kho"""
    stores = Store.objects.all().order_by('name')
    
    # Tính tổng tồn kho cho từng store
    for store in stores:
        total = StoreProduct.objects.filter(store=store).aggregate(models.Sum('stock'))['stock__sum'] or 0
        store.total_stock = total
    
    return render(request, 'shop/admin/inventory.html', {
        'stores': stores
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_inventory_detail(request, store_id):
    """Quản lý tồn kho của một chi nhánh cụ thể"""
    store = get_object_or_404(Store, id=store_id)
    
    if request.method == 'POST':
        # Cập nhật stock từ form
        for key, value in request.POST.items():
            if key.startswith('stock_'):
                product_id = key.replace('stock_', '')
                try:
                    new_stock = int(value)
                    StoreProduct.objects.update_or_create(
                        store=store,
                        product_id=product_id,
                        defaults={'stock': new_stock}
                    )
                except ValueError:
                    pass  # Bỏ qua nếu không phải số
        messages.success(request, f'Đã cập nhật tồn kho cho chi nhánh "{store.name}".')
        return redirect('shop:admin_inventory_detail', store_id=store_id)
    
    # Lấy danh sách sản phẩm và tồn kho hiện tại
    products = Product.objects.all().order_by('name')
    inventory_map = {
        sp.product_id: sp.stock
        for sp in StoreProduct.objects.filter(store=store)
    }
    
    for p in products:
        p.current_stock = inventory_map.get(p.id, 0)
    
    return render(request, 'shop/admin/inventory_detail.html', {
        'store': store,
        'products': products
    })