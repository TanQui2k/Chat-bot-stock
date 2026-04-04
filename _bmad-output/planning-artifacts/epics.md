---
stepsCompleted: [1, 2, 3, 4]
inputDocuments: ["docs/project-overview.md", "_bmad-output/planning-artifacts/architecture.md", "docs/ui-component-inventory-frontend.md"]
---

# Chat-bot-stock - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Chat-bot-stock, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: Tra cứu và hiển thị dữ liệu chứng khoán Việt Nam (HOSE, HNX, UPCOM) từ nguồn `vnstock`.
FR2: Hệ thống Chatbot AI tư vấn tài chính và giải đáp thắc mắc người dùng sử dụng OpenAI.
FR3: Thực hiện dự báo giá cổ phiếu (tăng/giảm/xác suất) dựa trên dữ liệu lịch sử bằng mô hình Prophet/ML.
FR4: Hệ thống xác thực đa phương thức: OTP điện thoại, Google OAuth, và Mật khẩu truyền thống.

### NonFunctional Requirements

NFR1: Hiệu năng — API phản hồi nhanh (FastAPI), UI tối ưu SSR/CSR (Next.js 16).
NFR2: Bảo mật — Xác thực JWT, Blacklist token khi logout, giới hạn tốc độ (Rate limiting).
NFR3: Mở rộng — Cấu trúc mã nguồn mô-đun hóa (Domain-driven), dễ dàng thay thế AI Provider.

### Additional Requirements

- AR1: Triển khai hạ tầng Redis để quản lý Caching và Rate limiting.
- AR2: Chuyển đổi toàn bộ cơ chế lưu trữ JWT sang HttpOnly Cookie.
- AR3: Cấu trúc Models theo dạng Domain-driven (auth.py, stock.py, chat.py).
- AR4: Sử dụng nghiêm ngặt Pydantic V2 cho validation dữ liệu Backend.

### UX Design Requirements

UX-DR1: Module AuthModal chuẩn (Login/Register/OAuth/OTP) với Modal Overlay UI.
UX-DR2: ChatInterface với Message bubbles và TextField quản lý giao diện đoạn hội thoại.
UX-DR3: InteractiveChart tích hợp Recharts chuyên sâu để biểu diễn trực quan dữ liệu.
UX-DR4: Navbar với Logo, Tab switching, Profile/Avatar (Layout Component).
UX-DR5: PredictionWidget hiển thị kết quả AI/ML (Mua/Bán, Rủi ro) từ predict endpoint.
UX-DR6: Sử dụng Tailwind CSS 4 với CSS variables cho thiết kế nhất quán.

### FR Coverage Map

- **FR1 (Market Data):** Epic 2 - Nền tảng dữ liệu chứng khoán & Trực quan hóa.
- **FR2 (AI Chat):** Epic 3 - Trợ lý AI tương tác và tư vấn tài chính.
- **FR3 (Prediction):** Epic 4 - Học máy và dự báo xu hướng cổ phiếu.
- **FR4 (Auth):** Epic 1 - Bảo mật xác thực và quản lý tài khoản người dùng.
- **Tất cả NFRs:** Được lồng ghép vào từng Epic và tập trung tinh chỉnh tại Epic 5.

## Epic List

### Epic 1: Hệ thống Xác thực & Quản lý Người dùng (Authentication & User Management)

Người dùng có thể đăng ký, đăng nhập an toàn bằng nhiều phương thức (Google, OTP, Mật khẩu) và quản lý phiên làm việc bảo mật.

**FRs covered:** FR4.

### Story 1.1: Đăng ký & Đăng nhập bằng Mật khẩu (Password-based Auth)

As a người dùng mới,
I want tạo tài khoản bằng email và mật khẩu,
So that tôi có thể truy cập các tính năng cá nhân hóa của hệ thống.

**Acceptance Criteria:**

**Given** người dùng ở giao diện AuthModal (UX-DR1)
**When** nhập email, mật khẩu hợp lệ (Pydantic V2 validation) và nhấn Đăng ký
**Then** hệ thống tạo user mới trong DB (SQLAlchemy), hash mật khẩu bằng bcrypt, và trả về JWT qua HttpOnly Cookie (AR2).

### Story 1.2: Đăng nhập bằng Google (Google OAuth2)

As a người dùng ưu tiên sự tiện lợi,
I want đăng nhập bằng tài khoản Google,
So that tôi không cần nhớ thêm mật khẩu mới.

**Acceptance Criteria:**

**Given** người dùng nhấn nút "Login with Google"
**When** xác thực thành công qua Google OAuth API
**Then** backend (FastAPI) kiểm tra/tạo user, và thiết lập phiên làm việc qua HttpOnly Cookie.

### Story 1.3: Xác thực OTP qua số điện thoại (Phone OTP Auth)

As a người dùng cần bảo mật cao,
I want nhận mã OTP và xác thực qua số điện thoại,
So that tôi có thể đăng nhập mà không cần mật khẩu.

**Acceptance Criteria:**

**Given** người dùng nhập số điện thoại hợp lệ
**When** backend gửi mã OTP và người dùng nhập đúng mã đó
**Then** hệ thống cho phép truy cập, cấp token và duy trì phiên làm việc.

### Story 1.4: Đăng xuất và Thu hồi Token (Logout & Redis Blacklist)

As a người dùng đã xong việc,
I want đăng nhập an toàn khỏi hệ thống,
So that tài khoản của tôi không bị xâm nhập trái phép.

**Acceptance Criteria:**

**Given** người dùng đang đăng nhập
**When** nhấn nút Logout trên Navbar (UX-DR4)
**Then** hệ thống xóa HttpOnly Cookie và đưa token vào Redis Blacklist (AR1, NFR2).

### Epic 2: Tra cứu & Trực quan hóa Dữ liệu Thị trường (Market Data Lookup & Visualization)

Người dùng có thể tìm kiếm mã chứng khoán (HOSE, HNX, UPCOM) và xem biểu đồ tương tác sinh động với dữ liệu thực tế từ vnstock.

**FRs covered:** FR1.

### Story 2.1: Tìm kiếm & Gợi ý Mã Cổ phiếu (Stock Search & Suggestions)

As a người dùng,
I want tìm kiếm nhanh các mã cổ phiếu (Ticker) từ sàn HOSE, HNX, UPCOM,
So that tôi chọn đúng doanh nghiệp mình đang quan tâm.

**Acceptance Criteria:**

**Given** người dùng nhập ký tự (ví dụ: "VCB") vào thanh tìm kiếm trên Navbar (UX-DR4)
**When** Backend gọi API từ vnstock để lấy danh sách gợi ý
**Then** hiển thị danh sách gồm Mã chứng khoán, Tên đầy đủ và Sàn tương ứng.

### Story 2.2: Lấy dữ liệu Lịch sử Giá (Historical Data Fetching)

As a người dùng hệ thống,
I want tải dữ liệu giá hằng ngày (Daily Prices) trong quá khứ,
So that làm cơ sở cho việc phân tích xu hướng.

**Acceptance Criteria:**

**Given** một mã cổ phiếu đã được chọn và người dùng chọn mốc thời gian (1 Tháng, 1 Năm)
**When** Backend thực hiện fetch dữ liệu lịch sử và ánh xạ vào schemas chuẩn hóa
**Then** dữ liệu được lưu trữ tạm thời và trả về cho Frontend theo định dạng JSON chuẩn.

### Story 2.3: Biểu đồ Tương tác (Interactive Chart Visualization)

As a nhà đầu tư,
I want xem biểu đồ đường hoặc nến sắc nét về biến động giá,
So that tôi dễ dàng nhận diện các điểm bùng nổ hoặc sụt giảm.

**Acceptance Criteria:**

**Given** dữ liệu lịch sử giá đã sẵn sàng
**When** InteractiveChart (UX-DR3) sử dụng Recharts để vẽ
**Then** biểu đồ hiển thị Tooltip chi tiết (Giá đóng cửa, Khối lượng) khi người dùng rê chuột qua các điểm dữ liệu.

### Story 2.4: Tối ưu hóa Dữ liệu bằng Redis (Market Data Caching)

As a hệ thống cần đạt hiệu suất cao,
I want lưu Cache kết quả từ vnstock vào Redis,
So that giảm độ trễ (Latency) cho các yêu cầu lặp lại.

**Acceptance Criteria:**

**Given** một yêu cầu xem mã cổ phiếu "FPT"
**When** dữ liệu đã tồn tại trong Redis
**Then** hệ thống trả về ngay lập tức từ Cache thay vì gọi lại API vnstock (NFR1).

### Epic 3: Trợ lý AI Tư vấn Tài chính (AI Financial Assistant Chatbot)

Người dùng có thể trò chuyện tự nhiên với AI để nhận lời khuyên, giải đáp thắc mắc về thị trường tài chính Việt Nam qua OpenAI.

**FRs covered:** FR2.

### Story 3.1: Giao diện Hội thoại (Chat UI Implementation)

As a người dùng,
I want một giao diện chat trực quan với bong bóng tin nhắn và ô nhập liệu,
So that tôi có thể trao đổi với AI một cách tự nhiên.

**Acceptance Criteria:**

**Given** người dùng mở ChatInterface (UX-DR2)
**When** nhập tin nhắn và nhấn "Gửi"
**Then** tin nhắn người dùng hiển thị ngay lập tức, kèm theo trạng thái "AI đang suy nghĩ..." (Loading state).

### Story 3.2: Tích hợp Dịch vụ OpenAI (OpenAI API Integration)

As a hệ thống,
I want kết nối và gửi câu hỏi tới OpenAI API,
So that nhận được phản hồi phân tích chứng khoán chất lượng cao.

**Acceptance Criteria:**

**Given** một yêu cầu chat từ người dùng
**When** openai_service (AR4) được gọi kèm theo ngữ cảnh (Context) về mã cổ phiếu đang xem
**Then** hệ thống trả về câu trả lời được định dạng rõ ràng (Markdown).

### Story 3.3: Quản lý Lịch sử Hội thoại (Chat History Management)

As a người dùng đã đăng nhập,
I want xem lại các đoạn hội thoại cũ của mình,
So that tôi không phải nhập lại các câu hỏi đã hỏi.

**Acceptance Criteria:**

**Given** người dùng quay lại ứng dụng sau khi đã logout/login
**When** giao diện Chat được tải
**Then** hệ thống truy xuất lịch sử từ DB thông qua Chat Models (AR3) và hiển thị chính xác theo thời gian.

### Story 3.4: Trải nghiệm AI Streaming (Real-time Response)

As a người dùng,
I want thấy văn bản phản hồi của AI hiện ra từng từ một,
So that cảm giác như đang trò chuyện với người thật và giảm thời gian chờ đợi.

**Acceptance Criteria:**

**Given** AI phản hồi một câu trả lời dài
**When** Backend sử dụng cơ chế Streaming của FastAPI
**Then** ChatInterface cập nhật nội dung tin nhắn liên tục mà không cần đợi tải xong toàn bộ.

### Epic 4: Dự báo & Phân tích Xu hướng Cổ phiếu (Stock Prediction & Trend Analysis)

Người dùng có thể xem các dự báo kỹ thuật và xác suất tăng/giảm rủi ro của cổ phiếu dựa trên mô hình Prophet/ML.

**FRs covered:** FR3.

### Story 4.1: Tích hợp Mô hình Dự báo Prophet (Prophet Engine Integration)

As a chuyên gia dữ liệu,
I want nạp dữ liệu lịch sử giá vào mô hình FaceBook Prophet,
So that hệ thống tính toán được quỹ đạo giá trong tương lai.

**Acceptance Criteria:**

**Given** dữ liệu chuỗi thời gian (Ticker Prices) từ Backend
**When** prophet_engine (AR4) thực hiện huấn luyện nhanh
**Then** trả về dữ liệu dự đoán (Yhat) và các dải tin cậy trong 7-30 ngày tới.

### Story 4.2: Thành phần Widget Hiển thị Dự báo (Prediction UI Implementation)

As a người dùng,
I want một bảng tóm tắt kết quả phân tích AI rõ ràng,
So that tôi biết ngay tình trạng cổ phiếu mà không cần đọc biểu đồ phức tạp.

**Acceptance Criteria:**

**Given** kết quả dự báo đã tải xong
**When** PredictionWidget (UX-DR5) được hiển thị trên giao diện
**Then** hiển thị trực quan các thẻ: Xu hướng (Tăng/Giảm), Độ tự tin (%), và Khuyến nghị (Mua/Bán/Nắm giữ).

### Story 4.3: Tính toán Độ tin cậy & Rủi ro (Scoring & Risk Assessment)

As a nhà đầu tư cần sự chính xác,
I want biết độ sai lệch của mô hình dựa trên dữ liệu quá khứ,
So that tôi tránh được các quyết định sai lầm khi thị trường biến động quá mạnh.

**Acceptance Criteria:**

**Given** kết quả từ mô hình Prophet
**When** Backend tính toán chỉ số sai số (ví dụ RMSE)
**Then** xuất ra một mức độ rủi ro (Thấp/Trung bình/Cao) để cảnh báo người dùng.

### Story 4.4: Giải thích Kết quả bằng AI (AI Insights Integration)

As a người dùng,
I want AI giải thích tại sao kết quả dự báo lại như vậy bằng ngôn ngữ tự nhiên,
So that tôi hiểu sâu hơn về bối cảnh của cổ phiếu.

**Acceptance Criteria:**

**Given** dữ liệu số từ Story 4.1 và 4.3
**When** gửi bảng thông số này tới OpenAI (tích hợp từ Epic 3)
**Then** hiển thị một đoạn văn bản "Insight từ AI" ngay dưới Widget dự báo.

### Epic 5: Tối ưu hóa Hệ thống & Hạ tầng Hiệu năng (System Optimization & Performance)

Đảm bảo hệ thống phản hồi cực nhanh, ổn định và bảo mật thông qua Redis Caching và Rate Limiting thực thụ.

**FRs covered:** NFR1, NFR2, NFR3.

### Story 5.1: Chuyển đổi Blacklist Token sang Redis (Redis Blacklist Setup)

As a chuyên gia bảo mật,
I want chuyển đổi cơ chế in-memory Blacklist hiện tại sang Redis,
So that trạng thái đăng xuất được đồng bộ giữa tất cả các máy chủ API nếu scale sytem lên.

**Acceptance Criteria:**

**Given** thông tin cấu hình Redis hợp lệ trong file .env
**When** user thực hiện hành động Logout (từ Story 1.4)
**Then** Backend kết nối và lưu JWT bị revoke vào Redis với TTL bằng đúng thời gian sống còn lại của token.

### Story 5.2: Áp dụng Rate Limiting bằng Redis (Global Rate Limit)

As a quản trị viên hệ thống,
I want giới hạn số lượng request từ một Client (theo IP/Token),
So that ngăn chặn các cuộc tấn công Brute-force hoặc lạm dụng API vnstock/OpenAI.

**Acceptance Criteria:**

**Given** Endpoint đang có quá trình Rate Limiting middleware
**When** Client gửi quá 100 requests / phút
**Then** hệ thống (xử lý qua Redis) chặn và trả mã lỗi 429 Too Many Requests.

### Story 5.3: Tối ưu Hóa Giao diện Next.js (SSR/CSR Hybrid Optimization)

As a người dùng truy cập web,
I want giao diện Dashboard tải ngay lập tức,
So that tôi không phải chờ màn hình loading trắng.

**Acceptance Criteria:**

**Given** kiến trúc Server Components của Next.js (NFR1)
**When** người truy cập trang chủ / dashboard
**Then** cấu trúc khung UI được render trước ở phía server (Server-Side), trong khi các dữ liệu biểu đồ nặng được hydrate và tải lùi lại sau ở phía Client.
