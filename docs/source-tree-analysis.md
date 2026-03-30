# Khảo Sát Cấu Trúc Hệ Thống (Source Tree)

*Tài liệu này được tạo tự động thông qua Quick Scan.*

Dự án Chat-bot-stock được cấu trúc theo kiến trúc có nhiều phần (*multi-part*) bao gồm `frontend` và `backend`. Dưới đây là cây thư mục chính và phân tích chức năng của chúng.

```text
Chat-bot-stock/
├── frontend/                 # Phần mềm Giao Diện (React/Next.js)
│   ├── src/
│   │   ├── app/              # (Suy đoán) Next.js App Router Pages
│   │   └── components/       # Các đoạn UI độc lập có thể tái sử dụng
│   │       ├── AuthModal.tsx
│   │       ├── ChatInterface.tsx
│   │       ├── InteractiveChart.tsx
│   │       ├── Navbar.tsx
│   │       └── PredictionWidget.tsx
│   ├── package.json          # Quản lý thư viện NPM của client
│   └── tsconfig.json         # Cấu hình Typescript
│
├── backend/                  # Nguồn cấp dữ liệu & AI (FastAPI/Python)
│   ├── src/
│   │   ├── api/
│   │   │   └── routes/       # Các Controller/Endpoints API (REST)
│   │   │       ├── anomaly.py
│   │   │       ├── assistant.py
│   │   │       ├── auth.py
│   │   │       ├── chat.py
│   │   │       ├── predict.py
│   │   │       └── stocks.py
│   │   ├── models/           # Mô hình cơ sở dữ liệu (Database Schema)
│   │   │   ├── stock.py      
│   │   │   └── user.py
│   │   ├── core/             # Cấu hình (vd: config.py) 
│   │   └── main.py           # Entry point của FastAPI Server
│   ├── alembic/              # Môi trường Database Migration (Dịch chuyển bảng)
│   ├── requirements.txt      # Gói Python dependencies cài đặt
│   └── run.py                # Script chạy server phát triển (Development)
│
├── docs/                     # Lưu trữ tài liệu (Cấu trúc, Context AI)
└── REFACTORING_SUMMARY.md    # Tài liệu lịch sử tóm tắt tái cấu trúc code cũ
```

### 1. Phân Tích Đường Dẫn (Frontend)

- **Entry Point**: Có vẻ như ứng dụng được chạy dựa trên lệnh `npm run dev` thông qua `next dev`. Cấu trúc của NextJS 14/15 thường dùng thư mục `src/app/` (App router) cho các Routes.
- **Thành Phần**: Các Component React như `ChatInterface.tsx` đóng vai trò rất quan trọng cho UI/UX chung. Sợi dây gắn với Backend là khả năng fetch (`fetch`/`axios`) hoặc server-actions tới cổng `localhost:8000`.

### 2. Phân Tích Đường Dẫn (Backend)

- **Entry Point**: Ứng dụng khởi chạy bắt đầu từ script `run.py` ở root của backend, mà sau đó sẽ gọi server bằng lệnh uvicorn ứng với app instance tại `src/main.py` (`src.main:app`).
- **Giao Tiếp (Integration)**: Đây là một khối monolith backend REST API hỗ trợ nhiều endpoints (chat/auth/stocks). Tích hợp Machine learning nằm ngay trong cùng một service (`predict.py`, `anomaly.py`). Backend kết nối PostgreSQL để lưu Users/Stocks.

_Ghi chú: Bản đồ rẽ nhánh (Tree) trên chỉ phân tích ở mức bề nổi do ràng buộc cài đặt Quick Scan._
