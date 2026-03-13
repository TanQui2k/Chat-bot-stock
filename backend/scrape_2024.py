"""
Scrape ALL Vietnamese stock historical prices for 2024 from HOSE, HNX, UPCOM.
"""
import os
import sys
import time
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
import functools

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.models.stock import Ticker, DailyPrice
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://root:postgres@127.0.0.1:5432/stock_db")
if "postgresql+psycopg2://" not in DATABASE_URL and "postgresql+psycopg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql+psycopg2://")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

EXCHANGES = ['HOSE', 'HNX', 'UPCOM']
# Community tier limit: 60 req/min => 1 second between requests 
REQUEST_DELAY = 1.2
RETRY_WAIT = 10
MAX_RETRIES = 2

# Register vnstock API key
os.environ['VNSTOCK_API_KEY'] = 'vnstock_48ee0184c86e49da9a5fea282ad3e2ea'

def get_all_tickers_by_exchange():
    from vnstock import Vnstock
    stock = Vnstock().stock(symbol='FPT', source='VCI')
    tickers_by_exchange = {}
    for exchange in EXCHANGES:
        symbols = stock.listing.symbols_by_group(exchange)
        symbol_list = symbols.tolist() if hasattr(symbols, 'tolist') else list(symbols)
        tickers_by_exchange[exchange] = symbol_list
        print(f"  {exchange}: {len(symbol_list)} tickers")
    return tickers_by_exchange

def fetch_history_with_retry(symbol, retries=MAX_RETRIES):
    from vnstock import Vnstock
    for attempt in range(retries):
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            history = stock.quote.history(start='2024-01-01', end='2024-12-31')
            return history
        except Exception as e:
            err_str = str(e).lower()
            if 'rate limit' in err_str or '429' in err_str or 'too many' in err_str:
                wait = RETRY_WAIT * (attempt + 1)
                print(f"RATE LIMITED, waiting {wait}s...", end=" ")
                time.sleep(wait)
            elif 'valueerror' in err_str:
                # Often means no data or ticker suspended
                print("NO DATA (ValueError)", end=" ")
                return None
            else:
                # Avoid long retries for missing tickers
                return None
    return None

def scrape():
    session = SessionLocal()
    print("Fetching all tickers from vnstock...")
    try:
        tickers_by_exchange = get_all_tickers_by_exchange()
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        return
        
    total_symbols = sum(len(v) for v in tickers_by_exchange.values())
    print(f"\nTotal tickers to process: {total_symbols}")
    
    processed = 0
    total_inserted = 0
    failed_symbols = []
    
    for exchange, symbols in tickers_by_exchange.items():
        print(f"\n{'='*60}")
        print(f"Processing {exchange} ({len(symbols)} tickers)")
        print(f"{'='*60}")
        
        for symbol in symbols:
            processed += 1
            ticker = session.execute(select(Ticker).where(Ticker.symbol == symbol)).scalar_one_or_none()
            if not ticker:
                ticker = Ticker(symbol=symbol, company_name=symbol, exchange=exchange, is_active=True)
                session.add(ticker)
                session.commit()
                session.refresh(ticker)
            elif not ticker.exchange:
                ticker.exchange = exchange
                session.commit()
            
            existing_count = session.execute(
                select(func.count(DailyPrice.id)).where(
                    DailyPrice.ticker_id == ticker.id,
                    DailyPrice.date >= '2024-01-01',
                    DailyPrice.date <= '2024-12-31'
                )
            ).scalar()
            
            if existing_count and existing_count > 0:
                print(f"[{processed}/{total_symbols}] {symbol} ({exchange})... SKIP (already has {existing_count} records)")
                continue
            
            print(f"[{processed}/{total_symbols}] {symbol} ({exchange})...", end=" ")
            
            try:
                history = fetch_history_with_retry(symbol)
            except Exception as e:
                print(f"FAIL ({e})")
                failed_symbols.append((symbol, exchange, str(e)))
                time.sleep(REQUEST_DELAY)
                continue
            
            if history is None or history.empty:
                print("NO DATA")
                time.sleep(REQUEST_DELAY)
                continue
            
            added = 0
            for idx, row in history.iterrows():
                date_val = None
                if 'time' in row.index:
                    date_val = pd.to_datetime(row['time']).date()
                elif isinstance(idx, (pd.Timestamp, datetime)):
                    date_val = idx.date()
                else:
                    date_val = pd.to_datetime(str(idx)).date()

                if not date_val:
                    continue
                
                existing_price = session.execute(
                    select(DailyPrice.id).where(DailyPrice.ticker_id == ticker.id, DailyPrice.date == date_val)
                ).scalar_one_or_none()
                
                if not existing_price:
                    try:
                        price = DailyPrice(
                            ticker_id=ticker.id,
                            date=date_val,
                            open=float(row.get('open', 0)),
                            high=float(row.get('high', 0)),
                            low=float(row.get('low', 0)),
                            close=float(row.get('close', 0)),
                            volume=int(row.get('volume', 0))
                        )
                        session.add(price)
                        added += 1
                    except Exception:
                        pass
            
            session.commit()
            total_inserted += added
            print(f"OK (+{added} records) [total: {total_inserted}]")
            time.sleep(REQUEST_DELAY)
            
    session.close()
    
    print(f"\n{'='*60}")
    print(f"DONE! Processed: {processed}, Inserted: {total_inserted}")
    if failed_symbols:
        print(f"Failed symbols: {len(failed_symbols)}")

if __name__ == "__main__":
    scrape()
