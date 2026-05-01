"""NIBRS SVA risk models

Migrated from:
- models/model_1_v3.py
- models/model_2_v3.py
"""

from typing import Dict, Any
import pandas as pd


# DOJ Harm Weights
_DOJ_HARM_RAW = {
    "Murder": 100,
    "Rape": 90,
    "Aggravated Assault": 80,
    "Robbery": 70,
    "Domestic Violence": 60,
    "Weapons Law Violations": 55,
    "Drug/Narcotic Violations": 50,
    "Simple Assault": 40,
    "Arson": 35,
    "Burglary": 30,
    "Motor Vehicle Theft": 25,
    "Theft": 20,
    "Law Violations": 15,
    "Traffic Law Violations": 10,
}

# Crime Scaling Factors
_CRIME_SCALING = {
    "Murder": 1.20,
    "Rape": 1.15,
    "Aggravated Assault": 1.10,
    "Domestic Violence": 1.10,
    "Weapons Law Violations": 1.10,
    "Drug/Narcotic Violations": 1.05,
    "Robbery": 1.00,
    "Simple Assault": 1.00,
    "Arson": 0.95,
    "Burglary": 0.90,
    "Motor Vehicle Theft": 0.85,
    "Theft": 0.80,
    "Law Violations": 0.80,
    "Traffic Law Violations": 0.70,
}


def compute_model_1_score(row: pd.Series) -> float:
    """
    Model 1 – Baseline population-only score.
    
    Uses:
    - Hospital population tier
    - Crime-specific weights
    
    Parameters
    ----------
    row : pd.Series
        Must contain "Hospital_Population" and "Crime"
    
    Returns
    -------
    float
        Baseline risk score
    """
    try:
        population = float(row["Hospital_Population"])
        crime_type = row["Crime"]
    except (KeyError, TypeError, ValueError):
        return 0.0

    # Population tier
    if population < 1000:
        base_score = 1
    elif population < 5000:
        base_score = 2
    elif population < 10000:
        base_score = 3
    else:
        base_score = 4

    # Crime weight
    weight = {
        "Murder": 1.4,
        "Rape": 1.4,
        "Aggravated Assault": 1.2,
        "Robbery": 1.1,
        "Domestic Violence": 1.1,
        "Weapons Law Violations": 1.2,
        "Drug/Narcotic Violations": 1.1,
        "Simple Assault": 1.0,
        "Arson": 0.9,
        "Burglary": 0.9,
        "Motor Vehicle Theft": 0.9,
        "Theft": 0.8,
        "Law Violations": 0.7,
        "Traffic Law Violations": 0.6,
    }.get(crime_type, 1.0)

    return round(base_score * weight, 2)


def _get_consequence_from_harm(crime_type: str) -> float:
    """Get normalized consequence from DOJ harm weights."""
    if not _DOJ_HARM_RAW:
        return 0.5
    max_harm = max(_DOJ_HARM_RAW.values())
    raw = _DOJ_HARM_RAW.get(crime_type, 30)
    c = raw / max_harm if max_harm > 0 else 0.5
    return max(0.0, min(1.0, c))


def _get_vulnerability(row: pd.Series) -> float:
    """
    Calculate vulnerability using:
    - Jurisdiction_Population
    - Hospital_Population
    - Hospital_SqFt
    """
    try:
        j_pop = float(row["Jurisdiction_Population"])
        h_pop = float(row["Hospital_Population"])
        sqft = float(row["Hospital_SqFt"])
    except (KeyError, TypeError, ValueError):
        return 0.5

    v1 = min(j_pop / 250_000.0, 1.0)
    v2 = min(h_pop / 5_000.0, 1.0)
    v3 = min(sqft / 1_000_000.0, 1.0)

    V = (v1 + v2 + v3) / 3.0
    return max(0.0, min(1.0, V))


def _get_consequence(row: pd.Series, crime_type: str) -> float:
    """
    Calculate consequence using:
    - Hospital population
    - County population
    - Square footage
    - DOJ harm weight
    """
    try:
        h_pop = float(row["Hospital_Population"])
        c_pop = float(row["County_Population"])
        sqft = float(row["Hospital_SqFt"])
    except (KeyError, TypeError, ValueError):
        return 0.5

    c1 = min(h_pop / 5_000.0, 1.0)
    c2 = min(c_pop / 500_000.0, 1.0)
    c3 = min(sqft / 1_000_000.0, 1.0)

    C_base = 0.5 * c1 + 0.3 * c2 + 0.2 * c3

    harm_mult = _get_consequence_from_harm(crime_type)
    C_c = C_base * harm_mult

    return max(0.0, min(1.0, C_c))


def _get_scaling(crime_type: str) -> float:
    """Get crime-specific scaling factor."""
    return _CRIME_SCALING.get(crime_type, 1.0)


def compute_model_2_tvc(
    row: pd.Series,
    threat_score: Dict[str, float],
    enable_scaling: bool = True,
) -> Dict[str, Any]:
    """
    Model 2 V3 – TVC + Scaling.
    
    Risk = T × V × C × S
    
    Parameters
    ----------
    row : pd.Series
        Must contain Hospital, Crime, and facility context
    threat_score : Dict[str, float]
        {crime_type: threat_score}
    enable_scaling : bool
        Whether to apply crime-specific scaling
    
    Returns
    -------
    dict
        Components: threat, vulnerability, consequence, scaling, risk
    """
    crime_type = row["Crime"]

    T = float(threat_score.get(crime_type, 0.0))
    T = max(0.0, min(1.0, T))

    V = _get_vulnerability(row)
    C = _get_consequence(row, crime_type)
    S = _get_scaling(crime_type) if enable_scaling else 1.0

    risk_raw = T * V * C * S
    risk_clamped = max(0.0, min(1.0, risk_raw))

    return {
        "threat": T,
        "vulnerability": V,
        "consequence": C,
        "scaling": S,
        "risk": risk_clamped,
    }


def compute_model_2_score(
    row: pd.Series,
    threat_score: Dict[str, float],
    enable_scaling: bool = True,
) -> float:
    """
    Compute Model 2 V3 risk score.
    
    Parameters
    ----------
    row : pd.Series
        Facility × Crime row
    threat_score : Dict[str, float]
        Pre-computed threat scores
    enable_scaling : bool
        Whether to apply scaling
    
    Returns
    -------
    float
        Risk score (0.0 to 1.0)
    """
    tvcs = compute_model_2_tvc(row, threat_score, enable_scaling=enable_scaling)
    return round(tvcs["risk"], 6)