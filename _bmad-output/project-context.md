---
project_name: 'Chat-bot-stock'
user_name: 'QUI'
date: '2026-03-30T09:47:00+07:00'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'workflow_rules', 'anti_patterns']
status: 'complete'
rule_count: 18
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

- **Frontend Environment**: Next.js (16.1.6) App Router, React (19.2.3), TypeScript (5.x). Styling bằng TailwindCSS (4).
- **Frontend Extras**: Data Visualization với `recharts` (^3.8.0). Auth Client bằng `@react-oauth/google`.
- **Backend Environment**: Python 3.10+ chạy Server bằng `FastAPI` (ASGI trên Uvicorn).
- **Backend Data/ORM**: Relational DB (PostgreSQL) kết nối với `SQLAlchemy`, quản lý migration bằng `alembic`.
- **Backend AI/ML**: Sử dụng `pandas/numpy` phân tích khung dữ liệu, huấn luyện/predict model bằng `scikit-learn`/`joblib`, load mã với `vnstock`. Gọi API LLM qua package `openai`.

## Critical Implementation Rules

### Language-Specific Rules

**1. Typescript (Frontend):**
- **Typing & Strict Mode:** Tránh tối đa sử dụng kiểu `any`. Định nghĩa `interface` hoặc `type` đầy đủ cho props của component, payload API, và hooks state.
- **Async/Await:** Ưu tiên dùng `async/await` thay vì chuỗi `.then().catch()` khi gọi API hoặc xử lý các lời gọi Google OAuth.
- **Import/Export:** Export default cho các Page/Route chính. Ưu tiên Named export cho các Function/Hook/Khối UI nhỏ (`export const Button = ...`). 

**2. Python 3.10+ (Backend):**
- **Type Hinting bắt buộc:** Sử dụng Type Hints chuẩn của Python (`str`, `int`, `List[dict]`, v.v) cho mọi tham số truyền vào hàm và giá trị trả về (`-> T`) để tận dụng sức mạnh validation tự động của `Pydantic` qua FastAPI.
- **Cấu trúc Import:** Sử dụng [Absolute Imports] bắt đầu bằng `src.` (ví dụ: `from src.models.user import User` hoặc `from src.api.routes.chat import route`). Hạn chế dùng relative imports (`from . import ...`).
- **Xử lý Bất đồng bộ (Concurrency):** Các request gọi đến OpenAI API, API ngoại vi (`vnstock`) hoặc Database thao tác nặng cần chuẩn hóa bọc trong `async def` và sử dụng hàm thư viện bất đồng bộ (`httpx.AsyncClient` hoặc wrap lại) nếu có thể để tận dụng Uvicorn Event Loop.
- **Xử Trí Ngoại Lệ (Error Handling):** Dùng `raise HTTPException(status_code=..., detail=...)` trong các Exception liên quan đến validation/auth nhằm trả về HTTP status chuẩn xác cho Client. Không dùng return JSON tay báo lỗi 400/500 làm rối logic.

### Framework-Specific Rules

**1. React & Next.js 16 (App Router):**
- **Client vs Server Components:** Bắt buộc khai báo `"use client"` ở dòng đầu tiên đối với các thẻ UI dùng React hooks (`useState`, `useEffect`) hoặc cần bắt sự kiện người dùng (`onClick`). Mặc định giữ các Page.tsx ở dạng Server Component để tối ưu hiệu suất.
- **Hooks Usage & Performance:** Bao bọc hàm và dữ liệu phức tạp bằng `useCallback` hoặc `useMemo` trước khi truyền vào các component nặng như biểu đồ (`recharts`) để chống re-render vô ích.
- **Styling Pipeline:** Sử dụng 100% utility class của TailwindCSS. Hạn chế tối đa inline styles (`style={{...}}`) hoặc file CSS module rời rạc.

**2. FastAPI & SQLAlchemy:**
- **Dependency Injection (DI):** Luôn dùng `Depends(...)` để truy xuất Connection DB hoặc lấy phiên bản tài khoản người dùng đang đăng nhập (Current User). VD: `db: Session = Depends(get_db)`. Nghiêm cấm mở connection thủ công trong controllers.
- **Pydantic Validator:** Tách bạch rõ Pydantic Schema cho Request (định nghĩa Input) và Response (định nghĩa Output). Ví dụ: `UserCreate`, `UserResponse`.
- **Database Migration:** Không dùng lệnh `Base.metadata.create_all()`. Mọi thay đổi về cấu trúc bảng trong thư mục `models/` phải được migration qua `alembic`.

### Testing Rules

- **Backend Testing & Cấu trúc File:** Tách tệp test API đặt vào `backend/tests/` và đặt tên bắt đầu bằng `test_` để `pytest` tự động nhận diện. 
- **Mocking Dữ liệu Ngoại vi/AI:** Tuyệt đối **không gọi thẳng API thật** (OpenAI / VNStock) khi chạy Unit Test để chống lãng phí chi phí (Rate Limits) và giảm tốc độ. Bắt buộc phải mock class OpenAI SDK hoặc `httpx.AsyncClient`.
- **FastAPI TestClient & DB Mock:** Đối với các API phụ thuộc Database SQL, hãy sử dụng Dependency Override của FastAPI (`app.dependency_overrides[get_db] = override_get_db`) để trỏ vào Test Database (như SQLite In-memory) hoặc dùng Mock Session.
- **Frontend Testing:** Khi bạn khai mở Unit tests ở UI sau này, hãy tập trung kiểm tra Logic của Custom Hooks và Event User thông qua `@testing-library/react`. Không test kiểm tra tính hợp lệ của mã CSS TailwindCSS.

### Code Quality & Style Rules

**1. Tiêu Chuẩn Đặt Tên (Naming Conventions):**
- **Frontend (TS/React):** Sử dụng `PascalCase` cho tên file Component dạng `.tsx` (`AuthModal.tsx`, `ChatInterface.tsx`) và tên Function Component. Sử dụng `camelCase` cho tên biến, props, hàm (`fetchData`, `handleLogin`).
- **Backend (Python):** Tuân thủ tuyệt đối [PEP8]. Đặt tên thư mục, file, hàm, biến bằng chữ thường kèm dấu gạch dưới `snake_case` (`crud_stock.py`, `llm_service.py`). Tên Pydantic/SQLAlchemy Class dùng `PascalCase` (`class Stock`).

**2. Linting & Code Design:**
- **Frontend:** Code tuân thủ cấu hình mặc định tại `eslint.config.mjs` với `eslint-config-next`.
- **Backend:** Thụt lề (indentation) 4 spaces chuẩn Python. Hạn chế lồng ghép câu lệnh điều kiện `if/else` quá 3 tầng do dễ tăng độ phức tạp thuật toán và sinh bug.

**3. Tổ Chức Code Sạch (Clean Code Organization):**
- Tách tất cả các dịch vụ tính toán, tương tác LLM, phân đoạn lấy dữ liệu AI ra khỏi các router API. Mọi route (`api/routes/*.py`) phải giữ lớp xử lý **Super Thin** (Rất mỏng). Toàn bộ logic lõi nằm tại thư mục `services/` hoặc `utils/`.

### Development Workflow Rules

**1. Quản lý Git & Phân Nhánh (Branching):**
- Phân nhánh tính năng theo định dạng: `feature/tên-chức-năng` (Ví dụ: `feature/auth-google`). Dành cho sửa lỗi dùng `fix/tên-lỗi`.
- Mọi khi cập nhật phía backend API, Agent bắt buộc phải test song song độ tương thích với frontend bằng thao tác `npm run dev` ở client để ngăn chặn gãy đổ chức năng.

**2. Commit Message (Theo chuẩn Conventional Commits):**
- Bắt buộc dùng cấu trúc: `type(scope): message`.
- Ví dụ: `feat(api): add anomaly detection endpoint` hoặc `fix(ui): resolve overflow on prediction widget`. 
- Các loại Type chính cần tuân thủ: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

**3. Lưu Ý Khi Chạy Local (Môi Trường Phát Triển):**
- Theo tài liệu `development-guide.md`, để thử nghiệm bất cứ module nào liên quan đến Account, Frontend luôn phải có file `.env.local` chứa các biến `GOOGLE_CLIENT_ID`.
- Backend yêu cầu file `.env` chứa `OPENAI_API_KEY` và `DATABASE_URL` chính xác. Nếu một module thiếu env, không được giả lập (fake data) mà phải ném ra lỗi (raise/throw errors) phù hợp để Dev dễ debug.

### Critical Don't-Miss Rules (Những Điều Tối Kỵ)

**1. Anti-Patterns (Tuyệt Đối Tránh):**
- **Không Hardcode Secret/API Keys:** Không bao giờ lưu cứng thông tin nhạy cảm, token, mật khẩu DB trực tiếp vào logic Python/TS. Mọi config cần gọi qua biến cấu hình Pydantic/`os.getenv()` ở backend, và `process.env` ở frontend.
- **Không Xâm Lấn Thư Viện:** Ở Frontend, tuyệt đối không chọc thẳng DOM bằng `document.getElementById` vào biểu đồ `recharts`. Ở Backend, không tùy tiện sửa code base thư viện gốc `vnstock`, nếu lỗi phải xử lý catch.

**2. Xử Lý Điểm Mù (Edge Cases):**
- **Rate Limit & Timeout:** Tính năng Machine Learning API nội bộ / OpenAI / `vnstock` cần nhiều thời gian phản hồi. Luôn xử lý bất đồng bộ timeout để không làm sập (block) server Uvicorn.
- **Client Render Tùy Trạng Thái:** Client Next.js không được phép render các Action Gửi Chat / Prediction nếu người dùng chưa thông qua lớp Auth và chưa sinh `session_id`.

**3. Bảo Mật Cốt Lõi (Security):**
- **Mật Khẩu:** Tuyệt đối không lưu text thô. Bắt buộc wrap qua `passlib` bcrypt trước khi update vào SQLAlchemy model.
- **Token Authorization:** Định nghĩa chặn ngay ở các API mang tính cá nhân (Chat History, Profile) bằng dependencies `Depends(get_current_user)` để chặn truy cập lậu.

---

## Usage Guidelines

**For AI Agents:**
- Bắt buộc phải đọc `project-context.md` này TRƯỚC khi tiến hành viết code.
- Tuân thủ toàn bộ 18 quy tắc ở trên. Không được phép ngoại lệ.
- Nếu gặp phải mẫu code không có trong context, hãy áp dụng quy tắc an toàn nhất và hỏi lại User.
- Tự động gợi ý cập nhật file nếu phát hiện ra thay đổi mới mẻ về cấu trúc.

**For Humans:**
- Hãy giữ cho file này thật sự cô đọng (LLM sẽ đọc dễ dàng và ít lãng phí token).
- Cập nhật lại mỗi khi có thay đổi lớn phiên bản thư viện (VD nâng cấp Next.js).

Last Updated: 2026-03-30T09:47:00+07:00
