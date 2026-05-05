"""
Scrape Vietnamese stock history from VCI and upsert it into PostgreSQL.

This script is intentionally incremental:
- First run backfills from START_DATE
- Later runs continue from the latest stored trading day per ticker
- Re-imported rows update existing OHLCV values instead of duplicating them
"""

import functools
import os
import sys
import time
from datetime import datetime, timedelta

import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
print = functools.partial(print, flush=True)

# Set path to import from src
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

from src.core.config import SessionLocal
from src.crud.crud_stock import upsert_daily_prices
from src.models.stock import DailyPrice, Ticker

# Register vnstock API key
os.environ["VNSTOCK_API_KEY"] = "vnstock_48ee0184c86e49da9a5fea282ad3e2ea"

EXCHANGES = ["HOSE", "HNX", "UPCOM"]
REQUEST_DELAY = 1.2
RETRY_WAIT = 10
MAX_RETRIES = 3
START_DATE = "2026-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")
START_DATE_OBJ = datetime.strptime(START_DATE, "%Y-%m-%d").date()
END_DATE_OBJ = datetime.strptime(END_DATE, "%Y-%m-%d").date()


def get_all_tickers_by_exchange():
    from vnstock import Vnstock

    stock = Vnstock().stock(symbol="FPT", source="VCI")
    tickers_by_exchange = {}

    for exchange in EXCHANGES:
        try:
            symbols = stock.listing.symbols_by_group(exchange)
            symbol_list = symbols.tolist() if hasattr(symbols, "tolist") else list(symbols)
            tickers_by_exchange[exchange] = symbol_list
            print(f"  {exchange}: {len(symbol_list)} tickers")
        except Exception as e:
            print(f"Failed to load symbols for {exchange}: {e}")
            tickers_by_exchange[exchange] = []

    return tickers_by_exchange


def fetch_history_with_retry(symbol: str, start_date: str, end_date: str, retries: int = MAX_RETRIES):
    from vnstock import Vnstock

    for attempt in range(retries):
        try:
            stock = Vnstock().stock(symbol=symbol, source="VCI")
            return stock.quote.history(start=start_date, end=end_date)
        except Exception as e:
            err_str = str(e).lower()
            if "rate limit" in err_str or "429" in err_str or "too many" in err_str:
                wait = RETRY_WAIT * (attempt + 1)
                print(f"RATE LIMITED, waiting {wait}s...", end=" ")
                time.sleep(wait)
            elif "valueerror" in err_str:
                print("NO DATA (ValueError)", end=" ")
                return None
            else:
                print(f"VCI API error: {e}", end=" ")
                time.sleep(REQUEST_DELAY)
                return None

    return None


def build_price_payload(history: pd.DataFrame) -> list[dict]:
    if "time" in history.columns:
        history = history.rename(columns={"time": "date"})

    history["date"] = pd.to_datetime(history["date"]).dt.date
    payload: list[dict] = []

    for _, row in history.iterrows():
        date_val = row["date"]
        if pd.isna(date_val):
            continue

        payload.append(
            {
                "date": date_val,
                "open": float(row.get("open")) if not pd.isna(row.get("open")) else None,
                "high": float(row.get("high")) if not pd.isna(row.get("high")) else None,
                "low": float(row.get("low")) if not pd.isna(row.get("low")) else None,
                "close": float(row.get("close")) if not pd.isna(row.get("close")) else None,
                "volume": int(row.get("volume")) if not pd.isna(row.get("volume")) else None,
            }
        )

    return payload


def scrape():
    session = SessionLocal()
    print("Loading tickers from vnstock (VCI)...")

    try:
        from vnstock import Vnstock  # noqa: F401
    except ImportError:
        print("vnstock is not installed. Run: pip install vnstock")
        return

    tickers_by_exchange = get_all_tickers_by_exchange()
    total_symbols = sum(len(v) for v in tickers_by_exchange.values())
    print(f"\nTotal symbols to process: {total_symbols}")

    processed = 0
    total_upserted = 0
    failed_symbols = []

    for exchange, symbols in tickers_by_exchange.items():
        print(f"\n{'=' * 60}")
        print(f"Processing exchange {exchange} ({len(symbols)} symbols)")
        print(f"{'=' * 60}")

        for symbol in symbols:
            processed += 1

            ticker = session.query(Ticker).filter(Ticker.symbol == symbol).first()
            if not ticker:
                ticker = Ticker(symbol=symbol, company_name=symbol, exchange=exchange, is_active=True)
                session.add(ticker)
                session.commit()
                session.refresh(ticker)
            elif not ticker.exchange:
                ticker.exchange = exchange
                session.commit()

            print(f"[{processed}/{total_symbols}] {symbol} ({exchange})...", end=" ")

            last_record = (
                session.query(DailyPrice)
                .filter(DailyPrice.ticker_id == ticker.id)
                .order_by(DailyPrice.date.desc())
                .first()
            )
            if last_record and last_record.date >= END_DATE_OBJ:
                print("Already up to date")
                continue

            fetch_start_date = START_DATE
            if last_record:
                next_date = max(START_DATE_OBJ, last_record.date + timedelta(days=1))
                fetch_start_date = next_date.strftime("%Y-%m-%d")

            try:
                history = fetch_history_with_retry(symbol, fetch_start_date, END_DATE)
            except Exception as e:
                print(f"FAIL ({e})")
                failed_symbols.append((symbol, exchange, str(e)))
                time.sleep(REQUEST_DELAY)
                continue

            if history is None or history.empty:
                print("NO DATA")
                time.sleep(REQUEST_DELAY)
                continue

            try:
                payload = build_price_payload(history)
                if payload:
                    affected_rows = upsert_daily_prices(session, ticker.id, payload)
                    total_upserted += affected_rows
                    print(f"OK (+{affected_rows} rows) [Total: {total_upserted}]")
                else:
                    print("OK (No valid rows)")
            except Exception as e:
                session.rollback()
                print(f"FAIL ({e})")
                failed_symbols.append((symbol, exchange, str(e)))

            time.sleep(REQUEST_DELAY)

    session.close()

    print(f"\n{'=' * 60}")
    print(f"DONE! Processed: {processed} symbols. Upserted: {total_upserted} rows.")
    if failed_symbols:
        print(f"Symbols with errors or no data: {len(failed_symbols)}")


if __name__ == "__main__":
    scrape()
