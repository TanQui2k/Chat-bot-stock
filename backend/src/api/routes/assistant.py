from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException

from src.schemas.assistant_schema import AskPriceRequest, AskPriceResponse
from src.services.llm_service import LLMService
from src.services.vnstock_service import VnStockPriceService


router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/price", response_model=AskPriceResponse)
def ask_price(payload: AskPriceRequest) -> AskPriceResponse:
    symbol = (payload.symbol or _extract_symbol(payload.question) or "").upper().strip()
    if not symbol:
        raise HTTPException(status_code=400, detail="Không tìm thấy mã cổ phiếu. Ví dụ: 'Giá FPT bao nhiêu?'")

    try:
        price_info = VnStockPriceService().get_latest_price(symbol)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Lỗi lấy giá từ vnstock: {e}") from e

    try:
        answer = LLMService().natural_price_answer(
            question=payload.question,
            symbol=price_info.symbol,
            price=price_info.price,
            currency=price_info.currency,
            as_of=price_info.as_of,
        )
    except Exception as e:
        # Fallback if OpenAI is down/missing key
        answer = f"Giá {price_info.symbol} hiện tại khoảng {price_info.price} {price_info.currency}."

    return AskPriceResponse(
        symbol=price_info.symbol,
        price=price_info.price,
        currency=price_info.currency,
        as_of=price_info.as_of,
        answer=answer,
    )


_TICKER_RE = re.compile(r"\b([A-Za-z]{3,5})\b")


def _extract_symbol(text: str) -> str | None:
    """
    Best-effort ticker extraction: match 3-5 letters (e.g., FPT, VCB, SSI).
    """
    m = _TICKER_RE.search(text or "")
    if not m:
        return None
    return m.group(1)

