from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Product, Store, Order, OrderItem
from math import radians, sin, cos, sqrt, atan2
import json

def calculate_distance(lat1, lon1, lat2, lon2):
    """Tính khoảng cách giữa 2 điểm (km) - công thức Haversine"""
    R = 6371  # Bán kính trái đất (km)
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

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
        
        # Tính khoảng cách cho mỗi cửa hàng
        store_list = list(stores)
        for store in store_list:
            store.distance = calculate_distance(
                user_lat, user_lng,
                store.latitude, store.longitude
            )
        
        # Sắp xếp theo khoảng cách
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
    """Đăng ký tài khoản"""
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
    """Đăng nhập"""
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
    """Đăng xuất"""
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('shop:home')

# ============== GIỎ HÀNG ==============

def cart_view(request):
    """Hiển thị giỏ hàng - chỉ render template, JavaScript sẽ xử lý"""
    return render(request, 'shop/cart.html')

def get_cart_items(request):
    """API: Lấy thông tin sản phẩm trong giỏ hàng"""
    from django.http import JsonResponse
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', {})
            
            items = []
            for product_id, quantity in cart.items():
                try:
                    product = Product.objects.get(id=int(product_id))
                    items.append({
                        'id': product.id,
                        'name': product.name,
                        'price': float(product.price),
                        'quantity': quantity,
                        'subtotal': float(product.price) * quantity,
                        'image': product.image.url if product.image else None
                    })
                except Product.DoesNotExist:
                    continue
            
            return JsonResponse({'items': items})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def checkout(request):
    """Thanh toán"""
    if request.method == 'POST':
        # Lấy thông tin giỏ hàng từ localStorage (gửi qua POST)
        cart_data = request.POST.get('cart_data', '{}')
        cart = json.loads(cart_data) if cart_data != '{}' else {}
        
        if not cart:
            messages.error(request, 'Giỏ hàng trống!')
            return redirect('shop:cart')
        
        # Tạo đơn hàng
        order = Order.objects.create(
            customer_name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address'),
            total=0  # Sẽ tính sau
        )
        
        # Thêm các sản phẩm vào đơn hàng
        total = 0
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=int(product_id))
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
                total += product.price * quantity
            except Product.DoesNotExist:
                continue
        
        # Cập nhật tổng tiền
        order.total = total
        order.save()
        
        messages.success(request, f'Đặt hàng thành công! Mã đơn hàng: {order.id}')
        return render(request, 'shop/order_success.html', {'order': order})
    
    return render(request, 'shop/checkout.html')