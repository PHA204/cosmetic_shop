from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
import urllib.request
import urllib.error
from .models import Product, Store, Order, OrderItem
from math import radians, sin, cos, sqrt, atan2
import json


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def is_staff(user):
    return user.is_staff


# ══════════════════════════════════════════════
#  TRANG CÔNG KHAI
# ══════════════════════════════════════════════

def home(request):
    products = Product.objects.all()[:8]
    return render(request, 'shop/home.html', {'products': products})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.exclude(pk=pk).order_by('?')[:4]
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


def store_locator(request):
    lat      = request.GET.get('lat', '').strip()
    lng      = request.GET.get('lng', '').strip()
    search   = request.GET.get('search', '').strip()
    max_dist = request.GET.get('distance', '').strip()

    stores = Store.objects.all()
    if search:
        stores = stores.filter(
            Q(name__icontains=search) | Q(address__icontains=search)
        )

    user_lat = user_lng = None
    if lat and lng:
        try:
            user_lat, user_lng = float(lat), float(lng)
        except ValueError:
            pass

    store_list = list(stores)
    if user_lat is not None:
        for s in store_list:
            s.distance = calculate_distance(user_lat, user_lng, s.latitude, s.longitude)
        if max_dist:
            try:
                store_list = [s for s in store_list if s.distance <= float(max_dist)]
            except ValueError:
                max_dist = ''
        store_list.sort(key=lambda s: s.distance)
    else:
        max_dist = ''

    return render(request, 'shop/store_locator.html', {
        'stores': store_list, 'user_lat': user_lat,
        'user_lng': user_lng, 'search': search, 'max_distance': max_dist,
    })


def order_tracking(request):
    order = error_message = None
    if request.method == 'POST':
        try:
            order = Order.objects.get(
                id=request.POST.get('order_id'),
                phone=request.POST.get('phone')
            )
        except Order.DoesNotExist:
            error_message = 'Không tìm thấy đơn hàng với thông tin này!'
    return render(request, 'shop/order_tracking.html', {
        'order': order, 'error_message': error_message
    })


# ══════════════════════════════════════════════
#  ĐĂNG NHẬP / ĐĂNG KÝ
# ══════════════════════════════════════════════

def register_view(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Đăng ký thành công!')
        return redirect('shop:home')
    return render(request, 'shop/Register.html', {'form': form})


def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user:
            login(request, user)
            messages.success(request, f'Chào mừng {user.username}!')
            return redirect('shop:home')
        messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    return render(request, 'shop/Login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('shop:home')


# ══════════════════════════════════════════════
#  GIỎ HÀNG
# ══════════════════════════════════════════════

def cart_view(request):
    return render(request, 'shop/cart.html')


def cart_items_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        cart = json.loads(request.body).get('cart', {})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    items, stock_errors = [], []
    for product_id, quantity in cart.items():
        try:
            product  = Product.objects.get(id=int(product_id))
            quantity = int(quantity)
            if quantity > product.stock:
                stock_errors.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'requested': quantity,
                    'available': product.stock,
                })
                quantity = product.stock
            if quantity > 0:
                items.append({
                    'id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': quantity,
                    'subtotal': float(product.price) * quantity,
                    'stock': product.stock,
                    'image': product.image.url if product.image else None,
                })
        except (Product.DoesNotExist, ValueError, TypeError):
            continue
    return JsonResponse({'items': items, 'stock_errors': stock_errors})


def checkout(request):
    if request.method == 'POST':
        try:
            cart = json.loads(request.POST.get('cart_data', '{}'))
        except json.JSONDecodeError:
            cart = {}

        if not cart:
            messages.error(request, 'Giỏ hàng trống!')
            return redirect('shop:cart')

        try:
            with transaction.atomic():
                product_ids     = [int(pid) for pid in cart]
                locked_products = {
                    p.id: p for p in
                    Product.objects.select_for_update().filter(id__in=product_ids)
                }
                errors, validated = [], []
                for pid_str, qty in cart.items():
                    product  = locked_products.get(int(pid_str))
                    quantity = int(qty)
                    if not product or quantity <= 0:
                        continue
                    if quantity > product.stock:
                        errors.append(
                            f'"{product.name}": yêu cầu {quantity}, chỉ còn {product.stock}.'
                        )
                    else:
                        validated.append((product, quantity))

                if errors:
                    for e in errors:
                        messages.error(request, f'Không đủ tồn kho — {e}')
                    raise ValueError('stock_error')

                if not validated:
                    messages.error(request, 'Không có sản phẩm hợp lệ!')
                    raise ValueError('no_items')

                order = Order.objects.create(
                    customer_name=request.POST.get('name', '').strip(),
                    phone=request.POST.get('phone', '').strip(),
                    address=request.POST.get('address', '').strip(),
                    total=0,
                )
                total = 0
                for product, quantity in validated:
                    OrderItem.objects.create(
                        order=order, product=product,
                        quantity=quantity, price=product.price,
                    )
                    total += product.price * quantity
                    product.stock -= quantity
                    product.save(update_fields=['stock'])

                order.total = total
                order.save(update_fields=['total'])

        except ValueError:
            return redirect('shop:cart')

        return render(request, 'shop/order_success.html', {'order': order})

    return render(request, 'shop/checkout.html')


# ══════════════════════════════════════════════
#  CUSTOM ADMIN DASHBOARD
# ══════════════════════════════════════════════

@login_required
@user_passes_test(is_staff)
def admin_dashboard(request):
    today = timezone.now().date()
    context = {
        'total_products':   Product.objects.count(),
        'total_orders':     Order.objects.count(),
        'total_stores':     Store.objects.count(),
        'total_revenue':    Order.objects.aggregate(Sum('total'))['total__sum'] or 0,
        'orders_today':     Order.objects.filter(created_at__date=today).count(),
        'pending_orders':   Order.objects.filter(status='pending').count(),
        'confirmed_orders': Order.objects.filter(status='confirmed').count(),
        'shipping_orders':  Order.objects.filter(status='shipping').count(),
        'delivered_orders': Order.objects.filter(status='delivered').count(),
        'low_stock':        Product.objects.filter(stock__lt=10).order_by('stock')[:5],
        'recent_orders':    Order.objects.order_by('-created_at')[:5],
    }
    return render(request, 'shop/admin/dashboard.html', context)


# ── Products ──

@login_required
@user_passes_test(is_staff)
def admin_products(request):
    search   = request.GET.get('search', '').strip()
    products = Product.objects.all().order_by('-id')
    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    return render(request, 'shop/admin/products.html', {
        'products': products, 'search': search
    })


@login_required
@user_passes_test(is_staff)
def admin_product_create(request):
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        price       = request.POST.get('price', '0')
        description = request.POST.get('description', '').strip()
        stock       = request.POST.get('stock', '0')
        image       = request.FILES.get('image')

        if not name:
            messages.error(request, 'Tên sản phẩm không được để trống.')
            return render(request, 'shop/admin/product_form.html', {'action': 'Thêm'})

        try:
            product = Product(
                name=name, price=int(price),
                description=description, stock=int(stock),
            )
            if image:
                product.image = image
            product.save()
            messages.success(request, f'Đã thêm sản phẩm "{product.name}".')
            return redirect('shop:admin_products')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Dữ liệu không hợp lệ: {e}')

    return render(request, 'shop/admin/product_form.html', {'action': 'Thêm'})


@login_required
@user_passes_test(is_staff)
def admin_product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name        = request.POST.get('name', '').strip()
        product.description = request.POST.get('description', '').strip()
        try:
            product.price = int(request.POST.get('price', 0))
            product.stock = int(request.POST.get('stock', 0))
        except (ValueError, TypeError):
            messages.error(request, 'Giá và tồn kho phải là số nguyên.')
            return render(request, 'shop/admin/product_form.html', {
                'product': product, 'action': 'Sửa'
            })
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
        messages.success(request, f'Đã cập nhật sản phẩm "{product.name}".')
        return redirect('shop:admin_products')

    return render(request, 'shop/admin/product_form.html', {
        'product': product, 'action': 'Sửa'
    })


@login_required
@user_passes_test(is_staff)
def admin_product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Đã xóa sản phẩm "{name}".')
        return redirect('shop:admin_products')
    return render(request, 'shop/admin/confirm_delete.html', {
        'object': product, 'object_type': 'sản phẩm',
        'cancel_url': 'shop:admin_products',
    })


# ── Orders ──

@login_required
@user_passes_test(is_staff)
def admin_orders(request):
    status = request.GET.get('status', '')
    search = request.GET.get('search', '').strip()
    orders = Order.objects.all().order_by('-created_at')
    if status:
        orders = orders.filter(status=status)
    if search:
        orders = orders.filter(
            Q(customer_name__icontains=search) | Q(phone__icontains=search)
        )
    return render(request, 'shop/admin/orders.html', {
        'orders': orders, 'current_status': status, 'search': search,
    })


@login_required
@user_passes_test(is_staff)
def admin_order_update(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save(update_fields=['status'])
            messages.success(request, f'Đã cập nhật trạng thái đơn #{order.id}.')
        return redirect('shop:admin_orders')
    return render(request, 'shop/admin/order_detail.html', {'order': order})


@login_required
@user_passes_test(is_staff)
def admin_order_delete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, f'Đã xóa đơn hàng #{order_id}.')
        return redirect('shop:admin_orders')
    return render(request, 'shop/admin/confirm_delete.html', {
        'object': order, 'object_type': 'đơn hàng',
        'cancel_url': 'shop:admin_orders',
    })


# ── Stores ──

@login_required
@user_passes_test(is_staff)
def admin_stores(request):
    stores = Store.objects.all()
    return render(request, 'shop/admin/stores.html', {'stores': stores})


@login_required
@user_passes_test(is_staff)
def admin_store_create(request):
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        phone   = request.POST.get('phone', '').strip()
        try:
            lat = float(request.POST.get('latitude', 0))
            lng = float(request.POST.get('longitude', 0))
        except ValueError:
            messages.error(request, 'Tọa độ không hợp lệ.')
            return render(request, 'shop/admin/store_form.html', {'action': 'Thêm'})

        Store.objects.create(name=name, address=address, phone=phone,
                             latitude=lat, longitude=lng)
        messages.success(request, f'Đã thêm cửa hàng "{name}".')
        return redirect('shop:admin_stores')

    return render(request, 'shop/admin/store_form.html', {'action': 'Thêm'})


@login_required
@user_passes_test(is_staff)
def admin_store_edit(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.method == 'POST':
        store.name    = request.POST.get('name', '').strip()
        store.address = request.POST.get('address', '').strip()
        store.phone   = request.POST.get('phone', '').strip()
        try:
            store.latitude  = float(request.POST.get('latitude', 0))
            store.longitude = float(request.POST.get('longitude', 0))
        except ValueError:
            messages.error(request, 'Tọa độ không hợp lệ.')
            return render(request, 'shop/admin/store_form.html', {
                'store': store, 'action': 'Sửa'
            })
        store.save()
        messages.success(request, f'Đã cập nhật cửa hàng "{store.name}".')
        return redirect('shop:admin_stores')

    return render(request, 'shop/admin/store_form.html', {
        'store': store, 'action': 'Sửa'
    })


@login_required
@user_passes_test(is_staff)
def admin_store_delete(request, store_id):
    store = get_object_or_404(Store, id=store_id)
    if request.method == 'POST':
        name = store.name
        store.delete()
        messages.success(request, f'Đã xóa cửa hàng "{name}".')
        return redirect('shop:admin_stores')
    return render(request, 'shop/admin/confirm_delete.html', {
        'object': store, 'object_type': 'cửa hàng',
        'cancel_url': 'shop:admin_stores',
    })


