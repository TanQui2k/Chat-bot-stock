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
    ) -> str | None:
        """
        Generic VN chat answer, with optional recent history + grounding context lines.
        history: list of OpenAI message dicts: {"role": "user"|"assistant", "content": "..."}
        Returns None if OpenAI is not configured.
        """
        if not self._client:
            logger.warning("OpenAI client not initialized. Cannot answer question.")
            return None

        system = (
            "Bạn là trợ lý chứng khoán Việt Nam. "
            "Nếu người dùng hỏi dữ liệu/giá cụ thể, chỉ trả lời khi có dữ liệu trong CONTEXT; "
            "nếu không có, hãy hỏi lại hoặc nói rõ giới hạn."
        )

        ctx = "\n".join([f"- {x}" for x in (context or [])]).strip()
        user = f"CÂU HỎI:\n{question}\n"
        if ctx:
            user += f"\nCONTEXT:\n{ctx}\n"
        user += "\nTrả lời tự nhiên, ngắn gọn bằng tiếng Việt."

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

