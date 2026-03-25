---
stepsCompleted: []
inputDocuments: ["frontend/src/components/AuthModal.tsx", "frontend/src/app/page.tsx"]
---

# UX Design Specification - Modern Authentication Interface
**Author:** User  
**Date:** 2026-03-25  
**Project:** StockAI Predictor - Authentication Design

---

## 1. Design Brief

### 1.1 Design Objective
Tạo giao diện đăng nhập/đăng ký hiện đại, trẻ trung, hấp dẫn cho hệ thống giao dịch chứng khoán StockAI Predictor.

### 1.2 Target Audience
- **Tuổi:** 18-35 tuổi (thế hệ trẻ, năng động)
- **Nhu cầu:** Phù hợp với người dùng Việt Nam yêu thích công nghệ
- **Phong cách:** Hiện đại, năng động, thân thiện với thiết bị di động

### 1.3 Core Principles
- **Hiện đại (Modern):** Sử dụng gradient, shadow mềm, glassmorphism
- **Trẻ trung (Youthful):** Màu sắc năng động, hiệu ứng chuyển động mượt mà
- **Thu hút (Attractive):** Visual hierarchy rõ ràng, call-to-action nổi bật
- **Tối giản (Minimal):** interface sạch, tập trung vào nội dung chính

---

## 2. Current State Analysis

### 2.1 Existing Authentication Flow
```
User truy cập trang chủ
    ↓
Click "Đăng nhập" button
    ↓
Hiển thị AuthModal
    ├─ Tab: Đăng nhập SMS (Phone)
    ├─ Tab: Đăng nhập Mật khẩu (Password)
    └─ Google Sign-In Button
```

### 2.2 Current Design Issues
- Thiếu màu sắc gradient hiện đại
- Không có hiệu ứng chuyển động
- Theme quá tối/static
- Thiếu sự trẻ trung và năng động

---

## 3. Design Concept: "StockAI Modern Auth"

### 3.1 Color Palette

#### Primary Colors (New)
| Name | Hex | Usage |
|------|-----|-------|
| Deep Violet | #6366f1 | Primary gradient start |
| Electric Cyan | #06b6d4 | Primary gradient end |
| Neon Emerald | #10b981 | Success, secondary accent |
| Deep Magenta | #d946ef | Accent highlights |

#### Background Colors
| Name | Hex | Usage |
|------|-----|-------|
| Dark Gradient | Gradient | Main background |
| Glass White | rgba(255,255,255,0.95) | Modal backgrounds |
| Card Dark | #0f172a | Card backgrounds |

### 3.2 Typography
| Element | Font | Size | Weight |
|---------|------|------|--------|
| Heading 1 | Inter | 2.5rem | 700 |
| Heading 2 | Inter | 1.5rem | 600 |
| Body | Inter | 1rem | 400 |
| Button | Inter | 1rem | 600 |

### 3.3 Components

#### Auth Modal - Modern Design

```
┌──────────────────────────────────────────────────────┐
│ [X]                                                  │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │   🌟 StockAI                                  │   │
│  │   Trợ lý AI Chứng khoán thông minh          │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │   [Google Logo]  Đăng nhập với Google       │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ──────── Hoặc ────────                             │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │ Tab: [SMS] [Mật khẩu]                      │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Số điện thoại 📱                            │   │
│  │  ┌──────────────────────────────────────┐   │   │
│  │  │ +84 ▼  123 456 789                   │   │   │
│  │  └──────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  [Gửi mã xác thực 🔐]                       │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Quên mật khẩu? 🔑                          │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

#### Button Styles
- **Primary Button:** Gradient violet → cyan, rounded-lg, hover effect
- **Secondary Button:** White fill, rounded-lg, hover shadow
- **Auth Button:** Gradient emerald → cyan, large padding

#### Animations
- **Modal Entrance:** Fade-in + Scale-up (300ms)
- **Button Hover:** Scale 1.05 + shadow increase
- **Input Focus:** Glow effect + border color transition
- **Loading Spinner:** Rotating gradient ring

---

## 4. Component Specifications

### 4.1 Auth Modal

#### Structure
```
AuthModal {
  Header (Gradient Background)
  - Logo StockAI
  - Tagline
  
  Google Sign-In Button
  - Logo Google
  - Text
  
  Divider (Or text)
  
  Tab Navigation
  - SMS Tab (Active)
  - Password Tab
  
  Phone Form (Active)
  - Phone Input
  - Send Code Button
  - Timer (Countdown)
  
  Or Content
  - Password Form (Alternative)
  - Email/Phone Input
  - Password Input
  - Login Button
}
```

### 4.2 Color Gradients

#### Primary Gradient
```css
background: linear-gradient(135deg, #6366f1 0%, #06b6d4 100%);
```

#### Success Gradient
```css
background: linear-gradient(135deg, #10b981 0%, #06b6d4 100%);
```

#### Background Gradient
```css
background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
```

### 4.3 Glassmorphism Effects

```css
background: rgba(255, 255, 255, 0.95);
backdrop-filter: blur(10px);
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
```

---

## 5. Mobile Responsive Design

### 5.1 Mobile Layout (320px - 768px)
```
┌──────────────────────┐
│ [X]                  │
│                      │
│   🌟 StockAI         │
│   Trợ lý AI          │
│                      │
│   [Google Button]    │
│                      │
│   ── Hoặc ──         │
│                      │
│   Tab: [SMS] [P]    │
│                      │
│   Số điện thoại      │
│   [Input]            │
│                      │
│   [Gửi mã]          │
│                      │
└──────────────────────┘
```

### 5.2 Tablet Layout (768px - 1024px)
```
┌────────────────────────────────┐
│                                │
│   [X]       StockAI           │
│            Trợ lý AI           │
│                                │
│   [Google Button]              │
│                                │
│   ── Hoặc ──                   │
│                                │
│   [SMS] [Password]             │
│                                │
│   [Input]                      │
│   [Button]                     │
│                                │
└────────────────────────────────┘
```

### 5.3 Desktop Layout (1024px+)
```
┌────────────────────────────────────────┐
│                                        │
│                                        │
│           [X] StockAI                  │
│        Trợ lý AI Thông Minh           │
│                                        │
│   ┌──────────────────────────────┐     │
│   │   [G] Đăng nhập với Google  │     │
│   └──────────────────────────────┘     │
│                                        │
│        ──────── Hoặc ────────          │
│                                        │
│   ┌──────────────────────────────┐     │
│   │  [SMS]  [Mật khẩu]          │     │
│   └──────────────────────────────┘     │
│                                        │
│   ┌──────────────────────────────┐     │
│   │  Số điện thoại              │     │
│   │  [Input]                    │     │
│   └──────────────────────────────┘     │
│                                        │
│   ┌──────────────────────────────┐     │
│   │  [Gửi mã xác thực]          │     │
│   └──────────────────────────────┘     │
│                                        │
└────────────────────────────────────────┘
```

---

## 6. Interactive States

### 6.1 Button States
| State | Color | Shadow |
|-------|-------|--------|
| Default | Gradient violet→cyan | None |
| Hover | Gradient violet→cyan | 0 4px 12px rgba(99, 102, 241, 0.4) |
| Active | Gradient violet→cyan | 0 2px 4px rgba(0,0,0,0.2) |
| Loading | Gradient gray→gray | None |

### 6.2 Input States
| State | Border | Placeholder |
|-------|--------|-------------|
| Default | #e2e8f0 | #94a3b8 |
| Focus | #6366f1 (Gradient) | #6366f1 |
| Error | #f43f5e | #f43f5e |

### 6.3 Loading States
- **Spinner:** Rotating gradient ring
- **Button Text:** "Đang gửi..." / "Đang xử lý..."
- **Opacity:** 0.7 for content during load

---

## 7. Animation Spec

### 7.1 Modal Entrance
```css
@keyframes fadeInScale {
  0% { opacity: 0; transform: scale(0.9); }
  100% { opacity: 1; transform: scale(1); }
}

animation: fadeInScale 0.3s cubic-bezier(0.16, 1, 0.3, 1);
```

### 7.2 Button Ripple Effect
```css
@keyframes ripple {
  0% { transform: scale(0); opacity: 1; }
  100% { transform: scale(4); opacity: 0; }
}
```

### 7.3 Input Glow
```css
@keyframes glow {
  0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
  70% { box-shadow: 0 0 0 6px rgba(99, 102, 241, 0); }
  100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
}
```

---

## 8. Implementation Checklist

### 8.1 Frontend Components
- [ ] AuthModal with modern gradient design
- [ ] Google Sign-In button with logo
- [ ] Tab navigation (SMS/Password)
- [ ] Phone input with country code selector
- [ ] Timer countdown for resending code
- [ ] Loading states for all actions
- [ ] Error message display

### 8.2 Styling
- [ ] Gradient backgrounds
- [ ] Glassmorphism effects
- [ ] Smooth transitions (0.2s-0.3s)
- [ ] Responsive breakpoints
- [ ] Mobile-first design

### 8.3 Animations
- [ ] Modal entrance animation
- [ ] Button hover effects
- [ ] Input focus glow
- [ ] Loading spinner
- [ ] Tab transition

---

## 9. Success Metrics

### 9.1 Visual Design
- Gradient effects visible on all major buttons
- Glassmorphism clear on modal
- Smooth animations without stutter

### 9.2 User Experience
- 95%+ users complete registration
- <2s load time
- Mobile-friendly (44px+ touch targets)
- Clear visual feedback on all interactions

### 9.3 Performance
- Optimized images (SVG for logos)
- Minified CSS
- Lazy loading animations

---

## 10. Design Assets

### 10.1 Icons
- Google Logo: SVG from Google
- Phone Icon: Heroicons
- Lock Icon: Heroicons
- User Icon: Heroicons

### 10.2 Fonts
- Primary: Inter (Google Fonts)
- Vietnamese support: Inter with language extension

### 10.3 Colors Reference
```
Primary: #6366f1 → #06b6d4 (Gradient)
Success: #10b981 → #06b6d4 (Gradient)
Background: #0f172a → #1e1b4b (Gradient)
Text: #f8fafc
```

---

## 11. Implementation Notes

### 11.1 Tech Stack
- **Framework:** Next.js 14
- **Styling:** Tailwind CSS
- **Icons:** Heroicons
- **Animations:** CSS Transitions + Keyframes

### 11.2 Design Patterns
- Mobile-first responsive design
- Gradient accents for visual interest
- Glassmorphism for depth
- Smooth micro-interactions

### 11.3 Accessibility
- High contrast text (4.5:1 ratio)
- Focus indicators on interactive elements
- Keyboard navigation support
- ARIA labels for screen readers

---

**End of Authentication UX Design Specification**