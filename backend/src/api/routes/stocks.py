from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.crud import crud_stock
from src.api.dependencies import get_db
from src.models.stock import DailyPrice, Ticker
from src.schemas.stock_schema import PriceResponse, TickerResponse, PredictionResponse
from src.services.vnstock_service import StockPrice, VnStockPriceService

router = APIRouter(prefix="/stocks", tags=["stocks"])


class LatestPriceResponse(BaseModel):
    symbol: str
    price: float
    currency: str
    as_of: str | None = None


class StockInfoResponse(BaseModel):
    symbol: str
    name: str | None = None
    price: float
    change: float | None = None
    change_percent: float | None = None
    volume: int | None = None
    market_cap: float | None = None


def _get_latest_price_with_database_fallback(symbol: str, db: Session) -> StockPrice:
    """Prefer the live provider, but keep the API useful if it is unavailable."""
    normalized_symbol = symbol.upper().strip()
    try:
        return VnStockPriceService().get_latest_price(normalized_symbol)
    except RuntimeError as live_error:
        stmt = (
            select(DailyPrice)
            .join(Ticker, Ticker.id == DailyPrice.ticker_id)
            .where(
                Ticker.symbol == normalized_symbol,
                DailyPrice.close.is_not(None),
            )
            .order_by(DailyPrice.date.desc())
            .limit(1)
        )
        stored_price = db.scalar(stmt)
        if stored_price is None or stored_price.close is None:
            raise live_error

        return StockPrice(
            symbol=normalized_symbol,
            price=float(stored_price.close),
            as_of=stored_price.date.isoformat(),
            source="database",
        )


@router.get("/", response_model=List[TickerResponse])
async def get_all_active_tickers(db: Session = Depends(get_db)):
    stmt = select(Ticker).where(Ticker.is_active == True)
    tickers = list(db.scalars(stmt).all())
    return tickers


@router.get("/price/{symbol}", response_model=LatestPriceResponse)
async def get_latest_price(symbol: str, db: Session = Depends(get_db)):
    try:
        price_info = _get_latest_price_with_database_fallback(symbol, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e

    return LatestPriceResponse(
        symbol=price_info.symbol,
        price=price_info.price,
        currency=price_info.currency,
        as_of=price_info.as_of,
    )


@router.get("/info/{symbol}", response_model=StockInfoResponse)
async def get_stock_info(symbol: str, db: Session = Depends(get_db)):
    try:
        price_info = _get_latest_price_with_database_fallback(symbol, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e

    ticker = crud_stock.get_ticker(db, symbol=symbol.upper())
    return StockInfoResponse(
        symbol=price_info.symbol,
        name=ticker.company_name if ticker else None,
        price=price_info.price,
    )

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
