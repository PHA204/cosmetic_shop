from django.db import models
from django.contrib.auth.models import User

class Store(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    phone = models.CharField(max_length=20)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    # max_digits=15, decimal_places=0 → chứa được tới 999,999,999,999,999 VND
    price = models.DecimalField(max_digits=15, decimal_places=0)
    category = models.ForeignKey(
       'Category',
       null=True, blank=True,
       on_delete=models.SET_NULL,
       related_name='products',
       verbose_name='Danh mục'
   )
    description = models.TextField()
    image = models.ImageField(upload_to='products/', blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping',  'Đng giao'),
        ('delivered', 'Đã giao'),
    ]

    user = models.ForeignKey(
        'auth.User',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='shop_orders',
        verbose_name='Khách hàng (Tài khoản)'
    )
    customer_name = models.CharField(max_length=200)
    phone         = models.CharField(max_length=20)
    address       = models.CharField(max_length=300)
    latitude      = models.FloatField(null=True, blank=True)
    longitude     = models.FloatField(null=True, blank=True)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at    = models.DateTimeField(auto_now_add=True)
    total         = models.DecimalField(max_digits=15, decimal_places=0, default=0)
    shipper = models.ForeignKey(
       'Shipper',
       null=True, blank=True,
       on_delete=models.SET_NULL,
       related_name='orders',
       verbose_name='Shipper phụ trách'
   )
    store = models.ForeignKey(
       'Store',
       null=True, blank=True,
       on_delete=models.SET_NULL,
       related_name='orders',
       verbose_name='Chi nhánh xử lý'
   )
    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order    = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product  = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price    = models.DecimalField(max_digits=15, decimal_places=0)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Shipper(models.Model):
    STATUS_CHOICES = [
        ('active',   'Đang hoạt động'),
        ('inactive', 'Tạm nghỉ'),
        ('busy',     'Đang giao hàng'),
    ]

    name      = models.CharField(max_length=200, verbose_name='Họ tên')
    phone     = models.CharField(max_length=20,  verbose_name='Số điện thoại')
    email     = models.EmailField(blank=True,     verbose_name='Email')
    vehicle   = models.CharField(max_length=100, blank=True, verbose_name='Phương tiện')
    avatar    = models.ImageField(upload_to='shippers/', blank=True, verbose_name='Ảnh đại diện')
    status    = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                 default='active', verbose_name='Trạng thái')
    area      = models.CharField(max_length=200, blank=True, verbose_name='Khu vực phụ trách')
    joined_at = models.DateField(auto_now_add=True, verbose_name='Ngày vào làm')
    note      = models.TextField(blank=True, verbose_name='Ghi chú')

    class Meta:
        verbose_name        = 'Shipper'
        verbose_name_plural = 'Shippers'
        ordering            = ['name']

    def __str__(self):
        return f'{self.name} ({self.phone})'

    @property
    def active_orders_count(self):
        return self.orders.filter(status__in=['confirmed', 'shipping']).count()

    @property
    def total_delivered(self):
        return self.orders.filter(status='delivered').count()


class Category(models.Model):
    ICON_CHOICES = [
        ('💄', 'Son môi'),
        ('🧴', 'Kem dưỡng'),
        ('💅', 'Nail & Móng'),
        ('🌸', 'Nước hoa'),
        ('👁️', 'Mắt'),
        ('🧖', 'Chăm sóc da'),
        ('💆', 'Chăm sóc tóc'),
        ('🧼', 'Làm sạch'),
        ('☀️', 'Chống nắng'),
        ('✨', 'Khác'),
    ]

    name        = models.CharField(max_length=100, unique=True, verbose_name='Tên danh mục')
    slug        = models.SlugField(max_length=120, unique=True, blank=True)
    icon        = models.CharField(max_length=10, default='✨', verbose_name='Icon')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    order       = models.PositiveIntegerField(default=0, verbose_name='Thứ tự hiển thị')

    class Meta:
        verbose_name        = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering            = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            import re, unicodedata
            # Simple Vietnamese slug
            value = self.name.lower()
            replacements = {
                'à':'a','á':'a','ả':'a','ã':'a','ạ':'a',
                'ă':'a','ắ':'a','ằ':'a','ẳ':'a','ẵ':'a','ặ':'a',
                'â':'a','ấ':'a','ầ':'a','ẩ':'a','ẫ':'a','ậ':'a',
                'đ':'d',
                'è':'e','é':'e','ẻ':'e','ẽ':'e','ẹ':'e',
                'ê':'e','ế':'e','ề':'e','ể':'e','ễ':'e','ệ':'e',
                'ì':'i','í':'i','ỉ':'i','ĩ':'i','ị':'i',
                'ò':'o','ó':'o','ỏ':'o','õ':'o','ọ':'o',
                'ô':'o','ố':'o','ồ':'o','ổ':'o','ỗ':'o','ộ':'o',
                'ơ':'o','ớ':'o','ờ':'o','ở':'o','ỡ':'o','ợ':'o',
                'ù':'u','ú':'u','ủ':'u','ũ':'u','ụ':'u',
                'ư':'u','ứ':'u','ừ':'u','ử':'u','ữ':'u','ự':'u',
                'ỳ':'y','ý':'y','ỷ':'y','ỹ':'y','ỵ':'y',
            }
            for vn, en in replacements.items():
                value = value.replace(vn, en)
            value = re.sub(r'[^a-z0-9\s-]', '', value)
            value = re.sub(r'[\s]+', '-', value.strip())
            self.slug = value or f'category-{self.pk}'
        super().save(*args, **kwargs)

    @property
    def product_count(self):
        from django.db.models import Sum
        # Đếm sản phẩm có tồn kho > 0 (tổng từ inventory)
        return self.products.annotate(
            total_stock=Sum('inventory__stock')
        ).filter(total_stock__gt=0).count()


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Sản phẩm'
    )
    image   = models.ImageField(upload_to='products/gallery/', verbose_name='Ảnh')
    order   = models.PositiveIntegerField(default=0, verbose_name='Thứ tự')
    alt     = models.CharField(max_length=200, blank=True, verbose_name='Alt text')

    class Meta:
        verbose_name        = 'Ảnh sản phẩm'
        verbose_name_plural = 'Ảnh sản phẩm'
        ordering            = ['order']

    def __str__(self):
        return f'{self.product.name} — ảnh {self.order}'


class StoreProduct(models.Model):
    """Quản lý tồn kho theo từng chi nhánh"""
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name='Chi nhánh'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name='Sản phẩm'
    )
    stock = models.PositiveIntegerField(default=0, verbose_name='Số lượng tồn kho')

    class Meta:
        verbose_name = 'Tồn kho chi nhánh'
        verbose_name_plural = 'Tồn kho chi nhánh'
        unique_together = [['store', 'product']]  # Mỗi chi nhánh chỉ có 1 dòng cho 1 sản phẩm

    def __str__(self):
        return f'{self.store.name} - {self.product.name}: {self.stock}'


class AboutPage(models.Model):
    """Quản lý nội dung trang giới thiệu"""
    # Hero Section
    hero_label = models.CharField(max_length=100, default='Về chúng tôi', verbose_name='Nhãn Hero')
    hero_title = models.CharField(max_length=200, default='Vẻ đẹp <em>chân thực</em><br>từ thiên nhiên', verbose_name='Tiêu đề Hero')
    hero_text = models.TextField(default='Cosmetic Shop — thương hiệu mỹ phẩm thuần thiên nhiên, chính hãng hàng đầu Việt Nam. Chúng tôi tin rằng mỗi người đều xứng đáng được chăm sóc bằng những sản phẩm an toàn, hiệu quả và bền vững.', verbose_name='Mô tả Hero')
    hero_image = models.ImageField(upload_to='about/', blank=True, verbose_name='Ảnh Hero')
    
    # Stats
    branches_text = models.CharField(max_length=50, default='Chi nhánh', verbose_name='Text Chi nhánh')
    customers_text = models.CharField(max_length=50, default='Khách hàng', verbose_name='Text Khách hàng')
    products_text = models.CharField(max_length=50, default='Sản phẩm', verbose_name='Text Sản phẩm')
    rating_text = models.CharField(max_length=50, default='Đánh giá', verbose_name='Text Đánh giá')
    
    # Story Section
    story_label = models.CharField(max_length=100, default='Câu chuyện của chúng tôi', verbose_name='Nhãn Story')
    story_title = models.CharField(max_length=200, default='Từ đam mê đến thương hiệu', verbose_name='Tiêu đề Story')
    story_year = models.CharField(max_length=10, default='2019', verbose_name='Năm thành lập')
    story_year_label = models.CharField(max_length=50, default='Năm thành lập', verbose_name='Label Năm')
    story_image = models.ImageField(upload_to='about/', blank=True, verbose_name='Ảnh Story')
    story_text_1 = models.TextField(default='Cosmetic Shop được thành lập năm 2019 bởi nhóm những người trẻ đam mê vẻ đẹp tự nhiên và bền vững. Khởi đầu từ một cửa hàng nhỏ tại Quận Tân Bình, TP.HCM, chúng tôi đã nhanh chóng chinh phục khách hàng bằng cam kết về chất lượng và sự tận tâm.', verbose_name='Đoạn văn 1')
    story_text_2 = models.TextField(default='Sau 5 năm phát triển, Cosmetic Shop đã mở rộng hệ thống chi nhánh trên toàn thành phố, phục vụ hàng chục nghìn khách hàng mỗi tháng. Mỗi sản phẩm đều được chọn lọc kỹ càng từ các thương hiệu uy tín trong và ngoài nước, đảm bảo an toàn và hiệu quả tuyệt đối.', verbose_name='Đoạn văn 2')
    
    # Stats badges
    authentic_text = models.CharField(max_length=50, default='Sản phẩm chính hãng', verbose_name='Text 100%')
    return_text = models.CharField(max_length=50, default='Ngày đổi trả', verbose_name='Text Đổi trả')
    support_text = models.CharField(max_length=50, default='Hỗ trợ khách hàng', verbose_name='Text Hỗ trợ')
    
    # Values Section
    values_label = models.CharField(max_length=100, default='Giá trị cốt lõi', verbose_name='Nhãn Giá trị')
    values_title = models.CharField(max_length=200, default='Những điều chúng tôi tin tưởng', verbose_name='Tiêu đề Giá trị')
    
    # CTA Section
    cta_title = models.CharField(max_length=200, default='Sẵn sàng trải nghiệm<br>vẻ đẹp <em>đích thực</em>?', verbose_name='Tiêu đề CTA')
    cta_text = models.TextField(default='Khám phá hàng trăm sản phẩm chính hãng hoặc ghé thăm chi nhánh gần nhất để được tư vấn miễn phí.', verbose_name='Mô tả CTA')
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật lần cuối')

    class Meta:
        verbose_name = 'Trang giới thiệu'
        verbose_name_plural = 'Trang giới thiệu'

    def __str__(self):
        return 'Trang Giới Thiệu'


class AboutValue(models.Model):
    """Giá trị cốt lõi trang giới thiệu"""
    about = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='values')
    icon = models.CharField(max_length=20, default='🌿', verbose_name='Icon')
    title = models.CharField(max_length=100, verbose_name='Tiêu đề')
    description = models.TextField(verbose_name='Mô tả')
    order = models.PositiveIntegerField(default=0, verbose_name='Thứ tự')

    class Meta:
        verbose_name = 'Giá trị cốt lõi'
        verbose_name_plural = 'Giá trị cốt lõi'
        ordering = ['order']

    def __str__(self):
        return self.title


class AboutGallery(models.Model):
    """Thư viện ảnh trang giới thiệu"""
    about = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='about/gallery/', verbose_name='Ảnh')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Chú thích')
    order = models.PositiveIntegerField(default=0, verbose_name='Thứ tự')

    class Meta:
        verbose_name = 'Ảnh thư viện'
        verbose_name_plural = 'Ảnh thư viện'
        ordering = ['order']

    def __str__(self):
        return self.caption or f'Ảnh #{self.order}'