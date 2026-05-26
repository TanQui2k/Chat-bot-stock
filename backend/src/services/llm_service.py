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
        Vietnamese stock-market chat answer with optional recent history and grounding context.
        Returns None if OpenAI is not configured or the API call fails.
        """
        if not self._client:
            logger.warning("OpenAI client not initialized. Cannot answer question.")
            return None

        system = """# Vai trò
Bạn là trợ lý AI chuyên hỗ trợ phân tích và dự báo chứng khoán Việt Nam.

# Phạm vi
- Chỉ trả lời các câu hỏi liên quan đến cổ phiếu, dữ liệu thị trường, phân tích kỹ thuật, xu hướng giá và dự báo.
- Nếu câu hỏi ngoài phạm vi, hãy từ chối lịch sự và hướng người dùng quay lại chủ đề chứng khoán.
- Không bịa dữ liệu. Nếu thiếu dữ liệu hoặc không chắc chắn, hãy nói rõ.
- Nếu có CONTEXT, ưu tiên trả lời dựa trên CONTEXT đó.

# Giọng văn
- Luôn trả lời bằng tiếng Việt có dấu.
- Ngắn gọn, tự nhiên, dễ hiểu.
- Không đưa lời khuyên đầu tư chắc chắn kiểu cam kết lợi nhuận.
- Có thể dùng gạch đầu dòng khi câu trả lời cần nhiều ý.

# Xưng hô
- Nếu người dùng tự xưng "mình", "tớ", "bé", "cháu", hãy xưng "mình" và gọi người dùng là "bạn".
- Nếu người dùng tự xưng "tôi", "anh", "chị" hoặc không có đại từ rõ ràng, hãy xưng "em" và gọi người dùng là "anh/chị".
- Không suy đoán giới tính từ tên riêng."""

        context_parts = []
        if structured_context:
            context_parts.append(structured_context)

        if context:
            plain_ctx = "\n".join([f"- {x}" for x in context])
            if plain_ctx:
                context_parts.append(f"PLAIN CONTEXT:\n{plain_ctx}")

        user = f"CÂU HỎI:\n{question}\n"
        if context_parts:
            user += f"\nCONTEXT:\n" + "\n\n".join(context_parts) + "\n"
        user += "\nLuôn trả lời bằng tiếng Việt có dấu, ngắn gọn và tự nhiên."

        messages: list[dict[str, str]] = [{"role": "system", "content": system}]
        if history:
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
        """Generate a natural Vietnamese answer grounded on provided price data."""
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
