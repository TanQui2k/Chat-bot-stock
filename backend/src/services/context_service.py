"""
Context Service - Multi-layer context for AI chatbot
Simplified and optimized version
"""

from __future__ import annotations

import re
from typing import Any


class ContextService:
    """Simplified context builder with intent, entities, and sentiment analysis."""
    
    # Stock tickers - Vietnamese VN30 and popular stocks
    VN_STOCKS = {
        "fpt", "vnm", "msn", "vic", "vpb", "vcb", "mb", "hdb", "stc", "dig",
        "hpg", "kdh", "ssi", "vci", "shb", "tpb", "vgr", "vds", "vgs", "vic",
        "vng", "vrs", "vsh", "vst", "vtc", "vtk", "vtr", "vtx", "vty"
    }
    
    # Intent keywords
    INTENTS = {
        "price": ["giá", "bao nhiêu", "price", "giá hiện tại"],
        "analysis": ["phân tích", "kỹ thuật", "biểu đồ", "MACD", "RSI", "MA"],
        "prediction": ["dự đoán", "dự báo", "sẽ", "tới", "24h"],
        "general": ["xin chào", "giới thiệu", "bạn là gì"],
    }
    
    # Sentiment words
    POSITIVE = {"tốt", "lợi nhuận", "tăng", "tích cực", "phát triển", "mua"}
    NEGATIVE = {"xấu", "lỗ", "giảm sâu", "tiêu cực", "rủi ro", "thua lỗ"}
    
    def __init__(self):
        self._last_context: dict[str, Any] = {}
    
    def build_context(self, query: str, history: list[dict[str, str]] | None = None) -> dict[str, Any]:
        """Build comprehensive context from query and history."""
        return {
            "intent": self._classify_intent(query),
            "entities": self._extract_entities(query),
            "sentiment": self._analyze_sentiment(query),
            "summary": self._summarize_history(history) if history else "",
        }
    
    def format_for_llm(self, query: str, history: list[dict[str, str]] | None = None) -> str:
        """Format context for LLM as structured text."""
        ctx = self.build_context(query, history)
        
        parts = ["# CONTEXT"]
        
        # Intent
        parts.append(f"INTENT: {ctx['intent']['name']} (confidence: {ctx['intent']['confidence']:.2f})")
        
        # Entities
        if ctx["entities"]["tickers"]:
            parts.append(f"STOCKS: {', '.join(ctx['entities']['tickers'])}")
        if ctx["entities"]["prices"]:
            parts.append(f"PRICES: {', '.join(ctx['entities']['prices'])}")
        if ctx["entities"]["dates"]:
            parts.append(f"DATES: {', '.join(ctx['entities']['dates'])}")
        
        # Sentiment
        parts.append(f"SENTIMENT: {ctx['sentiment']['sentiment']} (score: {ctx['sentiment']['score']})")
        
        # History summary
        if ctx["summary"]:
            parts.append(f"\n# HISTORY SUMMARY\n{ctx['summary']}")
        
        return "\n".join(parts)
    
    def _classify_intent(self, text: str) -> dict[str, Any]:
        """Classify user query intent."""
        text_lower = text.lower()
        scores = {}
        
        for intent, keywords in self.INTENTS.items():
            matches = [k for k in keywords if k in text_lower]
            if matches:
                scores[intent] = len(matches) / len(keywords)
        
        if not scores:
            return {"name": "unknown", "confidence": 0.0}
        
        best = max(scores.items(), key=lambda x: x[1])
        return {"name": best[0], "confidence": best[1]}
    
    def _extract_entities(self, text: str) -> dict[str, list[str]]:
        """Extract stocks, prices, dates from text."""
        tickers = []
        
        # Extract tickers (3-5 uppercase letters)
        for match in re.findall(r"\b([A-Z]{3,5})\b", text.upper()):
            if match.lower() in self.VN_STOCKS and match not in tickers:
                tickers.append(match)
        
        # Extract prices
        price_pattern = r"\b(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?)\s*(đ|vnd|usd)?\b"
        prices = [f"{m[0].replace('.', '').replace(',', '.')} {m[1]}".strip() 
                  for m in re.findall(price_pattern, text.lower())]
        
        # Extract dates
        date_patterns = [
            r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})\b",
            r"\b(hôm nay|hôm qua|ngày mai)\b",
            r"\b(tháng này|tháng trước)\b",
            r"\b(tuần này|tuần trước)\b",
        ]
        dates = []
        for p in date_patterns:
            dates.extend(re.findall(p, text.lower()))
        
        return {"tickers": tickers, "prices": list(dict.fromkeys(prices)), "dates": list(dict.fromkeys(dates))}
    
    def _analyze_sentiment(self, text: str) -> dict[str, Any]:
        """Analyze sentiment of text."""
        text_lower = text.lower()
        pos_count = sum(1 for w in self.POSITIVE if w in text_lower)
        neg_count = sum(1 for w in self.NEGATIVE if w in text_lower)
        total = pos_count + neg_count
        
        if total == 0:
            return {"sentiment": "neutral", "score": 0.0}
        
        score = (pos_count - neg_count) / total
        sentiment = "positive" if score > 0 else "negative"
        
        return {"sentiment": sentiment, "score": round(score, 2)}
    
    def _summarize_history(self, history: list[dict[str, str]]) -> str:
        """Summarize conversation history."""
        user_queries = [m["content"][:150] for m in history[-5:] if m.get("role") == "user"]
        if not user_queries:
            return ""
        
        return f"Previous {len(user_queries)} questions:\n" + "\n".join(f"- {q}" for q in user_queries)


# Singleton instance
context_service = ContextService()