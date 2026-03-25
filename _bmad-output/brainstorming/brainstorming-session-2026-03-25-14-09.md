---
stepsCompleted: [1]
inputDocuments: []
session_topic: 'Tăng cường khả năng hiểu ngữ cảnh của AI trong hệ thống chat chứng khoán'
session_goals: 'Xác định các phương pháp cải thiện khả năng bắt ngữ cảnh để AI đưa ra phản hồi chính xác và phù hợp hơn'
selected_approach: 'Progressive Flow - kết hợp nhiều kỹ thuật'
techniques_used: ['SCAMPER']
ideas_generated: 3
context_file: ''
---

# Brainstorming Session Results

**Facilitator:** User
**Date:** 2026-03-25

## Session Overview

**Topic:** Tăng cường khả năng hiểu ngữ cảnh của AI trong hệ thống chat chứng khoán

**Goals:** Xác định các phương pháp cải thiện khả năng bắt ngữ cảnh để AI đưa ra phản hồi chính xác và phù hợp hơn

### Context Guidance

The system is a Vietnamese stock trading chatbot with:
- Frontend: Next.js React application
- Backend: FastAPI with PostgreSQL
- AI: OpenAI GPT-4o-mini for natural language responses
- Features: Stock price queries, technical analysis, price predictions

Current issues identified:
1. AI không bắt tốt ngữ cảnh để cho phản hồi tốt nhất
2. History được truyền vào model nhưng không có hướng dẫn cụ thể để model sử dụng
3. Không có entity extraction từ các tin nhắn trước
4. Context passed to model là hạn chế

### Session Setup

This session will focus on brainstorming improvements for the AI's context understanding capability. We will explore techniques to:
- Better utilize conversation history
- Extract and persist entities (like stock symbols) across messages
- Improve system prompt instructions for context usage
- Build better context windows for more relevant responses

### SCAMPER Technique Execution

**Selected Approach:** Progressive Flow - kết hợp nhiều kỹ thuật

**SCAMPER - SUBSTITUTE Layer:**
- Thay đổi cách truyền context vào LLM
- Kết hợp nhiều phương pháp: metadata, vector search, summary

**Key Ideas Generated:**

**[Category #1]**: Multi-Layer Context System
_Concept_: Kết hợp metadata (vai trò, timestamp), vector embedding (tìm kiếm ngữ nghĩa), và summary tự động (tóm tắt lịch sử dài) để tạo ra hệ thống context thông minh
_Novelty_: Thay vì chỉ truyền raw text, hệ thống sẽ có 3 lớp context: superficial (metadata), semantic (embedding), và deep (summary)

**[Category #2]**: Multi-Layer Context Architecture
_Concept_: Thiết kế kiến trúc context gồm 3 lớp: Layer 1 - Metadata (intent, entities, sentiment), Layer 2 - Vector Database (semantic search với embeddings), Layer 3 - Smart Summary (tự động tóm tắt lịch sử). Hệ thống sẽ kết hợp tất cả các lớp để tạo ra context giàu thông tin nhất cho AI
_Novelty_: Thay vì chỉ truyền raw text, kiến trúc này có khả năng hiểu ngữ cảnh theo nhiều chiều: trực tiếp (metadata), ngữ nghĩa (vector), và tổng quan (summary)

**[Category #3]**: Comprehensive Context Intelligence Engine
_Concept_: Một hệ thống xử lý ngữ cảnh tích hợp đầy đủ bao gồm: Intent Classification (6+ intents), Entity Extraction (mã cổ phiếu, giá, ngày), Vector Database (semantic + keyword hybrid search), và Smart Summary. Hệ thống này sẽ hiểu rõ người dùng đang hỏi gì, về đâu, khi nào, và mối liên hệ với các câu hỏi trước
_Novelty_: Thay vì chỉ là chatbot trả lời theo từng câu, đây là một "Context Intelligence Engine" có khả năng hiểu sâu về người dùng và ngữ cảnh giao dịch chứng khoán
