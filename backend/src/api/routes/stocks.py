from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.api.dependencies import get_db
from src.crud import crud_stock
from src.schemas.stock_schema import TickerResponse, PredictionResponse

router = APIRouter(prefix="/stocks", tags=["stocks"])

@router.get("/{symbol}", response_model=TickerResponse)
def get_ticker(symbol: str, db: Session = Depends(get_db)):
    ticker = crud_stock.get_ticker(db, symbol=symbol.upper())
    if not ticker:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return ticker

@router.get("/{symbol}/predictions", response_model=List[PredictionResponse])
def get_predictions(symbol: str, limit: int = 10, db: Session = Depends(get_db)):
    return crud_stock.get_predictions(db, symbol=symbol.upper(), limit=limit)
