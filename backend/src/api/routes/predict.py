"""
Predict API Endpoint — Prophet Stock Prediction
Supports multi-day forecasting with confidence intervals.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from src.api.dependencies import get_db
from src.ml.prophet_service import ProphetService

logger = logging.getLogger(__name__)

router = APIRouter()


def _status_for_prediction_error(message: str) -> int:
    lowered = message.lower()
    if "not found" in lowered:
        return status.HTTP_404_NOT_FOUND
    if "not enough" in lowered or "train first" in lowered:
        return status.HTTP_422_UNPROCESSABLE_ENTITY
    return status.HTTP_500_INTERNAL_SERVER_ERROR


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


def _run_prediction(ticker: str, days: int, db: Session) -> ProphetPredictionResponse:
    try:
        result = ProphetService.predict(
            db=db,
            symbol=ticker,
            days=days,
            auto_train=True,
        )
        return ProphetPredictionResponse(**result)

    except ValueError as e:
        detail = str(e)
        status_code = _status_for_prediction_error(detail)
        if status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            logger.error(f"Unexpected prediction value error for {ticker}: {detail}", exc_info=True)
        raise HTTPException(
            status_code=status_code,
            detail=detail if status_code != status.HTTP_500_INTERNAL_SERVER_ERROR else f"Prediction failed: {detail}",
        )
    except Exception as e:
        logger.error(f"Prediction error for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


# ============================================================
# Endpoints
# ============================================================
@router.get("/")
async def predict_stock_get(
    ticker: Optional[str] = Query(default=None, description="Stock ticker symbol"),
    days: int = Query(default=10, ge=1, le=30, description="Number of trading days to forecast"),
    db: Session = Depends(get_db),
):
    """
    Compatibility GET endpoint.

    - `GET /api/predict/?ticker=FPT&days=10` returns a prediction response
    - `GET /api/predict/` returns usage instructions instead of 405
    """
    if not ticker:
        return {
            "message": "Prediction endpoint is available.",
            "usage": {
                "get": "/api/predict/?ticker=FPT&days=10",
                "get_by_symbol": "/api/predict/FPT?days=10",
                "post": {
                    "path": "/api/predict/",
                    "body": {"ticker": "FPT", "days": 10},
                },
            },
        }

    return _run_prediction(ticker=ticker, days=days, db=db)


@router.get("/{ticker}", response_model=ProphetPredictionResponse)
async def predict_stock_by_symbol(
    ticker: str,
    days: int = Query(default=10, ge=1, le=30, description="Number of trading days to forecast"),
    db: Session = Depends(get_db),
):
    """Compatibility GET endpoint for legacy clients using `/api/predict/{ticker}`."""
    return _run_prediction(ticker=ticker, days=days, db=db)


@router.post("/", response_model=ProphetPredictionResponse)
async def predict_stock(request: PredictionRequest, db: Session = Depends(get_db)):
    """
    Predict stock price for the next N trading days using Prophet.

    - Auto-trains the model if no trained model exists (lazy training)
    - Returns predictions with confidence intervals + recent history for charting
    """
    return _run_prediction(ticker=request.ticker, days=request.days, db=db)


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
