"""
Scrape ALL Vietnamese stock historical prices for 2018 from HOSE, HNX, UPCOM.
Uses vnstock to dynamically list all tickers and fetch their price data.

Rate limit: vnstock Guest = 20 requests/min. Script throttles to ~15 req/min to stay safe.
"""
import os
import sys
import time
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker

sys.stdout.reconfigure(encoding='utf-8')
# Force unbuffered output
import functools
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
# Community tier: 60 req/min => 1 second between requests (with some buffer)
REQUEST_DELAY = 1.2  # seconds between API calls
RETRY_WAIT = 10      # seconds to wait when rate-limited
MAX_RETRIES = 3

# Register vnstock API key for Community tier (60 req/min)
import os as _os
_os.environ['VNSTOCK_API_KEY'] = 'vnstock_48ee0184c86e49da9a5fea282ad3e2ea'


def get_all_tickers_by_exchange():
    """Use vnstock listing API to get all tickers grouped by exchange."""
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
    """Fetch history with retry logic for rate limits."""
    from vnstock import Vnstock
    for attempt in range(retries):
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            history = stock.quote.history(start='2018-01-01', end='2018-12-31')
            return history
        except Exception as e:
            err_str = str(e).lower()
            if 'rate limit' in err_str or '429' in err_str or 'too many' in err_str:
                wait = RETRY_WAIT * (attempt + 1)
                print(f"RATE LIMITED, waiting {wait}s...", end=" ")
                time.sleep(wait)
            else:
                raise e
    return None


def scrape():
    session = SessionLocal()
    
    print("Fetching all tickers from vnstock...")
    tickers_by_exchange = get_all_tickers_by_exchange()
    
    total_symbols = sum(len(v) for v in tickers_by_exchange.values())
    print(f"\nTotal tickers to process: {total_symbols}")
    print(f"Estimated time: ~{total_symbols * REQUEST_DELAY // 60} minutes (rate limited)\n")
    
    processed = 0
    total_inserted = 0
    skipped = 0
    failed_symbols = []
    
    for exchange, symbols in tickers_by_exchange.items():
        print(f"\n{'='*60}")
        print(f"Processing {exchange} ({len(symbols)} tickers)")
        print(f"{'='*60}")
        
        for symbol in symbols:
            processed += 1
            
            # Ensure ticker exists in DB
            ticker = session.execute(
                select(Ticker).where(Ticker.symbol == symbol)
            ).scalar_one_or_none()
            
            if not ticker:
                ticker = Ticker(symbol=symbol, company_name=symbol, exchange=exchange, is_active=True)
                session.add(ticker)
                session.commit()
                session.refresh(ticker)
            elif not ticker.exchange:
                ticker.exchange = exchange
                session.commit()
            
            # Check if already have data for this ticker in 2018
            existing_count = session.execute(
                select(func.count(DailyPrice.id)).where(
                    DailyPrice.ticker_id == ticker.id,
                    DailyPrice.date >= '2018-01-01',
                    DailyPrice.date <= '2018-12-31'
                )
            ).scalar()
            
            if existing_count and existing_count > 0:
                skipped += 1
                if skipped % 50 == 0:
                    print(f"  Skipped {skipped} tickers with existing data...")
                continue
            
            print(f"[{processed}/{total_symbols}] {symbol} ({exchange})...", end=" ")
            
            # Fetch historical data with rate limiting
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
            
            # Insert prices
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
            
            # Rate limit delay
            time.sleep(REQUEST_DELAY)
    
    session.close()
    
    print(f"\n{'='*60}")
    print(f"DONE!")
    print(f"Total tickers processed: {processed}")
    print(f"Skipped (already had data): {skipped}")
    print(f"Total new records inserted: {total_inserted}")
    if failed_symbols:
        print(f"Failed symbols ({len(failed_symbols)}):")
        for sym, exc, err in failed_symbols[:20]:
            print(f"  {sym} ({exc}): {err}")
        if len(failed_symbols) > 20:
            print(f"  ... and {len(failed_symbols) - 20} more")
    print(f"{'='*60}")


if __name__ == "__main__":
    scrape()
