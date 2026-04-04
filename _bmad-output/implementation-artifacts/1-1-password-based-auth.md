# Story 1.1: Password-based Auth

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a người dùng mới,
I want tạo tài khoản bằng email và mật khẩu,
so that tôi có thể truy cập các tính năng cá nhân hóa của hệ thống.

## Acceptance Criteria

1. Người dùng có thể đăng ký bằng email và mật khẩu tại giao diện AuthModal (UX-DR1).
2. Dữ liệu đầu vào (email, mật khẩu) được validate nghiêm ngặt bằng Pydantic V2.
3. Mật khẩu được hash an toàn bằng thuật toán bcrypt قبل lưu vào PostgreSQL.
4. Sau khi đăng ký thành công, hệ thống tự động đăng nhập và trả về JWT qua **HttpOnly Cookie** (AR2) thay vì JSON body để tăng cường bảo mật.
5. Endpoint `/login` hiện tại cũng phải được cập nhật để sử dụng cơ chế HttpOnly Cookie tương tự.

## Tasks / Subtasks

- [x] **Backend: Schemas & Models** (AC: 2)
  - [x] Thêm `UserRegister` schema vào `backend/src/schemas/user_schema.py`.
  - [x] Đảm bảo `UserResponse` bao phủ đủ các trường cần thiết.
- [x] **Backend: CRUD Logic** (AC: 3)
  - [x] Hoàn thiện hàm `create_user` trong `backend/src/crud/crud_user.py` để xử lý đăng ký email/password.
  - [x] Kiểm tra tính duy nhất của email trước khi tạo.
- [x] **Backend: API Routes & Security** (AC: 1, 4, 5)
  - [x] Triển khai endpoint `POST /auth/register` trong `backend/src/api/routes/auth.py`.
  - [x] Cập nhật logic trả về token trong `register` và `login` để set HttpOnly Cookie.
  - [x] Cấu hình `Response` để bao gồm các thuộc tính: `httponly=True`, `secure=True`, `samesite="strict"`.
- [x] **Backend: Core Security Helpers** 
  - [x] Đảm bảo `create_user_token` trong `backend/src/core/security.py` tương thích với cơ chế mới.
- [x] **Frontend: Auth Integration** (AC: 1, 4)
  - [x] Cập nhật `AuthContext.tsx` để xử lý việc đăng nhập/đăng ký thông qua cookie (không cần lưu token vào LocalStorage).
  - [x] Kiểm tra tích hợp với `AuthModal.tsx` để hiển thị thông báo thành công/lỗi (sonner toast).

## Dev Notes

- **Kiến trúc:** Tuân thủ AR2 (HttpOnly Cookies) là yêu cầu tiên quyết. Tránh rò rỉ token qua JavaScript.
- **Bảo mật:** Sử dụng `passlib[bcrypt]` cho việc hash mật khẩu.
- **Cấu trúc:** Backend code phải nằm đúng lớp (Route -> Service/CRUD -> Model). Không gọi DB trực tiếp từ endpoint route.
- **Validation:** Sử dụng `EmailStr` từ Pydantic cho email validation.

### Project Structure Notes

- Backend: `backend/src/api/routes/auth.py`, `backend/src/crud/crud_user.py`, `backend/src/schemas/user_schema.py`.
- Frontend: `frontend/src/context/AuthContext.tsx`.

### References

- [Architecture Document: d:\Chat-bot-stock\_bmad-output\planning-artifacts\architecture.md#Bảo mật & Xác thực]
- [Epic Document: d:\Chat-bot-stock\_bmad-output\planning-artifacts\epics.md#Story 1.1]

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

- Triển khai thành công hệ thống đăng ký và đăng nhập dựa trên email/mật khẩu.
- Chuyển đổi toàn bộ hệ thống xác thực sang sử dụng HttpOnly Cookies (Bảo mật AR2).
- Loại bỏ hoàn toàn LocalStorage cho việc lưu trữ JWT trên frontend.
- Tích hợp thêm giao diện Đăng ký ngay trong PasswordLoginForm.

### File List

- `backend/src/schemas/user_schema.py` (Modified)
- `backend/src/crud/crud_user.py` (Modified)
- `backend/src/api/routes/auth.py` (Modified)
- `frontend/src/lib/api.ts` (Modified)
- `frontend/src/context/AuthContext.tsx` (Modified)
- `frontend/src/components/auth/PasswordLoginForm.tsx` (Modified)
