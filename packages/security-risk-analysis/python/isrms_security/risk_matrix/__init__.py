"""Risk Matrix - Combined ASHER + NIBRS Visualization

Migrated from: C:\IRMS\ASHER_NIBRS_Risk_Matrix
"""

from pathlib import Path
from typing import Optional, List, Dict
import pandas as pd
import math


def load_risk_matrix_data(
    asher_results: List[Dict],
    nibrs_results: List[Dict],
) -> pd.DataFrame:
    """
    Combine ASHER and NIBRS results into unified risk matrix format.
    
    Parameters
    ----------
    asher_results : List[Dict]
        ASHER risk results with keys: facility, event, threat, vulnerability,
        consequence, risk_score
    nibrs_results : List[Dict]
        NIBRS risk results with keys: facility, crime, threat, vulnerability,
        consequence, scaling, risk_score
    
    Returns
    -------
    pd.DataFrame
        Unified risk matrix data
    """
    combined_rows = []
    
    # Process ASHER results
    for result in asher_results:
        combined_rows.append({
            "Facility": result["facility"],
            "Hazard": result["event"],
            "Hazard_Type": "ASHER",
            "Model": "ASHER",
            "Model_Label": "ASHER Model 2 (TVC)",
            "Threat (T)": result["threat"],
            "Vulnerability (V)": result["vulnerability"],
            "Consequence (C)": result["consequence"],
            "Scaling (S)": 1.0,
            "Score": result["risk_score"],
            "R": result["risk_score"],
        })
    
    # Process NIBRS results
    for result in nibrs_results:
        combined_rows.append({
            "Facility": result["facility"],
            "Hazard": result["crime"],
            "Hazard_Type": "NIBRS",
            "Model": "NIBRS_Model2",
            "Model_Label": "NIBRS Model 2 V3 (TVC+S)",
            "Threat (T)": result["threat"],
            "Vulnerability (V)": result["vulnerability"],
            "Consequence (C)": result["consequence"],
            "Scaling (S)": result.get("scaling", 1.0),
            "Score": result["risk_score"],
            "R": result["risk_score"],
        })
    
    df = pd.DataFrame(combined_rows)
    
    # Add banding
    df["T_Band"] = df["Threat (T)"].apply(_band_probability)
    df["C_Band"] = df["Consequence (C)"].apply(_band_consequence)
    df["R_Band"] = df["R"].apply(_band_risk)
    
    # Add log transform for visualization
    df["log10_T"] = df["Threat (T)"].apply(
        lambda x: math.log10(x) if x > 0 else None
    )
    
    return df


def _band_probability(T: float) -> str:
    """Categorize threat probability."""
    if T < 1e-6:
        return "Very Low"
    if T < 1e-4:
        return "Low"
    if T < 1e-3:
        return "Moderate"
    if T < 1e-2:
        return "High"
    return "Very High"


def _band_consequence(C: float) -> str:
    """Categorize consequence."""
    if C < 0.2:
        return "Very Low"
    if C < 0.4:
        return "Low"
    if C < 0.6:
        return "Moderate"
    if C < 0.8:
        return "High"
    return "Very High"


def _band_risk(R: float) -> str:
    """Categorize overall risk."""
    if R < 0.05:
        return "Very Low"
    if R < 0.15:
        return "Low"
    if R < 0.30:
        return "Moderate"
    if R < 0.50:
        return "High"
    return "Very High"


def export_risk_matrix(
    df: pd.DataFrame,
    output_path: Path,
) -> None:
    """
    Export risk matrix data to CSV.
    
    Parameters
    ----------
    df : pd.DataFrame
        Risk matrix data
    output_path : Path
        Output CSV path
    """
    df.to_csv(output_path, index=False)