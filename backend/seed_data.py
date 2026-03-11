import logging
import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.core.config import SessionLocal, engine
    from src.models.stock import Ticker, DailyPrice, Prediction
    from src.models.user import User, ChatSession, ChatMessage
    from src.models.base import Base
except ModuleNotFoundError:
    pass

# Đảm bảo các bảng (tables) đã được tạo trong Database trên PostgreSQL
Base.metadata.create_all(bind=engine)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

TARGET_SYMBOLS = ['AAPL', 'MSFT', 'TSLA', 'GOOGL']

def clean_float(val):
    """Return float value or None if NaN."""
    if pd.isna(val):
        return None
    return float(val)

def clean_int(val):
    """Return int value or None if NaN."""
    if pd.isna(val):
        return None
    return int(val)

def seed_stock_data():
    session: Session = SessionLocal()
    try:
        for symbol in TARGET_SYMBOLS:
            logger.info(f"Processing symbol: {symbol}")
            
            # --- 1. Check if Ticker exists ---
            stmt_ticker = select(Ticker).where(Ticker.symbol == symbol)
            ticker = session.scalars(stmt_ticker).first()
            
            if not ticker:
                # Insert new ticker
                yf_ticker = yf.Ticker(symbol)
                try:
                    # yfinance info dictionary can sometimes fail or miss 'shortName'
                    company_name = yf_ticker.info.get("shortName", symbol)
                except Exception:
                    company_name = symbol
                    
                ticker = Ticker(
                    symbol=symbol,
                    company_name=company_name,
                    is_active=True
                )
                session.add(ticker)
                
                # Commit to generate the ticker.id
                try:
                    session.commit()
                    session.refresh(ticker)
                    logger.info(f"Inserted new ticker: {symbol} (ID: {ticker.id})")
                except SQLAlchemyError as e:
                    session.rollback()
                    logger.error(f"Failed to insert ticker {symbol}. Error: {e}")
                    continue
            else:
                logger.info(f"Ticker {symbol} already exists (ID: {ticker.id}).")

            # --- 2. Download historical data (last 2 years) ---
            logger.info(f"Downloading historical data for {symbol}...")
            try:
                hist_data = yf.Ticker(symbol).history(period="2y")
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
                continue
                
            if hist_data.empty:
                logger.warning(f"No historical data found for {symbol}.")
                continue

            # --- 3. Iterate through DataFrame and insert DailyPrice records ---
            # Instead of hitting the DB for each row, fetch all existing dates for this ticker to improve performance
            stmt_existing_dates = select(DailyPrice.date).where(DailyPrice.ticker_id == ticker.id)
            existing_dates = set(session.scalars(stmt_existing_dates).all())

            new_records_count: int = 0
            
            # Reset index to access 'Date' as a regular column
            hist_data = hist_data.reset_index()

            for _, row in hist_data.iterrows():
                try:
                    # Extract pure date object, stripping timezone info
                    date_val = pd.to_datetime(row['Date']).date()
                    
                    # If this date is already present for the ticker, skip it
                    if date_val in existing_dates:
                        continue
                    
                    open_price = clean_float(row.get('Open'))
                    high_price = clean_float(row.get('High'))
                    low_price = clean_float(row.get('Low'))
                    close_price = clean_float(row.get('Close'))
                    volume = clean_int(row.get('Volume'))
                    
                    # Skip if core pricing is entirely missing
                    if close_price is None and open_price is None:
                        continue 

                    # Insert new price record
                    new_price = DailyPrice(
                        ticker_id=ticker.id,
                        date=date_val,
                        open=open_price,
                        high=high_price,
                        low=low_price,
                        close=close_price,
                        volume=volume
                    )
                    session.add(new_price)
                    new_records_count = new_records_count + 1
                    
                    # Add to existing dates cache so we don't accidentally insert duplicates within current run
                    existing_dates.add(date_val)
                        
                except Exception as row_error:
                    logger.error(f"Error processing row for {symbol} at {row.get('Date')}: {row_error}")
                    continue

            # --- 4. Commit records for the current ticker ---
            try:
                session.commit()
                if new_records_count > 0:
                    logger.info(f"Inserted {new_records_count} new records for {symbol}.")
                else:
                    logger.info(f"No new records to insert for {symbol}.")
            except SQLAlchemyError as commit_error:
                session.rollback()
                logger.error(f"Failed to commit daily prices for {symbol}: {commit_error}")
                
    except Exception as e:
        logger.error(f"Critical script error: {e}")
        session.rollback()
    finally:
        session.close()
        logger.info("Database connection closed.")

if __name__ == "__main__":
    logger.info("Starting database seed script...")
    seed_stock_data()
    logger.info("Seeding completed.")
