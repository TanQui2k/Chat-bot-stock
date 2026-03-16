from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AskPriceRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User question, e.g. 'Giá FPT hôm nay bao nhiêu?'")
    symbol: Optional[str] = Field(None, description="Optional ticker override, e.g. 'FPT'")


class AskPriceResponse(BaseModel):
    symbol: str
    price: float
    currency: str
    as_of: Optional[str] = None
    answer: str

