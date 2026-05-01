"""NIBRS SVA data loading utilities

Loads facility_profile.xlsx sheets for NIBRS SVA analysis.

Migrated from: logic/load_data.py
"""

from pathlib import Path
from typing import Dict, Tuple
import pandas as pd


def load_all_sheets(data_path: Path) -> Dict[str, pd.DataFrame]:
    """Load all sheets from facility_profile.xlsx into a dict."""
    xls = pd.ExcelFile(data_path)

    sheets = {
        "metadata": pd.read_excel(xls, "metadata"),
        "population": pd.read_excel(xls, "population"),
        "staffing_security": pd.read_excel(xls, "staffing_security"),
        "threat_context": pd.read_excel(xls, "threat_context"),
        "vulnerability_context": pd.read_excel(xls, "vulnerability_context"),
        "services": pd.read_excel(xls, "services"),
        "FSL_factors": pd.read_excel(xls, "FSL_factors"),
        "LOP_factors": pd.read_excel(xls, "LOP_factors"),
        "county_pop": pd.read_excel(xls, "County - Pop"),
        "jurisdiction_pop": pd.read_excel(xls, "Jurisdiction - Pop"),
        "US_ASHER": pd.read_excel(xls, "US_ASHER"),
        "State_ASHER": pd.read_excel(xls, "State_ASHER"),
        "County_NIBRS": pd.read_excel(xls, "County_NIBRS"),
        "State_NIBRS": pd.read_excel(xls, "State_NIBRS"),
        "State_Crime": pd.read_excel(xls, "State Crime"),
        "County_Crime": pd.read_excel(xls, "County Crime"),
    }

    return sheets


def build_facility_context(sheets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Merge metadata, population, county_pop, jurisdiction_pop, and square footage
    into a single facility-level context table.

    Output columns:
        facility_id
        Hospital (legacy name for NIBRS)
        Hospital_Population
        Jurisdiction_Population
        County_Population
        Hospital_SqFt
    """
    meta = sheets["metadata"].copy()
    pop = sheets["population"].copy()
    county_pop = sheets["county_pop"].copy()
    juris_pop = sheets["jurisdiction_pop"].copy()

    # Normalize names
    meta.rename(columns={"facility_name": "Hospital"}, inplace=True)
    meta.rename(columns={"square_footage": "Hospital_SqFt"}, inplace=True)

    # Merge population (daytime population used for NIBRS exposure)
    merged = meta.merge(
        pop[["facility_id", "total_population_day"]],
        on="facility_id",
        how="left",
    )
    merged.rename(columns={"total_population_day": "Hospital_Population"}, inplace=True)

    # Merge county population
    merged = merged.merge(
        county_pop[["Hospital", "County_Population"]],
        on="Hospital",
        how="left",
    )

    # Merge jurisdiction population
    merged = merged.merge(
        juris_pop[["Hospital", "Jurisdiction_Population"]],
        on="Hospital",
        how="left",
    )

    # Final ordering
    merged = merged[
        [
            "facility_id",
            "Hospital",
            "Hospital_Population",
            "Jurisdiction_Population",
            "County_Population",
            "Hospital_SqFt",
            "county",
            "state",
        ]
    ]

    return merged


def build_model_1_rows(
    facility_context: pd.DataFrame,
    county_crime_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Expand facility_context × crime types to produce Model 1 rows.

    Output columns:
        Hospital
        Crime
        Hospital_Population
    """
    crimes = list(county_crime_df["Crime"].unique())

    rows = []
    for _, fac in facility_context.iterrows():
        for crime in crimes:
            rows.append(
                {
                    "Hospital": fac["Hospital"],
                    "Crime": crime,
                    "Hospital_Population": fac["Hospital_Population"],
                }
            )

    return pd.DataFrame(rows)


def build_model_2_rows(
    facility_context: pd.DataFrame,
    county_crime_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Expand facility_context × crime types to produce Model 2 V3 rows.

    Output columns:
        Hospital
        Crime
        Hospital_Population
        Jurisdiction_Population
        County_Population
        Hospital_SqFt
    """
    crimes = list(county_crime_df["Crime"].unique())

    rows = []
    for _, fac in facility_context.iterrows():
        for crime in crimes:
            rows.append(
                {
                    "Hospital": fac["Hospital"],
                    "Crime": crime,
                    "Hospital_Population": fac["Hospital_Population"],
                    "Jurisdiction_Population": fac["Jurisdiction_Population"],
                    "County_Population": fac["County_Population"],
                    "Hospital_SqFt": fac["Hospital_SqFt"],
                }
            )

    return pd.DataFrame(rows)


def load_nibrs_data(data_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    High-level loader for NIBRS SVA dashboards.
    
    Parameters
    ----------
    data_path : Path
        Path to facility_profile.xlsx
    
    Returns
    -------
    facility_context : pd.DataFrame
        Facility-level context
    model_1_rows : pd.DataFrame
        Hospital × Crime for Model 1
    model_2_rows : pd.DataFrame
        Hospital × Crime with full context for Model 2
    """
    sheets = load_all_sheets(data_path)

    facility_context = build_facility_context(sheets)
    model_1_rows = build_model_1_rows(facility_context, sheets["County_Crime"])
    model_2_rows = build_model_2_rows(facility_context, sheets["County_Crime"])

    return facility_context, model_1_rows, model_2_rows