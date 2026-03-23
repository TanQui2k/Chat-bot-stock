from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.stock import DailyPrice, Ticker, Prediction

# Keep existing methods for compatibility
def get_ticker(db: Session, symbol: str):
    return db.query(Ticker).filter(Ticker.symbol == symbol).first()

def create_ticker(db: Session, symbol: str, company_name: str = None):
    db_ticker = Ticker(symbol=symbol, company_name=company_name)
    db.add(db_ticker)
    db.commit()
    db.refresh(db_ticker)
    return db_ticker

def get_predictions(db: Session, symbol: str, limit: int = 10):
    ticker = get_ticker(db, symbol)
    if not ticker:
        return []
    return db.query(Prediction).filter(Prediction.ticker_id == ticker.id).order_by(Prediction.target_date.desc()).limit(limit).all()

# Newly requested methods
async def get_ticker_by_symbol(db: Session, symbol: str):
    """Fetch a ticker by its symbol from the database."""
    stmt = select(Ticker).where(Ticker.symbol == symbol)
    return db.scalars(stmt).first()

async def get_historical_prices(
    db: Session, ticker_id: int, limit: int = 60
):
    """
    Returns the latest `limit` prices for a ticker, ordered by date ascending.
    """
    stmt = (
        select(DailyPrice)
        .where(DailyPrice.ticker_id == ticker_id)
        .order_by(DailyPrice.date.desc())
        .limit(limit)
    )
    prices = list(db.scalars(stmt).all())
    return prices[::-1]
