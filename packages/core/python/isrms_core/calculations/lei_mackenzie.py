"""Lei-Mackenzie Threat Model - Standardized Implementation

This is the canonical implementation used across all ISRMS modules.
Migrated from NIBRS_SVA_Dashboard/logic/lei_mackenzie_model2_v3.py
"""

import math
from typing import Dict, Optional, Tuple
import pandas as pd

from ..models import ThreatScore


def calculate_lei_mackenzie_threat(
    hospital_pop: float,
    county_name: Optional[str] = None,
    state_name: str = "idaho",
    calibration_factor: float = 0.01,
    crime_data_df: Optional[pd.DataFrame] = None,
    county_crime_df: Optional[pd.DataFrame] = None,
) -> Tuple[Dict[str, ThreatScore], Dict]:
    """
    Calculate Lei-Mackenzie threat scores for all crime types.
    
    Formula:
        T_c = 1 - exp(-lambda_c)
        
        lambda_c = nat_rate_per_capita_c 
                   × hospital_pop 
                   × state_multiplier_c 
                   × county_multiplier_c 
                   × calibration_factor
    
    Parameters
    ----------
    hospital_pop : float
        Facility population (day population)
    county_name : str, optional
        County name for county-specific multiplier
    state_name : str
        State identifier (default: "idaho")
    calibration_factor : float
        Tuning factor (default: 0.01)
    crime_data_df : pd.DataFrame, optional
        State-level crime data. If None, loads from default location.
    county_crime_df : pd.DataFrame, optional
        County-level crime data. If None, loads from default location.
    
    Returns
    -------
    threat_scores : Dict[str, ThreatScore]
        {crime_type: ThreatScore object}
    debug : Dict
        Detailed debug information per crime
    """
    
    # Load data if not provided
    if crime_data_df is None or county_crime_df is None:
        from ..utils.data_loader import load_crime_data
        crime_data_df, county_crime_df = load_crime_data()
    
    # Get state population (use as proxy for US pop in single-state case)
    us_pop = 330_000_000  # Default US population
    
    threat_scores: Dict[str, ThreatScore] = {}
    debug: Dict[str, Dict] = {}
    
    for _, row in crime_data_df.iterrows():
        crime = str(row["Crime"]).strip()
        state_count = float(row["Number of Reported Crimes"])
        
        # National rate (using state as proxy)
        nat_rate_per_capita_c = state_count / us_pop if us_pop > 0 else 0.0
        
        # State multiplier (always 1.0 for single-state)
        state_multiplier_c = 1.0
        
        # County multiplier
        county_multiplier_c = 1.0
        county_count = 0.0
        
        if county_name and county_crime_df is not None:
            # Get county-specific crime rate
            county_row = county_crime_df[
                (county_crime_df["Crime"] == crime) & 
                (county_crime_df["County"] == county_name)
            ]
            if not county_row.empty:
                county_count = float(county_row.iloc[0]["Count"])
                # Calculate multiplier based on county vs state rate
                if state_count > 0:
                    county_multiplier_c = county_count / state_count
        
        # Calculate lambda
        lam_c = (
            nat_rate_per_capita_c 
            * hospital_pop 
            * state_multiplier_c 
            * county_multiplier_c 
            * calibration_factor
        )
        
        # Calculate threat probability
        T_c = 1.0 - math.exp(-lam_c) if lam_c > 0 else 0.0
        T_c = max(0.0, min(1.0, T_c))  # Clamp to [0, 1]
        
        # Create ThreatScore object
        threat_scores[crime] = ThreatScore(
            crime_type=crime,
            score=T_c,
            lambda_value=lam_c,
            county_multiplier=county_multiplier_c,
            state_multiplier=state_multiplier_c,
            debug_info={
                "state_count": state_count,
                "county_count": county_count,
                "nat_rate_per_capita": nat_rate_per_capita_c,
            }
        )
        
        debug[crime] = {
            "state_count": state_count,
            "county_count": county_count,
            "county_name": county_name or "N/A",
            "nat_rate_per_capita_c": nat_rate_per_capita_c,
            "state_multiplier_c": state_multiplier_c,
            "county_multiplier_c": county_multiplier_c,
            "lambda_c": lam_c,
            "T_c": T_c,
        }
    
    return threat_scores, debug