from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import Product, Store, Order, OrderItem
from math import radians, sin, cos, sqrt, atan2
import json

def calculate_distance(lat1, lon1, lat2, lon2):
    """Tính khoảng cách giữa 2 điểm (km) - công thức Haversine"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# ============== TRANG CÔNG KHAI ==============

def home(request):
    products = Product.objects.all()[:8]
    return render(request, 'shop/home.html', {'products': products})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})

def store_locator(request):
    """Tìm cửa hàng gần nhất - TÍNH NĂNG GIS"""
    stores = Store.objects.all()
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')

    if lat and lng:
        user_lat = float(lat)
        user_lng = float(lng)
        store_list = list(stores)
        for store in store_list:
            store.distance = calculate_distance(
                user_lat, user_lng,
                store.latitude, store.longitude
            )
        stores = sorted(store_list, key=lambda x: x.distance)

    return render(request, 'shop/store_locator.html', {
        'stores': stores,
        'user_lat': lat,
        'user_lng': lng
    })

def order_tracking(request):
    """Theo dõi đơn hàng - TÍNH NĂNG GIS"""
    order = None
    error_message = None

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        phone = request.POST.get('phone')
        try:
            order = Order.objects.get(id=order_id, phone=phone)
        except Order.DoesNotExist:
            error_message = "Không tìm thấy đơn hàng với thông tin này!"

    return render(request, 'shop/order_tracking.html', {
        'order': order,
        'error_message': error_message
    })

# ============== ĐĂNG NHẬP / ĐĂNG KÝ ==============

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công! Chào mừng bạn đến với Cosmetic Shop.')
            return redirect('shop:home')
    else:
        form = UserCreationForm()
    return render(request, 'shop/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Chào mừng {username}!')
                return redirect('shop:home')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    else:
        form = AuthenticationForm()
    return render(request, 'shop/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('shop:home')

# ============== GIỎ HÀNG ==============

def cart_view(request):
    """Hiển thị giỏ hàng"""
    return render(request, 'shop/cart.html')


def cart_items_api(request):
    """
    API trả về thông tin sản phẩm trong giỏ hàng kèm kiểm tra tồn kho.
    POST body: { "cart": { "<product_id>": <quantity>, ... } }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        cart = data.get('cart', {})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    items = []
    stock_errors = []

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))

            # ── Kiểm tra số lượng không vượt tồn kho ──
            if quantity > product.stock:
                stock_errors.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'requested': quantity,
                    'available': product.stock,
                })
                # Giới hạn về mức tồn kho
                quantity = product.stock

            items.append({
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'quantity': quantity,
                'subtotal': float(product.price) * quantity,
                'stock': product.stock,
                'image': product.image.url if product.image else None,
            })
        except Product.DoesNotExist:
            continue

    return JsonResponse({
        'items': items,
        'stock_errors': stock_errors,   # Client dùng để hiển thị cảnh báo
    })


def checkout(request):
    """
    Thanh toán — kiểm tra tồn kho trước khi tạo đơn,
    trừ stock sau khi tạo đơn thành công.
    """
    if request.method == 'POST':
        cart_data = request.POST.get('cart_data', '{}')
        try:
            cart = json.loads(cart_data)
        except json.JSONDecodeError:
            cart = {}

        if not cart:
            messages.error(request, 'Giỏ hàng trống!')
            return redirect('shop:cart')

        # ── Pass 1: Kiểm tra tồn kho toàn bộ giỏ hàng ──
        errors = []
        validated_items = []   # [(product, quantity)]

        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=int(product_id))
            except Product.DoesNotExist:
                continue

            quantity = int(quantity)

            if quantity <= 0:
                continue

            if quantity > product.stock:
                errors.append(
                    f'"{product.name}": yêu cầu {quantity}, chỉ còn {product.stock} sản phẩm.'
                )
            else:
                validated_items.append((product, quantity))

        if errors:
            for err in errors:
                messages.error(request, f'Không đủ tồn kho — {err}')
            return redirect('shop:cart')

        if not validated_items:
            messages.error(request, 'Không có sản phẩm hợp lệ để đặt hàng!')
            return redirect('shop:cart')

        # ── Pass 2: Tạo đơn hàng ──
        order = Order.objects.create(
            customer_name=request.POST.get('name', ''),
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
            total=0,
        )

        total = 0
        for product, quantity in validated_items:
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            )
            total += product.price * quantity

            # ── Trừ tồn kho ──
            product.stock -= quantity
            product.save(update_fields=['stock'])

        order.total = total
        order.save(update_fields=['total'])

        messages.success(request, f'Đặt hàng thành công! Mã đơn hàng: {order.id}')
        return render(request, 'shop/order_success.html', {'order': order})

    return render(request, 'shop/checkout.html')

# ============== ADMIN ==============

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def admin_dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_stores = Store.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total'))['total__sum'] or 0
    today = timezone.now().date()
    orders_today = Order.objects.filter(created_at__date=today).count()
    pending_orders = Order.objects.filter(status='pending').count()
    shipping_orders = Order.objects.filter(status='shipping').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    low_stock = Product.objects.filter(stock__lt=10).order_by('stock')[:5]
    recent_orders = Order.objects.order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_stores': total_stores,
        'total_revenue': total_revenue,
        'orders_today': orders_today,
        'pending_orders': pending_orders,
        'shipping_orders': shipping_orders,
        'delivered_orders': delivered_orders,
        'low_stock': low_stock,
        'recent_orders': recent_orders,
    }
    return render(request, 'shop/admin/dashboard.html', context)

@login_required
@user_passes_test(is_staff)
def admin_products(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'shop/admin/products.html', {'products': products})

@login_required
@user_passes_test(is_staff)
def admin_orders(request):
    status = request.GET.get('status', '')
    if status:
        orders = Order.objects.filter(status=status).order_by('-created_at')
    else:
        orders = Order.objects.all().order_by('-created_at')
    return render(request, 'shop/admin/orders.html', {
        'orders': orders,
        'current_status': status,
    })

@login_required
@user_passes_test(is_staff)
def admin_order_update(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Đã cập nhật trạng thái đơn hàng #{order.id}')
        return redirect('shop:admin_orders')
    return render(request, 'shop/admin/order_detail.html', {'order': order})

@login_required
@user_passes_test(is_staff)
def admin_stores(request):
    stores = Store.objects.all()
    return render(request, 'shop/admin/stores.html', {'stores': stores})