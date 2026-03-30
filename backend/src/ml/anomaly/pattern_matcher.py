"""Pattern Matcher for Stock Trading System."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class PatternMatcher:
    """
    Technical pattern recognition for stock analysis.
    Detects common chart patterns and candlestick formations.
    """
    
    def __init__(
        self,
        momentum_threshold: float = 0.03,
        volume_threshold: float = 2.0,
        trend_days: int = 5
    ):
        """
        Initialize pattern matcher.
        
        Args:
            momentum_threshold: Threshold for momentum detection (default: 3%)
            volume_threshold: Volume multiplier for pattern confirmation (default: 2x)
            trend_days: Number of days for trend calculation (default: 5)
        """
        self.momentum_threshold = momentum_threshold
        self.volume_threshold = volume_threshold
        self.trend_days = trend_days
    
    def detect_patterns(
        self,
        prices_df: pd.DataFrame,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect all technical patterns in the price data.
        
        Args:
            prices_df: DataFrame with 'open', 'high', 'low', 'close', 'volume' columns
            lookback_days: Number of days to analyze
            
        Returns:
            Dictionary containing detected patterns
        """
        if prices_df.empty or 'close' not in prices_df.columns:
            return {
                'success': False,
                'message': 'No price data available',
                'patterns': [],
                'summary': {}
            }
        
        df = prices_df.copy().tail(lookback_days)
        df = df.sort_index()
        
        # Calculate necessary indicators
        df = self._calculate_indicators(df)
        
        # Detect all pattern types
        candlestick_patterns = self._detect_candlestick_patterns(df)
        trend_patterns = self._detect_trend_patterns(df)
        volume_patterns = self._detect_volume_patterns(df)
        support_resistance = self._detect_support_resistance(df)
        
        all_patterns = (
            candlestick_patterns + 
            trend_patterns + 
            volume_patterns + 
            support_resistance
        )
        
        # Sort by date (most recent first)
        all_patterns.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        summary = {
            'total_patterns': len(all_patterns),
            'by_category': {
                'candlestick': len(candlestick_patterns),
                'trend': len(trend_patterns),
                'volume': len(volume_patterns),
                'support_resistance': len(support_resistance)
            },
            'by_confidence': self._summarize_confidence(all_patterns)
        }
        
        return {
            'success': True,
            'symbol': prices_df.name if hasattr(prices_df, 'name') else 'Unknown',
            'date_range': {
                'start': str(df.index.min().date()) if hasattr(df.index.min(), 'date') else str(df.index.min()),
                'end': str(df.index.max().date()) if hasattr(df.index.max(), 'date') else str(df.index.max())
            },
            'patterns': all_patterns,
            'summary': summary
        }
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for pattern detection."""
        df = df.copy()
        
        # Moving averages
        df['sma_5'] = df['close'].rolling(window=5).mean()
        df['sma_10'] = df['close'].rolling(window=10).mean()
        df['sma_20'] = df['close'].rolling(window=20).mean()
        
        # Price momentum
        df['momentum_1d'] = df['close'].pct_change()
        df['momentum_3d'] = df['close'].pct_change(3)
        df['momentum_5d'] = df['close'].pct_change(5)
        
        # Volatility
        df['volatility_5d'] = df['momentum_1d'].rolling(window=5).std()
        
        # Volume
        if 'volume' in df.columns:
            df['volume_sma_10'] = df['volume'].rolling(window=10).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma_10']
        
        # High-Low range
        df['hl_range'] = (df['high'] - df['low']) / df['close']
        df['oc_range'] = (df['close'] - df['open']) / df['close']
        
        # Trend direction
        df['trend_direction'] = np.where(
            df['sma_5'] > df['sma_10'], 
            'bullish', 
            np.where(df['sma_5'] < df['sma_10'], 'bearish', 'neutral')
        )
        
        return df
    
    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect candlestick patterns."""
        patterns = []
        
        for i in range(2, len(df)):
            curr = df.iloc[i]
            prev1 = df.iloc[i-1]
            prev2 = df.iloc[i-2]
            
            # Hammer pattern (potential bullish reversal)
            if self._is_hammer(curr):
                patterns.append({
                    'type': 'hammer',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'confidence': 'high',
                    'description': "Mô hình búa (dự báo đảo chiều tăng)",
                    'pattern_location': 'bottom'
                })
            
            # Hanging man pattern (potential bearish reversal)
            if self._is_hanging_man(curr):
                patterns.append({
                    'type': 'hanging_man',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'confidence': 'medium',
                    'description': "Mô hình người treo cổ (dự báo đảo chiều giảm)",
                    'pattern_location': 'top'
                })
            
            # Bullish engulfing
            if (prev1['close'] < prev1['open'] and  # Bearish candle
                curr['close'] > curr['open'] and  # Bullish candle
                curr['close'] > prev1['open'] and
                curr['open'] < prev1['close']):
                patterns.append({
                    'type': 'bullish_engulfing',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'confidence': 'high',
                    'description': "Mô hình bao phủ tăng (dự báo đảo chiều tăng mạnh)"
                })
            
            # Bearish engulfing
            if (prev1['close'] > prev1['open'] and  # Bullish candle
                curr['close'] < curr['open'] and  # Bearish candle
                curr['close'] < prev1['open'] and
                curr['open'] > prev1['close']):
                patterns.append({
                    'type': 'bearish_engulfing',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'confidence': 'high',
                    'description': "Mô hình bao phủ giảm (dự báo đảo chiều giảm mạnh)"
                })
            
            # Morning star (potential bottom)
            if (prev2['close'] < prev2['open'] and  # Large bearish
                abs(curr['close'] - curr['open']) / curr['close'] < 0.01 and  # Small body (Doji)
                curr['close'] > prev1['close'] and
                curr['close'] > prev1['open'] and
                df.index[i] > df.index[i-2]):
                if i >= 2 and curr['close'] > prev2['open']:
                    patterns.append({
                        'type': 'morning_star',
                        'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                        'confidence': 'high',
                        'description': "Mô hình sao sáng (đảo chiều tăng mạnh)"
                    })
            
            # Evening star (potential top)
            if (prev2['close'] > prev2['open'] and  # Large bullish
                abs(curr['close'] - curr['open']) / curr['close'] < 0.01 and  # Small body
                curr['close'] < prev1['close'] and
                curr['close'] < prev1['open'] and
                df.index[i] > df.index[i-2]):
                if i >= 2 and curr['close'] < prev2['open']:
                    patterns.append({
                        'type': 'evening_star',
                        'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                        'confidence': 'high',
                        'description': "Mô hình sao tối (đảo chiều giảm mạnh)"
                    })
        
        return patterns
    
    def _is_hammer(self, row: pd.Series) -> bool:
        """Check if the candle is a hammer pattern."""
        body = abs(row['close'] - row['open'])
        wick_upper = row['high'] - max(row['open'], row['close'])
        wick_lower = min(row['open'], row['close']) - row['low']
        
        # Hammer: small body, long lower wick (at least 2x body)
        if body > 0 and wick_lower >= 2 * body:
            # Lower wick should be at least twice the upper wick
            if wick_lower >= 2 * wick_upper or wick_upper < 0.1 * body:
                return True
        return False
    
    def _is_hanging_man(self, row: pd.Series) -> bool:
        """Check if the candle is a hanging man pattern."""
        return self._is_hammer(row)
    
    def _detect_trend_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect trend-based patterns."""
        patterns = []
        
        # uptrend detection (higher highs and higher lows)
        for i in range(5, len(df)):
            window = df.iloc[i-5:i+1]
            
            # Count higher highs and higher lows
            hh = 0
            hl = 0
            for j in range(1, len(window)):
                if window['high'].iloc[j] > window['high'].iloc[j-1]:
                    hh += 1
                if window['low'].iloc[j] > window['low'].iloc[j-1]:
                    hl += 1
            
            if hh >= 3 and hl >= 3:
                patterns.append({
                    'type': 'uptrend',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'confidence': 'high' if hh >= 4 else 'medium',
                    'duration_days': 5,
                    'description': "Xu hướng tăng (các mức cao hơn và thấp hơn tăng)"
                })
            
            # downtrend detection (lower highs and lower lows)
            lh = 0
            ll = 0
            for j in range(1, len(window)):
                if window['high'].iloc[j] < window['high'].iloc[j-1]:
                    lh += 1
                if window['low'].iloc[j] < window['low'].iloc[j-1]:
                    ll += 1
            
            if lh >= 3 and ll >= 3:
                patterns.append({
                    'type': 'downtrend',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'confidence': 'high' if lh >= 4 else 'medium',
                    'duration_days': 5,
                    'description': "Xu hướng giảm (các mức cao hơn và thấp hơn giảm)"
                })
        
        return patterns
    
    def _detect_volume_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect volume-based patterns."""
        patterns = []
        
        if 'volume_ratio' not in df.columns:
            return patterns
        
        # Volume confirmation of trend
        for i in range(5, len(df)):
            curr = df.iloc[i]
            
            # Volume confirmation of uptrend
            if (curr['momentum_1d'] > self.momentum_threshold and  # Price up
                curr['volume_ratio'] > self.volume_threshold):  # Volume up
                patterns.append({
                    'type': 'volume_confirmation_uptrend',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'confidence': 'high' if curr['volume_ratio'] > 3 else 'medium',
                    'price_change': round(curr['momentum_1d'] * 100, 2),
                    'volume_ratio': round(curr['volume_ratio'], 2),
                    'description': "Khối lượng xác nhận xu hướng tăng"
                })
            
            # Volume confirmation of downtrend
            if (curr['momentum_1d'] < -self.momentum_threshold and  # Price down
                curr['volume_ratio'] > self.volume_threshold):  # Volume up
                patterns.append({
                    'type': 'volume_confirmation_downtrend',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'confidence': 'high' if curr['volume_ratio'] > 3 else 'medium',
                    'price_change': round(curr['momentum_1d'] * 100, 2),
                    'volume_ratio': round(curr['volume_ratio'], 2),
                    'description': "Khối lượng xác nhận xu hướng giảm"
                })
            
            # Divergence (price up but volume down)
            if (curr['momentum_1d'] > self.momentum_threshold and
                curr['volume_ratio'] < 0.8):
                patterns.append({
                    'type': 'volume_divergence_uptrend',
                    'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                    'confidence': 'medium',
                    'price_change': round(curr['momentum_1d'] * 100, 2),
                    'volume_ratio': round(curr['volume_ratio'], 2),
                    'description': "Giá tăng nhưng khối lượng giảm (mềm yếu)"
                })
        
        return patterns
    
    def _detect_support_resistance(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect support and resistance levels."""
        patterns = []
        
        # Calculate pivot points
        for i in range(5, len(df)):
            window = df.iloc[i-5:i+1]
            
            # Support level (local minimum)
            if i >= 3:
                prev_low = df['low'].iloc[i-1]
                curr_low = df['low'].iloc[i]
                next_low = df['low'].iloc[i+1] if i+1 < len(df) else float('inf')
                
                if curr_low < prev_low and curr_low < next_low:
                    patterns.append({
                        'type': 'support_level',
                        'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                        'level': round(curr_low, 2),
                        'confidence': 'high',
                        'description': "Mức giá hỗ trợ (đáy địa phương)"
                    })
            
            # Resistance level (local maximum)
            if i >= 3:
                prev_high = df['high'].iloc[i-1]
                curr_high = df['high'].iloc[i]
                next_high = df['high'].iloc[i+1] if i+1 < len(df) else 0
                
                if curr_high > prev_high and curr_high > next_high:
                    patterns.append({
                        'type': 'resistance_level',
                        'date': df.index[i].strftime('%Y-%m-%d') if hasattr(df.index[i], 'strftime') else str(df.index[i]),
                        'level': round(curr_high, 2),
                        'confidence': 'high',
                        'description': "Mức giá kháng cự (đỉnh địa phương)"
                    })
        
        return patterns
    
    def _summarize_confidence(self, patterns: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize pattern confidence levels."""
        summary = {'high': 0, 'medium': 0, 'low': 0}
        for pattern in patterns:
            conf = pattern.get('confidence', 'low')
            summary[conf] = summary.get(conf, 0) + 1
        return summary
    
    def get_pattern_report(self, symbol: str, prices_df: pd.DataFrame) -> str:
        """Generate human-readable pattern report."""
        analysis = self.detect_patterns(prices_df)
        
        if not analysis['success']:
            return f"Không thể phát hiện mẫu cho {symbol}: {analysis.get('message', 'Unknown error')}"
        
        lines = [
            f"=== BÁO CÁO MẪU: {symbol} ===",
            f"Thời gian: {analysis['date_range']['start']} đến {analysis['date_range']['end']}",
            "",
            "## Tổng hợp phát hiện",
            f"- Tổng số mẫu: {analysis['summary']['total_patterns']}",
            f"  + Mẫu nến: {analysis['summary']['by_category']['candlestick']}",
            f"  + Xu hướng: {analysis['summary']['by_category']['trend']}",
            f"  + Khối lượng: {analysis['summary']['by_category']['volume']}",
            f"  + Hỗ trợ/Kháng cự: {analysis['summary']['by_category']['support_resistance']}",
            f"  + Độ tin cậy cao: {analysis['summary']['by_confidence']['high']}",
            f"  + Độ tin cậy trung bình: {analysis['summary']['by_confidence']['medium']}",
            ""
        ]
        
        if analysis['patterns']:
            lines.append("## Các mẫu phát hiện")
            for pattern in analysis['patterns'][:10]:  # Top 10
                lines.append(f"- [{pattern['confidence'].upper()}] {pattern['type']}: {pattern['description']}")
            lines.append("")
        
        return "\n".join(lines)