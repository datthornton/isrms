"""System-level risk aggregation functions"""

from typing import List
from datetime import datetime

from ..models import FacilityRiskAssessment, SystemRiskAssessment, RiskLevel


def aggregate_system_risk(
    facilities: List[FacilityRiskAssessment]
) -> SystemRiskAssessment:
    """
    Aggregate facility-level risks to system-level assessment.
    
    Parameters
    ----------
    facilities : List[FacilityRiskAssessment]
        List of facility risk assessments
    
    Returns
    -------
    SystemRiskAssessment
        Aggregated system-level risk
    """
    if not facilities:
        return SystemRiskAssessment(
            timestamp=datetime.now(),
            overall_risk_level=RiskLevel.LOW,
            average_score=0.0,
            total_facilities=0,
            critical_count=0,
            high_count=0,
            medium_count=0,
            low_count=0,
            highest_risk_facilities=[],
            crime_risk_summary={},
            trend="stable",
        )
    
    # Count by risk level
    critical_count = sum(1 for f in facilities if f.risk_level == RiskLevel.CRITICAL)
    high_count = sum(1 for f in facilities if f.risk_level == RiskLevel.HIGH)
    medium_count = sum(1 for f in facilities if f.risk_level == RiskLevel.MEDIUM)
    low_count = sum(1 for f in facilities if f.risk_level == RiskLevel.LOW)
    
    # Calculate average score
    avg_score = sum(f.nibrs_composite_score for f in facilities) / len(facilities)
    
    # Determine overall risk level
    if critical_count > 0:
        overall_risk = RiskLevel.CRITICAL
    elif high_count > len(facilities) * 0.25:  # More than 25% high risk
        overall_risk = RiskLevel.HIGH
    elif avg_score >= 40:
        overall_risk = RiskLevel.MEDIUM
    else:
        overall_risk = RiskLevel.LOW
    
    # Get highest risk facilities (top 5)
    sorted_facilities = sorted(
        facilities, 
        key=lambda f: f.nibrs_composite_score, 
        reverse=True
    )
    highest_risk = [f.facility_name for f in sorted_facilities[:5]]
    
    # Aggregate crime risks
    crime_summary = {}
    for facility in facilities:
        for crime, score in facility.nibrs_crime_scores.items():
            if crime not in crime_summary:
                crime_summary[crime] = []
            crime_summary[crime].append(score)
    
    crime_risk_summary = {
        crime: sum(scores) / len(scores) 
        for crime, scores in crime_summary.items()
    }
    
    return SystemRiskAssessment(
        timestamp=datetime.now(),
        overall_risk_level=overall_risk,
        average_score=avg_score,
        total_facilities=len(facilities),
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        highest_risk_facilities=highest_risk,
        crime_risk_summary=crime_risk_summary,
        trend="stable",  # Would need historical data to determine
    )