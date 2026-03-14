# Chat-bot-stock (StockAI Predictor)

Dự án này bao gồm hai phần chính: **Backend** (FastAPI) và **Frontend** (Next.js). Dưới đây là hướng dẫn chi tiết để thiết lập và khởi chạy dự án trên máy tính cục bộ.

## 🛠 Yêu cầu hệ thống (Prerequisites)

Trước khi bắt đầu, hãy đảm bảo máy tính của bạn đã cài đặt các phần mềm sau:
- **Python 3.8+** (cho Backend)
- **Node.js 18+** & **npm/yarn/pnpm** (cho Frontend)
- **PostgreSQL** (Hệ quản trị cơ sở dữ liệu)

---

## ⚙️ Thiết lập Database

1. Cài đặt và khởi động PostgreSQL.
2. Tạo một database mới cho dự án (ví dụ: `stock_db`).
3. (Tùy chọn) Đảm bảo user/mật khẩu PostgreSQL khớp với cấu hình trong Backend.

---

## 🐍 Thiết lập Backend (FastAPI)

1. **Di chuyển vào thư mục backend**:
   ```bash
   cd backend
   ```

2. **Tạo và kích hoạt môi trường ảo (Virtual Environment)**:
   - Trên Windows:
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - Trên macOS/Linux:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Cài đặt các thư viện phụ thuộc (Dependencies)**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Cấu hình môi trường**:
   - Nếu chưa có file `.env`, hãy tạo một file tên `.env` trong thư mục `backend/` dựa trên cấu hình mẫu.
   - Cập nhật chuỗi kết nối PostgreSQL (thay thế `<username>`, `<password>`, `<host>`, `<port>`, `<database_name>` cho phù hợp với máy tính của bạn), ví dụ:
     ```env
     DATABASE_URL=postgresql+psycopg://root:postgres@127.0.0.1:5432/stock_db
     ```

5. **Chạy Migration Database (Khởi tạo các bảng cơ sở dữ liệu)**:
   ```bash
   alembic upgrade head
   ```
   *(Đảm bảo đã thiết lập database và file `.env` đúng với cấu hình database của bạn trước khi chạy bước này)*

6. **Chạy Server Backend**:
   ```bash
   uvicorn src.main:app --reload
   ```
   - Backend sẽ chạy tại: `http://localhost:8000`
   - Tài liệu API Swagger UI (dùng để test API): `http://localhost:8000/docs`

---

## 💻 Thiết lập Frontend (Next.js)

1. **Di chuyển vào thư mục frontend**:
   ```bash
   # Mở một cửa sổ terminal mới (hoặc tab mới), di chuyển vào thư mục root của dự án
   cd frontend
   ```

2. **Cài đặt dependencies**:
   ```bash
   npm install
   # hoặc
   yarn install
   # hoặc
   pnpm install
   ```

3. **Chạy Server Frontend (Development mode)**:
   ```bash
   npm run dev
   # hoặc
   yarn dev
   # hoặc
   pnpm dev
   ```
   - Frontend sẽ chạy tại: `http://localhost:3000`

---

## 🚀 Cách sử dụng

1. Đợi cả **Backend** và **Frontend** đều đang chạy trên hai terminal riêng biệt, không có lỗi.
2. Mở trình duyệt và truy cập vào [http://localhost:3000](http://localhost:3000) để sử dụng ứng dụng.
3. Nếu frontend cần gọi api, api sẽ tự gọi đến backend `http://localhost:8000/api/...` (đã được config CORS).