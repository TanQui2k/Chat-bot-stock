"""Price Anomaly Analyzer for Stock Trading System."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class PriceAnomalyAnalyzer:
    """
    Advanced price analysis for detecting unusual price movements.
    Focuses on identifying price spikes, volatility changes, and trend patterns.
    """
    
    def __init__(
        self,
        price_spike_threshold: float = 0.05,
        volatility_threshold: float = 2.0,
        trend_threshold: float = 0.03
    ):
        """
        Initialize price analyzer.
        
        Args:
            price_spike_threshold: Price change threshold for spike detection (default: 5%)
            volatility_threshold: Volatility multiplier for spike detection (default: 2x)
            trend_threshold: Threshold for trend detection (default: 3%)
        """
        self.price_spike_threshold = price_spike_threshold
        self.volatility_threshold = volatility_threshold
        self.trend_threshold = trend_threshold
    
    def analyze_price(
        self,
        prices_df: pd.DataFrame,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Perform comprehensive price analysis.
        
        Args:
            prices_df: DataFrame with 'close' column
            lookback_days: Number of days to analyze
            
        Returns:
            Dictionary containing price analysis results
        """
        if prices_df.empty or 'close' not in prices_df.columns:
            return {
                'success': False,
                'message': 'No price data available',
                'anomalies': [],
                'metrics': {}
            }
        
        df = prices_df.copy().tail(lookback_days)
        df = df.sort_index()
        
        # Calculate price statistics
        df['daily_return'] = df['close'].pct_change()
        df['daily_return_abs'] = df['daily_return'].abs()
        df['volatility_5d'] = df['daily_return'].rolling(window=5).std()
        df['volatility_10d'] = df['daily_return'].rolling(window=10).std()
        df['volatility_20d'] = df['daily_return'].rolling(window=20).std()
        df['price_sma_5'] = df['close'].rolling(window=5).mean()
        df['price_sma_10'] = df['close'].rolling(window=10).mean()
        df['price_sma_20'] = df['close'].rolling(window=20).mean()
        df['price_std'] = df['close'].rolling(window=10).std()
        df['zscore'] = (df['close'] - df['price_sma_10']) / df['price_std']
        df['bollinger_upper'] = df['price_sma_10'] + 2 * df['price_std']
        df['bollinger_lower'] = df['price_sma_10'] - 2 * df['price_std']
        
        # Detect anomalies
        anomalies = self._detect_price_anomalies(df)
        patterns = self._detect_price_patterns(df)
        
        # Calculate summary metrics
        metrics = self._calculate_metrics(df)
        
        return {
            'success': True,
            'symbol': prices_df.name if hasattr(prices_df, 'name') else 'Unknown',
            'date_range': {
                'start': str(df.index.min().date()) if hasattr(df.index.min(), 'date') else str(df.index.min()),
                'end': str(df.index.max().date()) if hasattr(df.index.max(), 'date') else str(df.index.max())
            },
            'anomalies': anomalies,
            'patterns': patterns,
            'metrics': metrics
        }
    
    def _detect_price_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect specific price anomalies."""
        anomalies = []
        
        for i, (date_idx, row) in enumerate(df.iterrows()):
            # Price spike detection (5% or more)
            if row['daily_return_abs'] >= self.price_spike_threshold:
                direction = 'TĂNG' if row['daily_return'] > 0 else 'GIẢM'
                severity = self._get_severity(row['daily_return_abs'])
                anomalies.append({
                    'type': 'price_spike',
                    'date': date_idx.strftime('%Y-%m-%d') if hasattr(date_idx, 'strftime') else str(date_idx),
                    'price_change_pct': round(row['daily_return'] * 100, 2),
                    'close': round(row['close'], 2),
                    'severity': severity,
                    'zscore': round(row['zscore'], 2),
                    'description': f"Giá {direction} mạnh {abs(row['daily_return'] * 100):.1f}% trong ngày"
                })
            
            # Volatility spike detection
            if (i >= 1 and 
                pd.notna(row['volatility_5d']) and 
                pd.notna(df.iloc[i-1]['volatility_10d']) and
                df.iloc[i-1]['volatility_10d'] > 0):
                vol_ratio = row['volatility_5d'] / df.iloc[i-1]['volatility_10d']
                if vol_ratio >= self.volatility_threshold:
                    anomalies.append({
                        'type': 'volatility_spike',
                        'date': date_idx.strftime('%Y-%m-%d') if hasattr(date_idx, 'strftime') else str(date_idx),
                        'volatility_ratio': round(vol_ratio, 2),
                        'current_vol': round(row['volatility_5d'] * 100, 2),
                        'previous_vol': round(df.iloc[i-1]['volatility_10d'] * 100, 2),
                        'description': "Biến động giá tăng đột ngột"
                    })
        
        return anomalies
    
    def _detect_price_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect price-based patterns."""
        patterns = []
        
        # Momentum run detection (consecutive gains/losses)
        for i in range(3, len(df)):
            window = df.iloc[i-3:i+1]
            consecutive_gains = (window['daily_return'] > 0).sum()
            consecutive_losses = (window['daily_return'] < 0).sum()
            
            if consecutive_gains >= 3:
                patterns.append({
                    'type': 'momentum_run_up',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'consecutive_gains': consecutive_gains,
                    'total_return': round(window['daily_return'].sum() * 100, 2),
                    'description': "Mô hình tăng giá liên tiếp (3 ngày trở lên)"
                })
            elif consecutive_losses >= 3:
                patterns.append({
                    'type': 'momentum_down',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'consecutive_losses': consecutive_losses,
                    'total_return': round(window['daily_return'].sum() * 100, 2),
                    'description': "Mô hình giảm giá liên tiếp (3 ngày trở lên)"
                })
        
        # Bollinger Band squeeze
        for i in range(10, len(df)):
            window = df.iloc[i-10:i]
            current = df.iloc[i]
            
            # Check for squeeze (narrow band)
            band_width = (current['bollinger_upper'] - current['bollinger_lower']) / current['price_sma_10'] if current['price_sma_10'] > 0 else 0
            
            # Previous band width
            prev_window = df.iloc[i-15:i-5]
            if len(prev_window) >= 5:
                prev_upper = prev_window['price_sma_10'] + 2 * prev_window['price_std']
                prev_lower = prev_window['price_sma_10'] - 2 * prev_window['price_std']
                prev_band_width = ((prev_upper - prev_lower) / prev_window['price_sma_10']).mean()
                
                if band_width < prev_band_width * 0.7:  # 30% narrower
                    patterns.append({
                        'type': 'bollinger_squeeze',
                        'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                        'band_width_pct': round(band_width * 100, 2),
                        'description': "Băng Bollinger hẹp (có thể là chuẩn bị bùng nổ)"
                    })
        
        # Reversal patterns
        for i in range(2, len(df)):
            window = df.iloc[i-2:i+1]
            
            # Morning star-like pattern (potential bottom)
            if (window['daily_return'].iloc[-3] < -0.03 and  # Large drop
                abs(window['daily_return'].iloc[-2]) < 0.02 and  # Doji/small
                window['daily_return'].iloc[-1] > 0.02):  # Large gain
                patterns.append({
                    'type': 'potential_reversal_bullish',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'description': "Mô hình đảo chiều tăng tiềm năng (mẫu sao sáng)"
                })
            
            # Evening star-like pattern (potential top)
            if (window['daily_return'].iloc[-3] > 0.03 and  # Large gain
                abs(window['daily_return'].iloc[-2]) < 0.02 and  # Doji/small
                window['daily_return'].iloc[-1] < -0.02):  # Large drop
                patterns.append({
                    'type': 'potential_reversal_bearish',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'description': "Mô hình đảo chiều giảm tiềm năng (mẫu sao tối)"
                })
        
        return patterns
    
    def _get_severity(self, price_change: float) -> str:
        """Determine severity based on price change."""
        if price_change >= 0.10:
            return 'critical'
        elif price_change >= 0.07:
            return 'high'
        elif price_change >= 0.05:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary price metrics."""
        metrics = {}
        
        if 'close' not in df.columns:
            return metrics
        
        # Price statistics
        metrics['start_price'] = round(df['close'].iloc[0], 2)
        metrics['end_price'] = round(df['close'].iloc[-1], 2)
        metrics['max_price'] = round(df['close'].max(), 2)
        metrics['min_price'] = round(df['close'].min(), 2)
        
        # Returns
        if len(df) >= 2:
            metrics['total_return'] = round((df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100, 2)
        
        # Volatility metrics
        if 'daily_return' in df.columns:
            metrics['avg_daily_return'] = round(df['daily_return'].mean() * 100, 2)
            metrics['volatility'] = round(df['daily_return'].std() * np.sqrt(252) * 100, 2)  # Annualized
            metrics['max_drawdown'] = round(self._calculate_max_drawdown(df) * 100, 2)
        
        # Price metrics
        metrics['price_std'] = round(df['close'].std(), 2)
        metrics['price_cv'] = round(df['close'].std() / df['close'].mean(), 4) if df['close'].mean() > 0 else 0
        
        return metrics
    
    def _calculate_max_drawdown(self, df: pd.DataFrame) -> float:
        """Calculate maximum drawdown."""
        if 'close' not in df.columns:
            return 0
        
        cumulative = df['close'] / df['close'].iloc[0]
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def get_price_report(self, symbol: str, prices_df: pd.DataFrame) -> str:
        """Generate human-readable price report."""
        analysis = self.analyze_price(prices_df)
        
        if not analysis['success']:
            return f"Không thể phân tích giá cho {symbol}: {analysis.get('message', 'Unknown error')}"
        
        lines = [
            f"=== BÁO CÁO GIÁ: {symbol} ===",
            f"Thời gian: {analysis['date_range']['start']} đến {analysis['date_range']['end']}",
            "",
            "## Thông số giá",
            f"- Giá đầu: {analysis['metrics'].get('start_price', 0):,.2f} VND",
            f"- Giá cuối: {analysis['metrics'].get('end_price', 0):,.2f} VND",
            f"- Giá cao nhất: {analysis['metrics'].get('max_price', 0):,.2f} VND",
            f"- Giá thấp nhất: {analysis['metrics'].get('min_price', 0):,.2f} VND",
            f"- Tổng lợi nhuận: {analysis['metrics'].get('total_return', 0):.2f}%",
            ""
        ]
        
        if analysis['metrics'].get('volatility'):
            lines.extend([
                "## Rủi ro & Biến động",
                f"- Biến động hàng ngày: {analysis['metrics']['avg_daily_return']:.2f}%",
                f"- Biến động annualized: {analysis['metrics']['volatility']:.2f}%",
                f"- Drawdown lớn nhất: {analysis['metrics']['max_drawdown']:.2f}%",
                ""
            ])
        
        if analysis['anomalies']:
            lines.append("## Phát hiện bất thường")
            for anomaly in analysis['anomalies'][:5]:
                lines.append(f"- [{anomaly['severity'].upper()}] {anomaly['type']}: {anomaly['description']}")
            lines.append("")
        
        if analysis['patterns']:
            lines.append("## Mô hình phát hiện")
            for pattern in analysis['patterns'][:5]:
                lines.append(f"- {pattern['type']}: {pattern['description']}")
            lines.append("")
        
        return "\n".join(lines)