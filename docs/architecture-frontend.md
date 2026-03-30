# Architecture - Frontend

## Mở Bài (Executive Summary)
Ứng dụng Web tĩnh, xây dựng theo kiểu Component-based dành cho dự án Quản trị thông tin và Bot hỗ trợ chứng khoán.

## Đặc tính Xây Dựng (Technology Stack)
- Framework cốt lõi: Tiếp cận với hệ sinh thái React 19 và sử dụng Next.js phiên bản 16 làm framework nền tảng để SSR/CSR các React hooks (App Router).
- CSS System (Xếp tầng): Dựng layout cùng TailwindCSS tối giản và hiện đại. Tương tác mảng thư viện biểu diễn đồ thị/ dữ kiện `recharts`.
- Authentication Service Client: Nhúng nền tảng bảo mật của Hệ sinh thái Google Account thông qua mã `@react-oauth/google`.

## Mẫu Kiến Trúc (Architecture Pattern)
Component-based Architecture & Layered pattern (Lấy Server Side Rendering làm trung tâm truy xuất từ Backend). 

## Thống Kê Source Tree:
(Tham khảo chi tiết ở `source-tree-analysis.md`)

## Development Workflow & Deployment:
(Tham khảo `development-guide.md`)
