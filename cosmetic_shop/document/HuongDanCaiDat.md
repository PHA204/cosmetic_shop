# Hướng Dẫn Cài Đặt - Cosmetic Shop

## Yêu Cầu Hệ Thống

- **Python**: 3.10 trở lên
- **Database**: PostgreSQL 14+
- **Hệ điều hành**: Windows / macOS / Linux

---

## Bước 1: Cài Đặt Python

1. Tải Python từ [python.org](https://www.python.org/downloads/)
2. Chọn phiên bản **Python 3.10** hoặc mới hơn
3. **Quan trọng**: Tick chọn "Add Python to PATH"
4. Kiểm tra cài đặt:
   ```bash
   python --version
   ```

---

## Bước 2: Cài Đặt PostgreSQL

### Windows
1. Tải PostgreSQL từ [postgresql.org](https://www.postgresql.org/download/windows/)
2. Cài đặt với các tùy chọn mặc định
3. Đặt mật khẩu cho user `postgres` (mặc định trong code là: `123456`)
4. Port mặc định: `5432`

### Tạo Database
Sau khi cài đặt PostgreSQL, tạo database `cosmetic_db`:

```bash
# Mở psql (PostgreSQL Command Line)
psql -U postgres

# Tạo database
CREATE DATABASE cosmetic_db;

# Thoát
\q
```

---

## Bước 3: Clone/Copy Project

```bash
# Di chuyển vào thư mục project
cd D:\Document\Python_Code\cosmetic_shop\cosmetic_shop
```

---

## Bước 4: Tạo Virtual Environment

```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

---

## Bước 5: Cài Đặt Dependencies

```bash
pip install django psycopg2-binary
```

**Các thư viện bổ sung (nếu cần):**
```bash
pip install pillow openpyxl
```

---

## Bước 6: Cấu Hình Database

Mở file `cosmetic_shop/settings.py` và kiểm tra cấu hình database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cosmetic_db',
        'USER': 'postgres',
        'PASSWORD': '123456',  # ← Đổi nếu bạn đặt mật khẩu khác
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Nếu chưa có PostgreSQL**, có thể tạm dùng SQLite:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

## Bước 7: Chạy Migration

```bash
python manage.py migrate
```

---

## Bước 8: Tạo Superuser (Admin)

```bash
python manage.py createsuperuser
```

Nhập:
- Username
- Email
- Password

---

## Bước 9: Chạy Server

```bash
python manage.py runserver
```

Truy cập:
- **Website**: http://127.0.0.1:8000
- **Admin**: http://127.0.0.1:8000/admin

---

## Cấu Hình Bổ Sung (Tùy Chọn)

### GEMINI_API_KEY
Nếu sử dụng tính năng AI, thêm API key trong `settings.py`:
```python
GEMINI_API_KEY = 'YOUR_API_KEY_HERE'
```

### Static & Media Files
Đã được cấu hình sẵn trong `settings.py`:
```python
STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## Các Lệnh Hữu Ích

| Lệnh | Mô tả |
|------|-------|
| `python manage.py runserver` | Chạy server |
| `python manage.py createsuperuser` | Tạo admin |
| `python manage.py makemigrations` | Tạo migration mới |
| `python manage.py migrate` | Áp dụng migration |
| `python manage.py collectstatic` | Thu thập static files |

---

## Xử Lý Sự Cố

### Lỗi "Module not found"
```bash
pip install -r requirements.txt
```

### Lỗi kết nối PostgreSQL
- Kiểm tra PostgreSQL đang chạy
- Kiểm tra username/password
- Kiểm tra database `cosmetic_db` đã được tạo

### Lỗi "Database does not exist"
```bash
# Tạo database trong psql
CREATE DATABASE cosmetic_db;
```

---

## Liên Hệ Hỗ Trợ

Nếu gặp vấn đề, hãy kiểm tra:
1. Python version: `python --version`
2. Django version: `python -m django --version`
3. PostgreSQL: `psql -U postgres -c "SELECT version();"`

---

**Chúc bạn cài đặt thành công!** 🎉