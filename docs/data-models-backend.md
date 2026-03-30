# Data Models - Backend (SQLAlchemy/PostgreSQL)

*Tài liệu này suy đoán cấu trúc qua tên các tệp model trong thư mục thư mục `backend/src/models/` (Dựa trên Quick Scan).*

## Cơ Sách Quản Trị CSDL
- **Công nghệ**: SQLAlchemy (ORM) tích hợp cùng Alembic.
- **Thư mục Migration**: `backend/alembic/` (có thể bị clone ra ngoài gốc do phát hiện lúc trước)
- **Base Class**: Được định nghĩa tại `base.py`.

## Danh Sách Models

### 1. User Model
- **Tệp nguồn**: `user.py`
- **Mục đích**: Lưu trữ thông tin tài khoản người dùng, email, mật khẩu mã hóa (bcrypt), và token kết nối OAuth.

### 2. Stock Model
- **Tệp nguồn**: `stock.py`
- **Mục đích**: Lưu cấu hình mã chứng khoán (Ticker), lịch sử giá (OHLCV), và các kết quả dự đoán (prediction history).

_Ghi chú: Để lấy thông tin về chi tiết từng trường dữ liệu (Schema constraints, Relationship foreign keys), vui lòng thực hiện Deep Scan hoặc Exhaustive Scan._
