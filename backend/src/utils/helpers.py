"""Helper utilities for the stock chatbot application."""

from __future__ import annotations

import re
from typing import Any


def extract_tickers(text: str, allowed: set[str] | None = None) -> list[str]:
    """Extract stock tickers from text (3-5 uppercase letters)."""
    if allowed is None:
        allowed = {
            "fpt", "vnm", "msn", "vic", "vpb", "vcb", "mb", "hdb", "stc", "dig",
            "hpg", "kdh", "ssi", "vci", "shb", "tpb", "vgr", "vds", "vgs", "vic",
            "vng", "vrs", "vsh", "vst", "vtc", "vtk", "vtr", "vtx", "vty"
        }
    
    return list(dict.fromkeys(
        m.upper() for m in re.findall(r"\b([A-Z]{3,5})\b", text.upper())
        if m.lower() in allowed
    ))


def extract_prices(text: str) -> list[str]:
    """Extract price mentions from text."""
    pattern = r"\b(\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?)\s*(đ|vnd|usd)?\b"
    return [
        f"{m[0].replace('.', '').replace(',', '.')} {m[1]}".strip()
        for m in re.findall(pattern, text.lower())
    ]


def classify_intent(text: str) -> dict[str, Any]:
    """Classify user query intent based on keywords."""
    text_lower = text.lower()
    intents = {
        "price": ["giá", "bao nhiêu", "price"],
        "analysis": ["phân tích", "kỹ thuật", "biểu đồ", "MACD", "RSI"],
        "prediction": ["dự đoán", "dự báo", "sẽ", "tới"],
        "general": ["xin chào", "giới thiệu", "bạn là gì"],
    }
    
    scores = {}
    for intent, keywords in intents.items():
        matches = [k for k in keywords if k in text_lower]
        if matches:
            scores[intent] = len(matches) / len(keywords)
    
    if not scores:
        return {"name": "unknown", "confidence": 0.0}
    
    best = max(scores.items(), key=lambda x: x[1])
    return {"name": best[0], "confidence": best[1]}


def analyze_sentiment(text: str) -> dict[str, Any]:
    """Analyze sentiment of Vietnamese text."""
    text_lower = text.lower()
    positive = {"tốt", "lợi nhuận", "tăng", "tích cực", "phát triển", "mua"}
    negative = {"xấu", "lỗ", "giảm sâu", "tiêu cực", "rủi ro", "thua lỗ"}
    
    pos_count = sum(1 for w in positive if w in text_lower)
    neg_count = sum(1 for w in negative if w in text_lower)
    total = pos_count + neg_count
    
    if total == 0:
        return {"sentiment": "neutral", "score": 0.0}
    
    score = (pos_count - neg_count) / total
    return {"sentiment": "positive" if score > 0 else "negative", "score": round(score, 2)}


def summarize_history(messages: list[dict[str, str]], max_items: int = 5) -> str:
    """Summarize conversation history."""
    user_queries = [m["content"][:150] for m in messages[-max_items:] if m.get("role") == "user"]
    if not user_queries:
        return ""
    
    return f"Previous {len(user_queries)} questions:\n" + "\n".join(f"- {q}" for q in user_queries)


def build_context(
    query: str,
    history: list[dict[str, str]] | None = None,
    include_summary: bool = True
) -> dict[str, Any]:
    """Build comprehensive context from query and history."""
    return {
        "intent": classify_intent(query),
        "entities": {
            "tickers": extract_tickers(query),
            "prices": extract_prices(query),
            "dates": [],
        },
        "sentiment": analyze_sentiment(query),
        "summary": summarize_history(history or []) if include_summary else "",
    }


def format_context_for_llm(query: str, history: list[dict[str, str]] | None = None) -> str:
    """Format context as structured text for LLM."""
    ctx = build_context(query, history)
    
    parts = ["# CONTEXT", f"INTENT: {ctx['intent']['name']} (confidence: {ctx['intent']['confidence']:.2f})"]
    
    entities = ctx["entities"]
    if entities["tickers"]:
        parts.append(f"STOCKS: {', '.join(entities['tickers'])}")
    if entities["prices"]:
        parts.append(f"PRICES: {', '.join(entities['prices'])}")
    
    parts.append(f"SENTIMENT: {ctx['sentiment']['sentiment']} (score: {ctx['sentiment']['score']})")
    
    if ctx["summary"]:
        parts.append(f"\n# HISTORY SUMMARY\n{ctx['summary']}")
    
    return "\n".join(parts)