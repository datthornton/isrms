"""
Mobilization Indicator Tracker

Tracks and correlates threat mobilization indicators for early warning.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum


class ThreatLevel(Enum):
    """Threat level enumeration."""
    LOW = 1
    MODERATE = 2
    ELEVATED = 3
    HIGH = 4
    CRITICAL = 5


class IndicatorType(Enum):
    """Mobilization indicator types."""
    RECONNAISSANCE = "reconnaissance"
    RESOURCE_GATHERING = "resource_gathering"
    COMMUNICATIONS = "communications"
    POSITIONING = "positioning"
    CAPABILITY_DEVELOPMENT = "capability_development"


class MobilizationIndicatorTracker:
    """
    Tracks threat mobilization indicators and generates alerts.
    
    Monitors various indicators of threat actor mobilization including
    reconnaissance activity, resource gathering, communications patterns,
    and capability development.
    
    Attributes:
        indicators: List of tracked indicators
        thresholds: Alert thresholds for each indicator type
        alerts: Generated alerts based on indicator patterns
    """
    
    def __init__(self):
        """Initialize the mobilization indicator tracker."""
        self.indicators = []
        self.thresholds = {
            IndicatorType.RECONNAISSANCE: 0.6,
            IndicatorType.RESOURCE_GATHERING: 0.7,
            IndicatorType.COMMUNICATIONS: 0.5,
            IndicatorType.POSITIONING: 0.8,
            IndicatorType.CAPABILITY_DEVELOPMENT: 0.75,
        }
        self.alerts = []
        
    def add_indicator(
        self,
        indicator_type: IndicatorType,
        description: str,
        confidence: float,
        source: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Add a mobilization indicator observation.
        
        Args:
            indicator_type: Type of indicator observed
            description: Description of the indicator
            confidence: Confidence level (0-1)
            source: Intelligence source
            timestamp: Observation timestamp (defaults to now)
        """
        if not 0 <= confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        
        indicator = {
            "type": indicator_type,
            "description": description,
            "confidence": confidence,
            "source": source,
            "timestamp": timestamp or datetime.now()
        }
        
        self.indicators.append(indicator)
        self._check_thresholds(indicator_type, confidence)
        
    def _check_thresholds(self, indicator_type: IndicatorType, confidence: float) -> None:
        """
        Check if indicator exceeds alert threshold.
        
        Args:
            indicator_type: Type of indicator
            confidence: Confidence level
        """
        threshold = self.thresholds.get(indicator_type, 0.7)
        
        if confidence >= threshold:
            self._generate_alert(indicator_type, confidence)
            
    def _generate_alert(self, indicator_type: IndicatorType, confidence: float) -> None:
        """
        Generate an alert for high-confidence indicators.
        
        Args:
            indicator_type: Type of indicator triggering alert
            confidence: Confidence level
        """
        alert = {
            "timestamp": datetime.now(),
            "indicator_type": indicator_type,
            "confidence": confidence,
            "message": f"High-confidence {indicator_type.value} activity detected"
        }
        
        self.alerts.append(alert)
        
    def get_threat_level(self) -> ThreatLevel:
        """
        Calculate overall threat level based on indicators.
        
        Returns:
            Current threat level
        """
        if not self.indicators:
            return ThreatLevel.LOW
        
        # Calculate weighted average of recent indicators
        recent_indicators = self.indicators[-10:]  # Last 10 indicators
        avg_confidence = sum(i["confidence"] for i in recent_indicators) / len(recent_indicators)
        
        # Map confidence to threat level
        if avg_confidence >= 0.9:
            return ThreatLevel.CRITICAL
        elif avg_confidence >= 0.75:
            return ThreatLevel.HIGH
        elif avg_confidence >= 0.6:
            return ThreatLevel.ELEVATED
        elif avg_confidence >= 0.4:
            return ThreatLevel.MODERATE
        else:
            return ThreatLevel.LOW
            
    def get_indicators_summary(self) -> pd.DataFrame:
        """
        Get summary of all tracked indicators.
        
        Returns:
            DataFrame with indicator summary
        """
        if not self.indicators:
            return pd.DataFrame()
        
        data = []
        for indicator in self.indicators:
            data.append({
                "timestamp": indicator["timestamp"],
                "type": indicator["type"].value,
                "confidence": indicator["confidence"],
                "source": indicator["source"],
                "description": indicator["description"]
            })
        
        df = pd.DataFrame(data)
        return df.sort_values("timestamp", ascending=False).reset_index(drop=True)
        
    def get_alerts(self) -> List[Dict]:
        """
        Get all generated alerts.
        
        Returns:
            List of alert dictionaries
        """
        return sorted(self.alerts, key=lambda x: x["timestamp"], reverse=True)
        
    def correlate_indicators(self) -> Dict:
        """
        Correlate indicators to identify patterns.
        
        Returns:
            Dictionary with correlation analysis
        """
        if len(self.indicators) < 2:
            return {"patterns": [], "correlations": {}}
        
        # Group indicators by type
        by_type = {}
        for indicator in self.indicators:
            itype = indicator["type"]
            if itype not in by_type:
                by_type[itype] = []
            by_type[itype].append(indicator)
        
        # Identify patterns (simplified)
        patterns = []
        for itype, indicators_list in by_type.items():
            if len(indicators_list) >= 3:
                avg_conf = sum(i["confidence"] for i in indicators_list) / len(indicators_list)
                if avg_conf >= 0.7:
                    patterns.append({
                        "type": itype.value,
                        "count": len(indicators_list),
                        "avg_confidence": avg_conf,
                        "significance": "High" if avg_conf >= 0.8 else "Moderate"
                    })
        
        return {
            "patterns": patterns,
            "total_indicators": len(self.indicators),
            "threat_level": self.get_threat_level().name
        }
