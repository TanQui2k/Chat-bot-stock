# UI Component Inventory - Frontend (Next.js/React)

*Tài liệu này suy đoán dựa theo tên các React Component trong thư mục `frontend/src/components/` qua quá trình Quick Scan.*

### Công nghệ nền:
- React (Function Components) 
- Tailwind CSS
- Data Visualization (Recharts)

### Tổng kho Component (*.tsx)

1. **AuthModal.tsx**
   - **Xử lý**: Hiển thị hộp thoại Đăng nhập/Đăng ký dành cho tài khoản cục bộ / OAuth (Sử dụng `@react-oauth/google`). 
   - **Đặc tính**: Modal Overlay UI.

2. **ChatInterface.tsx**
   - **Xử lý**: Quản lý giao diện đoạn hội thoại giữa Người dùng và AI Trợ lý. Bao gồm TextField, Message bubbles.
   - **Giao diện**: Component chính cung cấp trải nghiệm Chatbot.

3. **InteractiveChart.tsx**
   - **Xử lý**: Đảm nhiệm biểu diễn trực quan dữ liệu chứng khoán (Giá thay đổi, Lịch sử... ) qua biểu đồ. 
   - **Dependencies**: Liên kết chặt chẽ với thư viện `recharts`.

4. **Navbar.tsx**
   - **Xử lý**: Thanh điều hướng trang web / Header chứa Logo, Tùy chọn chuyển tab và Profile người dùng (Auth Button/ Avatar).
   - **Thuộc tính**: Layout Component (`<header>`, `<nav>`).

5. **PredictionWidget.tsx**
   - **Xử lý**: Hiển thị kết quả AI / Machine Learning (Tăng, Giảm, Rủi ro, ...), xác suất mua/bán từ Backend Endpoint `predict.py`.
   - **Chức năng**: Data Display Component.

_Để tìm hiểu luồng Hook và Fetch API cụ thể (SWR/Axios/Fetch/Data Fetching theo Next), cần chạy Deep Scan._
