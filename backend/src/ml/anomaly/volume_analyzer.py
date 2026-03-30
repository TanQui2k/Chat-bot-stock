"""Volume Anomaly Analyzer for Stock Trading System."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class VolumeAnomalyAnalyzer:
    """
    Advanced volume analysis for detecting unusual trading patterns.
    Focuses on identifying accumulation, distribution, and volume spikes.
    """
    
    def __init__(
        self,
        volume_threshold: float = 3.0,
        volume_spike_threshold: float = 5.0,
        volume_drop_threshold: float = 0.5
    ):
        """
        Initialize volume analyzer.
        
        Args:
            volume_threshold: Multiplier for average volume to flag as anomaly (default: 3x)
            volume_spike_threshold: Multiplier for severe volume spike (default: 5x)
            volume_drop_threshold: Threshold for volume drop after spike (default: 0.5 = 50%)
        """
        self.volume_threshold = volume_threshold
        self.volume_spike_threshold = volume_spike_threshold
        self.volume_drop_threshold = volume_drop_threshold
    
    def analyze_volume(
        self,
        prices_df: pd.DataFrame,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Perform comprehensive volume analysis.
        
        Args:
            prices_df: DataFrame with 'close', 'volume' columns
            lookback_days: Number of days to analyze
            
        Returns:
            Dictionary containing volume analysis results
        """
        if prices_df.empty or 'volume' not in prices_df.columns:
            return {
                'success': False,
                'message': 'No volume data available',
                'anomalies': [],
                'metrics': {}
            }
        
        df = prices_df.copy().tail(lookback_days)
        df = df.sort_index()  # Ensure ascending order
        
        # Calculate volume statistics
        df['volume_sma_5'] = df['volume'].rolling(window=5).mean()
        df['volume_sma_10'] = df['volume'].rolling(window=10).mean()
        df['volume_sma_20'] = df['volume'].rolling(window=20).mean()
        df['volume_std'] = df['volume'].rolling(window=10).std()
        df['volume_ratio_5'] = df['volume'] / df['volume_sma_5']
        df['volume_ratio_10'] = df['volume'] / df['volume_sma_10']
        df['volume_zscore'] = (df['volume'] - df['volume_sma_10']) / df['volume_std']
        
        # Detect anomalies
        anomalies = self._detect_volume_anomalies(df)
        patterns = self._detect_volume_patterns(df)
        
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
    
    def _detect_volume_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect specific volume anomalies."""
        anomalies = []
        
        for i, (date_idx, row) in enumerate(df.iterrows()):
            # Volume spike detection
            if row['volume_ratio_10'] >= self.volume_threshold:
                severity = self._get_severity(row['volume_ratio_10'])
                anomalies.append({
                    'type': 'volume_spike',
                    'date': date_idx.strftime('%Y-%m-%d') if hasattr(date_idx, 'strftime') else str(date_idx),
                    'volume': int(row['volume']),
                    'average_volume': int(row['volume_sma_10']),
                    'ratio': round(row['volume_ratio_10'], 2),
                    'severity': severity,
                    'zscore': round(row['volume_zscore'], 2),
                    'description': f"Khối lượng giao dịch tăng {row['volume_ratio_10']:.1f}x so với trung bình 10 ngày"
                })
            
            # Volume reversal (drop after high volume)
            if i >= 1:
                prev_row = df.iloc[i-1]
                if (prev_row['volume_ratio_10'] >= 2.0 and 
                    row['volume_ratio_10'] <= 0.5):
                    anomalies.append({
                        'type': 'volume_reversal',
                        'date': date_idx.strftime('%Y-%m-%d') if hasattr(date_idx, 'strftime') else str(date_idx),
                        'previous_ratio': round(prev_row['volume_ratio_10'], 2),
                        'current_ratio': round(row['volume_ratio_10'], 2),
                        'drop_pct': round((1 - row['volume_ratio_10'] / prev_row['volume_ratio_10']) * 100, 1),
                        'description': "Khối lượng giảm mạnh sau phiên giao dịch cao"
                    })
        
        return anomalies
    
    def _detect_volume_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect volume-based trading patterns."""
        patterns = []
        
        # Accumulation pattern (gradual volume increase with stable price)
        for i in range(5, len(df)):
            window = df.iloc[i-5:i]
            volume_trend = window['volume_ratio_10'].mean()
            price_volatility = window['close'].pct_change().std() if 'close' in window.columns else 0
            
            if volume_trend > 1.2 and price_volatility < 0.01:
                patterns.append({
                    'type': 'accumulation',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'volume_trend': round(volume_trend, 2),
                    'price_volatility': round(price_volatility * 100, 2),
                    'confidence': 'high' if volume_trend > 1.5 else 'medium',
                    'description': "Mô hình tích lũy: Volume tăng dần, giá ổn định (có thể là chuẩn bị tăng)"
                })
        
        # Distribution pattern (gradual volume increase with falling price)
        for i in range(5, len(df)):
            window = df.iloc[i-5:i]
            volume_trend = window['volume_ratio_10'].mean()
            price_trend = window['close'].pct_change().mean() if 'close' in window.columns else 0
            
            if volume_trend > 1.2 and price_trend < -0.003:
                patterns.append({
                    'type': 'distribution',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'volume_trend': round(volume_trend, 2),
                    'price_trend': round(price_trend * 100, 2),
                    'confidence': 'high' if volume_trend > 1.5 else 'medium',
                    'description': "Mô hình phân phối: Volume tăng dần, giá giảm (có thể là bán ra mạnh)"
                })
        
        # Breakout volume pattern
        for i in range(10, len(df)):
            window = df.iloc[i-10:i]
            current = df.iloc[i]
            
            # Check for price breakout
            if 'close' in window.columns:
                price_max = window['close'].max()
                price_current = current['close']
                price_change = (price_current - price_max) / price_max if price_max > 0 else 0
                
                if price_change > 0.03 and current['volume_ratio_10'] > 2:
                    patterns.append({
                        'type': 'breakout_volume',
                        'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                        'price_change': round(price_change * 100, 2),
                        'volume_ratio': round(current['volume_ratio_10'], 2),
                        'description': "Khối lượng tăng mạnh khi giá突破 ngưỡng"
                    })
        
        return patterns
    
    def _get_severity(self, volume_ratio: float) -> str:
        """Determine severity based on volume ratio."""
        if volume_ratio >= self.volume_spike_threshold:
            return 'critical'
        elif volume_ratio >= 5:
            return 'high'
        elif volume_ratio >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary volume metrics."""
        metrics = {}
        
        if 'volume' not in df.columns:
            return metrics
        
        # Basic statistics
        metrics['total_volume'] = int(df['volume'].sum())
        metrics['avg_volume'] = int(df['volume'].mean())
        metrics['max_volume'] = int(df['volume'].max())
        metrics['min_volume'] = int(df['volume'].min())
        
        # Volume metrics
        metrics['volume_std'] = round(df['volume'].std(), 2)
        metrics['volume_cv'] = round(df['volume'].std() / df['volume'].mean(), 4) if df['volume'].mean() > 0 else 0
        
        # Ratio metrics
        if 'volume_ratio_10' in df.columns:
            metrics['avg_volume_ratio'] = round(df['volume_ratio_10'].mean(), 2)
            metrics['max_volume_ratio'] = round(df['volume_ratio_10'].max(), 2)
        
        # Volume trends
        if len(df) >= 5:
            recent = df.tail(5)
            metrics['recent_volume_trend'] = round(
                (recent['volume'].iloc[-1] / recent['volume'].iloc[0] - 1) * 100, 2
            ) if recent['volume'].iloc[0] > 0 else 0
        
        return metrics
    
    def get_volume_report(self, symbol: str, prices_df: pd.DataFrame) -> str:
        """Generate human-readable volume report."""
        analysis = self.analyze_volume(prices_df)
        
        if not analysis['success']:
            return f"Không thể phân tích khối lượng cho {symbol}: {analysis.get('message', 'Unknown error')}"
        
        lines = [
            f"=== BÁO CÁO KHỐI LƯỢNG: {symbol} ===",
            f"Thời gian: {analysis['date_range']['start']} đến {analysis['date_range']['end']}",
            "",
            "## Thông số khối lượng",
            f"- Tổng khối lượng: {analysis['metrics'].get('total_volume', 0):,} cổ phiếu",
            f"- Khối lượng trung bình: {analysis['metrics'].get('avg_volume', 0):,} cổ phiếu",
            f"- Khối lượng cao nhất: {analysis['metrics'].get('max_volume', 0):,} cổ phiếu",
            f"- Biến động khối lượng (CV): {analysis['metrics'].get('volume_cv', 0)}",
            ""
        ]
        
        if analysis['anomalies']:
            lines.append("## Phát hiện bất thường")
            for anomaly in analysis['anomalies'][:5]:  # Top 5
                lines.append(f"- [{anomaly['severity'].upper()}] {anomaly['type']}: {anomaly['description']}")
            lines.append("")
        
        if analysis['patterns']:
            lines.append("## Mô hình phát hiện")
            for pattern in analysis['patterns'][:5]:
                lines.append(f"- {pattern['type']}: {pattern['description']}")
            lines.append("")
        
        return "\n".join(lines)