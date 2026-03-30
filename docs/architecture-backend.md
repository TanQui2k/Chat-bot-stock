# Architecture - Backend

## Mở Bài (Executive Summary)
Máy chủ trung tâm phân tích dữ liệu chuyên nghiệp kết nối người dùng/client với AI/Machine Learning cho việc định hướng thị trường.

## Đặc tính Xây Dựng (Technology Stack)
- Mô hình chính: Python 3.10+, Framework mở rộng HTTP không rào cản ASGI thông qua `FastAPI`, quản trị nền bởi `Uvicorn`.
- Tương tác Database: Relational database thông qua PostgreSQL và SQLAlchemy làm ánh xạ (ORM), kèm các migration bảo chứng qua `Alembic`.
- Bảo Mật (Security/Authn): Hỗ trợ sinh hàm băm/bcrypt qua `passlib` và hỗ trợ token JWT từ `python-jose[cryptography]`.
- Năng lực Cốt lõi (AI & Toán): Dùng Dataframes tính toán cổ phiếu bởi `pandas` và `numpy` (Dự đoán). Học mô hình (được save với đuôi thư viện `joblib` hoặc thông qua `sklearn`). Nguồn mã chứng khoán/thị trường (`vnstock`). Hỗ trợ LLM Chat OpenAi API (`openai/httpx`).

## Mẫu Kiến Trúc (Architecture Pattern)
Service / API-centric architecture (Kiến trúc phân luồng tầng, dựa theo thiết kế Python Web). Cấu trúc Microservice.

## Dữ Liệu Nền Tảng (Data Architecture)
(Tham khảo tại `data-models-backend.md`)

## Thiết kế API (API Design)
(Tham khảo tại `api-contracts-backend.md`)

## Thống Kê Source Tree:
(Tham khảo tại `source-tree-analysis.md`)

## Development Workflow & Deployment:
(Tham khảo `development-guide.md`)
