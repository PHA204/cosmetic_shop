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
from .models import Product, Store, Order, OrderItem, Shipper, Category, ProductImage
from math import radians, sin, cos, sqrt, atan2
from datetime import date, timedelta
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
import csv, json
from django.http import HttpResponse
import qrcode
import base64
from io import BytesIO

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
    product          = get_object_or_404(Product, pk=pk)
    gallery          = product.images.all().order_by('order')
    related_products = Product.objects.exclude(pk=pk).order_by('?')[:4]
    return render(request, 'shop/product_detail.html', {
        'product':          product,
        'gallery':          gallery,
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

        payment_method = request.POST.get('payment_method', 'cod')
        if payment_method == 'momo':
         return redirect('shop:momo_payment', order_id=order.id)
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
                'product': product, 'action': 'Sửa',
                'categories': Category.objects.all(),
                'gallery': product.images.all(),
            })
 
        product.category_id = request.POST.get('category') or None
        if request.FILES.get('image'):
            product.image = request.FILES['image']
        product.save()
 
        # Xoá ảnh gallery được tick
        delete_ids = request.POST.getlist('delete_image')
        if delete_ids:
            ProductImage.objects.filter(id__in=delete_ids, product=product).delete()
 
        # Thêm ảnh gallery mới (tối đa 3 ảnh tổng cộng)
        new_images    = request.FILES.getlist('gallery_images')
        current_count = product.images.count()
        for i, img in enumerate(new_images):
            if current_count + i >= 3:
                break
            ProductImage.objects.create(
                product=product, image=img,
                order=current_count + i, alt=product.name,
            )
 
        messages.success(request, f'Đã cập nhật sản phẩm "{product.name}".')
        return redirect('shop:admin_products')
 
    return render(request, 'shop/admin/product_form.html', {
        'product':    product,
        'action':     'Sửa',
        'categories': Category.objects.all(),
        'gallery':    product.images.all(),
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
        category_id = request.POST.get('category') or None
 
        if not name:
            messages.error(request, 'Tên sản phẩm không được để trống.')
            return render(request, 'shop/admin/product_form.html', {
                'action': 'Thêm', 'categories': Category.objects.all(),
            })
 
        try:
            product = Product(
                name=name, price=int(price), description=description,
                stock=int(stock), category_id=category_id,
            )
            if image:
                product.image = image
            product.save()
 
            # Lưu ảnh gallery (tối đa 3)
            for i, img in enumerate(request.FILES.getlist('gallery_images')[:3]):
                ProductImage.objects.create(
                    product=product, image=img, order=i, alt=name,
                )
 
            messages.success(request, f'Đã thêm sản phẩm "{product.name}".')
            return redirect('shop:admin_products')
        except (ValueError, TypeError) as e:
            messages.error(request, f'Dữ liệu không hợp lệ: {e}')
 
    return render(request, 'shop/admin/product_form.html', {
        'action': 'Thêm', 'categories': Category.objects.all(),
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

def about(request):
    stores   = Store.objects.all()
    products = Product.objects.count()
    values   = [
        {'icon': '🌿', 'title': 'Thiên nhiên & Thuần chay',
         'desc': 'Ưu tiên thành phần thiên nhiên, không thử nghiệm trên động vật, thân thiện với môi trường trong từng sản phẩm.'},
        {'icon': '💎', 'title': 'Chất lượng & Uy tín',
         'desc': '100% hàng chính hãng có nguồn gốc rõ ràng, được kiểm định chất lượng nghiêm ngặt trước khi đến tay khách hàng.'},
        {'icon': '❤️', 'title': 'Tận tâm & Chuyên nghiệp',
         'desc': 'Đội ngũ tư vấn viên được đào tạo bài bản, luôn lắng nghe và đồng hành cùng khách hàng trên hành trình làm đẹp.'},
    ]
    return render(request, 'shop/about.html', {
        'stores': stores,
        'total_products': products,
        'values': values,
    })
 
 
# ══════════════════════════════════════════════
#  THANH TOÁN MOMO
# ══════════════════════════════════════════════
 
def momo_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.status != 'pending':
        messages.warning(request, 'Đơn hàng không cần thanh toán.')
        return redirect('shop:order_tracking')

    # Thông tin MoMo (lấy từ settings hoặc điền trực tiếp)
    momo_phone   = getattr(settings, 'MOMO_PHONE',   '0901234567')
    momo_account = getattr(settings, 'MOMO_ACCOUNT', 'COSMETIC SHOP')
    transfer_content = f'DONHANG{order.id}'
    amount = int(order.total)

    # Deep link MoMo — mở thẳng app và điền sẵn thông tin
    momo_deeplink = (
        f'momo://app?action=payWithApp'
        f'&isScanQR=true'
        f'&phone={momo_phone}'
        f'&amount={amount}'
        f'&description={transfer_content}'
        f'&merchantname={momo_account}'
    )

    # Tạo ảnh QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=3,
    )
    qr.add_data(momo_deeplink)
    qr.make(fit=True)

    img = qr.make_image(fill_color='#ae2070', back_color='white')

    # Chuyển sang base64 để nhúng thẳng vào HTML
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'shop/momo_payment.html', {
        'order_id':          order_id,
        'order_total':       order.total,
        'order':             order,
        'qr_base64':         qr_base64,
        'momo_phone':        momo_phone,
        'transfer_content':  transfer_content,
        'amount':            amount,
    })
 
def momo_confirm(request, order_id):
    """
    Xử lý sau khi khách bấm 'Tôi đã thanh toán xong'.
    Trong môi trường thực tế, đây là nơi gọi MoMo API để verify.
    Hiện tại: chuyển sang trạng thái 'confirmed' và redirect về order_success.
    """
    if request.method != 'POST':
        return redirect('shop:momo_payment', order_id=order_id)
 
    order = get_object_or_404(Order, id=order_id)
    # TODO: Tích hợp MoMo IPN callback để verify thực tế
    order.status = 'confirmed'
    order.save(update_fields=['status'])
    messages.success(request, f'Thanh toán MoMo đơn #{order_id} đã được ghi nhận!')
    return render(request, 'shop/order_success.html', {'order': order})
 
 
# ══════════════════════════════════════════════
#  BÁO CÁO DOANH THU (Admin)
# ══════════════════════════════════════════════
 
@login_required
@user_passes_test(is_staff)
def admin_revenue(request):
    from datetime import date, timedelta
    from django.db.models import Count, Avg
    from django.db.models.functions import TruncDay, TruncWeek, TruncMonth
    import csv
 
    # ── Tham số lọc ──
    today     = date.today()
    from_str  = request.GET.get('from_date', '')
    to_str    = request.GET.get('to_date', '')
    group_by  = request.GET.get('group_by', 'day')
 
    try:
        from_date = date.fromisoformat(from_str) if from_str else today - timedelta(days=29)
    except ValueError:
        from_date = today - timedelta(days=29)
 
    try:
        to_date = date.fromisoformat(to_str) if to_str else today
    except ValueError:
        to_date = today
 
    # ── Queryset cơ sở ──
    qs = Order.objects.filter(created_at__date__gte=from_date, created_at__date__lte=to_date)
 
    # ── Xuất CSV ──
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = f'attachment; filename="revenue_{from_date}_{to_date}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Mã đơn', 'Khách hàng', 'SĐT', 'Địa chỉ', 'Trạng thái', 'Ngày đặt', 'Tổng tiền'])
        for o in qs.order_by('-created_at'):
            writer.writerow([o.id, o.customer_name, o.phone, o.address,
                             o.get_status_display(), o.created_at.strftime('%d/%m/%Y %H:%M'),
                             float(o.total)])
        return response
 
    # ── KPI ──
    total_revenue   = qs.aggregate(s=Sum('total'))['s'] or 0
    total_orders    = qs.count()
    delivered_orders = qs.filter(status='delivered').count()
    avg_order_value = (total_revenue / total_orders) if total_orders else 0
 
    # ── Trạng thái breakdown ──
    status_map = {
        'pending':   ('Chờ xác nhận', '#ffc107', '#fff3cd'),
        'confirmed': ('Đã xác nhận',  '#0dcaf0', '#cff4fc'),
        'shipping':  ('Đang giao',    '#0d6efd', '#cfe2ff'),
        'delivered': ('Đã giao',      '#198754', '#d1e7dd'),
    }
    status_breakdown = []
    for code, (label, color, _) in status_map.items():
        cnt = qs.filter(status=code).count()
        pct = (cnt / total_orders * 100) if total_orders else 0
        status_breakdown.append({'label': label, 'count': cnt, 'pct': pct, 'color': color})
 
    # ── Nhóm doanh thu theo kỳ ──
    trunc_map = {'day': TruncDay, 'week': TruncWeek, 'month': TruncMonth}
    group_label_map = {'day': 'ngày', 'week': 'tuần', 'month': 'tháng'}
    TruncFn = trunc_map.get(group_by, TruncDay)
 
    grouped = (
        qs.annotate(period=TruncFn('created_at'))
          .values('period')
          .annotate(revenue=Sum('total'), order_count=Count('id'))
          .order_by('period')
    )
 
    revenue_rows = []
    max_rev = float(max((g['revenue'] or 0 for g in grouped), default=1))
    for g in grouped:
        rev = float(g['revenue'] or 0)
        cnt = g['order_count']
        revenue_rows.append({
            'period':      g['period'].strftime('%d/%m/%Y') if group_by == 'day'
                        else (f"Tuần {g['period'].strftime('%W/%Y')}" if group_by == 'week'
                                else g['period'].strftime('%m/%Y')),
            'revenue':     rev,
            'order_count': cnt,
            'avg':         rev / cnt if cnt else 0,
            'pct':         rev / max_rev * 100 if max_rev else 0,
        })
 
    # ── Chart data ──
    chart_labels  = [r['period'] for r in revenue_rows]
    chart_revenue = [r['revenue'] for r in revenue_rows]
    chart_orders  = [r['order_count'] for r in revenue_rows]
 
    # ── Top sản phẩm ──
    from django.db.models import F
    top_raw = (
        OrderItem.objects.filter(order__in=qs)
                         .values('product__name')
                         .annotate(total_qty=Sum('quantity'),
                                   revenue=Sum(F('price') * F('quantity')))
                         .order_by('-revenue')[:10]
    )
    max_prod_rev = float(max((p['revenue'] or 0 for p in top_raw), default=1))
    top_products = [
        {
            'name':      p['product__name'],
            'total_qty': p['total_qty'],
            'revenue':   float(p['revenue'] or 0),
            'pct':       float(p['revenue'] or 0) / float(max_prod_rev) * 100,
        }
        for p in top_raw
    ]
 
    import json
    context = {
        'from_date':        from_date.isoformat(),
        'to_date':          to_date.isoformat(),
        'group_by':         group_by,
        'group_by_label':   group_label_map.get(group_by, 'ngày'),
        'total_revenue':    total_revenue,
        'total_orders':     total_orders,
        'delivered_orders': delivered_orders,
        'avg_order_value':  avg_order_value,
        'status_breakdown': status_breakdown,
        'revenue_rows':     revenue_rows,
        'top_products':     top_products,
        'recent_orders':    qs.order_by('-created_at')[:8],
        # JSON for charts
        'chart_labels':     json.dumps(chart_labels),
        'chart_revenue':    json.dumps(chart_revenue),
        'chart_orders':     json.dumps(chart_orders),
        'status_labels':    json.dumps([s['label'] for s in status_breakdown]),
        'status_counts':    json.dumps([s['count'] for s in status_breakdown]),
        'status_colors':    json.dumps([s['color'] for s in status_breakdown]),
    }
    return render(request, 'shop/admin/revenue_report.html', context)
 
@login_required
@user_passes_test(is_staff)
def admin_shippers(request):
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
 
    shippers = Shipper.objects.all()
 
    if search:
        shippers = shippers.filter(
            Q(name__icontains=search) | Q(phone__icontains=search) | Q(area__icontains=search)
        )
    if status:
        shippers = shippers.filter(status=status)
 
    # Thống kê nhanh
    from django.db.models import Count
    stats = {
        'total':    Shipper.objects.count(),
        'active':   Shipper.objects.filter(status='active').count(),
        'busy':     Shipper.objects.filter(status='busy').count(),
        'inactive': Shipper.objects.filter(status='inactive').count(),
    }
 
    return render(request, 'shop/admin/shippers.html', {
        'shippers':       shippers,
        'search':         search,
        'current_status': status,
        'stats':          stats,
    })
 
 
@login_required
@user_passes_test(is_staff)
def admin_shipper_detail(request, shipper_id):
    shipper = get_object_or_404(Shipper, id=shipper_id)
 
    # Đơn hàng được giao cho shipper này
    order_status = request.GET.get('order_status', '')
    orders = shipper.orders.all().order_by('-created_at')
    if order_status:
        orders = orders.filter(status=order_status)
 
    # Thống kê shipper
    from django.db.models import Sum, Count
    stats = shipper.orders.aggregate(
        total_orders=Count('id'),
        delivered=Count('id', filter=Q(status='delivered')),
        total_revenue=Sum('total', filter=Q(status='delivered')),
    )
    stats['active_orders'] = shipper.orders.filter(
        status__in=['confirmed', 'shipping']
    ).count()
 
    return render(request, 'shop/admin/shipper_detail.html', {
        'shipper':        shipper,
        'orders':         orders,
        'stats':          stats,
        'order_status':   order_status,
    })
 
 
@login_required
@user_passes_test(is_staff)
def admin_shipper_create(request):
    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        phone   = request.POST.get('phone', '').strip()
        email   = request.POST.get('email', '').strip()
        vehicle = request.POST.get('vehicle', '').strip()
        area    = request.POST.get('area', '').strip()
        status  = request.POST.get('status', 'active')
        note    = request.POST.get('note', '').strip()
        avatar  = request.FILES.get('avatar')
 
        if not name or not phone:
            messages.error(request, 'Họ tên và số điện thoại không được để trống.')
            return render(request, 'shop/admin/shipper_form.html', {'action': 'Thêm'})
 
        shipper = Shipper(
            name=name, phone=phone, email=email,
            vehicle=vehicle, area=area, status=status, note=note,
        )
        if avatar:
            shipper.avatar = avatar
        shipper.save()
        messages.success(request, f'Đã thêm shipper "{name}".')
        return redirect('shop:admin_shippers')
 
    return render(request, 'shop/admin/shipper_form.html', {
        'action': 'Thêm',
        'status_choices': Shipper.STATUS_CHOICES,
    })
 
 
@login_required
@user_passes_test(is_staff)
def admin_shipper_edit(request, shipper_id):
    shipper = get_object_or_404(Shipper, id=shipper_id)
 
    if request.method == 'POST':
        shipper.name    = request.POST.get('name', '').strip()
        shipper.phone   = request.POST.get('phone', '').strip()
        shipper.email   = request.POST.get('email', '').strip()
        shipper.vehicle = request.POST.get('vehicle', '').strip()
        shipper.area    = request.POST.get('area', '').strip()
        shipper.status  = request.POST.get('status', 'active')
        shipper.note    = request.POST.get('note', '').strip()
        if request.FILES.get('avatar'):
            shipper.avatar = request.FILES['avatar']
        shipper.save()
        messages.success(request, f'Đã cập nhật shipper "{shipper.name}".')
        return redirect('shop:admin_shippers')
 
    return render(request, 'shop/admin/shipper_form.html', {
        'shipper':        shipper,
        'action':         'Sửa',
        'status_choices': Shipper.STATUS_CHOICES,
    })
 
 
@login_required
@user_passes_test(is_staff)
def admin_shipper_delete(request, shipper_id):
    shipper = get_object_or_404(Shipper, id=shipper_id)
    if request.method == 'POST':
        name = shipper.name
        shipper.delete()
        messages.success(request, f'Đã xóa shipper "{name}".')
        return redirect('shop:admin_shippers')
    return render(request, 'shop/admin/confirm_delete.html', {
        'object':      shipper,
        'object_type': 'shipper',
        'cancel_url':  'shop:admin_shippers',
    })
 
 
@login_required
@user_passes_test(is_staff)
def admin_assign_shipper(request, order_id):
    """Gán hoặc thay đổi shipper cho một đơn hàng."""
    order = get_object_or_404(Order, id=order_id)
 
    if request.method == 'POST':
        shipper_id = request.POST.get('shipper_id')
        if shipper_id:
            shipper = get_object_or_404(Shipper, id=shipper_id)
            order.shipper = shipper
            # Tự động chuyển sang trạng thái "shipping" nếu đang confirmed
            if order.status == 'confirmed':
                order.status = 'shipping'
            order.save(update_fields=['shipper', 'status'])
            messages.success(
                request,
                f'Đã gán shipper "{shipper.name}" cho đơn #{order.id}.'
            )
        else:
            order.shipper = None
            order.save(update_fields=['shipper'])
            messages.info(request, f'Đã bỏ gán shipper khỏi đơn #{order.id}.')
 
        # Redirect về trang trước (detail order hoặc danh sách)
        next_url = request.POST.get('next', '')
        if next_url:
            return redirect(next_url)
        return redirect('shop:admin_order_update', order_id=order_id)
 
    # GET — hiển thị form chọn shipper
    available_shippers = Shipper.objects.filter(
        status__in=['active', 'busy']
    ).order_by('name')
 
    return render(request, 'shop/admin/assign_shipper.html', {
        'order':               order,
        'available_shippers':  available_shippers,
        'current_shipper':     order.shipper,
    })

def product_list(request):
    """
    Trang danh sách sản phẩm tích hợp tìm kiếm đa tiêu chí:
    - Tìm theo tên / mô tả
    - Lọc theo danh mục
    - Lọc theo khoảng giá
    - Sắp xếp
    - Chuyển đổi chế độ xem grid / list
    """
    # ── Lấy tham số ──
    q          = request.GET.get('q', '').strip()
    category   = request.GET.get('category', '').strip()
    price_min  = request.GET.get('price_min', '').strip()
    price_max  = request.GET.get('price_max', '').strip()
    sort       = request.GET.get('sort', 'default')
    in_stock   = request.GET.get('in_stock', '')
 
    # ── Base queryset ──
    products = Product.objects.select_related('category').all()
 
    # ── Lọc ──
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )
 
    if category:
        products = products.filter(category__slug=category)
 
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            pass
 
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            pass
 
    if in_stock:
        products = products.filter(stock__gt=0)
 
    # ── Sắp xếp ──
    sort_map = {
        'price_asc':  'price',
        'price_desc': '-price',
        'newest':     '-id',
        'name_asc':   'name',
        'default':    '-id',
    }
    products = products.order_by(sort_map.get(sort, '-id'))
 
    # ── Danh mục cho sidebar ──
    categories = Category.objects.all()
 
    # ── Khoảng giá cho slider (dùng min/max thực tế) ──
    from django.db.models import Min, Max
    price_range = Product.objects.aggregate(
        min_price=Min('price'), max_price=Max('price')
    )
 
    total = products.count()
 
    return render(request, 'shop/product_list.html', {
        'products':    products,
        'categories':  categories,
        'q':           q,
        'category':    category,
        'price_min':   price_min,
        'price_max':   price_max,
        'sort':        sort,
        'in_stock':    in_stock,
        'total':       total,
        'price_range': price_range,
    })
 
 
def search_ajax(request):
    """
    API gợi ý tìm kiếm nhanh (AJAX) — trả về JSON tối đa 6 sản phẩm
    """
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
 
    products = Product.objects.filter(
        Q(name__icontains=q) | Q(description__icontains=q)
    ).filter(stock__gt=0)[:6]
 
    results = [{
        'id':    p.id,
        'name':  p.name,
        'price': float(p.price),
        'image': p.image.url if p.image else None,
        'url':   f'/product/{p.id}/',
        'stock': p.stock,
        'category': p.category.name if p.category else '',
    } for p in products]
 
    return JsonResponse({'results': results, 'total': Product.objects.filter(
        Q(name__icontains=q) | Q(description__icontains=q)
    ).count()})
 
 
# ══════════════════════════════════════════════════════════════
#  ADMIN — CATEGORY MANAGEMENT
# ══════════════════════════════════════════════════════════════
 
@login_required
@user_passes_test(is_staff)
def admin_categories(request):
    categories = Category.objects.all()
    return render(request, 'shop/admin/categories.html', {
        'categories': categories
    })
 
 
@login_required
@user_passes_test(is_staff)
def admin_category_create(request):
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        icon        = request.POST.get('icon', '✨')
        description = request.POST.get('description', '').strip()
        order       = request.POST.get('order', 0)
 
        if not name:
            messages.error(request, 'Tên danh mục không được để trống.')
            return render(request, 'shop/admin/category_form.html', {'action': 'Thêm'})
 
        cat = Category(name=name, icon=icon, description=description, order=int(order))
        cat.save()
        messages.success(request, f'Đã thêm danh mục "{name}".')
        return redirect('shop:admin_categories')
 
    return render(request, 'shop/admin/category_form.html', {'action': 'Thêm'})
 
 
@login_required
@user_passes_test(is_staff)
def admin_category_edit(request, category_id):
    cat = get_object_or_404(Category, id=category_id)
 
    if request.method == 'POST':
        cat.name        = request.POST.get('name', '').strip()
        cat.icon        = request.POST.get('icon', '✨')
        cat.description = request.POST.get('description', '').strip()
        try:
            cat.order = int(request.POST.get('order', 0))
        except ValueError:
            cat.order = 0
        # Reset slug để tự sinh lại theo tên mới
        cat.slug = ''
        cat.save()
        messages.success(request, f'Đã cập nhật danh mục "{cat.name}".')
        return redirect('shop:admin_categories')
 
    return render(request, 'shop/admin/category_form.html', {
        'category': cat, 'action': 'Sửa'
    })
 
 
@login_required
@user_passes_test(is_staff)
def admin_category_delete(request, category_id):
    cat = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        name = cat.name
        cat.delete()
        messages.success(request, f'Đã xóa danh mục "{name}".')
        return redirect('shop:admin_categories')
    return render(request, 'shop/admin/confirm_delete.html', {
        'object': cat, 'object_type': 'danh mục',
        'cancel_url': 'shop:admin_categories',
    })
  