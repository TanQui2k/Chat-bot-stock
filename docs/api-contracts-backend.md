# API Contracts - Backend (FastAPI)

*Tài liệu này được tạo tự động thông qua Quick Scan (phân tích file pattern, không đọc code chi tiết).*

Dự án back-end sử dụng cấu trúc route tách biệt. Các endpoints chính được phát hiện qua các files trong thư mục `backend/src/api/routes/`:

## 1. Anomaly API
- **File path**: `routes/anomaly.py`
- **Mô tả dự đoán**: Xử lý các chức năng phát hiện bất thường (anomaly detection), tìm kiếm diễn biến giá trị bất thường trên thị trường.

## 2. Assistant API
- **File path**: `routes/assistant.py`
- **Mô tả dự đoán**: Các API liên quan đến cấu hình/gọi trợ lý AI.

## 3. Auth API
- **File path**: `routes/auth.py`
- **Mô tả dự đoán**: Cung cấp chức năng xác thực người dùng (login, register, token generation, Google OAuth).

## 4. Chat API
- **File path**: `routes/chat.py`
- **Mô tả dự đoán**: Quản trị kết nối chatbot, nhận prompt người dùng và phản hồi kết quả AI.

## 5. Predict API
- **File path**: `routes/predict.py`
- **Mô tả dự đoán**: Điểm cuối (endpoints) cho chức năng học máy (Machine Learning) để dự đoán giá trị cổ phiếu.

## 6. Stocks API
- **File path**: `routes/stocks.py`
- **Mô tả dự đoán**: Cung cấp dữ liệu chứng khoán, thông tin lịch sử giao dịch và trích xuất dữ liệu thị trường (có thể từ `vnstock`).

_Ghi chú: Để có schemas request/response chi tiết, vui lòng thực hiện Deep/Exhaustive Scan._
