from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import stocks, chat, predict, assistant

app = FastAPI(
    title="StockAI Predictor API",
    description="API for StockAI Predictor Application",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://0.0.0.0:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stocks.router, prefix="/api")
app.include_router(predict.router, prefix="/api/predict", tags=["Prediction"])
app.include_router(chat.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to StockAI API"}
