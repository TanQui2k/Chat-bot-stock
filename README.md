# StockAI Predictor

Ứng dụng phân tích, dự đoán và hỏi đáp về chứng khoán, gồm FastAPI, Next.js và PostgreSQL.

## Cấu trúc repository

```text
Chat-bot-stock/
├── backend/
│   ├── alembic/             # Migration database
│   ├── scripts/             # Tác vụ nhập/cập nhật dữ liệu
│   ├── src/
│   │   ├── api/             # Router và dependency HTTP
│   │   ├── core/            # Settings, database, security
│   │   ├── crud/            # Truy cập dữ liệu
│   │   ├── middleware/      # Middleware FastAPI
│   │   ├── ml/              # Prophet và anomaly detection
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Nghiệp vụ và tích hợp bên ngoài
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/             # Next.js App Router
│       ├── components/      # UI components
│       ├── context/         # React contexts
│       ├── lib/             # API client và cấu hình
│       └── services/        # Nghiệp vụ phía client
├── scripts/                 # Lệnh quản trị toàn repository
├── docs/                    # Tài liệu kiến trúc và phát triển
└── setup_project.bat        # Lối tắt setup trên Windows
```

## Yêu cầu

- Python 3.10+
- Node.js 20+
- PostgreSQL 17
- PowerShell 5.1+

Môi trường local của dự án dùng PostgreSQL tại `127.0.0.1:5433`, database `stock_db`, user `postgres`, không đặt password.

## Cài đặt

Từ thư mục gốc repository:

```powershell
.\scripts\setup.ps1
```

Script sẽ tạo `backend/.venv`, cài dependency backend/frontend, tạo file môi trường còn thiếu, khởi động PostgreSQL local và chạy migration.

Nếu chỉ muốn cài dependency, không khởi động database:

```powershell
.\scripts\setup.ps1 -SkipDatabase
```

## Chạy development

Mở hai terminal.

Terminal backend:

```powershell
cd backend
.\run_server.ps1
```

Terminal frontend:

```powershell
cd frontend
npm run dev
```

Các địa chỉ chính:

- Giao diện: http://localhost:3000
- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

## Kiểm tra chất lượng

Chạy toàn bộ dependency check, backend tests, frontend lint và production build:

```powershell
.\scripts\check.ps1
```

Để bỏ qua production build trong vòng lặp phát triển nhanh:

```powershell
.\scripts\check.ps1 -SkipBuild
```

## Cập nhật dữ liệu chứng khoán

```powershell
.\scripts\update-data.ps1
```

Tool sẽ tiếp tục từ ngày cuối đang lưu của từng mã và upsert theo khóa `(ticker_id, date)`, vì vậy có thể chạy lại mà không tạo bản ghi trùng.

## Cấu hình

- Backend: sao chép `backend/.env.example` thành `backend/.env`.
- Frontend: sao chép `frontend/.env.example` thành `frontend/.env.local`.
- Không commit `.env`, API key, database local, logs, `.venv`, `node_modules` hoặc `.next`.

Xem thêm tài liệu trong [`docs/index.md`](docs/index.md).
