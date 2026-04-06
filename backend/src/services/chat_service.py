from typing import List, Dict, Optional
from src.services.llm_service import LLMService
from src.services.vnstock_service import VnStockPriceService
from src.utils.helpers import extract_tickers, format_context_for_llm
import re

class ChatService:
    def __init__(self):
        self.llm_service = LLMService()
        self.vnstock_service = VnStockPriceService()
        self._price_kw = re.compile(r"(giá|bao\s*nhiêu|price)", re.IGNORECASE)

    def route_intent(self, user_text: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Main routing logic for chat interactions.
        """
        # 1. Build structured context
        structured_context = format_context_for_llm(user_text, history)
        
        # 2. Extract potential tickers
        tickers = extract_tickers(user_text)

        # 3. Handle Price Intent
        if self._is_price_intent(user_text):
            return self._handle_price_intent(user_text, tickers, history, structured_context)
            
        # 4. Fallback: Natural chat via LLM
        return self._handle_natural_chat(user_text, history, structured_context)

    def _is_price_intent(self, user_text: str) -> bool:
        return bool(self._price_kw.search(user_text))

    def _handle_price_intent(
        self, 
        user_text: str, 
        tickers: List[str], 
        history: Optional[List[Dict[str, str]]] = None,
        structured_context: Optional[str] = None
    ) -> str:
        """Handle specific requests for stock prices."""
        if not tickers:
            return "Bạn cho mình xin mã cổ phiếu (VD: FPT, VCB) để mình báo giá nhé."

        symbol = tickers[0] # Handle the first found ticker
        
        try:
            price_info = self.vnstock_service.get_latest_price(symbol)
            
            # Combine real-time data with general context
            price_context = [
                f"Mã: {price_info.symbol}",
                f"Giá hiện tại được ghi nhận: {price_info.price} {price_info.currency}",
                *( [f"Thời điểm ghi nhận: {price_info.as_of}"] if price_info.as_of else [] ),
            ]
            
            full_context = price_context + [structured_context] if structured_context else price_context
            
            # Ask LLM to format the final answer naturally
            return self._handle_natural_chat(user_text, history, full_context)
            
        except Exception as e:
            # Fallback if service fails but we know they asked for price
            return f"Hiện tại mình không lấy được giá chuẩn của {symbol}. Bạn thử lại sau nhé."

    def _handle_natural_chat(
        self, 
        user_text: str, 
        history: Optional[List[Dict[str, str]]] = None,
        context: Optional[List[str]] = None
    ) -> str:
        """Pass message to LLM for natural conversation."""
        try:
            # Type safety: LLMService expects structured_context as str, context as list[str]
            kwargs = {
                "question": user_text,
                "history": history
            }
            
            if isinstance(context, list):
                kwargs["context"] = context
            elif isinstance(context, str):
                kwargs["structured_context"] = context
            elif context is not None:
                kwargs["structured_context"] = str(context)

            ans = self.llm_service.natural_chat_answer(**kwargs)
            return ans or "Mình đã nhận câu hỏi của bạn. Bạn có thể hỏi theo dạng: 'Giá FPT bao nhiêu?'."
        except Exception:
            return "Xin lỗi, hiện tại hệ thống AI đang bảo trì. Bạn có thể hỏi giá trực tiếp ví dụ: 'Giá FPT là bao nhiêu?'"
