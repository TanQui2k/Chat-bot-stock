"""Create all tables defined in SQLAlchemy models."""
from src.core.config import engine
from src.models.base import Base
# Import all models so that Base.metadata knows about them
from src.models.stock import Ticker, DailyPrice, Prediction
from src.models.user import User, ChatSession, ChatMessage

print("Creating all tables...")
Base.metadata.create_all(bind=engine)
print("Done! All tables created successfully.")
