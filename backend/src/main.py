import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from src.api.routes import anomaly, assistant, auth, chat, predict, stocks
from src.middleware.rate_limiter import RateLimitMiddleware

logger = logging.getLogger(__name__)

app = FastAPI(
    title="StockAI Predictor API",
    description="API for StockAI Predictor Application",
    version="1.0.0",
)

# ==========================================
# Middleware Stack
# ==========================================

# 1. Rate limiter protects selected sensitive endpoints.
app.add_middleware(RateLimitMiddleware)

# 2. CORS stays outermost so even error responses keep CORS headers.
_default_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
_env_origins = os.environ.get("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [o.strip() for o in _env_origins.split(",") if o.strip()] if _env_origins else _default_origins
LOCAL_DEV_ORIGIN_REGEX = (
    r"^https?://("
    r"localhost|127\.0\.0\.1|"
    r"192\.168\.\d{1,3}\.\d{1,3}|"
    r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
    r"172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}"
    r"):3000$"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=None if _env_origins else LOCAL_DEV_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    max_age=600,
)


@app.exception_handler(OperationalError)
async def operational_error_handler(request: Request, exc: OperationalError):
    logger.exception("Database operation failed for %s", request.url.path, exc_info=exc)
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database connection failed. Check PostgreSQL credentials in backend/.env.",
            "error_code": "database_unavailable",
        },
    )


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
