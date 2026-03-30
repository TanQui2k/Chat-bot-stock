# Bảng Hướng Dẫn Phát Triển (Development Guide)

*Đây là tài liệu chỉ định các bước chuẩn bị, cài đặt môi trường và các lệnh cần thiết để phát triển hệ thống Chat-bot-stock. Tài liệu khởi chiếu thông qua quá trình Quét Nhanh.*

## 1. Yêu Cầu Chung (Prerequisites)
- **Node.js**: Phiên bản ^20.x được khuyến nghị. Dùng để biên dịch và chạy Frontend. Môi trường `npm` cài đặt.
- **Python**: Phiên bản 3.10+ vì Backend dùng nhiều thư viện khoa học dữ liệu mới (Pandas, Joblib, Scikit) và FastAPI.
- **Database**: PostgreSQL dịch vụ cài đặt locally (port: 5432).

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

```bash
# 1. Di chuyển vào thư mục
cd backend

# 2. Tạo một môi trường Ảo (Virtual Environment)
python -m venv .venv

# 3. Kích hoạt môi trường (Windows)
.venv\\Scripts\\activate
# HOẶC (MacOS/Linux): source .venv/bin/activate

# 4. Cài đặt Python Dependencies
pip install -r requirements.txt
```

### Thiết Lập `.env` Vận Hành
Hệ thống Back-end sử dụng dữ liệu mật trong `backend/.env`. Sao chép dự thảo gốc:
`cp .env.example .env` (Hoặc chỉnh thủ công theo template). Cập nhật `DATABASE_URL` chỉ đến PostgreSQL và điền `OPENAI_API_KEY`.

### Thiết Lập Cơ Sở Dữ Liệu
PostgreSQL lưu trữ mã chứng khoán/người dùng. Migrate CSDL:
```bash
alembic upgrade head
```

### Lệnh Chạy Server
Sử dụng script để khởi chạy Development Server:
```bash
# Sẽ tự load config/host/port. Mặc định nằm tại :8000
python run.py
```
*(Swagger UI Docs API tham khảo tại http://localhost:8000/docs)*
