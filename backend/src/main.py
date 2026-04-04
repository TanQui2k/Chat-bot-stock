from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import stocks, chat, predict, assistant, auth, anomaly
from src.middleware.rate_limiter import RateLimitMiddleware

app = FastAPI(
    title="StockAI Predictor API",
    description="API for StockAI Predictor Application",
    version="1.0.0"
)

# ==========================================
# Middleware Stack (order matters: last added = first executed)
# ==========================================

# 1. CORS — Chỉ cho phép origins đã biết, không dùng wildcard cho credentials
import os

# Production: đọc từ biến môi trường ALLOWED_ORIGINS (comma-separated)
# Development: cho phép localhost
_default_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
_env_origins = os.environ.get("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in _env_origins.split(",") if o.strip()] if _env_origins else _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],  # Chỉ định rõ thay vì wildcard
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],  # Chỉ các header cần thiết
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],  # Cho phép frontend đọc rate limit headers
    max_age=600,  # Cache preflight requests 10 phút
)

# 2. Rate Limiter — Bảo vệ endpoints nhạy cảm (OTP, login)
app.add_middleware(RateLimitMiddleware)

# ==========================================
# Routes
# ==========================================
app.include_router(stocks.router, prefix="/api")
app.include_router(predict.router, prefix="/api/predict", tags=["Prediction"])
app.include_router(chat.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(anomaly.router, prefix="/api", tags=["Anomaly Detection"])

@app.get("/")
def read_root():
    return {"message": "Welcome to StockAI API"}
