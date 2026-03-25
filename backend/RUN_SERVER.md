# Hướng dẫn chạy Backend Server

## Cấu hình

Tất cả cấu hình server được lưu trong file `.env` ở thư mục `backend/`.

### Biến cấu hình chính:
- **SERVER_HOST**: Địa chỉ host server (mặc định: `127.0.0.1`)
- **SERVER_PORT**: Cổng server (mặc định: `8000`)
- **DATABASE_URL**: Chuỗi kết nối PostgreSQL
- **OPENAI_API_KEY**: API key của OpenAI
- **OPENAI_MODEL**: Model OpenAI sử dụng (mặc định: `gpt-4o-mini`)
- **SECRET_KEY**: Khóa bí mật cho JWT (thay đổi trong production)

## Cách chạy Server

### Cách 1: Dùng script Python (Khuyến nghị)

```bash
python run.py
```

Script sẽ tự động đọc cấu hình từ `.env` và khởi động server.

### Cách 2: Dùng batch file (Windows)

```bash
run_server.bat
```

### Cách 3: Dùng PowerShell (Windows)

```powershell
.\run_server.ps1
```

### Cách 4: Dùng uvicorn trực tiếp

```bash
# Set PYTHONPATH trước (Windows PowerShell)
$env:PYTHONPATH = "$PWD"

# Chạy uvicorn
uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload
```

## Thay đổi cấu hình

Để thay đổi port hoặc host, đơn giản là chỉnh sửa file `.env`:

```env
SERVER_HOST=0.0.0.0      # Lắng nghe tất cả interfaces
SERVER_PORT=9000         # Thay đổi port sang 9000
```

Sau đó chạy lại server - cấu hình mới sẽ được tự động sử dụng!

## Truy cập API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000

## Troubleshooting

### Lỗi `ModuleNotFoundError: No module named 'src'`

Đảm bảo bạn đang ở thư mục `backend/` khi chạy server:

```bash
cd backend
python run.py
```

### Lỗi kết nối database

Kiểm tra:
1. PostgreSQL đang chạy
2. Chuỗi `DATABASE_URL` trong `.env` đúng
3. Username/password đúng
4. Database `stock_db` đã được tạo

### Port đang được sử dụng

Nếu port 8000 đã được sử dụng, thay đổi `SERVER_PORT` trong `.env` sang port khác.
