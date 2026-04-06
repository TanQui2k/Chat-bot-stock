import os
import sys
import pandas as pd
from datetime import datetime, timedelta, date
import time
import math
from sqlalchemy.orm import Session
from sqlalchemy import select, func

# Thêm thư mục backend vào sys.path để có thể import từ src
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

from src.core.config import SessionLocal
from src.models.stock import Ticker, DailyPrice

# Import vnstock - Thử import theo cả 2 version cũ và mới
try:
    from vnstock import stock_historical_data
    VNSTOCK_V3 = True
except ImportError:
    try:
        from vnstock.api.quote import Quote
        VNSTOCK_V3 = False
    except ImportError:
        print("Vui lòng cài đặt vnstock: pip install vnstock")
        sys.exit(1)

def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise

def update_ticker_data(db: Session, ticker: Ticker, today_str: str):
    """Cập nhật dữ liệu cho một mã chứng khoán đơn lẻ."""
    # 1. Tìm ngày cuối cùng có dữ liệu trong DB
    last_date_query = db.query(func.max(DailyPrice.date)).filter(DailyPrice.ticker_id == ticker.id).scalar()
    
    start_date = "2024-01-01" # Mặc định lấy từ đầu năm 2024 nếu DB trống
    if last_date_query:
        # Nếu đã có dữ liệu, lấy từ ngày tiếp theo
        start_date = (last_date_query + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Nếu start_date đã vượt quá hôm nay, không cần làm gì
    if datetime.strptime(start_date, "%Y-%m-%d").date() > datetime.now().date():
        return 0, "Already updated"

    # 2. Lấy dữ liệu từ vnstock
    try:
        df = None
        if VNSTOCK_V3:
            # vnstock v3 (vnstock3)
            df = stock_historical_data(symbol=ticker.symbol, start_date=start_date, end_date=today_str, resolution="1D", type="stock")
        else:
            # vnstock v0.2.x
            df = Quote(symbol=ticker.symbol).history(start=start_date, end=today_str)
        
        if df is None or df.empty:
            return 0, "No new data"
        
        # Chuẩn hóa format (vnstock trả về khác nhau tùy version/nguồn)
        # Thông thường có: time/date, open, high, low, close, volume
        if 'time' in df.columns:
            df = df.rename(columns={'time': 'date'})
        
        # Đảm bảo có các cột cần thiết
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in df.columns:
                if col == 'volume' and 'vol' in df.columns:
                    df = df.rename(columns={'vol': 'volume'})
                else:
                    df[col] = None
        
        records_to_insert = []
        for _, row in df.iterrows():
            # Chuyển đổi date
            d = row['date']
            if isinstance(d, str):
                try:
                    d = datetime.strptime(d, "%Y-%m-%d").date()
                except:
                    continue
            elif hasattr(d, 'date'):
                d = d.date()
            
            # Bỏ qua nếu ngày này đã có trong DB (để chắc chắn)
            if last_date_query and d <= last_date_query:
                continue
                
            dp = DailyPrice(
                ticker_id=ticker.id,
                date=d,
                open=float(row['open']) if not pd.isna(row['open']) else None,
                high=float(row['high']) if not pd.isna(row['high']) else None,
                low=float(row['low']) if not pd.isna(row['low']) else None,
                close=float(row['close']) if not pd.isna(row['close']) else None,
                volume=int(row['volume']) if not pd.isna(row['volume']) else None
            )
            records_to_insert.append(dp)
        
        if records_to_insert:
            db.bulk_save_objects(records_to_insert)
            db.commit()
            return len(records_to_insert), "Success"
        
        return 0, "No new data after filtering"

    except Exception as e:
        db.rollback()
        return 0, f"Error: {str(e)}"

def main():
    print(f"=== DAILY UPDATE SCRIPT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    db = get_db()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Lấy danh sách tất cả các mã VN
    tickers = db.query(Ticker).filter(Ticker.is_active == True).all()
    # Nếu bạn chỉ muốn update VN stock: .filter(Ticker.exchange.in_(['HOSE', 'HNX', 'UPCOM']))
    
    print(f"Found {len(tickers)} active tickers to update.")
    
    total_added = 0
    errors = []
    
    for i, t in enumerate(tickers):
        print(f"[{i+1}/{len(tickers)}] Updating {t.symbol:6}...", end=" ", flush=True)
        
        start_time = time.time()
        added, status = update_ticker_data(db, t, today_str)
        elapsed = time.time() - start_time
        
        if added > 0:
            print(f"✅ Added {added} rows ({elapsed:.2f}s)")
            total_added += added
        elif status == "Already updated":
            print(f"⏭️ {status} ({elapsed:.2f}s)")
        elif status == "No new data":
            print(f"⚪ {status} ({elapsed:.2f}s)")
        else:
            print(f"❌ {status} ({elapsed:.2f}s)")
            errors.append((t.symbol, status))
        
        # Nghỉ ngắn để tránh bị block API (quan trọng với Vnstock)
        time.sleep(0.5)
    
    db.close()
    
    print("\n" + "="*50)
    print(f"FINISHED DAILY UPDATE")
    print(f"Total new records added: {total_added}")
    print(f"Tickers with errors: {len(errors)}")
    if errors:
        print("\nDetail errors:")
        for sym, err in errors[:10]:
            print(f"- {sym}: {err}")
        if len(errors) > 10:
            print(f"... and {len(errors)-10} more")
    print("="*50)

if __name__ == "__main__":
    main()
