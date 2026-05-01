"""Security Assessment - Physical Security Criteria Evaluation

Conducts facility-level physical security assessments using standardized indicators.

Migrated from: C:\IRMS\Security Assessment\dashboard.py
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd


@dataclass
class SecurityIndicator:
    """Security assessment indicator"""
    indicator_id: str
    domain_code: str
    domain_name: str
    subdomain_code: str
    subdomain_name: str
    standard_text: str
    response_type: str
    default_weight: float
    risk_impact: str  # High, Medium, Low
    legal_reg_flag: bool
    active: bool


@dataclass
class SecurityAssessment:
    """Facility security assessment result"""
    assessment_id: str
    facility_name: str
    assessment_date: datetime
    total_risk_score: float
    domain_scores: Dict[str, float]
    adequacy_band: str
    indicators: List[Dict]


RISK_IMPACT_MULTIPLIER = {
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


def response_to_risk_factor(response: str) -> float:
    """
    Convert Y/N/N/A response to risk factor.
    
    Parameters
    ----------
    response : str
        Y (compliant), N (non-compliant), N/A (not applicable)
    
    Returns
    -------
    float
        Risk factor (0.0 = no risk, 1.0 = full risk)
    """
    r = (response or "").upper()
    if r == "Y":
        return 0.0  # Compliant = no risk
    if r == "N":
        return 1.0  # Non-compliant = full risk
    return 0.0  # N/A = ignore


def compute_indicator_score(
    default_weight: float,
    risk_impact: str,
    response: str,
) -> float:
    """
    Calculate risk score for a single indicator.
    
    Score = Weight × Impact_Multiplier × Risk_Factor
    
    Parameters
    ----------
    default_weight : float
        Indicator weight
    risk_impact : str
        High, Medium, or Low
    response : str
        Y/N/N/A
    
    Returns
    -------
    float
        Indicator risk score
    """
    impact_mult = RISK_IMPACT_MULTIPLIER.get(str(risk_impact), 2)
    resp_factor = response_to_risk_factor(response)
    return default_weight * impact_mult * resp_factor


def compute_domain_scores(
    indicators: List[Dict],
) -> Dict[str, float]:
    """
    Aggregate indicator scores by domain.
    
    Parameters
    ----------
    indicators : List[Dict]
        List of indicator results with keys: domain_code, indicator_score
    
    Returns
    -------
    dict
        {domain_code: total_domain_score}
    """
    domain_scores = {}
    
    for ind in indicators:
        domain = ind.get("domain_code")
        score = ind.get("indicator_score", 0.0)
        
        if domain not in domain_scores:
            domain_scores[domain] = 0.0
        
        domain_scores[domain] += score
    
    return domain_scores


def apply_adequacy_band(
    score: float,
    scoring_bands: pd.DataFrame,
    scope: str = "Facility",
) -> str:
    """
    Determine adequacy band based on risk score.
    
    Parameters
    ----------
    score : float
        Total risk score
    scoring_bands : pd.DataFrame
        Adequacy bands with columns: Scope, Band_Name, Min_Score, Max_Score
    scope : str
        "Facility" or "Domain"
    
    Returns
    -------
    str
        Adequacy band name (e.g., "Effective", "Limited Improvement", etc.)
    """
    if scoring_bands.empty:
        return "Not Rated"
    
    scope_df = scoring_bands[
        scoring_bands["Scope"].str.upper() == scope.upper()
    ]
    
    if scope_df.empty:
        return "Not Rated"
    
    for _, row in scope_df.iterrows():
        if row["Min_Score"] <= score <= row["Max_Score"]:
            return str(row["Band_Name"])
    
    return "Not Rated"


def conduct_security_assessment(
    facility_name: str,
    indicator_responses: Dict[str, str],
    indicators_df: pd.DataFrame,
    scoring_bands_df: pd.DataFrame,
) -> SecurityAssessment:
    """
    Conduct complete facility security assessment.
    
    Parameters
    ----------
    facility_name : str
        Facility identifier
    indicator_responses : dict
        {indicator_id: response (Y/N/N/A)}
    indicators_df : pd.DataFrame
        Security indicators master list
    scoring_bands_df : pd.DataFrame
        Adequacy scoring bands
    
    Returns
    -------
    SecurityAssessment
        Complete assessment result
    """
    indicator_results = []
    
    for ind_id, response in indicator_responses.items():
        ind_row = indicators_df[
            indicators_df["Indicator_ID"] == ind_id
        ]
        
        if ind_row.empty:
            continue
        
        ind_row = ind_row.iloc[0]
        
        score = compute_indicator_score(
            default_weight=float(ind_row["Default_Weight"]),
            risk_impact=str(ind_row["Risk_Impact"]),
            response=response,
        )
        
        indicator_results.append({
            "indicator_id": ind_id,
            "domain_code": ind_row["Domain_Code"],
            "domain_name": ind_row["Domain_Name"],
            "response": response,
            "indicator_score": score,
        })
    
    # Compute domain scores
    domain_scores = compute_domain_scores(indicator_results)
    
    # Compute total risk
    total_risk_score = sum(domain_scores.values())
    
    # Determine adequacy band
    adequacy_band = apply_adequacy_band(
        total_risk_score,
        scoring_bands_df,
        scope="Facility",
    )
    
    return SecurityAssessment(
        assessment_id=f"{facility_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        facility_name=facility_name,
        assessment_date=datetime.now(),
        total_risk_score=total_risk_score,
        domain_scores=domain_scores,
        adequacy_band=adequacy_band,
        indicators=indicator_results,
    )