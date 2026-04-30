"""Risk assessment data models"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class RiskLevel(str, Enum):
    """Standardized risk levels across all ISRMS modules"""
    CRITICAL = "CRITICAL"  # 80-100
    HIGH = "HIGH"          # 60-79
    MEDIUM = "MEDIUM"      # 40-59
    LOW = "LOW"            # 0-39

    @classmethod
    def from_score(cls, score: float) -> "RiskLevel":
        """Convert numeric score to risk level"""
        if score >= 80:
            return cls.CRITICAL
        elif score >= 60:
            return cls.HIGH
        elif score >= 40:
            return cls.MEDIUM
        else:
            return cls.LOW


@dataclass
class ThreatScore:
    """Threat score for a specific crime type"""
    crime_type: str
    score: float  # 0.0 to 1.0
    lambda_value: float
    county_multiplier: float
    state_multiplier: float
    debug_info: Dict


@dataclass
class FacilityRiskAssessment:
    """Facility-level risk assessment result"""
    facility_id: str
    facility_name: str
    timestamp: datetime
    risk_level: RiskLevel
    
    # NIBRS Scores
    nibrs_composite_score: float
    nibrs_crime_scores: Dict[str, float]  # {crime_type: score}
    
    # ASHER Scores (optional)
    asher_composite_score: Optional[float] = None
    asher_event_scores: Optional[Dict[str, float]] = None
    
    # Context
    population: int = 0
    square_footage: int = 0
    county: Optional[str] = None
    state: str = "idaho"
    
    # Recommendations
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


@dataclass
class SystemRiskAssessment:
    """System-level aggregated risk assessment"""
    timestamp: datetime
    overall_risk_level: RiskLevel
    average_score: float
    
    # Facility breakdown
    total_facilities: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    
    # Highest risk facilities
    highest_risk_facilities: List[str]
    
    # Aggregated crime risks
    crime_risk_summary: Dict[str, float]
    
    # Trend data
    trend: str  # "increasing", "decreasing", "stable"
    variance_from_forecast: Optional[float] = None