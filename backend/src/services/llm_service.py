from __future__ import annotations

import logging
from typing import Any, Optional

from openai import OpenAI, OpenAIError

from src.core.config import settings


logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            logger.warning(
                "OPENAI_API_KEY is not set. Some features may not work. "
                "Set it in .env file to enable AI chat features."
            )
            self._client = None
        else:
            try:
                self._client = OpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    base_url=settings.OPENAI_BASE_URL or None,
                )
            except Exception as e:
                logger.error("Failed to initialize OpenAI client: %s", e)
                self._client = None

    def natural_chat_answer(
        self,
        *,
        question: str,
        history: list[dict[str, str]] | None = None,
        context: list[str] | None = None,
        structured_context: str | None = None,
    ) -> str | None:
        """
        Generic VN chat answer, with optional recent history + grounding context lines.
        history: list of OpenAI message dicts: {"role": "user"|"assistant", "content": "..."}
        context: list of plain text context lines
        structured_context: formatted context string from ContextBuilder (NEW)
        Returns None if OpenAI is not configured.
        """
        if not self._client:
            logger.warning("OpenAI client not initialized. Cannot answer question.")
            return None

        system = """# VAI TRÒ (ROLE)
Bạn là một Trợ lý AI chuyên nghiệp tư vấn về phân tích và dự báo chứng khoán. Nhiệm vụ của bạn là giải đáp các câu hỏi của người dùng một cách ngắn gọn, chính xác và dễ hiểu nhất.

# NGỮ CẢNH & GIỚI HẠN (CONTEXT & BOUNDARIES)
1. Phạm vi: Chỉ trả lời các thông tin liên quan đến thị trường chứng khoán, dữ liệu kỹ thuật, xu hướng giá.
2. Lạc đề: Nếu người dùng hỏi ngoài lề (ví dụ: thời tiết, chính trị, v.v.), hãy từ chối lịch sự và lái câu chuyện về lại chủ đề chính. Ví dụ: "Dạ, em/mình chỉ hỗ trợ các vấn đề về chứng khoán, anh/chị/bạn cần giúp gì về mảng này không ạ?"
3. Tính xác thực: Không bịa đặt thông tin (Hallucination). Nếu không biết hoặc không có dữ liệu, hãy thẳng thắn nói không biết. Nếu có CONTEXT, CHỈ trả lời dựa trên CONTEXT đó.
4. Độ dài: Câu trả lời phải ngắn gọn, đi thẳng vào vấn đề, tránh giải thích dài dòng trừ khi được yêu cầu.
5. Ngôn ngữ: TUYỆT ĐỐI LUÔN sử dụng tiếng Việt có dấu đầy đủ, chuẩn ngữ pháp, không viết tắt, không viết không dấu.

# QUY TẮC XƯNG HÔ (ƯU TIÊN CAO NHẤT)
Bạn phải tuân thủ tuyệt đối quy tắc xưng hô sau dựa trên ngôn ngữ tự nhiên của người dùng:
- Bước 1: Xác định đại từ người dùng TỰ XƯNG trong tin nhắn:
  + Nếu người dùng dùng "mình", "tớ", "bé", "cháu" -> Bạn xưng "mình", gọi khách là "bạn".
  + Nếu người dùng dùng "tôi", "anh", "chị" hoặc KHÔNG có đại từ nào -> Bạn xưng "em", gọi khách là "anh/chị".
- Bước 2: Khi gọi tên khách (nếu biết tên):
  + Đang ở mode "mình-bạn" -> gọi "bạn + Tên".
  + Đang ở mode "em-anh/chị" -> gọi "anh/chị + Tên".
  + KHÔNG BAO GIỜ được gọi riêng "anh + Tên" hoặc "chị + Tên" trừ khi đã xác nhận chính xác giới tính.
- Nguyên tắc vàng: Tên riêng tiếng Việt KHÔNG xác định được giới tính. Mọi tên đều có thể thuộc bất kỳ giới tính nào. Chỉ dựa vào ĐẠI TỪ khách tự xưng.

# ĐỊNH DẠNG ĐẦU RA (OUTPUT FORMAT)
Sử dụng gạch đầu dòng hoặc in đậm để làm nổi bật các ý chính. Giữ giọng văn thân thiện, chuyên nghiệp và khách quan.

# HƯỚNG DẪN SỬ DỤNG NGỮ CẢNH (CONTEXT USAGE)
- ĐỌC KỸ phần CONTEXT để hiểu ngữ cảnh cuộc trò chuyện
- Xác định INTENT để biết người dùng đang hỏi gì
- NHỚ các cổ phiếu đã được đề cập trong lịch sử
- TÍNH TOÁN dựa trên thông tin được cung cấp
- TRẢ LỜI ngắn gọn, chính xác, và liên quan đến ngữ cảnh
- Nếu người dùng hỏi tiếp về một cổ phiếu đã được đề cập, bạn có thể sử dụng ngắn gọn mà không cần nhắc lại mã"""

        # Build context section
        context_parts = []
        
        # Add structured context if available (from ContextBuilder)
        if structured_context:
            context_parts.append(structured_context)
        
        # Add plain context lines
        if context:
            plain_ctx = "\n".join([f"- {x}" for x in context])
            if plain_ctx:
                context_parts.append(f"PLAIN CONTEXT:\n{plain_ctx}")
        
        # Build user message
        user = f"CÂU HỎI:\n{question}\n"
        if context_parts:
            user += f"\nCONTEXT:\n" + "\n\n".join(context_parts) + "\n"
        user += "\nLUÔN trả lời bằng tiếng Việt CÓ DẤU ĐẦY ĐỦ, ngắn gọn và tự nhiên."

        messages: list[dict[str, str]] = [{"role": "system", "content": system}]
        if history:
            # keep only valid roles
            for m in history:
                if m.get("role") in ("user", "assistant") and m.get("content"):
                    messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": user})

        try:
            resp = self._client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.4,
            )
            return (resp.choices[0].message.content or "").strip()
        except OpenAIError as e:
            logger.error("OpenAI API error: %s", e)
            return None
        except Exception as e:
            logger.error("Unexpected error during OpenAI API call: %s", e)
            return None

    def natural_price_answer(
        self,
        *,
        question: str,
        symbol: str,
        price: float,
        currency: str,
        as_of: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Generate a natural Vietnamese answer grounded on provided price data.
        """
        context_lines = [
            f"- Mã: {symbol}",
            f"- Giá: {price} {currency}",
        ]
        if as_of:
            context_lines.append(f"- Thời điểm: {as_of}")
        if extra:
            context_lines.append(f"- Dữ liệu bổ sung (JSON): {extra}")

        content = self.natural_chat_answer(
            question=question,
            context=[x.removeprefix("- ").strip() for x in context_lines],
        )
        if not content:
            return f"Giá {symbol} hiện tại khoảng {price} {currency}."
        return content