# Quy ước cấu trúc và bảo trì

## Ranh giới module backend

- `api/`: chỉ xử lý HTTP, validate request và chuyển lỗi nghiệp vụ thành HTTP status.
- `services/`: nghiệp vụ, tích hợp OpenAI/vnstock và orchestration.
- `crud/`: truy vấn và ghi dữ liệu; không phụ thuộc FastAPI.
- `models/`: định nghĩa bảng SQLAlchemy.
- `schemas/`: request/response Pydantic dùng qua ranh giới API.
- `core/config.py`: chỉ khai báo và load settings.
- `core/database.py`: engine và session SQLAlchemy.
- `ml/`: huấn luyện/suy luận và phân tích bất thường.

Router mới được khai báo trong `api/routes/` và đăng ký một lần tại `api/router.py`.

## Ranh giới module frontend

- `app/`: route, layout và composition cấp trang.
- `components/`: thành phần giao diện tái sử dụng.
- `context/`: trạng thái xuyên suốt ứng dụng.
- `lib/`: client HTTP và tiện ích nền tảng.
- `services/`: workflow nghiệp vụ phía client.

Component lớn nên được tách theo feature, ví dụ `components/chart/`, thay vì tiếp tục thêm logic vào một file duy nhất.

## Quy trình thay đổi

1. Tạo migration Alembic cho mọi thay đổi schema database.
2. Không đặt API key hoặc password trực tiếp trong source code.
3. Chạy `.\scripts\check.ps1` trước khi commit.
4. Chạy `.\scripts\update-data.ps1` cho cập nhật thường ngày; chỉ dùng `scrape_vci.py` khi cần đồng bộ lại danh sách mã.
5. Không commit artifact runtime: `.venv`, `.next`, `node_modules`, `.local-postgres`, logs và file `.env`.

## Backlog refactor an toàn

- Tách `frontend/src/components/InteractiveChart.tsx` theo chart toolbar, series và data hooks.
- Tách schema request/response đang khai báo trong route sang `schemas/`.
- Bổ sung unit test cho services/CRUD và integration test cho các route database.
- Thay API key vnstock từng bị lưu trong lịch sử Git và thu hồi key cũ nếu repository đã được chia sẻ.
