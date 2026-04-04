# Story 1.2: Google OAuth2

Status: completed

## Story

As a người dùng ưu tiên sự tiện lợi,
I want đăng nhập bằng tài khoản Google,
so that tôi không cần nhớ thêm mật khẩu mới.

## Acceptance Criteria

1. Khi nhấp vào "Login with Google", hệ thống mở giao diện xác thực của Google (Google OAuth2).
2. Sau khi người dùng xác thực với Google, Frontend nhận `access_token` và gửi lên Backend endpoint `/auth/google/login`.
3. Backend sử dụng `verify_google_access_token` để xác thực token và lấy thông tin người dùng từ Google (name, email, avatar).
4. Hệ thống kiểm tra:
   - Nếu `google_id` đã tồn tại: Cập nhật thông tin và trả về phiên làm việc.
   - Nếu `email` đã tồn tại nhưng chưa có `google_id`: Liên kết (link) tài khoản Google vào email hiện tại.
   - Nếu chưa tồn tại: Tạo user mới.
5. Sau khi thành công, hệ thống tự động đăng nhập và thiết lập HttpOnly Cookie (AR2).

## Tasks / Subtasks

- [x] **Frontend: Integration** (AC: 1, 2)
  - [x] Đảm bảo `GoogleLoginButton.tsx` được tích hợp chính xác vào `AuthModal.tsx`.
  - [x] Cấu hình `NEXT_PUBLIC_GOOGLE_CLIENT_ID` trong biến môi trường (nếu chưa có).
  - [x] Kiểm tra việc nhận `tokenResponse` và gọi `authApi.googleLogin`.
- [x] **Backend: Logic Refinement** (AC: 3, 4, 5)
  - [x] Kiểm tra hàm `create_user_from_google` trong `backend/src/crud/crud_user.py` để đảm bảo logic liên kết email hoạt động tốt.
  - [x] Đảm bảo `verify_google_access_token` xử lý tốt các trường hợp token hết hạn/không hợp lệ.
- [x] **Backend: Cookie Handling** (AC: 5)
  - [x] Chắc chắn rằng endpoint `/auth/google/login` sử dụng hàm helper `set_auth_cookie` (đã triển khai ở Story 1.1).

## Dev Notes

- **Kiến trúc:** Tuân thủ AR2 (HttpOnly Cookies). Token không bao giờ được lộ ra frontend code.
- **Bảo mật:** Sử dụng `httpx` để gọi Google Userinfo API với timeout hợp lý.
- **Frontend library:** Sử dụng `@react-oauth/google` (đã có trong dependencies).

### Project Structure Notes

- Backend: `backend/src/api/routes/auth.py`, `backend/src/services/google_auth_service.py`, `backend/src/crud/crud_user.py`.
- Frontend: `frontend/src/components/auth/GoogleLoginButton.tsx`, `frontend/src/context/AuthContext.tsx`.

## Dev Agent Record

### Agent Model Used

Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

- Xác thực Google OAuth2 Implicit Flow (access_token) thành công.
- Implement HttpOnly Cookie AR2 cho Google Login flow.
- Tự động liên kết tài khoản Google nếu email đã tồn tại trong DB.
- Chuẩn hóa email (lowercase) khi xác thực Google.

### File List

- `backend/src/crud/crud_user.py` (Modified)
- `backend/src/api/routes/auth.py` (Previously updated in 1.1 refactor)
- `frontend/src/components/AuthModal.tsx` (Verified)
- `frontend/src/components/auth/GoogleLoginButton.tsx` (Verified)
