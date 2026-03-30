# Kiến trúc Tích hợp (Integration Architecture)

*Mô tả cách các thành phần trong dự án Chat-bot-stock giao tiếp và làm việc với nhau. (Từ Quick Scan).*

## 1. Kết Nối Tổng Quan (Overview)
Dự án được ứng dụng mô hình client-server truyền thống.
- **Client (Frontend)**: Next.js SSR/CSR quản trị giao diện người dùng và gửi request qua Client components (hoặc Server Actions).
- **Trạm Xử Lý Giao Tiếp (Middleware Network)**: Sử dụng các HTTP Requests truyền đạt nội dung JSON.
- **Server (Backend API)**: Trạm REST API bằng FastAPI đảm nhận Authentication, AI prompt parsing, gọi external Models (OpenAI), và tương tác Database.

## 2. Các Luồng Hệ Thống Chính
### Dữ liệu Giao Hàng Xuyên Tuyến (Cross-Network Workloads)

1. **Authentication Flow (Google OIDC)**
   - Client (`@react-oauth/google`) mở popup nhận token từ Google.
   - Thẻ token/code được nạp qua endpoint `POST /api/routes/auth/google-login` tại Backend.
   - Backend xác nhận chuỗi signature (bằng thư viện nội bộ/Google API), sau đó sinh riêng ra JWT Session Cookie/Token và trả về Frontend lưu trữ.

2. **Realtime Chat Flow**
   - User nhập tin nhắn qua component `ChatInterface.tsx`.
   - Payload Text JSON được gọi đến endpoint `POST /api/routes/chat` cùng Authentication Header JWT.
   - Backend phân loại (classify_intent) -> Nếu là cổ phiếu: đọc CSDL qua SQLAlchemy (Stock models) hoặc gọi VnStock library -> Nếu là thông tin cấu hình: tương tác LLM OpenAI (`llm_service.py`).
   - Kết quả phản hồi (Response) dạng đoạn chat và meta-data (nếu có biểu đồ) được trả về Frontend.

3. **Machine Learning Predictions Flow**
   - Component `PredictionWidget.tsx` lấy biểu đồ/nhận định AI từ endpoint `predict.py` qua HTTP GET/POST.
   - FastAPI tải Machine Learning model (Scikit-Learn/Joblib) trong cấu hình backend, phân tích TimeSeries dữ liệu Pandas.
   - Mật độ thông tin rủi ro/đầu tư đưa vào JSON object Response để Recharts (Frontend) xây dựng dạng biểu diễn đồ hoạ tương tác.

_Chi tiết từng endpoint hợp đồng payload hãy xem trong `api-contracts.md`_
