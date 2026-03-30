"""Core Anomaly Detector for Stock Trading System."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.crud.crud_stock import get_historical_prices
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Core anomaly detection system for stock trading.
    Detects volume anomalies, price spikes, and trading patterns.
    """
    
    def __init__(self):
        self.volume_threshold = 3.0  # 3x average volume
        self.price_spike_threshold = 0.05  # 5% price change
        self.volatility_threshold = 2.0  # 2x average volatility
        
    def detect_all_anomalies(
        self,
        symbol: str,
        prices_df: pd.DataFrame,
        db: Session
    ) -> Dict[str, Any]:
        """
        Run all anomaly detection algorithms.
        
        Args:
            symbol: Stock symbol
            prices_df: Historical price data DataFrame
            db: Database session
            
        Returns:
            Dictionary containing all detected anomalies
        """
        anomalies = {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'volume_anomalies': [],
            'price_anomalies': [],
            'pattern_anomalies': [],
            'summary': {}
        }
        
        if prices_df.empty:
            anomalies['summary'] = {
                'total_anomalies': 0,
                'severity': 'low',
                'message': 'No price data available'
            }
            return anomalies
        
        # Run all detectors
        volume_anomalies = self._detect_volume_anomalies(prices_df)
        price_anomalies = self._detect_price_anomalies(prices_df)
        pattern_anomalies = self._detect_patterns(prices_df)
        
        anomalies['volume_anomalies'] = volume_anomalies
        anomalies['price_anomalies'] = price_anomalies
        anomalies['pattern_anomalies'] = pattern_anomalies
        
        # Calculate summary
        total = len(volume_anomalies) + len(price_anomalies) + len(pattern_anomalies)
        anomalies['summary'] = {
            'total_anomalies': total,
            'severity': self._calculate_severity(total),
            'last_anomaly_date': self._get_last_anomaly_date(anomalies),
            'message': self._generate_message(total)
        }
        
        return anomalies
    
    def _detect_volume_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect unusual trading volume patterns."""
        anomalies = []
        
        if 'volume' not in df.columns:
            return anomalies
        
        # Calculate volume statistics
        df = df.copy()
        df['volume_sma_5'] = df['volume'].rolling(window=5).mean()
        df['volume_sma_10'] = df['volume'].rolling(window=10).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma_10']
        
        # Detect volume spikes (3x average or more)
        volume_spikes = df[df['volume_ratio'] >= self.volume_threshold]
        
        for date_idx, row in volume_spikes.iterrows():
            anomalies.append({
                'type': 'volume_spike',
                'date': date_idx.strftime('%Y-%m-%d') if hasattr(date_idx, 'strftime') else str(date_idx),
                'volume': int(row['volume']),
                'average_volume': int(row['volume_sma_10']),
                'ratio': round(row['volume_ratio'], 2),
                'severity': 'high' if row['volume_ratio'] >= 5 else 'medium' if row['volume_ratio'] >= 3 else 'low',
                'description': f"Khối lượng giao dịch tăng {row['volume_ratio']:.1f}x so với trung bình"
            })
        
        # Detect volume reversal (sharp drop after high volume)
        if len(df) >= 3:
            df['volume_change'] = df['volume'].pct_change()
            df['high_volume'] = df['volume_ratio'] >= 2.0
            
            for i in range(2, len(df)):
                if df['high_volume'].iloc[i-1] and df['volume_change'].iloc[i] < -0.5:
                    anomalies.append({
                        'type': 'volume_reversal',
                        'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                        'volume_drop': round(df['volume_change'].iloc[i] * 100, 1),
                        'description': "Khối lượng giao dịch giảm mạnh sau phiên giao dịch cao"
                    })
        
        return anomalies
    
    def _detect_price_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect unusual price movements."""
        anomalies = []
        
        if 'close' not in df.columns:
            return anomalies
        
        df = df.copy()
        df['daily_return'] = df['close'].pct_change()
        df['volatility_5d'] = df['daily_return'].rolling(window=5).std()
        df['volatility_10d'] = df['daily_return'].rolling(window=10).std()
        
        # Detect price spikes (5% or more in a day)
        price_spikes = df[df['daily_return'].abs() >= self.price_spike_threshold]
        
        for date_idx, row in price_spikes.iterrows():
            direction = 'TĂNG' if row['daily_return'] > 0 else 'GIẢM'
            anomalies.append({
                'type': 'price_spike',
                'date': date_idx.strftime('%Y-%m-%d') if hasattr(date_idx, 'strftime') else str(date_idx),
                'price_change_pct': round(row['daily_return'] * 100, 2),
                'close': round(row['close'], 2),
                'severity': 'high' if abs(row['daily_return']) >= 0.07 else 'medium',
                'description': f"Giá {direction} mạnh {abs(row['daily_return'] * 100):.1f}% trong ngày"
            })
        
        # Detect volatility spikes
        vol_spikes = df[df['volatility_5d'] >= self.volatility_threshold * df['volatility_10d'].shift(1)]
        
        for date_idx, row in vol_spikes.iterrows():
            if pd.notna(row['volatility_10d']) and row['volatility_10d'] > 0:
                anomalies.append({
                    'type': 'volatility_spike',
                    'date': date_idx.strftime('%Y-%m-%d') if hasattr(date_idx, 'strftime') else str(date_idx),
                    'volatility_ratio': round(row['volatility_5d'] / row['volatility_10d'], 2),
                    'description': "Biến động giá tăng đột ngột"
                })
        
        return anomalies
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect suspicious trading patterns."""
        anomalies = []
        
        if len(df) < 5:
            return anomalies
        
        df = df.copy()
        
        # Detect accumulation pattern (gradual volume increase with stable price)
        for i in range(5, len(df)):
            window = df.iloc[i-5:i]
            volume_trend = window['volume'].pct_change().mean()
            price_stability = window['close'].pct_change().std()
            
            if volume_trend > 0.1 and price_stability < 0.01:  # Volume up, price stable
                anomalies.append({
                    'type': 'accumulation_pattern',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'volume_trend': round(volume_trend * 100, 2),
                    'price_stability': round(price_stability * 100, 4),
                    'description': "Mô hình tích lũy: Volume tăng dần, giá ổn định (có thể là chuẩn bị tăng)"
                })
        
        # Detect distribution pattern (gradual volume increase with falling price)
        for i in range(5, len(df)):
            window = df.iloc[i-5:i]
            volume_trend = window['volume'].pct_change().mean()
            price_trend = window['close'].pct_change().mean()
            
            if volume_trend > 0.1 and price_trend < -0.005:  # Volume up, price falling
                anomalies.append({
                    'type': 'distribution_pattern',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'volume_trend': round(volume_trend * 100, 2),
                    'price_trend': round(price_trend * 100, 2),
                    'description': "Mô hình phân phối: Volume tăng dần, giá giảm (có thể là bán ra mạnh)"
                })
        
        # Detect momentum spike (consecutive gains/losses)
        for i in range(3, len(df)):
            window = df.iloc[i-3:i+1]
            consecutive_gains = (window['close'].pct_change() > 0).sum()
            consecutive_losses = (window['close'].pct_change() < 0).sum()
            
            if consecutive_gains >= 3:
                anomalies.append({
                    'type': 'momentum_run_up',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'consecutive_gains': consecutive_gains,
                    'description': "Mô hình tăng giá liên tiếp (3 ngày trở lên)"
                })
            elif consecutive_losses >= 3:
                anomalies.append({
                    'type': 'momentum_down',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'consecutive_losses': consecutive_losses,
                    'description': "Mô hình giảm giá liên tiếp (3 ngày trở lên)"
                })
        
        return anomalies
    
    def _calculate_severity(self, anomaly_count: int) -> str:
        """Calculate overall severity based on anomaly count."""
        if anomaly_count == 0:
            return 'low'
        elif anomaly_count <= 2:
            return 'medium'
        elif anomaly_count <= 5:
            return 'high'
        else:
            return 'critical'
    
    def _get_last_anomaly_date(self, anomalies: Dict[str, Any]) -> Optional[str]:
        """Get the date of the most recent anomaly."""
        all_dates = []
        
        for category in ['volume_anomalies', 'price_anomalies', 'pattern_anomalies']:
            for anomaly in anomalies.get(category, []):
                if 'date' in anomaly:
                    all_dates.append(anomaly['date'])
        
        return max(all_dates) if all_dates else None
    
    def _generate_message(self, anomaly_count: int) -> str:
        """Generate a summary message based on anomaly count."""
        if anomaly_count == 0:
            return "Không phát hiện bất thường nào. Thị trường ổn định."
        elif anomaly_count <= 2:
            return "Phát hiện một số bất thường nhỏ. Cần theo dõi sát."
        elif anomaly_count <= 5:
            return "Phát hiện nhiều bất thường. Đề nghị phân tích kỹ hơn."
        else:
            return "Phát hiện rất nhiều bất thường. Cần hành động ngay!"


def create_anomaly_table(db: Session) -> None:
    """Create anomaly detection results table if not exists."""
    from sqlalchemy import text
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS anomaly_detection (
        id SERIAL PRIMARY KEY,
        ticker_id INTEGER REFERENCES tickers(id) ON DELETE CASCADE,
        anomaly_type VARCHAR(50) NOT NULL,
        anomaly_date DATE NOT NULL,
        severity VARCHAR(20) NOT NULL,
        details JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        is_active BOOLEAN DEFAULT TRUE
    );
    
    CREATE INDEX IF NOT EXISTS idx_anomaly_ticker ON anomaly_detection(ticker_id);
    CREATE INDEX IF NOT EXISTS idx_anomaly_date ON anomaly_detection(anomaly_date);
    CREATE INDEX IF NOT EXISTS idx_anomaly_severity ON anomaly_detection(severity);
    """
    
    db.execute(text(create_table_sql))
    db.commit()
    logger.info("Anomaly detection table created/verified successfully")