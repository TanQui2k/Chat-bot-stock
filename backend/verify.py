import os
import sys
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.models.stock import Ticker, DailyPrice
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://root:postgres@127.0.0.1:5432/stock_db")
if "postgresql+psycopg2://" not in DATABASE_URL and "postgresql+psycopg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql+psycopg2://")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify():
    session = SessionLocal()
    tickers = session.execute(select(Ticker)).scalars().all()
    print(f"Total Tickers in DB: {len(tickers)}")
    for t in tickers:
        count = session.execute(select(func.count(DailyPrice.id)).where(DailyPrice.ticker_id == t.id)).scalar()
        print(f"Ticker: {t.symbol}, DailyPrices count: {count}")
    
    total_prices = session.execute(select(func.count(DailyPrice.id))).scalar()
    print(f"Total DailyPrice records: {total_prices}")
    session.close()

if __name__ == "__main__":
    verify()
