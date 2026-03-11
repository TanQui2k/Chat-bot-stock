from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict

# ==========================================
# Ticker Schemas
# ==========================================
class TickerBase(BaseModel):
    symbol: str
    company_name: Optional[str] = None
    is_active: bool = True

class TickerResponse(TickerBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Daily Price Schemas
# ==========================================
class PriceBase(BaseModel):
    date: date
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None

class PriceResponse(PriceBase):
    id: int
    ticker_id: int
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Prediction Schemas
# ==========================================
class PredictionBase(BaseModel):
    target_date: date
    predicted_close: float
    confidence_score: Optional[float] = None
    model_version: str

class PredictionCreate(PredictionBase):
    ticker_id: int

class PredictionResponse(PredictionBase):
    id: int
    ticker_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
