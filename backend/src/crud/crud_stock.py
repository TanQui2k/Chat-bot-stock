from datetime import date, datetime
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
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


def upsert_daily_prices(db: Session, ticker_id: int, price_rows: list[dict]) -> int:
    """
    Insert or update daily price rows for one ticker.

    The database is the source of truth for uniqueness on `(ticker_id, date)`.
    If an importer sends the same trading day again, we update OHLCV fields
    instead of creating duplicates.
    """
    normalized_rows: dict[date, dict] = {}

    for row in price_rows:
        raw_date = row.get('date')
        if isinstance(raw_date, datetime):
            raw_date = raw_date.date()

        if not isinstance(raw_date, date):
            continue

        normalized_rows[raw_date] = {
            'ticker_id': ticker_id,
            'date': raw_date,
            'open': row.get('open'),
            'high': row.get('high'),
            'low': row.get('low'),
            'close': row.get('close'),
            'volume': row.get('volume'),
        }

    if not normalized_rows:
        return 0

    stmt = insert(DailyPrice).values(list(normalized_rows.values()))
    stmt = stmt.on_conflict_do_update(
        index_elements=[DailyPrice.ticker_id, DailyPrice.date],
        set_={
            'open': stmt.excluded.open,
            'high': stmt.excluded.high,
            'low': stmt.excluded.low,
            'close': stmt.excluded.close,
            'volume': stmt.excluded.volume,
        },
    )
    result = db.execute(stmt)
    db.commit()
    return int(result.rowcount or 0)


def create_predictions(db: Session, ticker_id: int, predictions_list: list, model_version: str):
    """
    Save generated predictions to the database.
    """
    for p in predictions_list:
        db_prediction = Prediction(
            ticker_id=ticker_id,
            target_date=datetime.strptime(p['date'], '%Y-%m-%d').date(),
            predicted_close=p['predicted_close'],
            model_version=model_version,
            confidence_score=p.get('confidence_score') # Optional: based on MAPE or range
        )
        db.add(db_prediction)
    
    db.commit()
