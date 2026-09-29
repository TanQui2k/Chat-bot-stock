# Data scripts

Các script trong thư mục này là tác vụ vận hành, không phải mã khởi động API.

| Script | Mục đích |
| --- | --- |
| `daily_update.py` | Bổ sung dữ liệu giá từ ngày cuối đang lưu đến hiện tại. Đây là lựa chọn mặc định để cập nhật hằng ngày. |
| `scrape_vci.py` | Đồng bộ danh sách HOSE/HNX/UPCoM và backfill từ nguồn VCI. Dùng khi cần làm mới danh sách mã. |
| `test_session.py` | Tiện ích chẩn đoán session/database trong quá trình phát triển. |

Từ thư mục gốc repository, chạy cập nhật thường ngày bằng:

```powershell
.\scripts\update-data.ps1
```

API key vnstock được đọc từ `backend/.env` qua biến `VNSTOCK_API_KEY`; không đặt key trực tiếp trong source code.
