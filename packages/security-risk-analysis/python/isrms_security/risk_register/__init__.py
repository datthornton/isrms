"""Risk Register Generator

Automated generation of facility and system-level risk registers.

Migrated from: logic/risk_register.py
"""

from pathlib import Path
from typing import List, Optional
import pandas as pd
from datetime import datetime

from isrms_core.models import FacilityRiskAssessment, SystemRiskAssessment


def generate_facility_risk_register(
    facility_id: str,
    nibrs_scores: dict,
    asher_scores: dict,
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Generate risk register for a single facility.
    
    Parameters
    ----------
    facility_id : str
        Facility identifier
    nibrs_scores : dict
        {crime_type: risk_score}
    asher_scores : dict
        {event_type: risk_score}
    output_path : Path, optional
        If provided, save to CSV
    
    Returns
    -------
    pd.DataFrame
        Risk register
    """
    records = []
    
    # NIBRS entries
    for crime, score in nibrs_scores.items():
        records.append({
            "Facility_ID": facility_id,
            "Hazard_Type": "NIBRS Crime",
            "Hazard": crime,
            "Risk_Score": score,
            "Risk_Level": _get_risk_level(score),
            "Timestamp": datetime.now().isoformat(),
        })
    
    # ASHER entries
    for event, score in asher_scores.items():
        records.append({
            "Facility_ID": facility_id,
            "Hazard_Type": "ASHER Event",
            "Hazard": event,
            "Risk_Score": score,
            "Risk_Level": _get_risk_level(score),
            "Timestamp": datetime.now().isoformat(),
        })
    
    df = pd.DataFrame(records)
    
    if output_path:
        df.to_csv(output_path, index=False)
    
    return df


def generate_system_risk_register(
    facilities: List[FacilityRiskAssessment],
    output_path: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Generate system-level risk register aggregating all facilities.
    
    Parameters
    ----------
    facilities : List[FacilityRiskAssessment]
        List of facility assessments
    output_path : Path, optional
        If provided, save to CSV
    
    Returns
    -------
    pd.DataFrame
        System-level risk register
    """
    records = []
    
    for facility in facilities:
        # Aggregate NIBRS risk
        nibrs_total = sum(facility.nibrs_crime_scores.values())
        
        # Aggregate ASHER risk
        asher_total = 0.0
        if facility.asher_event_scores:
            asher_total = sum(facility.asher_event_scores.values())
        
        records.append({
            "Facility_ID": facility.facility_id,
            "Facility_Name": facility.facility_name,
            "NIBRS_Aggregate_Risk": round(nibrs_total, 6),
            "ASHER_Aggregate_Risk": round(asher_total, 10),
            "Total_Risk": round(nibrs_total + asher_total, 6),
            "Risk_Level": facility.risk_level.value,
            "County": facility.county,
            "State": facility.state,
            "Timestamp": facility.timestamp.isoformat(),
        })
    
    df = pd.DataFrame(records)
    df = df.sort_values("Total_Risk", ascending=False)
    
    if output_path:
        df.to_csv(output_path, index=False)
    
    return df


def _get_risk_level(score: float) -> str:
    """Convert risk score to level."""
    score_100 = score * 100
    if score_100 >= 80:
        return "CRITICAL"
    elif score_100 >= 60:
        return "HIGH"
    elif score_100 >= 40:
        return "MEDIUM"
    else:
        return "LOW"