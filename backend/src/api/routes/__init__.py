# API Routes Package
from src.api.routes.anomaly import router as anomaly_router
from src.api.routes.stocks import router as stocks_router
from src.api.routes.predict import router as predict_router
from src.api.routes.chat import router as chat_router
from src.api.routes.auth import router as auth_router
from src.api.routes.assistant import router as assistant_router

__all__ = [
    'anomaly_router',
    'stocks_router', 
    'predict_router',
    'chat_router',
    'auth_router',
    'assistant_router'
]