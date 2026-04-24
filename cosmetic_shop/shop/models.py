from django.db import models

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
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('shipping',  'Đang giao'),
        ('delivered', 'Đã giao'),
    ]

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
        return self.products.filter(stock__gt=0).count()    
    

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