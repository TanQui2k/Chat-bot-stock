# 🚀 Chat-bot-stock (StockAI Predictor)

Một ứng dụng hỗ trợ dự đoán và phân tích chứng khoán sử dụng trí tuệ nhân tạo (AI). Dự án được xây dựng với kiến trúc hiện đại, bao gồm **Backend (FastAPI)** và **Frontend (Next.js)**.

## ✨ Tính năng nổi bật

- 📈 **Phân tích chứng khoán**: Theo dõi và phân tích dữ liệu thị trường.
- 🤖 **Chat-bot thông minh**: Hỗ trợ giải đáp các câu hỏi về tài chính và chứng khoán.
- ⚡ **Hiệu năng cao**: Backend viết bằng FastAPI cung cấp phản hồi cực nhanh.
- 🎨 **Giao diện hiện đại**: Frontend chuẩn React/Next.js mượt mà và trực quan.

## 🏗 Cấu trúc dự án

```text
Chat-bot-stock/
├── backend/          # Nguồn cấp dữ liệu và xử lý AI (FastAPI)
├── frontend/         # Giao diện người dùng (Next.js/React)
├── .gitignore        # Cấu hình bỏ qua các tệp không cần thiết
└── README.md         # Hướng dẫn dự án
```

---

## 🛠 Yêu cầu hệ thống (Prerequisites)

Đảm bảo máy của bạn đã cài:

- **Python 3.10+** (Backend)
- **Node.js 18+** & **npm/yarn/pnpm** (Frontend)
- **PostgreSQL** (Cơ sở dữ liệu)

---

## ⚙️ Hướng dẫn cài đặt

### 1. Thiết lập Database

1. Cài đặt và chạy dịch vụ **PostgreSQL**.
2. Tạo một database mới tên: `stock_db`.

### 2. Thiết lập Backend (FastAPI)

1. **Di chuyển vào thư mục backend**:

   ```bash
   cd backend
   ```

2. **Tạo môi trường ảo & Cài đặt thư viện**:

   ```bash
   python -m venv .venv
   # Active trên Windows:
   .venv\Scripts\activate
   # Active trên Linux/MacOS:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Cấu hình môi trường**:

   - Tạo file `.env` trong thư mục `backend/`.
   - Cập nhật chuỗi kết nối PostgreSQL:

     ```env
     DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/stock_db
     ```

4. **Khởi tạo Database (Migrations)**:

   ```bash
   alembic upgrade head
   ```

5. **Chạy Server**:

   ```bash
   uvicorn src.main:app --reload
   ```

   > 🔗 Truy cập: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

### 3. Thiết lập Frontend (Next.js)

1. **Di chuyển vào thư mục frontend**:

   ```bash
   cd frontend
   ```

2. **Cài đặt & Chạy Development**:

   ```bash
   npm install
   npm run dev
   ```

   > 🔗 Truy cập: [http://localhost:3000](http://localhost:3000)

---

## 🚀 Quy trình sử dụng

1. Đảm bảo cả hai máy chủ (Backend & Frontend) đang chạy đồng thời.
2. Truy cập cổng `3000` trên trình duyệt để bắt đầu trải nghiệm.

## 📄 Giấy phép

Dự án được phát triển cho mục đích học tập và nghiên cứu.