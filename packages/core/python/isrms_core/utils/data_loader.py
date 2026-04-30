"""Centralized data loading utilities

Provides a single source for loading crime data, facility data, etc.
Will be replaced by database queries once PostgreSQL is integrated.
"""

from pathlib import Path
from typing import Tuple, Optional
import pandas as pd


def get_default_data_path() -> Path:
    """
    Get default path to NIBRS_SVA_estimate_dataset_REBUILT.xlsx.
    
    Returns
    -------
    Path
        Path to Excel file
    """
    # This will be configurable via environment variables
    return Path("data/NIBRS_SVA_estimate_dataset_REBUILT.xlsx")


def load_crime_data(
    data_path: Optional[Path] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load state and county crime data.
    
    Parameters
    ----------
    data_path : Path, optional
        Path to Excel file. If None, uses default.
    
    Returns
    -------
    state_crime_df : pd.DataFrame
        State-level crime counts
    county_crime_df : pd.DataFrame
        County-level crime counts
    """
    if data_path is None:
        data_path = get_default_data_path()
    
    state_crime_df = pd.read_excel(data_path, sheet_name="State Crime")
    county_crime_df = pd.read_excel(data_path, sheet_name="County Crime")
    
    return state_crime_df, county_crime_df


def load_facility_data(
    data_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Load facility information.
    
    Parameters
    ----------
    data_path : Path, optional
        Path to Excel file. If None, uses default.
    
    Returns
    -------
    pd.DataFrame
        Facility information
    """
    if data_path is None:
        data_path = get_default_data_path()
    
    return pd.read_excel(data_path, sheet_name="Facility_Information")