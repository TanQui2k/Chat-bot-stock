---
stepsCompleted: [1, 2]
inputDocuments: ["README.md", "frontend/src/components/ChatInterface.tsx", "frontend/src/components/InteractiveChart.tsx", "frontend/src/components/PredictionWidget.tsx", "frontend/src/app/layout.tsx", "frontend/src/app/page.tsx"]
---

# Specification Thiết kế Trải nghiệm Người dùng - Chat-bot-stock (StockAI Predictor)

**Tác giả:** QUI  
**Ngày:** 2026-03-25

---

## 1. Tổng quan Dự án

### 1.1 Mô tả Dự án
**StockAI Predictor** là một nền tảng hỗ trợ dự đoán và phân tích thị trường chứng khoán sử dụng trí tuệ nhân tạo (AI). Dự án kết hợp **Backend (FastAPI)** và **Frontend (Next.js)** để cung cấp trải nghiệm người dùng hiện đại, trực quan và thông minh.

### 1.2 Mục tiêu Chính
- Phân tích thị trường chứng khoán theo thời gian thực
- Dự đoán xu hướng giá cổ phiếu bằng AI/Machine Learning
- Cung cấp trợ lý AI để giải đáp thắc mắc về tài chính và chứng khoán
- Hiển thị dữ liệu thị trường dưới dạng biểu đồ trực quan

### 1.3 Đối tượng Người dùng
- Nhà đầu tư cá nhân
- Người quan tâm đến thị trường chứng khoán Việt Nam
- Người dùng có kiến thức cơ bản về tài chính

---

## 2. Phân tích Hiện trạng

### 2.1 Các thành phần giao diện hiện tại

#### ChatInterface (Trợ lý AI)
- **Chức năng**: Chatbot tương tác để trả lời câu hỏi về chứng khoán
- **Thiết kế**: Dark theme với gradient emerald-cyan cho avatar AI
- **Tính năng**:
  - Hiển thị lịch sử hội thoại
  - Hiển thị trạng thái "đang trả lời" (loading animation)
  - Auto-focus ô input sau khi AI trả lời
  - Nút làm mới cuộc trò chuyện

#### InteractiveChart (Biểu đồ Giá)
- **Chức năng**: Hiển thị biểu đồ giá cổ phiếu theo thời gian
- **Thiết kế**: Dark theme với gradient background cho area chart
- **Tính năng**:
  - Biểu đồ area sử dụng Recharts
  - Hiển thị giá đóng cửa, biến động giá (%)
  - Tooltip hiển thị thông tin chi tiết khi hover
  - Loading state khi đang tải dữ liệu

#### PredictionWidget (Dự đoán AI)
- **Chức năng**: Hiển thị dự đoán xu hướng giá cổ phiếu trong 24h tới
- **Thiết kế**: Dark theme với gradient overlay
- **Tính năng**:
  - Dự đoán tăng/giảm giá
  - Mục tiêu giá dự kiến
  - Thanh progress hiển thị độ tin cậy
  - Visual indicators cho hướng tăng/giảm

### 2.2 Cấu trúc Trang Dashboard

```
┌─────────────────────────────────────────────────────┐
│                    Header (Navigation)              │
│  StockAI Predictor | Bảng điều khiển | Thị trường │
├─────────────────────────────────────────────────────┤
│  Tổng quan thị trường | Filter (1 Ngày/1 Tuần...) │
├──────────────────┬──────────────────────────────────┤
│                  │                                  │
│  Interactive     │    ChatInterface                 │
│  Chart (FPT)     │    (AI Trading Assistant)        │
│  - Biểu đồ giá   │    - Trợ lý AI                    │
│                  │    - Hỏi đáp                      │
├──────────────────┼──────────────────────────────────┤
│  Sentiment Widget│    PredictionWidget              │
│  - Phân tích cảm │    - Dự đoán 24h                   │
│    xúc           │    - Độ tin cậy                  │
└──────────────────┴──────────────────────────────────┘
```

### 2.3 Theme hiện tại
- **Background chính**: `bg-slate-950` (dark slate)
- **Background secondary**: `bg-slate-800/40` đến `bg-slate-800/90`
- **Primary accent**: `emerald-500` (màu xanh lá)
- **Secondary accent**: `cyan-500` (màu xanh nước biển)
- **Negative**: `rose-500` (màu đỏ)
- **Text**: `slate-50` đến `slate-300`

---

## 3. Khuyến nghị Thiết kế UX

### 3.1 Nguyên tắc Thiết kế

#### 3.1.1 Trải nghiệm Người dùng
1. **Trực quan và dễ hiểu**: Người dùng có thể dễ dàng hiểu được thông tin thị trường
2. **Phản hồi nhanh**: Hiển thị loading states rõ ràng và feedback tức thì
3. **Tập trung vào dữ liệu**: UI tối giản để không làm lu mờ dữ liệu quan trọng
4. **Tính nhất quán**: Thiết kế đồng bộ qua tất cả các thành phần

#### 3.1.2 Quy tắc Thiết kế
1. **Dark theme nhất quán**: Toàn bộ ứng dụng sử dụng dark theme
2. **Color psychology**: 
   - Xanh lá (emerald) cho tăng giá, thành công
   - Đỏ (rose) cho giảm giá, cảnh báo
   - Xanh nước biển (cyan) cho thông tin, hỗ trợ
3. **Typography**: Sử dụng Inter font với Vietnamese support
4. **Spacing**: Consistent spacing scale (4px, 8px, 16px, 24px, 32px)

### 3.2 Cải tiến Đề xuất

#### 3.2.1 Giai đoạn 1 - Cải tiến Ngay lập tức

##### A. Trang tổng quan (Dashboard)
1. **Thêm thanh tìm kiếm mã cổ phiếu**: Người dùng có thể nhanh chóng chuyển đổi giữa các mã cổ phiếu khác nhau
2. **Nút chọn mã cổ phiếu**: Danh sách mã phổ biến (FPT, VNM, MSN, VPB,...)
3. **Thay đổi biểu tượng avatar**: Avatar "VA" (User) nên là hình ảnh người thật hoặc icon người dùng

##### B. Trợ lý AI (ChatInterface)
1. **Cải thiện prompt gốc**: Prompt "Xin chào!" nên mở rộng để giới thiệu rõ hơn khả năng của AI
2. **Hiển thị loại tin nhắn**: Có thể thêm icon hoặc badge cho biết tin nhắn từ AI
3. **Menu nhanh**: Nút menu để xem lại lịch sử hoặc reset session

##### C. Biểu đồ (InteractiveChart)
1. **Chỉ mục biểu đồ**: Thêm các chỉ số như MA (Moving Average), RSI khi hover
2. **Lưới dữ liệu**: Thêm đường lưới ngang để dễ so sánh giá
3. **Nút download biểu đồ**: Cho phép người dùng lưu biểu đồ

##### D. Dự đoán (PredictionWidget)
1. **Thời gian dự đoán**: Hiển thị rõ thời gian dự đoán (24h tới)
2. **Lý do dự đoán**: Giải thích ngắn gọn lý do cho dự đoán tăng/giảm
3. **So sánh quá khứ**: Hiển thị độ chính xác của mô hình trong quá khứ

#### 3.2.2 Giai đoạn 2 - Tính năng Mới

##### A. Trang "Thị trường"
- Danh sách toàn bộ mã cổ phiếu
- Filter theo ngành, капит hóa
- So sánh nhiều mã cổ phiếu cùng lúc

##### B. Trang "Theo dõi"
- Danh sách mã cổ phiếu người dùng quan tâm
- Cảnh báo giá
- Lịch sử theo dõi

##### C. Trang "Bảng điều khiển"
- Tổng quan tài khoản
- Lịch sử giao dịch
- Báo cáo hiệu suất

##### D. Tính năng mới
1. **Tùy chọn theme**: Cho phép chuyển đổi giữa dark/light theme
2. **Cài đặt cảnh báo**: Cảnh báo khi giá đạt ngưỡng cụ thể
3. **Báo cáo AI**: Báo cáo phân tích chi tiết hàng ngày/tuần
4. **Chế độ demo**: Chế độ simulation để người dùng thử nghiệm

---

## 4. Sơ đồ Luồng Người dùng

### 4.1 Luồng Chính - Truy cập Dashboard

```
Người dùng truy cập trang chủ
        │
        ▼
Hiển thị Header với Navigation
        │
        ▼
Hiển thị Dashboard với:
  - InteractiveChart (mã FPT mặc định)
  - Sentiment Widget
  - PredictionWidget
  - ChatInterface
        │
        ▼
Người dùng tương tác với:
  - ChatInterface (hỏi đáp)
  - Chọn mã cổ phiếu khác
  - Thay đổi khoảng thời gian
```

### 4.2 Luồng - Chat với AI

```
Người dùng nhập câu hỏi
        │
        ▼
AI xử lý và phản hồi
        │
        ▼
Hiển thị tin nhắn trong lịch sử
        │
        ▼
Người dùng có thể:
  - Hỏi tiếp
  - Làm mới cuộc trò chuyện
  - Xem lại tin nhắn cũ
```

### 4.3 Luồng - Xem dự đoán

```
Dự liệu được tải
        │
        ▼
Mô hình ML phân tích
        │
        ▼
Hiển thị dự đoán:
  - Tăng/Giảm
  - Mục tiêu giá
  - Độ tin cậy
```

---

## 5. Thiết kế Chi tiết Các Component

### 5.1 Component: Header (Navigation)

#### Hiện tại
- Logo StockAI Predictor
- Navigation: Bảng điều khiển, Thị trường, Theo dõi
- Nút đăng nhập

#### Cải tiến
```markdown
┌──────────────────────────────────────────────────────────────┐
│ [StockAI] Bảng điều khiển | Thị trường | Theo dõi          │
│                                                              │
│                    [Tìm kiếm...] [⚙️] [VA]                 │
└──────────────────────────────────────────────────────────────┘
```

**Yêu cầu**:
- Thanh tìm kiếm nhanh mã cổ phiếu
- Cài đặt (⚙️) để thay đổi cài đặt
- Dropdown menu cho user profile

### 5.2 Component: Dashboard Grid

#### Hiện tại
- Left column: InteractiveChart (2/3)
- Right column: ChatInterface (1/3)
- Widgets bên dưới chart

#### Cải tiến
```markdown
┌──────────────────────────────────────────────────────────────┐
│  Filter: [1 ngày ▼] [FPT ▼] [Tìm kiếm...]                 │
├───────────────────────────────┬──────────────────────────────┤
│                               │                              │
│   InteractiveChart            │   ChatInterface              │
│   - Chart chi tiết            │   - Trợ lý AI                 │
│   - Indicators                │   - Quick actions            │
│                               │                              │
├───────────────────┬───────────┼──────────────────────────────┤
│   Sentiment       │   Quick   │   PredictionWidget           │
│   - Cảm xúc thị   │   Stats   │   - Dự đoán AI               │
│     trường           |   - Tốc độ phản hồi             │
│                               │   - Độ tin cậy                │
└───────────────────┴───────────┴──────────────────────────────┘
```

### 5.3 Component: ChatInterface

#### Hiện tại
- Avatar AI (emerald-cyan gradient)
- Avatar User (indigo-purple gradient)
- tin nhắn với bubble style

#### Cải tiến
```markdown
┌──────────────────────────────────────────────────────────────┐
│ [AI Trợ lý] [⚙️] [ℹ️]                                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [AI] Xin chào! Mình là Trợ lý AI Chứng khoán.              │
│       Mình có thể hỗ trợ thông tin giá và phân tích        │
│       chuyên sâu. Ví dụ: "Giá FPT bao nhiêu?"              │
│                                                              │
│  [User] Giá FPT hiện tại là bao nhiêu?                      │
│                                                              │
│  [AI] Giá FPT hiện tại là 98,500 ₫ (tăng 1,2% hôm nay).    │
│       Mình có thể cung cấp thêm thông tin chi tiết hoặc     │
│       dự đoán xu hướng cho mã này.                          │
│                                                              │
│  ───────────────────────────────────────────                 │
│                                                              │
│  [Tìm kiếm câu hỏi phổ biến...] [📞] [💾]                  │
│                                                              │
│  Nhắn tin cho AI...                                           │
│  [Gửi]                                                       │
└──────────────────────────────────────────────────────────────┘
```

**Yêu cầu**:
- Quick actions bar (Tìm kiếm câu hỏi, Gọi điện, Lưu cuộc trò chuyện)
- History menu để xem lại cuộc trò chuyện trước
- Quick responses cho các câu hỏi phổ biến

### 5.4 Component: InteractiveChart

#### Hiện tại
- Area chart với Recharts
- Hiển thị giá đóng cửa
- Tooltip khi hover

#### Cải tiến
```markdown
┌──────────────────────────────────────────────────────────────┐
│ [FPT] Mã cổ phiếu FPT                                       │
│  LỊCH SỬ GIAO DỊCH - PostgreSQL                            │
│                                                              │
│  Giá hiện tại: 98,500 ₫ (+1,200 ₫ / +1.22%)                │
│                                                              │
│  [Indicators ▼] [Timeframe ▼] [Download ▼]                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   [Biểu đồ khu vực với các chỉ số kỹ thuật]                │
│                                                              │
│   Indicators: MA20, MA50, RSI                              │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  Công cụ: [Zoom] [Pan] [Reset] [Measure]                   │
└──────────────────────────────────────────────────────────────┘
```

**Yêu cầu**:
- Indicators kỹ thuật (MA, RSI, MACD)
- Timeframe selector (1 ngày, 1 tuần, 1 tháng, 1 năm, YTD)
- Download biểu đồ dưới dạng PNG/PDF
- Công cụ measure để so sánh giá

### 5.5 Component: PredictionWidget

#### Hiện tại
- Dự đoán tăng/giảm
- Độ tin cậy
- Mục tiêu giá

#### Cải tiến
```markdown
┌──────────────────────────────────────────────────────────────┐
│ [📈] Mô hình ML Dự đoán (24h tới)                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Xu hướng: TĂNG GIÁ 📈                                      │
│  Mục tiêu: 100,200 ₫                                        │
│                                                              │
│  ĐỘ TIN CẬY: 85.3%                                          │
│  ██████████████████████████████████                         │
│                                                              │
│  Lý do dự đoán:                                              │
│  • Volume giao dịch tăng 15%                                │
│  • Chỉ số RSI ở mức mua quá mức                             │
│  • Tin tức tích cực về ngành                               │
│                                                              │
│  [Xem chi tiết ▼] [Chia sẻ 📤]                              │
└──────────────────────────────────────────────────────────────┘
```

**Yêu cầu**:
- Giải thích lý do dự đoán (AI explainability)
- Chia sẻ dự đoán
- Lịch sử độ tin cậy

---

## 6. Trải nghiệm Di động (Responsive Design)

### 6.1 Mobile First Approach

#### Layout trên Mobile
```markdown
┌──────────────────────────────────────┐
│ Header (Navigation)                  │
├──────────────────────────────────────┤
│ Filter: [1 ngày] [FPT]              │
├──────────────────────────────────────┤
│ [InteractiveChart]                   │
│  - Full width                        │
├──────────────────────────────────────┤
│ [Sentiment Widget] [Prediction]     │
│  - 2 cột side-by-side                │
├──────────────────────────────────────┤
│ [ChatInterface]                      │
│  - Full width                        │
└──────────────────────────────────────┘
```

#### Yêu cầu Responsive
- **Mobile (320px - 768px)**: Single column layout
- **Tablet (768px - 1024px)**: 2-3 columns
- **Desktop (1024px+)**: Full grid layout

### 6.2 Touch Targets
- Minimum size: 44x44px
- Spacing: 8px giữa các elements
- Scroll: Smooth scrolling

---

## 7. Trợ năng (Accessibility)

### 7.1 WCAG Compliance

#### Color Contrast
- Text trên background:Ratio ≥ 4.5:1
- Large text:Ratio ≥ 3:1

#### Keyboard Navigation
- Tab order hợp lý
- Focus indicators rõ ràng
- Skip links

#### Screen Reader
- ARIA labels đầy đủ
- Semantic HTML
- alt text cho hình ảnh

---

## 8. Hướng dẫn Thiết kế Tài liệu

### 8.1 Design System

#### Colors
| Name | Hex | Usage |
|------|-----|-------|
| Emerald | #10b981 | Primary, success, positive |
| Cyan | #06b6d4 | Secondary, info |
| Indigo | #6366f1 | User, interactive |
| Rose | #f43f5e | Negative, danger |
| Slate 950 | #020617 | Background primary |
| Slate 900 | #0f172a | Background secondary |
| Slate 800 | #1e293b | Card background |
| Slate 50 | #f8fafc | Text primary |

#### Typography
| Element | Font | Size | Weight |
|---------|------|------|--------|
| Heading 1 | Inter | 2rem | 700 |
| Heading 2 | Inter | 1.5rem | 600 |
| Heading 3 | Inter | 1.25rem | 600 |
| Body | Inter | 1rem | 400 |
| Small | Inter | 0.875rem | 400 |

#### Spacing Scale
| Value | Pixel |
|-------|-------|
| xs | 4px |
| sm | 8px |
| md | 16px |
| lg | 24px |
| xl | 32px |

---

## 9. Bảng Kiểm tra Thiết kế

### 9.1 Thiết kế Component

- [ ] Header có thanh tìm kiếm nhanh
- [ ] ChatInterface có quick actions
- [ ] InteractiveChart có indicators kỹ thuật
- [ ] PredictionWidget có giải thích lý do
- [ ] Dashboard có responsive layout

### 9.2 Trải nghiệm Người dùng

- [ ] Loading states rõ ràng
- [ ] Feedback tức thì khi tương tác
- [ ] Error messages thân thiện
- [ ] Empty states rõ ràng

### 9.3 Trợ năng

- [ ] Color contrast đạt WCAG AA
- [ ] Keyboard navigation hoạt động
- [ ] Screen reader đọc đúng nội dung

---

## 10. Triển khai Đã hoàn thành

### 10.1 Cải tiến Giao diện (Giai đoạn 1)

#### InteractiveChart (Biểu đồ Giá)
- ✅ Thêm chỉ số kỹ thuật (MA20, MA50, RSI)
- ✅ Bộ chọn timeframe (1D, 1W, 1M, 3M, 6M, 1Y)
- ✅ Tải biểu đồ (button)
- ✅ Công cụ Measure và Reset
- ✅ Hiển thị giá hiện tại với biến động %

#### PredictionWidget (Dự đoán AI)
- ✅ Giải thích lý do dự đoán (collapsible)
- ✅ Chức năng chia sẻ
- ✅ Hiển thị rõ thời gian dự đoán (24h tới)

#### ChatInterface (Trợ lý AI)
- ✅ Quick actions bar với các mẫu câu hỏi phổ biến
- ✅ Cải thiện welcome message
- ✅ Menu nhanh để làm mới cuộc trò chuyện

#### Dashboard (Trang tổng quan)
- ✅ Trình chọn mã cổ phiếu với dropdown
- ✅ Danh sách mã phổ biến (FPT, VNM, MSN, VPB, ACB, HPG, VIC, VCB)
- ✅ Bộ chọn timeframe tích hợp

### 10.2 Các file đã cập nhật

| File | Thay đổi |
|------|----------|
| `frontend/src/components/InteractiveChart.tsx` | Thêm indicators, timeframe selector, download button |
| `frontend/src/components/PredictionWidget.tsx` | Thêm lý do dự đoán, chia sẻ |
| `frontend/src/components/ChatInterface.tsx` | Thêm quick actions, improved prompt |
| `frontend/src/app/page.tsx` | Thêm stock selector, improved filters |

### 10.3 Hướng dẫn sử dụng

Để xem các thay đổi, chạy frontend development server:

```bash
cd frontend
npm run dev
```

Sau đó truy cập `http://localhost:3000` để xem dashboard đã được cải tiến.

---

<!-- UX design content will be appended sequentially through collaborative workflow steps -->
