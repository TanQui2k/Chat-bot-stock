# Bảng Hướng Dẫn Phát Triển (Development Guide)

*Đây là tài liệu chỉ định các bước chuẩn bị, cài đặt môi trường và các lệnh cần thiết để phát triển hệ thống Chat-bot-stock. Tài liệu khởi chiếu thông qua quá trình Quét Nhanh.*

## 1. Yêu Cầu Chung (Prerequisites)
- **Node.js**: Phiên bản ^20.x được khuyến nghị. Dùng để biên dịch và chạy Frontend. Môi trường `npm` cài đặt.
- **Python**: Phiên bản 3.10+ vì Backend dùng nhiều thư viện khoa học dữ liệu mới (Pandas, Joblib, Scikit) và FastAPI.
- **Database**: PostgreSQL 17. Môi trường local của dự án chạy ở port `5433`.

---

## 2. Phần Giao Diện (Frontend - Next.js)

### Thiết Kế Môi Trường 
Thư mục gốc: `Chat-bot-stock/frontend/`

```bash
# Di chuyển vào thư mục frontend
cd frontend

# Cài đặt thư viện (dependencies)
npm install
```

### Các Lệnh Quản Trị Hệ Thống Next
Dựa vào tệp (package.json):
- `npm run dev`: Chạy server phát triển (Development Server) ở cổng `:3000`.
- `npm run build`: Build bản production tối ưu hóa (Optimized Production Output).
- `npm start`: Khởi động lại dịch vụ Next.js production đã phân bổ.
- `npm run lint`: Thực hiện kiếm soát quy tắc Code style (ESLint).

---

## 3. Phần Dịch Vụ API & AI (Backend - FastAPI)

### Thiết Kế Môi Trường
Thư mục gốc: `Chat-bot-stock/backend/`

Từ thư mục gốc, cách khuyến nghị là chạy `scripts/setup.ps1`. Script tạo virtual environment, cài cả backend/frontend, khởi động PostgreSQL local và áp dụng migration.

```powershell
.\scripts\setup.ps1
```

Thiết lập thủ công vẫn có thể thực hiện trong `backend/` bằng `python -m venv .venv` và `pip install -r requirements.txt`.

### Thiết Lập `.env` Vận Hành
Hệ thống Back-end sử dụng dữ liệu mật trong `backend/.env`. Sao chép dự thảo gốc:
`cp .env.example .env` (Hoặc chỉnh thủ công theo template). Cập nhật `DATABASE_URL` chỉ đến PostgreSQL và điền `OPENAI_API_KEY`.

### Thiết Lập Cơ Sở Dữ Liệu
PostgreSQL lưu trữ mã chứng khoán/người dùng. Database local mặc định là `postgres@127.0.0.1:5433/stock_db`. Migrate CSDL:
```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### Lệnh Chạy Server
Sử dụng script để khởi chạy Development Server:
```powershell
# Sẽ tự load config/host/port. Mặc định nằm tại :8000
.\run_server.ps1
```
*(Swagger UI Docs API tham khảo tại http://localhost:8000/docs)*

## 4. Kiểm tra và cập nhật dữ liệu

Từ thư mục gốc repository:

```powershell
# Test backend, lint và build frontend
.\scripts\check.ps1

# Bổ sung dữ liệu giá còn thiếu
.\scripts\update-data.ps1
```
