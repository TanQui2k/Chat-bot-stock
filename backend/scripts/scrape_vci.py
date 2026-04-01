"""
Scrape ALL Vietnamese stock historical prices from HOSE, HNX, UPCOM.
Dựa trên script VCI của bạn nhưng được tối ưu tốc độ Insert và điều chỉnh ngày từ 1/1/2026 tới nay.
"""
import os
import sys
import time
from datetime import datetime, timedelta
import pandas as pd
import functools

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# Set path to import from src
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from src.core.config import SessionLocal, engine
from src.models.stock import Ticker, DailyPrice

# Register vnstock API key
os.environ['VNSTOCK_API_KEY'] = 'vnstock_48ee0184c86e49da9a5fea282ad3e2ea'

EXCHANGES = ['HOSE', 'HNX', 'UPCOM']
REQUEST_DELAY = 1.2
RETRY_WAIT = 10
MAX_RETRIES = 3
START_DATE = '2026-01-01'
END_DATE = datetime.now().strftime('%Y-%m-%d')

def get_all_tickers_by_exchange():
    from vnstock import Vnstock
    # Cần khởi tạo tạm 1 symbol để vào được group
    stock = Vnstock().stock(symbol='FPT', source='VCI')
    tickers_by_exchange = {}
    for exchange in EXCHANGES:
        try:
            symbols = stock.listing.symbols_by_group(exchange)
            symbol_list = symbols.tolist() if hasattr(symbols, 'tolist') else list(symbols)
            tickers_by_exchange[exchange] = symbol_list
            print(f"  {exchange}: {len(symbol_list)} tickers")
        except Exception as e:
            print(f"Lỗi khi lấy danh sách mã {exchange}: {e}")
            tickers_by_exchange[exchange] = []
    # Thêm thủ công các mã US nếu cần, bạn có thể bổ sung sau
    return tickers_by_exchange

def fetch_history_with_retry(symbol, retries=MAX_RETRIES):
    from vnstock import Vnstock
    for attempt in range(retries):
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')
            history = stock.quote.history(start=START_DATE, end=END_DATE)
            return history
        except Exception as e:
            err_str = str(e).lower()
            if 'rate limit' in err_str or '429' in err_str or 'too many' in err_str or 'vượt quá' in err_str:
                wait = RETRY_WAIT * (attempt + 1)
                print(f"RATE LIMITED, waiting {wait}s...", end=" ")
                time.sleep(wait)
            elif 'valueerror' in err_str:
                print("NO DATA (ValueError)", end=" ")
                return None
            else:
                print(f"Lỗi VCI API: {e}", end=" ")
                time.sleep(REQUEST_DELAY)
                return None
    return None

def scrape():
    session = SessionLocal()
    print("Đang lấy danh sách tickers từ vnstock (VCI)...")
    try:
        from vnstock import Vnstock
    except ImportError:
        print("Không tìm thấy vnstock. Vui lòng cài đặt: pip install vnstock")
        return
        
    tickers_by_exchange = get_all_tickers_by_exchange()
        
    total_symbols = sum(len(v) for v in tickers_by_exchange.values())
    print(f"\\nTổng số mã cần xử lý: {total_symbols}")
    
    processed = 0
    total_inserted = 0
    failed_symbols = []
    
    for exchange, symbols in tickers_by_exchange.items():
        print(f"\\n{'='*60}")
        print(f"Đang xử lý sàn {exchange} ({len(symbols)} mã)")
        print(f"{'='*60}")
        
        for symbol in symbols:
            processed += 1
            # 1. Check or Create Ticker
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
            
            # 2. Get last updated date for this ticker to avoid fetching duplicate dates
            last_record = session.query(DailyPrice).filter(DailyPrice.ticker_id == ticker.id).order_by(DailyPrice.date.desc()).first()
            if last_record and last_record.date >= datetime.strptime(END_DATE, "%Y-%m-%d").date():
                print("Đã lấy đủ (Skip)")
                continue
            
            history = None
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
                
            # 3. Lọc và chuẩn bị dữ liệu (Tối ưu insert bằng Bulk Save)
            added = 0
            new_prices = []
            
            # Đảm bảo các cột cần thiết tồn tại
            if 'time' in history.columns:
                history = history.rename(columns={'time': 'date'})
                
            # Xử lý datetime
            history['date'] = pd.to_datetime(history['date']).dt.date
            
            # Query ngày đã có sẵn trong khoảng thời gian này
            existing_dates = session.query(DailyPrice.date).filter(
                DailyPrice.ticker_id == ticker.id, 
                DailyPrice.date >= datetime.strptime(START_DATE, "%Y-%m-%d").date()
            ).all()
            existing_dates_set = set(d[0] for d in existing_dates)
            
            for _, row in history.iterrows():
                date_val = row['date']
                if pd.isna(date_val) or date_val in existing_dates_set:
                    continue
                
                try:
                    price = DailyPrice(
                        ticker_id=ticker.id,
                        date=date_val,
                        open=float(row.get('open', 0)) if not pd.isna(row.get('open')) else None,
                        high=float(row.get('high', 0)) if not pd.isna(row.get('high')) else None,
                        low=float(row.get('low', 0)) if not pd.isna(row.get('low')) else None,
                        close=float(row.get('close', 0)),
                        volume=int(row.get('volume', 0)) if not pd.isna(row.get('volume')) else None
                    )
                    new_prices.append(price)
                    existing_dates_set.add(date_val)
                    added += 1
                except Exception:
                    pass
            
            if new_prices:
                session.bulk_save_objects(new_prices)
                session.commit()
                total_inserted += added
                print(f"OK (+{added} dòng) [Total: {total_inserted}]")
            else:
                print(f"OK (Chưa có ngày mới)")
                
            time.sleep(REQUEST_DELAY)
            
    session.close()
    
    print(f"\\n{'='*60}")
    print(f"HOÀN TẤT! Đã quét: {processed} mã. Đã thêm mới: {total_inserted} dòng.")
    if failed_symbols:
        print(f"Số mã lỗi/không có data: {len(failed_symbols)}")

if __name__ == "__main__":
    scrape()
