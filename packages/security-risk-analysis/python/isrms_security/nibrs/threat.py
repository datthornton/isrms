"""NIBRS Threat calculation using Lei-Mackenzie model

Migrated from: logic/lei_mackenzie_model2_v3.py
"""

import math
from pathlib import Path
from typing import Dict, Tuple
import pandas as pd


def calculate_nibrs_threat(
    hospital_pop: float,
    state_crime_df: pd.DataFrame,
    state_nibrs_df: pd.DataFrame,
    calibration_factor: float = 0.01,
    state_name: str = "idaho",
) -> Tuple[Dict[str, float], Dict]:
    """
    Lei-MacKenzie-style Threat T_c per crime type for NIBRS SVA V3.

    T_c = 1 - exp(-lambda_c)

    lambda_c = nat_rate_per_capita_c
               × hospital_pop
               × state_multiplier_c
               × calibration_factor

    Parameters
    ----------
    hospital_pop : float
        Facility population (Hospital_Population)
    state_crime_df : pd.DataFrame
        State Crime sheet from facility_profile.xlsx
    state_nibrs_df : pd.DataFrame
        State_NIBRS sheet from facility_profile.xlsx
    calibration_factor : float
        Tuning factor to bring probabilities into realistic range
    state_name : str
        State key in State_NIBRS (default "idaho")

    Returns
    -------
    threat_T : dict
        {crime_type: T_c in [0,1]}
    debug : dict
        Debug info: lambda_c, nat_rate_per_capita_c, state_multiplier_c
    """
    state_row = state_nibrs_df[
        state_nibrs_df["state"].str.lower() == state_name.lower()
    ].iloc[0]
    us_pop = float(state_row["population"])

    # Build national and state averages
    nat_avg_by_crime = {}
    state_avg_by_crime = {}
    
    for _, row in state_crime_df.iterrows():
        crime = str(row["Crime"]).strip()
        count = float(row["Number of Reported Crimes"])
        nat_avg_by_crime[crime] = count
        state_avg_by_crime[crime] = count

    threat_T: Dict[str, float] = {}
    debug: Dict[str, Dict] = {}

    for crime, nat_avg_c in nat_avg_by_crime.items():
        state_avg_c = state_avg_by_crime.get(crime, nat_avg_c)

        nat_rate_per_capita_c = nat_avg_c / us_pop if us_pop > 0 else 0.0

        if nat_avg_c > 0:
            state_multiplier_c = state_avg_c / nat_avg_c
        else:
            state_multiplier_c = 1.0

        lam_c = (
            nat_rate_per_capita_c * hospital_pop * state_multiplier_c * calibration_factor
        )

        T_c = 1.0 - math.exp(-lam_c) if lam_c > 0 else 0.0

        threat_T[crime] = max(0.0, min(1.0, T_c))
        debug[crime] = {
            "nat_avg_c": nat_avg_c,
            "state_avg_c": state_avg_c,
            "nat_rate_per_capita_c": nat_rate_per_capita_c,
            "state_multiplier_c": state_multiplier_c,
            "lambda_c": lam_c,
            "T_c": T_c,
        }

    return threat_T, debug