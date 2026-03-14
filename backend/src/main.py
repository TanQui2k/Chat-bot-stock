from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import stocks, chat, predict
from src.core.config import settings

app = FastAPI(
    title="StockAI Predictor API",
    description="API for StockAI Predictor Application",
    version="1.0.0"
)

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(predict.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to StockAI Predictor API"}
