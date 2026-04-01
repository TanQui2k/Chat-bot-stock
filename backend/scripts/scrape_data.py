import os
import sys
from datetime import datetime, timedelta, date

# Thêm thư mục backend vào sys.path để có thể import từ src
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from src.core.config import SessionLocal, engine
from src.models.stock import Ticker, DailyPrice

try:
    import yfinance as yf
except ImportError:
    print("Vui lòng cài đặt yfinance: pip install yfinance")
    sys.exit(1)

try:
    from vnstock.api.quote import Quote
except ImportError:
    print("Không tìm thấy vnstock. API Quote không có sẵn.")
    sys.exit(1)

import pandas as pd
import math
import time

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def main():
    START_DATE = "2026-01-01"
    TODAY = datetime.now().strftime("%Y-%m-%d")
    
    db = next(get_db())
    tickers = db.query(Ticker).filter(Ticker.is_active == True).all()
    
    print(f"Bắt đầu cập nhật dữ liệu cho {len(tickers)} mã cổ phiếu từ {START_DATE} đến {TODAY}")
    
    # Chúng ta lấy max_date cho từng ticker trước để tránh insert lại
    # Tránh query N lần nếu quá nhiều, nhưng hiện có 1400 cổ phiếu nên vẫn OK
    
    count_success = 0
    count_failed = 0
    total_new_records = 0
    
    for i, t in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] Đang xử lý {t.symbol}...", end=" ")
        
        # Tìm ngày mới nhất trong DB của mã này (nếu có)
        last_record = db.query(DailyPrice).filter(DailyPrice.ticker_id == t.id).order_by(DailyPrice.date.desc()).first()
        
        # Determine fetch start date
        fetch_start = START_DATE
        if last_record and last_record.date >= datetime.strptime(START_DATE, "%Y-%m-%d").date():
            # Tăng 1 ngày từ ngày cuối cùng trong DB để không bị lặp
            fetch_start = (last_record.date + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Nếu fetch_start lớn hơn TODAY thì skip
        if datetime.strptime(fetch_start, "%Y-%m-%d").date() > datetime.now().date():
            print("Đã cập nhật đầy đủ tới hôm nay.")
            continue
            
        try:
            df = None
            # Nếu ko có exchange, nghĩa là US stock
            if not t.exchange or t.symbol in ['AAPL', 'GOOGL', 'MSFT', 'TSLA']:
                df = yf.download(t.symbol, start=fetch_start, end=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"), progress=False)
                if df.empty:
                    print("Không có dữ liệu mới.")
                    continue
                # Xử lý format của df từ yfinance (index là Date, các cột Open, High, Low, Close, Volume)
                df = df.reset_index()
                df.columns = [str(c[0]) if isinstance(c, tuple) else str(c) for c in df.columns]
                # Map columns
                col_map = {
                    'Date': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 
                    'Close': 'close', 'Volume': 'volume'
                }
                df = df.rename(columns=col_map)
                
            else: # VN Stock
                for retry_count in range(5):
                    try:
                        df = Quote(symbol=t.symbol).history(start=fetch_start, end=TODAY)
                        time.sleep(1)  # Giảm tải cho API VCI/VNDirect
                        break
                    except Exception as e:
                        if retry_count == 4:
                            raise e
                        print(f"\\n[Quá tải API, nghỉ 15s để thử lại...] ({retry_count+1}/5)")
                        time.sleep(15)
                        
                # Map columns cho vnstock (time -> date)
                if df is None or len(df) == 0:
                    print("Không có dữ liệu mới.")
                    continue
                # vnstock trả về cột 'time' là ngày
                df = df.rename(columns={'time': 'date'})
                
            if df is None or df.empty:
                print("Không có dữ liệu mới.")
                continue
                
            # Chuẩn bị dữ liệu insert
            # Lọc chỉ lấy các cột cần thiết
            records = df[['date', 'open', 'high', 'low', 'close', 'volume']].copy()
            
            # Đảm bảo cột date có định dạng datetime chuẩn
            records['date'] = pd.to_datetime(records['date']).dt.date
            
            # Drop null values
            records = records.dropna(subset=['close'])
            
            # Xử lý các giá trị NaN, fill bằng None để SQLAlchemy hiểu là NULL
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in records.columns:
                    records[col] = records[col].apply(lambda x: None if pd.isna(x) or math.isnan(x) else float(x) if col != 'volume' else int(x))
            
            new_prices = []
            for _, row in records.iterrows():
                # Bỏ qua nếu cột date rỗng
                if pd.isna(row['date']) or row['date'] is None:
                    continue
                    
                dp = DailyPrice(
                    ticker_id=t.id,
                    date=row['date'],
                    open=row['open'] if 'open' in row else None,
                    high=row['high'] if 'high' in row else None,
                    low=row['low'] if 'low' in row else None,
                    close=row['close'],
                    volume=row['volume'] if 'volume' in row else None
                )
                new_prices.append(dp)
            
            if new_prices:
                db.bulk_save_objects(new_prices)
                db.commit()
                total_new_records += len(new_prices)
                print(f"Đã lưu {len(new_prices)} dòng mới.")
            else:
                print("Không có dữ liệu mới để lưu.")
            
            count_success += 1
            
        except Exception as e:
            db.rollback()
            print(f"LỖI: {str(e)}")
            count_failed += 1
            
    print("-" * 50)
    print(f"HOÀN TẤT! Cập nhật thành công {count_success}/{len(tickers)} mã.")
    print(f"Tổng số bản ghi mới đã thêm vào Database: {total_new_records}")
    print(f"Số mã bị lỗi: {count_failed}")

if __name__ == "__main__":
    main()
