"""MCS Version 2 – Data Cleaning Utilities

Pre-processing and validation functions for MCS v2 input data.
Cleans raw Excel/CSV input files before simulation runs.

Migrated from: MCS Simulation Version 2/mcs_v2_clean.py
Changes from original:
- Removed hardcoded Windows paths
- Added type hints and docstrings
- Uses pandas for data validation
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Minimum required columns for bundle input data
_BUNDLE_REQUIRED_COLUMNS = {
    "bundle_id",
    "name",
    "estimated_cost",
    "expected_risk_reduction",
}

# Minimum required columns for scenario input data
_SCENARIO_REQUIRED_COLUMNS = {
    "scenario_id",
    "threat_name",
    "asset_value",
    "exposure_factor_min",
    "exposure_factor_mode",
    "exposure_factor_max",
    "aro_min",
    "aro_mode",
    "aro_max",
}


def clean_simulation_data(
    df: pd.DataFrame,
    required_columns: Optional[set[str]] = None,
    drop_duplicates_on: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Clean and validate a simulation input DataFrame.

    Steps applied:
    1. Normalise column names (strip whitespace, lowercase, underscores).
    2. Drop rows where all values are NaN.
    3. Validate required columns are present.
    4. Coerce numeric columns to float, replacing non-numeric with NaN.
    5. Drop duplicate rows (optional).
    6. Log a summary of the cleaning results.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw input DataFrame to clean.
    required_columns : set[str], optional
        Column names that must be present. Raises ``ValueError`` if missing.
    drop_duplicates_on : list[str], optional
        Subset of column names for duplicate detection.

    Returns
    -------
    pandas.DataFrame
        Cleaned DataFrame.

    Raises
    ------
    ValueError
        If required columns are missing from the cleaned DataFrame.
    """
    original_rows = len(df)

    # Step 1: Normalise column names
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

    # Step 2: Drop fully-empty rows
    df.dropna(how="all", inplace=True)

    # Step 3: Validate required columns
    if required_columns:
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"Input data is missing required columns: {missing}")

    # Step 4: Coerce numeric columns
    for col in df.columns:
        if col not in {"scenario_id", "bundle_id", "name", "threat_name", "tags"}:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Step 5: Drop duplicate rows
    if drop_duplicates_on:
        before_dedup = len(df)
        df.drop_duplicates(subset=drop_duplicates_on, inplace=True)
        dropped = before_dedup - len(df)
        if dropped:
            logger.info("Dropped %d duplicate rows.", dropped)

    # Step 6: Log summary
    final_rows = len(df)
    logger.info(
        "Data cleaning complete: %d → %d rows (%d dropped).",
        original_rows,
        final_rows,
        original_rows - final_rows,
    )

    return df.reset_index(drop=True)


def clean_bundle_data(path: Path) -> pd.DataFrame:
    """Load and clean bundle configuration data from an Excel or CSV file.

    Parameters
    ----------
    path : Path
        Path to the input file (.xlsx or .csv).

    Returns
    -------
    pandas.DataFrame
        Cleaned bundle DataFrame.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    ValueError
        If required columns are missing.
    """
    if not path.exists():
        raise FileNotFoundError(f"Bundle data file not found: {path}")

    if path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    return clean_simulation_data(
        df,
        required_columns=_BUNDLE_REQUIRED_COLUMNS,
        drop_duplicates_on=["bundle_id"],
    )


def clean_scenario_data(path: Path) -> pd.DataFrame:
    """Load and clean scenario data from an Excel or CSV file.

    Parameters
    ----------
    path : Path
        Path to the input file (.xlsx or .csv).

    Returns
    -------
    pandas.DataFrame
        Cleaned scenario DataFrame.
    """
    if not path.exists():
        raise FileNotFoundError(f"Scenario data file not found: {path}")

    if path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    return clean_simulation_data(
        df,
        required_columns=_SCENARIO_REQUIRED_COLUMNS,
        drop_duplicates_on=["scenario_id"],
    )


def validate_numeric_ranges(
    df: pd.DataFrame,
    range_checks: dict[str, tuple[float, float]],
) -> pd.DataFrame:
    """Validate that numeric columns fall within expected ranges and clip outliers.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to validate.
    range_checks : dict[str, tuple[float, float]]
        Mapping of column name → (min_value, max_value).

    Returns
    -------
    pandas.DataFrame
        DataFrame with out-of-range values clipped and warnings logged.
    """
    df = df.copy()
    for col, (lo, hi) in range_checks.items():
        if col not in df.columns:
            continue
        out_of_range = ((df[col] < lo) | (df[col] > hi)).sum()
        if out_of_range:
            logger.warning(
                "Column '%s': %d values outside [%.4f, %.4f] – clipping.",
                col,
                out_of_range,
                lo,
                hi,
            )
        df[col] = df[col].clip(lo, hi)
    return df
