---
title: 'Implement UX Design Specification for ChatInterface and InteractiveChart'
type: 'feature'
created: '2026-03-30T10:15:00Z'
status: 'done'
context: ['_bmad-output/planning-artifacts/ux-design-specification.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Chúng ta đã hoàn tất Bản Đặc tả Thiết kế UX (UX Design Specification) nhưng các component hiện tại chưa được cập nhật giao diện "Responsive Cyber-Pro" (dark theme Emerald/Violet, bố cục Grid, trạng thái Empty/Loading).

**Approach:** Cập nhật file Layout chính (`page.tsx`), `InteractiveChart.tsx` và `ChatInterface.tsx` để tuân thủ chặt chẽ các quy tắc về Layout (Desktop: 8-4, Mobile: 100% + Bottom Sheet), Màu sắc (Slate, Violet, Emerald), và Component Strategy đã đề ra.

## Boundaries & Constraints

**Always:** Sử dụng Tailwind css classes theo các mã màu đã quy định (`slate-950`, `violet-500`, `emerald-400`); tuân thủ quy tắc "No Dead End" (hiển thị gợi ý khi Chat rỗng) và ưu tiên Responsive Mobile First.

**Ask First:** Khi cần cài đặt thêm thư viện animation (như Framer Motion) hoặc nếu shadcn/ui thiếu component bắt buộc.

**Never:** Viết custom CSS ra một file tách biệt (trừ khi thực sự cần thiết); Không sử dụng thẻ `<style>`.

</frozen-after-approval>

## Code Map

- `frontend/src/app/page.tsx` -- Khung Layout Grid tổng thể (12 cột).
- `frontend/src/components/InteractiveChart.tsx` -- Vùng hiển thị Biểu đồ (chiếm 8/12 cột Desktop, 100% Mobile). Cần Skeleton UI và Glassmorphism wrapper.
- `frontend/src/components/ChatInterface.tsx` -- Khung đàm thoại AI (chiếm 4/12 cột Desktop, FAB/Bottom Sheet Mobile). Chứa Empty State pills.

## Tasks & Acceptance

**Execution:**
- [x] `frontend/src/app/page.tsx` -- CẤU TRÚC LẠI Layout sử dụng Grid 12 cột. Chart chiếm `col-span-12 md:col-span-8`, Chat chiếm `col-span-12 md:col-span-4` (Desktop) và quản lý state cho mobile -- Để thiết lập Layout tổng "Cyber-Pro" an toàn.
- [x] `frontend/src/components/InteractiveChart.tsx` -- NÂNG CẤP giao diện bọc ngoài bằng Glassmorphism (`backdrop-blur bg-slate-900/40`), thêm trạng thái Loading Skeleton -- Tối ưu hoá hiển thị khu vực màn hình chính.
- [x] `frontend/src/components/ChatInterface.tsx` -- TRIỂN KHAI Empty State (hiển thị 3 nút gợi ý câu hỏi), nút Primary nền `violet-500`, và tuỳ chỉnh giao diện Input Bar -- Khớp 100% Specification.

**Acceptance Criteria:**
- Given người dùng mở bằng Màn hình lớn (Desktop), when trang tải xong, then Biểu đồ chiếm bên trái (66%) và Khung Chat mở mặc định ở bên phải (33%).
- Given trong Khung Chat chưa có tin nhắn nào, when xem khung chat, then có ít nhất 3 viên thuốc (Pills) chứa câu hỏi gợi ý để bấm vào.
- Given người dùng thấy Nút Gửi tin nhắn, when để ý màu sắc, then nó màu Solid Violet (`bg-violet-500`).

## Verification

**Commands:**
- `npm run dev` -- expected: UI sẽ compile thành công không có lỗi CSS hay TS, hiển thị đúng Grid 12 cột trên trình duyệt.

**Manual checks (if no CLI):**
- Co giãn trình duyệt nhỏ lại thành kích thước điện thoại. Khung chat sẽ xuống dòng hoặc thu về dạng Modal/Khu vực dưới cùng.
- Nhấp thử vào Nút Gửi/Phản hồi để kích hoạt hiệu ứng glow.

## Suggested Review Order

**Layout Bố cục tổng thể & Responsive Modal**
- Triển khai Grid 3/4 Desktop và Mobile Floating Action Button với Bottom Sheet.
  [`page.tsx:42`](../../frontend/src/app/page.tsx#L42)

**Theme & Skeleton Biểu đồ**
- Thêm hiệu ứng Glassmorphism và layout khung xương Loading Skeleton cho vùng tải.
  [`InteractiveChart.tsx:94`](../../frontend/src/components/InteractiveChart.tsx#L94)

**Trạng thái trống & Branding Nút bấm**
- Cập nhật tự động hiển thị Quick Actions khi Chat rỗng và đổi Nút bấm sang màu Tím.
  [`ChatInterface.tsx:184`](../../frontend/src/components/ChatInterface.tsx#L184)
