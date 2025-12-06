# API Reference - Website Bán Mỹ Phẩm

## 🔐 Authentication APIs

### Đăng Ký
- **URL**: `POST /api/auth/register`
- **Body**: 
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "fullName": "string",
  "phone": "string",
  "address": "string"
}
```
- **Response**: 
```json
{
  "message": "Đăng ký thành công",
  "userId": "long"
}
```

### Đăng Nhập
- **URL**: `POST /api/auth/login`
- **Body**: 
```json
{
  "username": "string",
  "password": "string"
}
```
- **Response**: 
```json
{
  "token": "string",
  "userId": "long",
  "username": "string",
  "role": "string"
}
```

## 🛍️ Product APIs

### Lấy Danh Sách Sản Phẩm
- **URL**: `GET /api/products`
- **Query Params**: 
  - `page` (int, default: 0)
  - `size` (int, default: 10)
  - `category` (long, optional)
  - `search` (string, optional)
- **Response**: 
```json
{
  "products": [],
  "totalPages": "int",
  "totalElements": "long"
}
```

### Lấy Chi Tiết Sản Phẩm
- **URL**: `GET /api/products/{id}`
- **Response**: 
```json
{
  "id": "long",
  "name": "string",
  "description": "string",
  "price": "double",
  "image": "string",
  "category": "object",
  "stock": "int"
}
```

### Tạo Sản Phẩm (Admin)
- **URL**: `POST /api/products`
- **Headers**: `Authorization: Bearer {token}`
- **Body**: 
```json
{
  "name": "string",
  "description": "string",
  "price": "double",
  "image": "string",
  "categoryId": "long",
  "stock": "int"
}
```
- **Response**: 
```json
{
  "message": "Tạo sản phẩm thành công",
  "productId": "long"
}
```

### Cập Nhật Sản Phẩm (Admin)
- **URL**: `PUT /api/products/{id}`
- **Headers**: `Authorization: Bearer {token}`
- **Body**: 
```json
{
  "name": "string",
  "description": "string",
  "price": "double",
  "image": "string",
  "categoryId": "long",
  "stock": "int"
}
```
- **Response**: 
```json
{
  "message": "Cập nhật sản phẩm thành công"
}
```

### Xóa Sản Phẩm (Admin)
- **URL**: `DELETE /api/products/{id}`
- **Headers**: `Authorization: Bearer {token}`
- **Query Params**: `confirm=true` ⚠️ **BẮT BUỘC**
- **Response**: 
```json
{
  "message": "Xóa sản phẩm thành công"
}
```

## 🛒 Cart APIs

### Lấy Giỏ Hàng
- **URL**: `GET /api/cart`
- **Headers**: `Authorization: Bearer {token}`
- **Response**: 
```json
{
  "items": [],
  "totalAmount": "double"
}
```

### Thêm Vào Giỏ
- **URL**: `POST /api/cart/items`
- **Headers**: `Authorization: Bearer {token}`
- **Body**: 
```json
{
  "productId": "long",
  "quantity": "int"
}
```
- **Response**: 
```json
{
  "message": "Thêm vào giỏ hàng thành công"
}
```

### Cập Nhật Số Lượng
- **URL**: `PUT /api/cart/items/{itemId}`
- **Headers**: `Authorization: Bearer {token}`
- **Body**: 
```json
{
  "quantity": "int"
}
```
- **Response**: 
```json
{
  "message": "Cập nhật giỏ hàng thành công"
}
```

### Xóa Khỏi Giỏ
- **URL**: `DELETE /api/cart/items/{itemId}`
- **Headers**: `Authorization: Bearer {token}`
- **Query Params**: `confirm=true` ⚠️ **BẮT BUỘC**
- **Response**: 
```json
{
  "message": "Xóa sản phẩm khỏi giỏ hàng thành công"
}
```

## 📦 Order APIs

### Đặt Hàng
- **URL**: `POST /api/orders`
- **Headers**: `Authorization: Bearer {token}`
- **Body**: 
```json
{
  "shippingAddress": "string",
  "phone": "string",
  "note": "string"
}
```
- **Response**: 
```json
{
  "message": "Đặt hàng thành công",
  "orderId": "long",
  "totalAmount": "double"
}
```

### Lấy Danh Sách Đơn Hàng
- **URL**: `GET /api/orders`
- **Headers**: `Authorization: Bearer {token}`
- **Query Params**: 
  - `page` (int, default: 0)
  - `size` (int, default: 10)
- **Response**: 
```json
{
  "orders": []
}
```

### Chi Tiết Đơn Hàng
- **URL**: `GET /api/orders/{id}`
- **Headers**: `Authorization: Bearer {token}`
- **Response**: 
```json
{
  "id": "long",
  "items": [],
  "totalAmount": "double",
  "status": "string",
  "createdAt": "datetime"
}
```

### Hủy Đơn Hàng
- **URL**: `PUT /api/orders/{id}/cancel`
- **Headers**: `Authorization: Bearer {token}`
- **Query Params**: `confirm=true` ⚠️ **BẮT BUỘC**
- **Response**: 
```json
{
  "message": "Hủy đơn hàng thành công"
}
```

## 📂 Category APIs

### Lấy Danh Mục
- **URL**: `GET /api/categories`
- **Response**: 
```json
{
  "categories": []
}
```

### Tạo Danh Mục (Admin)
- **URL**: `POST /api/categories`
- **Headers**: `Authorization: Bearer {token}`
- **Body**: 
```json
{
  "name": "string",
  "description": "string"
}
```
- **Response**: 
```json
{
  "message": "Tạo danh mục thành công",
  "categoryId": "long"
}
```

### Cập Nhật Danh Mục (Admin)
- **URL**: `PUT /api/categories/{id}`
- **Headers**: `Authorization: Bearer {token}`
- **Body**: 
```json
{
  "name": "string",
  "description": "string"
}
```
- **Response**: 
```json
{
  "message": "Cập nhật danh mục thành công"
}
```

### Xóa Danh Mục (Admin)
- **URL**: `DELETE /api/categories/{id}`
- **Headers**: `Authorization: Bearer {token}`
- **Query Params**: `confirm=true` ⚠️ **BẮT BUỘC**
- **Response**: 
```json
{
  "message": "Xóa danh mục thành công"
}
```

## 🔑 Keywords & Concepts

### Security
- **JWT (JSON Web Token)**: Token-based authentication
- **BCrypt Password Hashing**: Mã hóa mật khẩu an toàn
- **Role-based Access Control**: Phân quyền USER, ADMIN
- **Token Expiration**: 24 giờ

### Database Tables
- `users` - Người dùng
- `products` - Sản phẩm mỹ phẩm
- `categories` - Danh mục sản phẩm
- `carts` - Giỏ hàng
- `cart_items` - Sản phẩm trong giỏ
- `orders` - Đơn hàng
- `order_items` - Chi tiết đơn hàng

### HTTP Status Codes
- **200 OK**: Thành công
- **201 Created**: Tạo mới thành công
- **400 Bad Request**: Dữ liệu không hợp lệ
- **401 Unauthorized**: Chưa đăng nhập
- **403 Forbidden**: Không có quyền truy cập
- **404 Not Found**: Không tìm thấy
- **500 Server Error**: Lỗi server

### Validation Rules
- **Username**: 3-50 ký tự, không chứa ký tự đặc biệt
- **Email**: Định dạng email hợp lệ
- **Password**: Tối thiểu 6 ký tự
- **Phone**: 10-11 số
- **Quantity**: Phải > 0
- **Price**: Phải > 0
- **Stock**: Phải >= 0

### Order Status
- `PENDING` - Chờ xác nhận
- `CONFIRMED` - Đã xác nhận
- `SHIPPING` - Đang giao
- `DELIVERED` - Đã giao
- `CANCELLED` - Đã hủy

## ⚠️ Lưu Ý Quan Trọng

### Xác Nhận Xóa
Tất cả các thao tác xóa đều yêu cầu tham số `?confirm=true`:
- Xóa sản phẩm
- Xóa khỏi giỏ hàng
- Hủy đơn hàng
- Xóa danh mục

### Authentication
- Token phải được gửi trong header: `Authorization: Bearer {token}`
- Token hết hạn sau 24 giờ
- API không yêu cầu authentication: `/api/auth/*`, `GET /api/products`, `GET /api/categories`

### Pagination
- Trang đầu tiên: `page=0`
- Kích thước mặc định: `size=10`
- Kích thước tối đa: `size=100`