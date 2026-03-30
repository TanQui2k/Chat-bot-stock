"""Alert Generator for Anomaly Detection System."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertGenerator:
    """
    Generate actionable alerts based on anomaly detection results.
    Prioritizes alerts by severity and provides context-aware notifications.
    """
    
    def __init__(
        self,
        severity_weights: Optional[Dict[str, int]] = None
    ):
        """
        Initialize alert generator.
        
        Args:
            severity_weights: Weight for each severity level (default: critical=10, high=5, medium=3, low=1)
        """
        self.severity_weights = severity_weights or {
            'critical': 10,
            'high': 5,
            'medium': 3,
            'low': 1
        }
    
    def generate_alerts(
        self,
        anomalies: Dict[str, Any],
        threshold: str = 'medium'
    ) -> List[Dict[str, Any]]:
        """
        Generate alerts from anomaly detection results.
        
        Args:
            anomalies: Anomaly detection results dictionary
            threshold: Minimum severity level for alerts ('low', 'medium', 'high', 'critical')
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        if not anomalies.get('success', True):
            return alerts
        
        symbol = anomalies.get('symbol', 'UNKNOWN')
        timestamp = anomalies.get('timestamp', datetime.now().isoformat())
        
        # Get minimum weight based on threshold
        min_weight = self.severity_weights.get(threshold, 1)
        
        # Process volume anomalies
        for anomaly in anomalies.get('volume_anomalies', []):
            if self._should_alert(anomaly, min_weight):
                alerts.append(self._create_alert(
                    symbol=symbol,
                    anomaly=anomaly,
                    category='volume',
                    timestamp=timestamp
                ))
        
        # Process price anomalies
        for anomaly in anomalies.get('price_anomalies', []):
            if self._should_alert(anomaly, min_weight):
                alerts.append(self._create_alert(
                    symbol=symbol,
                    anomaly=anomaly,
                    category='price',
                    timestamp=timestamp
                ))
        
        # Process pattern anomalies
        for anomaly in anomalies.get('pattern_anomalies', []):
            if self._should_alert(anomaly, min_weight):
                alerts.append(self._create_alert(
                    symbol=symbol,
                    anomaly=anomaly,
                    category='pattern',
                    timestamp=timestamp
                ))
        
        # Sort by severity (critical first)
        alerts.sort(key=lambda x: self.severity_weights.get(x['severity'], 0), reverse=True)
        
        return alerts
    
    def _should_alert(self, anomaly: Dict[str, Any], min_weight: int) -> bool:
        """Check if an anomaly should trigger an alert."""
        severity = anomaly.get('severity', 'low')
        return self.severity_weights.get(severity, 0) >= min_weight
    
    def _create_alert(
        self,
        symbol: str,
        anomaly: Dict[str, Any],
        category: str,
        timestamp: str
    ) -> Dict[str, Any]:
        """Create a formatted alert from an anomaly."""
        return {
            'id': None,  # Will be assigned by database
            'symbol': symbol,
            'category': category,
            'type': anomaly.get('type', 'unknown'),
            'date': anomaly.get('date', ''),
            'severity': anomaly.get('severity', 'low'),
            'description': anomaly.get('description', ''),
            'details': self._extract_details(anomaly, category),
            'timestamp': timestamp,
            'created_at': datetime.now().isoformat(),
            'is_active': True
        }
    
    def _extract_details(self, anomaly: Dict[str, Any], category: str) -> Dict[str, Any]:
        """Extract relevant details for the alert."""
        details = {}
        
        if category == 'volume':
            details['volume'] = anomaly.get('volume')
            details['ratio'] = anomaly.get('ratio')
            details['average_volume'] = anomaly.get('average_volume')
            details['zscore'] = anomaly.get('zscore')
        
        elif category == 'price':
            details['price_change_pct'] = anomaly.get('price_change_pct')
            details['close_price'] = anomaly.get('close')
            details['zscore'] = anomaly.get('zscore')
        
        elif category == 'pattern':
            details['pattern_type'] = anomaly.get('type')
            details['pattern_location'] = anomaly.get('pattern_location')
        
        # Add pattern-specific details
        if 'volume_trend' in anomaly:
            details['volume_trend'] = anomaly['volume_trend']
        if 'price_trend' in anomaly:
            details['price_trend'] = anomaly['price_trend']
        if 'consecutive_gains' in anomaly:
            details['consecutive_gains'] = anomaly['consecutive_gains']
        if 'consecutive_losses' in anomaly:
            details['consecutive_losses'] = anomaly['consecutive_losses']
        
        return details
    
    def generate_summary_alert(
        self,
        anomalies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a summary alert for all anomalies.
        
        Args:
            anomalies: Anomaly detection results
            
        Returns:
            Summary alert dictionary
        """
        summary = anomalies.get('summary', {})
        
        return {
            'type': 'summary',
            'date': anomalies.get('timestamp', datetime.now().isoformat()),
            'total_anomalies': summary.get('total_anomalies', 0),
            'severity': summary.get('severity', 'low'),
            'message': summary.get('message', ''),
            'last_anomaly_date': summary.get('last_anomaly_date')
        }
    
    def get_critical_alerts(
        self,
        anomalies: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get only critical severity alerts."""
        return self.generate_alerts(anomalies, threshold='critical')
    
    def get_high_priority_alerts(
        self,
        anomalies: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get high and critical severity alerts."""
        return self.generate_alerts(anomalies, threshold='high')
    
    def format_alert_for_display(
        self,
        alert: Dict[str, Any]
    ) -> str:
        """Format an alert for human-readable display."""
        severity_icons = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        icon = severity_icons.get(alert.get('severity', 'low'), '⚪')
        symbol = alert.get('symbol', 'UNKNOWN')
        desc = alert.get('description', '')
        date = alert.get('date', '')
        
        return f"{icon} [{symbol}] {date}: {desc}"
    
    def format_alerts_for_display(
        self,
        alerts: List[Dict[str, Any]],
        max_alerts: int = 10
    ) -> str:
        """Format multiple alerts for display."""
        if not alerts:
            return "Không có cảnh báo nào."
        
        lines = [
            f"=== CẢNH BÁO BẤT THƯỜNG ({len(alerts)} cảnh báo) ===",
            ""
        ]
        
        for alert in alerts[:max_alerts]:
            lines.append(self.format_alert_for_display(alert))
        
        return "\n".join(lines)