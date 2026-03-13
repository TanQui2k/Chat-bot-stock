"""Add exchange column to tickers table and update existing records."""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://root:postgres@127.0.0.1:5432/stock_db")
if "postgresql+psycopg2://" not in DATABASE_URL and "postgresql+psycopg://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql+psycopg2://")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # 1. Add exchange column if not exists
    conn.execute(text("""
        ALTER TABLE tickers ADD COLUMN IF NOT EXISTS exchange VARCHAR(10);
    """))
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_tickers_exchange ON tickers (exchange);
    """))
    
    # 2. Update existing tickers with their exchange
    hose_symbols = ('FPT', 'VIC', 'VNM', 'VCB', 'HPG', 'VHM', 'TCB', 'ACB', 'MBB', 'SSI')
    for s in hose_symbols:
        conn.execute(text("UPDATE tickers SET exchange = 'HOSE' WHERE symbol = :sym AND exchange IS NULL"), {"sym": s})
    
    conn.commit()
    print("Migration completed! Added 'exchange' column and updated existing tickers.")

    # Verify
    result = conn.execute(text("SELECT symbol, exchange FROM tickers ORDER BY id"))
    for row in result:
        print(f"  {row[0]}: {row[1]}")
