"""ASHER data loading utilities

Handles loading facility_profile.xlsx sheets.
"""

from pathlib import Path
from typing import Tuple
import pandas as pd


def load_asher_data(data_path: Path) -> Tuple[
    pd.DataFrame,  # metadata
    pd.DataFrame,  # threat_context
    pd.DataFrame,  # vulnerability_context
    pd.DataFrame,  # FSL_factors
    pd.DataFrame,  # LOP_factors
    pd.DataFrame,  # services
    pd.DataFrame,  # population
]:
    """
    Load all ASHER data sheets from facility_profile.xlsx.
    
    Parameters
    ----------
    data_path : Path
        Path to facility_profile.xlsx
    
    Returns
    -------
    tuple of DataFrames
        (metadata, threat_context, vulnerability_context, FSL_factors,
         LOP_factors, services, population)
    """
    metadata = pd.read_excel(data_path, sheet_name="metadata")
    threat_context = pd.read_excel(data_path, sheet_name="threat_context")
    vulnerability_context = pd.read_excel(data_path, sheet_name="vulnerability_context")
    fsl_factors = pd.read_excel(data_path, sheet_name="FSL_factors")
    lop_factors = pd.read_excel(data_path, sheet_name="LOP_factors")
    services = pd.read_excel(data_path, sheet_name="services")
    population = pd.read_excel(data_path, sheet_name="population")
    
    return (
        metadata,
        threat_context,
        vulnerability_context,
        fsl_factors,
        lop_factors,
        services,
        population,
    )