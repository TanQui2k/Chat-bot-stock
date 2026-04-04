---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments: ["_bmad-output/project-context.md", "docs/project-overview.md", "docs/architecture-backend.md", "docs/architecture-frontend.md", "docs/integration-architecture.md"]
workflowType: 'architecture'
project_name: 'Chat-bot-stock'
user_name: 'QUI'
date: '2026-04-03'
lastStep: 8
status: 'complete'
completedAt: '2026-04-03'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Phân tích Ngữ cảnh Dự án (Project Context Analysis)

### Tổng quan Yêu cầu

**Yêu cầu Chức năng (Functional Requirements):**

- Tra cứu và hiển thị dữ liệu chứng khoán Việt Nam (HOSE, HNX, UPCOM).
- Cung cấp Chatbot AI tư vấn tài chính và giải đáp thắc mắc người dùng.
- Thực hiện dự báo giá cổ phiếu dựa trên dữ liệu lịch sử bằng mô hình Machine Learning.
- Hệ thống xác thực đa phương thức: OTP qua điện thoại, Google OAuth, và Mật khẩu truyền thống.

**Yêu cầu Phi chức năng (Non-Functional Requirements):**

- **Hiệu năng:** API phản hồi nhanh (FastAPI/Uvicorn), UI tối ưu SSR/CSR (Next.js).
- **Bảo mật:** Xác thực JWT, Blacklist token khi logout, giới hạn tốc độ (Rate limiting) cho các endpoint nhạy cảm.
- **Mở rộng:** Cấu trúc mã nguồn mô-đun hóa cao, dễ dàng thay thế Provider AI hoặc Nguồn dữ liệu chứng khoán.

**Quy mô & Độ phức tạp:**

Dự án có độ phức tạp trung bình, đòi hỏi sự phối hợp nhịp nhàng giữa xử lý dữ liệu nặng (Backend) và hiển thị trực quan (Frontend).

- Miền kỹ thuật chính: Web App & API Service
- Mức độ phức tạp: Medium
- Các thành phần kiến trúc dự kiến: 10+ (Controllers, Services, CRUD, ML Engines, UI Components, State Stores).

### Ràng buộc Kỹ thuật & Phụ thuộc

- Ngôn ngữ: Python 3.10+, TypeScript 5+.
- Cơ sở dữ liệu: PostgreSQL (bắt buộc dùng SQLAlchemy + Alembic).
- Framework: Next.js 16 (App Router), FastAPI.

### Các vấn đề Xuyên suốt (Cross-Cutting Concerns)

- Xác thực và Phân quyền (AuthN/AuthZ).
- Chuẩn hóa Schema dữ liệu giữa Backend và Frontend.
- Xử lý lỗi toàn cục và hệ thống thông báo người dùng (Toasts/Alerts).
- Rate Limiting và bảo vệ tài nguyên API.

## Đánh giá Nền tảng Khởi tạo (Starter Foundation Evaluation)

### Miền Công nghệ Chính

**Full-stack Web Application** dựa trên kiến trúc App Router (Frontend) và RESTful API (Backend).

### Lựa chọn Công nghệ đã thiết lập

Dự án không sử dụng một Starter Template duy nhất mà là sự kết hợp tùy chỉnh (Custom Foundation) tối ưu cho AI/Fintech:

**Quyết định Kiến trúc từ Nền tảng:**

- **Language & Runtime:** TypeScript 5+ (Frontend) và Python 3.10+ (Backend). Đảm bảo Type-safety ở cả hai đầu.
- **Styling Solution:** Tailwind CSS 4 (Beta/@theme) — Sử dụng CSS variables hiện đại, giảm thiểu runtime CSS.
- **Build Tooling:** Next.js Compiler (SWC) và Uvicorn cho backend.
- **Testing Framework:** Pytest (Backend) và kế hoạch tích hợp Vitest (Frontend).
- **Tổ chức Mã nguồn:**
  - Backend: Cấu trúc phân tầng (CRUD -> Schemas -> Services -> Routes).
  - Frontend: Component-based (Atomic/Modular) kết hợp với Custom Hooks cho logic dữ liệu.

**Lý do chọn lựa:**

Sự kết hợp này cung cấp tốc độ phát triển cao (FastAPI/Zustand) trong khi vẫn duy trì khả năng mở rộng cho các tính năng ML phức tạp.

## Quyết định Kiến trúc Cốt lõi (Core Architectural Decisions)

### Phân tích Ưu tiên Quyết định

**Quyết định Quan trọng (Chặn việc thực thi):**

- **Cấu trúc Dữ liệu:** Chuyển sang mô hình Domain-driven (`models/auth.py`, `models/stock.py`) thay vì `user.py` và `stock.py` đơn lẻ.
- **Xác thực:** Chuyển đổi từ LocalStorage sang **HttpOnly Cookie** để ngăn chặn tấn công XSS và tăng tính bảo mật cho Web.

**Quyết định quan trọng (Hình thành kiến trúc):**

- **Chiến lược Caching:** Sử dụng **Redis** cho dữ liệu cổ phiếu thị trường có tính thời điểm cao.
- **Xử lý lỗi:** Triển khai **Global Exception Handlers** trong FastAPI để trả về lỗi JSON chuẩn hóa.

### Kiến trúc Dữ liệu (Data Architecture)

- **Database:** PostgreSQL v15+ (LTS).
- **ORM:** SQLAlchemy v2 (Sử dụng Declarative Mapping).
- **Caching:** Redis v7+. Sử dụng cho:
  - Token Blacklist (Thay thế bản in-memory hiện tại khi scale).
  - Kết quả API stock từ `vnstock` với TTL (Time-to-Live) ngắn.

### Bảo mật & Xác thực (Authentication & Security)

- **Method:** JWT (RS256 hoặc HS256).
- **Storage:** HttpOnly + Secure + Samesite=Strict Cookies.
- **Middlewares:**
  - `RateLimitMiddleware` (Đã triển khai in-memory, sẵn sàng chuyển Redis).
  - `CORSMiddleware` (Siết chặt origins theo whitelist).

### Kiến trúc Frontend (Frontend Architecture)

- **Cấu trúc Component:** **Atomic/Modular approach** (Tránh components quá lớn).
- **Form Management:** **React Hook Form** kết hợp với **Zod** cho client-side validation.
- **State Management:** **Zustand** (Global state) và **TanStack Query** (Server state sync).

### Hạ tầng & Triển khai (Infrastructure)

- **Containerization:** Docker & Docker Compose (cho dev/prod).
- **Hosting:** Dự kiến Vercel (Frontend) và Railway/DigitalOcean (Backend).

## Mẫu Triển khai & Quy tắc Nhất quán (Implementation Patterns)

### Quy tắc Đặt tên

- **Database:** `snake_case` plural cho bảng, `snake_case` cho cột.
- **API URL:** RESTful plural nouns (ví dụ: `/api/v1/stocks`).
- **Code:** Tuân thủ chuẩn PEP8 (Python) cho backend và Google TypeScript Style Guide cho frontend.

### Tổ chức Mã nguồn

- **Frontend Layering:** Chia tách Client Components (`'use client'`) và Server Components rõ ràng. Logic phức tạp phải nằm trong Custom Hooks.
- **Backend Layering:** `api -> services -> crud -> models`. Tuyệt đối không gọi DB từ Route.

### Chuẩn hóa Giao tiếp API

- **Success Format:** `{ "success": true, "data": any, "message": string }`.
- **Error Format:** `{ "detail": string, "code": string }`.
- **Date/Time:** Luôn sử dụng ISO 8601 (UTC) cho mọi trao đổi dữ liệu qua API.

### Chỉ dẫn Thực thi cho AI Agent (Mandatory Rules)

**Mọi AI Agent PHẢI:**

- Tách nhỏ component và trích xuất logic phức tạp vào custom hooks.
- Mọi thay đổi schema database phải thông qua Alembic migrations.
- Không được sử dụng kiểu dữ liệu `any` trong TypeScript.
- Luôn bọc logic gọi API trong `async/await` với chuẩn JSON wrapper.

## Cấu trúc Dự án & Ranh giới (Project Structure & Boundaries)

### Cây Thư mục Hoàn chỉnh

```text
Chat-bot-stock/
├── backend/
│   ├── src/
│   │   ├── api/                # Cổng vào (Routes & Dependencies)
│   │   │   ├── routes/         # auth.py, stocks.py, chat.py
│   │   │   └── dependencies.py # Auth checks, DB sessions
│   │   ├── core/               # Cấu hình hệ thống (Config, Security)
│   │   ├── crud/               # Truy vấn DB nguyên bản
│   │   ├── models/             # Domain-driven Models (auth.py, stock.py)
│   │   ├── schemas/            # Pydantic models (Giao tiếp API)
│   │   ├── services/           # Logic nghiệp vụ & AI (google_auth, prophet_engine)
│   │   └── main.py             # Entry point
│   ├── tests/                  # Unit & Integration tests
│   ├── alembic/                # DB Migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                # Next.js App Router (Pages & Layouts)
│   │   ├── components/
│   │   │   ├── ui/             # Shadcn-like base components
│   │   │   ├── features/       # Modular features (auth/, chat/, dashboard/)
│   │   │   └── shared/         # Layout components (Navbar, Footer)
│   │   ├── hooks/              # Custom shared hooks (useAuth, useMarketData)
│   │   ├── services/           # Client-side API services (api-client.ts)
│   │   ├── store/              # Zustand state stores
│   │   ├── types/              # TypeScript interfaces/types
│   │   └── lib/                # Config & Utils
│   ├── public/                 # Static assets
│   └── tailwind.config.ts
└── docs/                       # Project documentation
```

### Ranh giới Kiến trúc (Architectural Boundaries)

- **API Boundaries:** Mọi giao tiếp Frontend-Backend phải thông qua JSON wrapper chuẩn.
- **Service Boundaries:** Logic AI (OpenAI) và ML (Prophet) phải được đóng gói hoàn toàn trong lớp `services/`, không rò rỉ vào Route.
- **Data Boundaries:** Cấm truy cập Database trực tiếp từ Route. Phải đi qua `services` hoặc ít nhất là `crud` layer.

### Ánh xạ Tính năng (Requirement Mapping)

- **Feature: Authentication** -> `components/features/auth/` & `backend/src/models/auth.py`.
- **Feature: AI Chat** -> `components/features/chat/` & `backend/src/services/openai_service.py`.
- **Feature: Prediction** -> `components/features/dashboard/` & `backend/src/services/prophet_engine.py`.

## Kết quả Xác thực Kiến trúc (Architecture Validation Results)

### Coherence Validation ✅

Các quyết định về Backend (FastAPI Layered) và Frontend (Next.js Modular) hoàn toàn tương thích. Việc sử dụng JSON wrapper chuẩn đảm bảo ranh giới API ổn định.

### Requirements Coverage Validation ✅

- **Functional:** 100% các tính năng trong `project-overview.md` đã có vị trí đặt code tương ứng trong project tree.
- **Non-Functional:** Bảo mật và hiệu năng đã được giải quyết thông qua Rate Limiting, Blacklist Service và FastAPI.

### Đánh giá Mức độ Sẵn sàng ✅

- **Trạng thái:** SẴN SÀNG TRIỂN KHAI (READY FOR IMPLEMENTATION)
- **Mức độ tự tin:** Cao (High)
- **Điểm mạnh:** Cấu trúc phân lớp rõ ràng, ranh giới AI logic, bảo mật được chú trọng ngay từ đầu.

### Hướng dẫn bàn giao (Implementation Handoff)

1. **Ưu tiên 1:** Triển khai hạ tầng Redis để thay thế các bản in-memory (Blacklist/Rate limit).
2. **Ưu tiên 3:** Chuyển đổi cơ chế lưu trữ Token sang HttpOnly Cookie.
3. **Ưu tiên 3:** Xây dựng khung các module trong `services/` cho AI và ML.

### Architecture Completeness Checklist ✅

- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed
- [x] Technical constraints identified
- [x] Cross-cutting concerns mapped
- [x] Critical decisions documented with versions
- [x] Technology stack fully specified
- [x] Integration patterns defined
- [x] Performance considerations addressed
- [x] Naming conventions established
- [x] Structure patterns defined
- [x] Communication patterns specified
- [x] Process patterns documented
- [x] Complete directory structure defined
- [x] Component boundaries established
- [x] Integration points mapped
- [x] Requirements to structure mapping complete
