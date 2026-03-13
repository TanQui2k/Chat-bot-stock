import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://root:postgres@127.0.0.1:5432/stock_db")
if "postgresql+psycopg2://" not in DATABASE_URL and "postgresql+psycopg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql+psycopg2://")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clear_data():
    session = SessionLocal()
    try:
        session.execute(text("TRUNCATE TABLE daily_prices CASCADE;"))
        session.commit()
        print("Đã xóa toàn bộ dữ liệu trong bảng daily_prices!")
    except Exception as e:
        session.rollback()
        print(f"Lỗi khi xóa dữ liệu: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    clear_data()
