import os
import joblib
import pandas as pd
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.crud import crud_stock
from src.api.dependencies import get_db
from src.schemas.stock_schema import PredictionResponse

router = APIRouter()

# 1. Global Model Loading (loads once at server startup)
MODEL_PATH = os.path.join("src", "ml", "saved_models", "lightweight_model.pkl")

try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load model from {MODEL_PATH}. Error: {e}")
    model = None


class PredictionRequest(BaseModel):
    ticker: str


@router.post("/", response_model=PredictionResponse)
async def predict_stock_trend(request: PredictionRequest, db: Session = Depends(get_db)):
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Machine learning model is not loaded gracefully on the server."
        )

    formatted_symbol = request.ticker.upper()
    ticker = await crud_stock.get_ticker_by_symbol(db, symbol=formatted_symbol)
    
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker '{formatted_symbol}' not found in the database."
        )

    # 2. Fetch the latest 20 days of historical prices
    prices = await crud_stock.get_historical_prices(db, ticker_id=ticker.id, limit=20)
    
    # 3. Error Handling if data is insufficient
    # SMA_10 requires a minimum of 10 days, and pct_change needs 1 extra. Total = 11 days.
    if len(prices) < 11:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough historical data for {formatted_symbol}. Need at least 11 records to calculate features, found {len(prices)}."
        )

    # Convert to Pandas DataFrame
    data = [{
        'Date': p.date,
        'Close': p.close
    } for p in prices]
    
    df = pd.DataFrame(data)
    df.sort_values(by='Date', inplace=True)
    df.set_index('Date', inplace=True)

    # 4. Same Feature Engineering as ML Training Script
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['Daily_Return'] = df['Close'].pct_change()
    df.dropna(inplace=True)

    # Pass the last row to the model
    latest_features = df.iloc[-1]
    last_close_price = latest_features['Close']
    
    # Structure matching exactly the training phase: ['Close', 'SMA_10', 'Daily_Return']
    X_latest = pd.DataFrame([{
        'Close': latest_features['Close'],
        'SMA_10': latest_features['SMA_10'],
        'Daily_Return': latest_features['Daily_Return']
    }])

    # 5. Prediction
    try:
        prediction = model.predict(X_latest)[0]          # 1 for UP, 0 for DOWN
        probabilities = model.predict_proba(X_latest)[0] # Extract the chance [prob_0, prob_1]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model prediction failed: {str(e)}"
        )
    
    # Map the result
    predicted_trend = "UP" if prediction == 1 else "DOWN"
    confidence_score = probabilities[1] if prediction == 1 else probabilities[0]
    
    # Derived mock predicted_close to fulfill the Pydantic schema requirements (PredictionBase)
    pseudo_predicted_close = last_close_price * 1.01 if prediction == 1 else last_close_price * 0.99
    
    target_date = date.today() + timedelta(days=1)

    # 6. Return response matching stock_schema.PredictionResponse
    return PredictionResponse(
        id=999,  # Unsaved mock ID since we're generating this on the fly
        ticker_id=ticker.id,
        target_date=target_date,
        predicted_close=round(pseudo_predicted_close, 2),
        confidence_score=round(confidence_score, 4),
        model_version="lightweight_v1",
        created_at=datetime.now()
    )
