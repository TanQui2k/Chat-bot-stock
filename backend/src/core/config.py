import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Tìm và load file .env trong project (từ thư mục gốc backend)
load_dotenv()

# Địa chỉ CSDL PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:your_password@localhost:5432/stock_db")

# Khởi tạo SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Tạo SessionLocal class cho các phiên làm việc với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
