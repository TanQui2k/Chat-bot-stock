"""Top-level API router.

Feature routers stay independent while this module owns the public ``/api``
layout. Adding a new feature should require one include here and no changes to
the application bootstrap.
"""

from fastapi import APIRouter

from src.api.routes import anomaly, assistant, auth, chat, predict, stocks


api_router = APIRouter()
api_router.include_router(stocks.router)
api_router.include_router(predict.router, prefix="/predict", tags=["Prediction"])
api_router.include_router(chat.router)
api_router.include_router(assistant.router)
api_router.include_router(auth.router)
api_router.include_router(anomaly.router, tags=["Anomaly Detection"])
