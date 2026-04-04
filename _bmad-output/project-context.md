---
project_name: 'Chat-bot-stock'
user_name: 'QUI'
date: '2026-04-02'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
rule_count: 32
optimized_for_llm: true
---

# Ngữ cảnh dự án dành cho AI Agent (Project Context)

_Tệp này chứa các quy tắc và mẫu thiết kế quan trọng mà AI agent phải tuân thủ khi triển khai mã nguồn trong dự án này. Tập trung vào các chi tiết không hiển nhiên mà AI có thể bỏ lỡ._

---

## 🛠 Ngôn ngữ và Công nghệ (Technology Stack)

### Frontend

- **Framework:** Next.js 16.1.6 (App Router)
- **UI Library:** React 19.2.3 (Sử dụng hooks hiện đại)
- **Styling:** Tailwind CSS 4 (Cấu hình qua CSS variables `@theme`)
- **State Management:** Zustand 5.0.12
- **Data Fetching:** TanStack Query 5.96.1, Axios 1.14.0
- **Visualization:** Recharts 3.8.0
- **Icons:** Lucide React
- **I18n:** react-i18next

### Backend

- **Framework:** FastAPI
- **Database:** PostgreSQL (SQLAlchemy + Alembic)
- **Validation:** Pydantic V2 (Tuân thủ nghiêm ngặt cú pháp V2)
- **AI/LLM:** OpenAI API
- **Data Analysis:** Pandas, Scikit-learn, Prophet (Dự báo chứng khoán)
- **Data Sources:** vnstock (Dữ liệu thị trường Việt Nam)
- **Security:** python-jose, passlib[bcrypt]

---

## 📐 Quy tắc triển khai quan trọng (Critical Implementation Rules)

### 1. Các lỗi cần tránh & Bảo mật (Critical Don't-Miss Rules)

- **Hardcoded URLs:** Không để URL `localhost:8000` trực tiếp trong mã Frontend. Sử dụng `process.env.NEXT_PUBLIC_API_URL`.
- **Direct DB Access:** Routes không được truy cập DB trực tiếp, phải đi qua lớp `crud`.
- **Outdated Logic:** Tránh dùng `useEffect` cho form/fetching nếu có thể dùng React 19 hooks hoặc TanStack Query.
- **Silent Errors:** Luôn xử lý lỗi trong khối `catch` và hiển thị thông báo thân thiện (Sonner/UI alerts).
- **Security:** Không commit API Keys hay mật khẩu. Luôn sử dụng `.env` và xác thực JWT cho các endpoint nhạy cảm.

### 2. Luồng phát triển (Development Workflow Rules)

- **Môi trường:** Sử dụng môi trường ảo (venv) cho Python và tệp `.env.local` cho Frontend. Không đẩy các API Key lên repository.
- **Khởi tạo:** Luôn tuân thủ quy trình trong `setup_project.bat` khi cài đặt dự án mới.
- **Database Migrations:** Mọi thay đổi schema phải qua `Alembic` (`revision --autogenerate` và `upgrade head`). Không sửa DB thủ công.
- **Commit Guard:** Hệ thống `Husky` tự động kiểm tra lint/format. Hãy đảm bảo mã nguồn vượt qua các bài kiểm tra này trước khi đẩy lên.

### 3. Chất lượng mã & Phong cách (Code Quality & Style Rules)

#### Frontend (React/Next.js)

- **Linting:** Sử dụng `ESLint 9` và `Prettier`. Tuân thủ quy trình `Husky` + `lint-staged` trước khi commit.
- **Naming:** Components (`PascalCase`), Hooks (`camelCase` bắt đầu bằng `use`), Variables (`camelCase`).
- **Organization:** Tách nhỏ component và trích xuất logic phức tạp vào custom hooks.

#### Backend (Python/FastAPI)

- **Naming:** Functions & Variables (`snake_case`), Classes & Models (`PascalCase`).
- **Documentation:** Mọi hàm nghiệp vụ (services) phải có docstring rõ ràng.
- **Structure:** Duy trì phân tách: `crud` (DB), `schemas` (Data models), `services` (Business logic).

### 4. Quy tắc Kiểm thử (Testing Rules)

#### Backend (Python)

- **Framework:** Sử dụng `pytest` và `TestClient`. Các tệp kiểm thử đặt tại `backend/tests`.
- **Mocking Services:** Bắt buộc mock các API bên ngoài như OpenAI và vnstock để đảm bảo tính ổn định và tiết kiệm chi phí trong môi trường CI/CD.
- **Database Strategy:** Chỉ chạy các bài kiểm thử liên quan đến cơ sở dữ liệu nếu có cấu hình `TEST_DATABASE_URL` riêng biệt, tránh làm sạch dữ liệu phát triển (dev data).

#### Frontend (React)

- **Future Setup:** Dự án khuyến nghị tích hợp `Vitest` và `React Testing Library` nếu cần triển khai kiểm thử giao diện trong tương lai.

### 5. Quy tắc theo Framework (Framework-Specific Rules)

#### Next.js (Frontend)

- **Component Standard:** Mọi component mặc định là Server Component. Chỉ thêm `'use client';` khi cần dùng React hooks hoặc tương tác client-side.
- **Data Management:** Sử dụng `TanStack Query` cho mọi thao tác fetch dữ liệu động từ API để tận dụng cơ chế cache và sync trạng thái.
- **SEO Optimization:** Đảm bảo định nghĩa `metadata` cho từng trang (`page.tsx`) hoặc dùng `generateMetadata` linh hoạt.

#### FastAPI (Backend)

- **Router Module:** Luôn tách biệt các miền logic vào các `APIRouter` riêng biệt kèm `prefix` và `tags` chuẩn OpenAPI.
- **Response Schemas:** Mọi endpoint phải khai báo `response_model` và bao gồm docstring mô tả chức năng của API.
- **Schema Validation:** Sử dụng Pydantic cho cả input đầu vào (body) và output đầu ra để đảm bảo dữ liệu luôn hợp lệ và khớp với frontend.

### 6. Quy tắc theo Ngôn ngữ (Language-Specific Rules)

#### Python (Backend)

- **Import Style:** Sử dụng `src.` làm tiền tố cho các import nội bộ (ví dụ: `from src.api.dependencies import get_db`).
- **Type Safety:** Sử dụng nghiêm ngặt `typing` (List, dict, Optional) và Pydantic models cho mọi input/output của routes.
- **Error Handling:** Luôn dùng `HTTPException` của FastAPI để trả về lỗi thay vì ném (raise) exception cơ bản của Python.

#### TypeScript (Frontend)

- **No 'any' Policy:** Luôn dùng `interface` hoặc `type` để định nghĩa cấu trúc dữ liệu cho response từ API.
- **Import Aliases:** Sử dụng `@/` để tham chiếu đến thư mục `src` cốt lõi thay vì dùng đường dẫn tương đối dài (../../../).
- **Async Logic:** Ưu tiên bọc logic gọi API trong `async/await` kết hợp với `try/catch` để xử lý lỗi tại chỗ.

---

## 📖 Hướng dẫn sử dụng & Bảo trì (Usage Guidelines)

**Dành cho AI Agent:**

- Đọc tệp này trước khi triển khai bất kỳ mã nguồn nào.
- Tuân thủ TUYỆT ĐỐI tất cả các quy tắc đã được ghi chép.
- Khi không chắc chắn, hãy ưu tiên các lựa chọn có tính ràng buộc cao hơn.
- Cập nhật tệp này nếu có các mẫu thiết kế (patterns) mới xuất hiện.

**Dành cho Con người:**

- Giữ tệp này gọn gàng và tập trung vào nhu cầu của AI agent.
- Cập nhật khi có thay đổi về ngăn xếp công nghệ (technology stack).
- Xem xét lại hàng quý để loại bỏ các quy tắc đã lỗi thời hoặc đã trở nên hiển nhiên.

Cập nhật lần cuối: 2026-04-02
