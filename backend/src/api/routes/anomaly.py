"""Anomaly Detection API Routes for Stock Trading System."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.ml.anomaly import AnomalyDetector, VolumeAnomalyAnalyzer, PriceAnomalyAnalyzer, PatternMatcher, AlertGenerator
from src.api.dependencies import get_db
from src.crud import crud_stock

router = APIRouter(prefix="/ml/anomaly", tags=["anomaly-detection"])


# Pydantic Models
class AnomalyResponse(BaseModel):
    symbol: str
    timestamp: str
    volume_anomalies: List[dict]
    price_anomalies: List[dict]
    pattern_anomalies: List[dict]
    summary: dict


class AlertResponse(BaseModel):
    id: int
    symbol: str
    category: str
    type: str
    date: str
    severity: str
    description: str
    details: dict
    timestamp: str
    created_at: str
    is_active: bool


class ScanAllResponse(BaseModel):
    total_analyzed: int
    with_anomalies: int
    results: List[dict]


@router.post("/detect/{symbol}", response_model=AnomalyResponse)
async def detect_anomalies(symbol: str, db: Session = Depends(get_db)):
    """
    Detect anomalies for a specific stock symbol.
    
    - **symbol**: Stock ticker symbol (e.g., FPT, VNM)
    """
    formatted_symbol = symbol.upper().strip()
    
    # Get historical prices
    ticker = await crud_stock.get_ticker_by_symbol(db, symbol=formatted_symbol)
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker '{formatted_symbol}' not found in the database."
        )
    
    prices = await crud_stock.get_historical_prices(db, ticker_id=ticker.id, limit=30)
    
    if not prices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No historical price data found for '{formatted_symbol}'."
        )
    
    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame([{
        'date': p.date,
        'open': p.open,
        'high': p.high,
        'low': p.low,
        'close': p.close,
        'volume': p.volume
    } for p in prices])
    df.set_index('date', inplace=True)
    
    # Run anomaly detection
    detector = AnomalyDetector()
    anomalies = detector.detect_all_anomalies(formatted_symbol, df, db)
    
    return anomalies


@router.get("/alerts/{symbol}", response_model=List[AlertResponse])
async def get_alerts(symbol: str, severity: str = 'medium', db: Session = Depends(get_db)):
    """
    Get active alerts for a specific stock symbol.
    
    - **symbol**: Stock ticker symbol
    - **severity**: Minimum severity level (low, medium, high, critical)
    """
    formatted_symbol = symbol.upper().strip()
    
    # Get historical prices
    ticker = await crud_stock.get_ticker_by_symbol(db, symbol=formatted_symbol)
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker '{formatted_symbol}' not found in the database."
        )
    
    prices = await crud_stock.get_historical_prices(db, ticker_id=ticker.id, limit=30)
    
    if not prices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No historical price data found for '{formatted_symbol}'."
        )
    
    # Convert to DataFrame
    import pandas as pd
    df = pd.DataFrame([{
        'date': p.date,
        'open': p.open,
        'high': p.high,
        'low': p.low,
        'close': p.close,
        'volume': p.volume
    } for p in prices])
    df.set_index('date', inplace=True)
    
    # Run detection and generate alerts
    detector = AnomalyDetector()
    anomalies = detector.detect_all_anomalies(formatted_symbol, df, db)
    
    generator = AlertGenerator()
    alerts = generator.generate_alerts(anomalies, threshold=severity)
    
    return alerts


@router.get("/volume/{symbol}")
async def get_volume_analysis(symbol: str, db: Session = Depends(get_db)):
    """
    Get detailed volume analysis for a stock.
    
    - **symbol**: Stock ticker symbol
    """
    formatted_symbol = symbol.upper().strip()
    
    ticker = await crud_stock.get_ticker_by_symbol(db, symbol=formatted_symbol)
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker '{formatted_symbol}' not found in the database."
        )
    
    prices = await crud_stock.get_historical_prices(db, ticker_id=ticker.id, limit=30)
    
    if not prices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No historical price data found for '{formatted_symbol}'."
        )
    
    import pandas as pd
    df = pd.DataFrame([{
        'date': p.date,
        'close': p.close,
        'volume': p.volume
    } for p in prices])
    df.set_index('date', inplace=True)
    
    analyzer = VolumeAnomalyAnalyzer()
    analysis = analyzer.analyze_volume(df)
    
    return analysis


@router.get("/price/{symbol}")
async def get_price_analysis(symbol: str, db: Session = Depends(get_db)):
    """
    Get detailed price analysis for a stock.
    
    - **symbol**: Stock ticker symbol
    """
    formatted_symbol = symbol.upper().strip()
    
    ticker = await crud_stock.get_ticker_by_symbol(db, symbol=formatted_symbol)
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker '{formatted_symbol}' not found in the database."
        )
    
    prices = await crud_stock.get_historical_prices(db, ticker_id=ticker.id, limit=30)
    
    if not prices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No historical price data found for '{formatted_symbol}'."
        )
    
    import pandas as pd
    df = pd.DataFrame([{
        'date': p.date,
        'close': p.close,
        'open': p.open,
        'high': p.high,
        'low': p.low
    } for p in prices])
    df.set_index('date', inplace=True)
    
    analyzer = PriceAnomalyAnalyzer()
    analysis = analyzer.analyze_price(df)
    
    return analysis


@router.get("/patterns/{symbol}")
async def get_patterns(symbol: str, db: Session = Depends(get_db)):
    """
    Get detected technical patterns for a stock.
    
    - **symbol**: Stock ticker symbol
    """
    formatted_symbol = symbol.upper().strip()
    
    ticker = await crud_stock.get_ticker_by_symbol(db, symbol=formatted_symbol)
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticker '{formatted_symbol}' not found in the database."
        )
    
    prices = await crud_stock.get_historical_prices(db, ticker_id=ticker.id, limit=30)
    
    if not prices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No historical price data found for '{formatted_symbol}'."
        )
    
    import pandas as pd
    df = pd.DataFrame([{
        'date': p.date,
        'open': p.open,
        'high': p.high,
        'low': p.low,
        'close': p.close,
        'volume': p.volume
    } for p in prices])
    df.set_index('date', inplace=True)
    
    matcher = PatternMatcher()
    analysis = matcher.detect_patterns(df)
    
    return analysis


@router.post("/scan-all", response_model=ScanAllResponse)
async def scan_all_stocks(db: Session = Depends(get_db)):
    """
    Scan all stocks for anomalies.
    
    Returns a summary of anomalies across all stocks.
    """
    # Get all active tickers
    from sqlalchemy import select
    from src.models.stock import Ticker
    
    stmt = select(Ticker).where(Ticker.is_active == True)
    tickers = list(db.scalars(stmt).all())
    
    if not tickers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active tickers found in the database."
        )
    
    results = []
    with_anomalies = 0
    
    detector = AnomalyDetector()
    
    for ticker in tickers:
        try:
            prices = await crud_stock.get_historical_prices(db, ticker_id=ticker.id, limit=30)
            
            if not prices:
                continue
            
            import pandas as pd
            df = pd.DataFrame([{
                'date': p.date,
                'open': p.open,
                'high': p.high,
                'low': p.low,
                'close': p.close,
                'volume': p.volume
            } for p in prices])
            df.set_index('date', inplace=True)
            
            anomalies = detector.detect_all_anomalies(ticker.symbol, df, db)
            
            total = anomalies['summary'].get('total_anomalies', 0)
            if total > 0:
                with_anomalies += 1
            
            results.append({
                'symbol': ticker.symbol,
                'total_anomalies': total,
                'severity': anomalies['summary'].get('severity', 'low'),
                'message': anomalies['summary'].get('message', '')
            })
            
        except Exception as e:
            # Log error but continue with other stocks
            continue
    
    return ScanAllResponse(
        total_analyzed=len(results),
        with_anomalies=with_anomalies,
        results=results
    )


@router.get("/summary")
async def get_anomaly_summary(severity: str = 'medium', db: Session = Depends(get_db)):
    """
    Get a summary of all current anomalies across stocks.
    
    - **severity**: Minimum severity level to include
    """
    from sqlalchemy import select
    from src.models.stock import Ticker
    
    stmt = select(Ticker).where(Ticker.is_active == True)
    tickers = list(db.scalars(stmt).all())
    
    if not tickers:
        return {
            'total_stocks': 0,
            'stocks_with_anomalies': 0,
            'total_anomalies': 0,
            'by_severity': {},
            'top_anomalies': []
        }
    
    all_alerts = []
    by_severity = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    
    detector = AnomalyDetector()
    generator = AlertGenerator()
    
    for ticker in tickers:
        try:
            prices = await crud_stock.get_historical_prices(db, ticker_id=ticker.id, limit=30)
            
            if not prices:
                continue
            
            import pandas as pd
            df = pd.DataFrame([{
                'date': p.date,
                'open': p.open,
                'high': p.high,
                'low': p.low,
                'close': p.close,
                'volume': p.volume
            } for p in prices])
            df.set_index('date', inplace=True)
            
            anomalies = detector.detect_all_anomalies(ticker.symbol, df, db)
            alerts = generator.generate_alerts(anomalies, threshold=severity)
            
            all_alerts.extend(alerts)
            
            for alert in alerts:
                sev = alert.get('severity', 'low')
                by_severity[sev] = by_severity.get(sev, 0) + 1
                
        except Exception:
            continue
    
    # Sort by severity
    all_alerts.sort(key=lambda x: by_severity.get(x.get('severity', 'low'), 0), reverse=True)
    
    return {
        'total_stocks': len(tickers),
        'stocks_with_anomalies': len(set(a['symbol'] for a in all_alerts)),
        'total_anomalies': len(all_alerts),
        'by_severity': by_severity,
        'top_anomalies': all_alerts[:10]
    }