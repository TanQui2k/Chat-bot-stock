---
stepsCompleted: [2]
inputDocuments: ["_bmad-output/project-context.md"]
---

# UX Design Specification Chat-bot-stock

**Author:** QUI
**Date:** 2026-04-04

---

## 🎨 Trạng thái hiện tại & Quyết định thiết kế (Current State & Design Decisions)

### 1. Loại bỏ các chỉ báo kỹ thuật (Technical Indicators Removal)

- **Vấn đề:** Biểu đồ quá rườm rà với các đường MA20, MA50 và RSI, gây khó khăn cho việc quan sát biến động giá chính và dự báo AI.
- **Quyết định:**
  - Loại bỏ hoàn toàn các đường MA trên biểu đồ (`ReferenceLine`).
  - Gỡ bỏ nút "Indicators" và dòng tóm tắt thông số kỹ thuật.
  - Cải thiện bố cục Header để tập trung vào **Giá hiện tại** và **Dự báo AI (Prophet)**.
- **Lợi ích:** Giao diện tối giản, cao cấp và nhấn mạnh vào tính năng AI đặc trưng của ứng dụng.

### 2. Tuân thủ Quy tắc Dự án (Project Rule Compliance)

- Cập nhật tất cả các logic gọi API để sử dụng biến môi trường `process.env.NEXT_PUBLIC_API_URL` thay vì hardcode `localhost:8000`.

---
