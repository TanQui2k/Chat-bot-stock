from sqlalchemy.orm import Session
from src.models.stock import Ticker, DailyPrice, Prediction
from src.schemas.stock_schema import PredictionCreate

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
