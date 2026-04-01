"""
Predict API Endpoint — Prophet Stock Prediction
Supports multi-day forecasting with confidence intervals.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from src.api.dependencies import get_db
from src.ml.prophet_service import ProphetService

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================
# Request / Response Schemas
# ============================================================
class PredictionRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol", examples=["KBC"])
    days: int = Field(default=10, ge=1, le=30, description="Number of trading days to forecast")


class SinglePrediction(BaseModel):
    date: str
    predicted_close: float
    lower_bound: float
    upper_bound: float
    trend: str  # "UP" or "DOWN"


class HistoryPoint(BaseModel):
    date: str
    close: Optional[float] = None


class ModelMetrics(BaseModel):
    mae: Optional[float] = None
    rmse: Optional[float] = None
    mape: Optional[float] = None


class ProphetPredictionResponse(BaseModel):
    symbol: str
    version: str
    trained_at: str
    metrics: ModelMetrics
    predictions: list[SinglePrediction]
    history: list[HistoryPoint]


# ============================================================
# Endpoints
# ============================================================
@router.post("/", response_model=ProphetPredictionResponse)
async def predict_stock(request: PredictionRequest, db: Session = Depends(get_db)):
    """
    Predict stock price for the next N trading days using Prophet.

    - Auto-trains the model if no trained model exists (lazy training)
    - Returns predictions with confidence intervals + recent history for charting
    """
    try:
        result = ProphetService.predict(
            db=db,
            symbol=request.ticker,
            days=request.days,
            auto_train=True,
        )
        return ProphetPredictionResponse(**result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Prediction error for {request.ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@router.post("/train")
async def train_model(request: PredictionRequest, db: Session = Depends(get_db)):
    """
    Manually trigger model training for a specific ticker.
    Useful for refreshing models after new data is scraped.
    """
    try:
        metadata = ProphetService.train_model(db=db, symbol=request.ticker)
        return {
            "message": f"Model trained successfully for {request.ticker.upper()}",
            "metadata": metadata,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Training error for {request.ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Training failed: {str(e)}",
        )
