from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.api.dependencies import get_db
import random

router = APIRouter(prefix="/predict", tags=["prediction"])

class PredictRequest(BaseModel):
    ticker: str

class PredictResponse(BaseModel):
    ticker: str
    prediction: str
    probability: float

@router.post("", response_model=PredictResponse)
def predict_stock(request: PredictRequest, db: Session = Depends(get_db)):
    # Mock return logic based on frontend lib/api.ts expectations
    prediction = random.choice(["Tăng giá", "Giảm giá", "Đi ngang"])
    probability = round(random.uniform(0.5, 0.99), 2)
    return PredictResponse(
        ticker=request.ticker.upper(),
        prediction=prediction,
        probability=probability
    )
