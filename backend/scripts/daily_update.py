import os
import sys
import time
from datetime import datetime, timedelta

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

# Add backend directory to Python path for local imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

from src.core.config import SessionLocal
from src.crud.crud_stock import upsert_daily_prices
from src.models.stock import DailyPrice, Ticker

try:
    from vnstock import stock_historical_data

    VNSTOCK_V3 = True
except ImportError:
    try:
        from vnstock.api.quote import Quote

        VNSTOCK_V3 = False
    except ImportError:
        print("Please install vnstock: pip install vnstock")
        sys.exit(1)

REQUEST_DELAY = 0.9
RETRY_WAIT = 30
MAX_RETRIES = 5


def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def fetch_history_with_retry(symbol: str, start_date: str, end_date: str):
    for attempt in range(MAX_RETRIES):
        try:
            if VNSTOCK_V3:
                return stock_historical_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    resolution="1D",
                    type="stock",
                )
            return Quote(symbol=symbol).history(start=start_date, end=end_date)
        except Exception as e:
            err_str = str(e).lower()
            if "rate limit" in err_str or "429" in err_str or "too many" in err_str or "quá nhiều request" in err_str:
                wait_seconds = RETRY_WAIT * (attempt + 1)
                print(f"Rate limited, waiting {wait_seconds}s...", end=" ", flush=True)
                time.sleep(wait_seconds)
                continue
            raise
    return None


def update_ticker_data(db: Session, ticker: Ticker, today_str: str):
    """Incrementally update one ticker from the last stored date to today."""
    last_date_query = (
        db.query(func.max(DailyPrice.date))
        .filter(DailyPrice.ticker_id == ticker.id)
        .scalar()
    )

    start_date = "2024-01-01"
    if last_date_query:
        start_date = (last_date_query + timedelta(days=1)).strftime("%Y-%m-%d")

    if datetime.strptime(start_date, "%Y-%m-%d").date() > datetime.now().date():
        return 0, "Already updated"

    try:
        df = fetch_history_with_retry(ticker.symbol, start_date, today_str)
        if df is None or df.empty:
            return 0, "No new data"

        if "time" in df.columns:
            df = df.rename(columns={"time": "date"})

        required_cols = ["date", "open", "high", "low", "close", "volume"]
        for col in required_cols:
            if col not in df.columns:
                if col == "volume" and "vol" in df.columns:
                    df = df.rename(columns={"vol": "volume"})
                else:
                    df[col] = None

        records_to_upsert = []
        for _, row in df.iterrows():
            day_value = row["date"]

            if isinstance(day_value, str):
                try:
                    day_value = datetime.strptime(day_value, "%Y-%m-%d").date()
                except ValueError:
                    continue
            elif hasattr(day_value, "date"):
                day_value = day_value.date()

            if last_date_query and day_value <= last_date_query:
                continue

            records_to_upsert.append(
                {
                    "date": day_value,
                    "open": float(row["open"]) if not pd.isna(row["open"]) else None,
                    "high": float(row["high"]) if not pd.isna(row["high"]) else None,
                    "low": float(row["low"]) if not pd.isna(row["low"]) else None,
                    "close": float(row["close"]) if not pd.isna(row["close"]) else None,
                    "volume": int(row["volume"]) if not pd.isna(row["volume"]) else None,
                }
            )

        if records_to_upsert:
            affected_rows = upsert_daily_prices(db, ticker.id, records_to_upsert)
            return affected_rows, "Success"

        return 0, "No new data after filtering"

    except Exception as e:
        db.rollback()
        return 0, f"Error: {str(e)}"


def main():
    print(f"=== DAILY UPDATE SCRIPT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    db = get_db()
    today_str = datetime.now().strftime("%Y-%m-%d")
    tickers = db.query(Ticker).filter(Ticker.is_active.is_(True)).all()

    print(f"Found {len(tickers)} active tickers to update.")

    total_added = 0
    errors = []

    for index, ticker in enumerate(tickers, start=1):
        print(f"[{index}/{len(tickers)}] Updating {ticker.symbol:6}...", end=" ", flush=True)

        start_time = time.time()
        added, status = update_ticker_data(db, ticker, today_str)
        elapsed = time.time() - start_time

        if added > 0:
            print(f"Added {added} rows ({elapsed:.2f}s)")
            total_added += added
        elif status == "Already updated":
            print(f"{status} ({elapsed:.2f}s)")
        elif status == "No new data":
            print(f"{status} ({elapsed:.2f}s)")
        else:
            print(f"{status} ({elapsed:.2f}s)")
            errors.append((ticker.symbol, status))

        if status != "Already updated":
            time.sleep(REQUEST_DELAY)

    db.close()

    print("\n" + "=" * 50)
    print("FINISHED DAILY UPDATE")
    print(f"Total new records added: {total_added}")
    print(f"Tickers with errors: {len(errors)}")
    if errors:
        print("\nDetail errors:")
        for symbol, err in errors[:10]:
            print(f"- {symbol}: {err}")
        if len(errors) > 10:
            print(f"... and {len(errors) - 10} more")
    print("=" * 50)


if __name__ == "__main__":
    main()
