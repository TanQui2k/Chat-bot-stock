# Tổng Quan Dự Án (Project Overview)

## 1. Tên và Mục Đích Dự Án
- **Tên**: Chat-bot-stock
- **Mục đích**: Một ứng dụng hỗ trợ dự đoán và phân tích chứng khoán sử dụng trí tuệ nhân tạo (AI). Dự án cung cấp chatbot thông minh giải đáp các câu hỏi về tài chính, cùng với biểu đồ và luồng xử lý học máy (ML) nhằm tối ưu trải nghiệm người dùng cuối.

## 2. Loại Hình Cấu Trúc Mã Nguồn (Repository Structure)
- **Multi-part Monorepo**: Hai mảng chính gộp chung (Frontend/Backend)

## 3. Bản Đồ Tổng Quan (Executive Summary)
Đây là tổ hợp Ứng dụng Web / Dịch vụ API phát triển theo tiêu chuẩn cực kỳ linh hoạt và hiện thực hoá bởi:
- Giao diện trực diện Web (Web Browser SPA, App Router Next.js 16 / React 19 / TypeScript).
- Dịch vụ máy chủ REST cấp tốc (Backend OpenAPI, FastAPI / Python).
- Dữ liệu kết nối trung tâm Cơ Sở Dữ Liệu Quan Hệ Postgres.

## 4. Danh sách Nền Tảng Kỹ Thuật (Tech Stack Summary)
| Lớp Hệ Thống | Công nghệ | Kiến trúc lõi | Phiên bản |
| :--- | :--- | :--- | :--- |
| **Frontend** | Next.js, React, TailwindCSS, Recharts | Component-based Layers, Server Component | React ^19, Next >=16, Tailwind ^4 |
| **Backend** | FastAPI, Uvicorn, Python, SQLAlchemy | REST API, Backend-for-frontend | Python 3.10+, FastAPI |
| **AI/ML Core** | Scikit-learn, OpenAI API, vnstock | Model predict routines, OpenAI LLMs Service | openai |
| **Authentication**| @react-oauth/google, jose, passlib | JWT / OAuth2 Cookie State Session Auth | passlib[bcrypt] |
| **Database** | PostgreSQL, Alembic | Relational DB | psycopg2 |

## 5. Danh Sách Các Tài Liệu Tham Khảo Liên Kết 
- [Cây Thư Mục & Phân Tích Đường Dẫn](./source-tree-analysis.md)
- [Kiến Trúc Tích Hợp (Mạch Hoạt Động)](./integration-architecture.md)
- Phụ Trách Dữ Liệu API ([Backend API](./api-contracts-backend.md)) và ([Backend Models](./data-models-backend.md))  
- Chức Năng UI Giao Diện ([Frontend UI Tồn Kho](./ui-component-inventory-frontend.md))
- Hướng dẫn Phát triển Local ([Development Setup Local](./development-guide.md))
