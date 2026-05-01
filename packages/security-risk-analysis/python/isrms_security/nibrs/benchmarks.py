"""NIBRS SVA benchmarks

Migrated from: config/benchmarks.py
"""

from pathlib import Path
from typing import Dict
import pandas as pd


def get_national_benchmarks(us_asher_df: pd.DataFrame) -> Dict:
    """
    Derive national-level benchmarks.

    Parameters
    ----------
    us_asher_df : pd.DataFrame
        US_ASHER sheet from facility_profile.xlsx

    Returns
    -------
    dict
        Keys: population, asher_total
    """
    latest = us_asher_df.sort_values("Year").iloc[-1]

    asher_total = float(
        latest["ASE"]
        + latest["IED"]
        + latest["VBIED"]
        + latest["VRA"]
        + latest["IID"]
    )

    return {
        "population": 330_000_000,
        "asher_total": asher_total,
    }


def get_state_benchmarks(
    state_nibrs_df: pd.DataFrame,
    state_name: str = "idaho"
) -> Dict:
    """
    Derive state-level benchmarks.

    Parameters
    ----------
    state_nibrs_df : pd.DataFrame
        State_NIBRS sheet from facility_profile.xlsx
    state_name : str
        State identifier

    Returns
    -------
    dict
        Keys: population, crime_rate, unemployment_rate
    """
    row = state_nibrs_df[
        state_nibrs_df["state"].str.lower() == state_name.lower()
    ].iloc[0]

    population = float(row["population"])
    crime_rate_per_100k = float(row["NIBRS_A_crime_rate_per_100000"])
    unemployment_rate_per_100k = float(row["unemployment_rate_per_100000"])

    return {
        "population": population,
        "crime_rate": crime_rate_per_100k / 100_000.0,
        "unemployment_rate": unemployment_rate_per_100k / 100_000.0,
    }