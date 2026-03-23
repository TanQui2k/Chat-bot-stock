from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud import crud_stock
from src.api.dependencies import get_db
from src.models.stock import Ticker
from src.schemas.stock_schema import PriceResponse, TickerResponse, PredictionResponse

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("/", response_model=List[TickerResponse])
async def get_all_active_tickers(db: Session = Depends(get_db)):
    stmt = select(Ticker).where(Ticker.is_active == True)
    tickers = list(db.scalars(stmt).all())
    return tickers

@router.get("/{symbol}", response_model=TickerResponse)
def get_ticker(symbol: str, db: Session = Depends(get_db)):
    ticker = crud_stock.get_ticker(db, symbol=symbol.upper())
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return ticker

@router.get("/{symbol}/history", response_model=List[PriceResponse])
async def get_ticker_history(symbol: str, db: Session = Depends(get_db)):
    formatted_symbol = symbol.upper()
    ticker = await crud_stock.get_ticker_by_symbol(db, symbol=formatted_symbol)
    
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker '{formatted_symbol}' not found in the database."
        )
    
    prices = await crud_stock.get_historical_prices(db, ticker_id=ticker.id)
    return prices

@router.get("/{symbol}/predictions", response_model=List[PredictionResponse])
def get_predictions(symbol: str, limit: int = 10, db: Session = Depends(get_db)):
    return crud_stock.get_predictions(db, symbol=symbol.upper(), limit=limit)
