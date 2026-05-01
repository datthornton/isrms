"""ASHER Risk Calculator - Version 3

Active Shooter Hazard Exposure Rating using Lei-Mackenzie TVC model.

Migrated from:
- C:\IRMS\ASHER Risk Calculator V2\lei_mackenzie_asher_v3.py
- C:\IRMS\ASHER Risk Calculator V2\ASHER_Dashboard_v3.py

Changes from original:
- Standardized data loading (uses isrms_core utilities)
- Removed hardcoded paths
- Added type hints
- Integrated with isrms_core models
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

import pandas as pd

from isrms_core.calculations import calculate_tvc_risk
from isrms_core.models import RiskLevel

logging.basicConfig(level=logging.INFO)


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp a value between min_val and max_val."""
    return max(min_val, min(float(value), max_val))


@dataclass
class ASHERRiskResult:
    """ASHER risk assessment result"""
    facility_id: str
    incident_type: str
    threat: float
    vulnerability: float
    consequence: float
    risk_score: float
    risk_level: RiskLevel


def calculate_asher_threat(
    incident_type: str,
    facility_id: str,
    threat_context_df: pd.DataFrame,
    default_threat: float = 1e-8,
) -> float:
    """
    Calculate ASHER Threat (T) using precomputed micro-probabilities.
    
    Parameters
    ----------
    incident_type : str
        One of ["ASE", "IED", "VBIED", "VRA", "IID"]
    facility_id : str
        Facility identifier (e.g., "PH1A")
    threat_context_df : pd.DataFrame
        Threat context data from facility_profile.xlsx
    default_threat : float
        Default threat value if calculation fails
    
    Returns
    -------
    float
        Threat score (0.0 to 1.0)
    """
    try:
        row = threat_context_df[threat_context_df["facility_id"] == facility_id].iloc[0]

        col_map: Dict[str, str] = {
            "ASE": "ASHER_probability_AS",
            "IED": "ASHER_probability_IED",
            "VBIED": "ASHER_probability_VBIED",
            "VRA": "ASHER_probability_VRA",
            "IID": "ASHER_probability_IID",
        }

        if incident_type not in col_map:
            return clamp(default_threat)

        base_prob = float(row.get(col_map[incident_type], default_threat))

        # Modifiers: crime, ideological, symbolic
        community_crime = float(row.get("community_crime_level", 0.0))
        facility_crime = float(row.get("facility_crime_level", 0.0))
        ideological = float(row.get("ideological_threat_level", 0.0))
        symbolic = float(row.get("symbolic_value", 0.0))

        crime_factor = 0.5 + 0.5 * max(community_crime, facility_crime)
        ideological_factor = 0.5 + 0.5 * ideological
        symbolic_factor = 0.5 + 0.5 * symbolic

        threat = base_prob * crime_factor * ideological_factor * symbolic_factor
        return clamp(threat)

    except Exception as e:
        logging.warning(f"ASHER threat calculation failed for {facility_id}: {e}")
        return clamp(default_threat)


def calculate_asher_vulnerability(
    facility_id: str,
    vulnerability_context_df: pd.DataFrame,
) -> float:
    """
    Calculate ASHER Vulnerability (V) using physical hardening, access control,
    detection, and response capabilities.
    
    Parameters
    ----------
    facility_id : str
        Facility identifier
    vulnerability_context_df : pd.DataFrame
        Vulnerability context from facility_profile.xlsx
    
    Returns
    -------
    float
        Vulnerability score (0.0 to 1.0)
    """
    try:
        row = vulnerability_context_df[
            vulnerability_context_df["facility_id"] == facility_id
        ].iloc[0]

        # Physical hardening (higher = stronger = lower vulnerability)
        construction = float(row.get("construction_type", 0.0))
        glazing = float(row.get("glazing_type", 0.0))
        standoff = float(row.get("standoff_distance", 0.0))

        # Access control
        access_ctrl = float(row.get("access_control_maturity", 0.0))
        circulation = float(row.get("circulation_complexity", 0.0))
        perimeter = float(row.get("perimeter_security_score", 0.0))
        cameras = float(row.get("camera_coverage_score", 0.0))
        ids = float(row.get("IDS_coverage_score", 0.0))
        pacs = float(row.get("PACS_maturity", 0.0))

        # Response capabilities
        rt_police = float(row.get("response_time_police", 0.0))
        rt_fire = float(row.get("response_time_fire", 0.0))
        rt_ems = float(row.get("response_time_EMS", 0.0))
        le_cap = float(row.get("LE_capabilities", 0.0))
        fire_ems_cap = float(row.get("fire_EMS_capabilities", 0.0))

        # Calculate component vulnerabilities (invert strengths)
        phys_strength = (construction + glazing + standoff) / 3.0
        v_phys = 1.0 - phys_strength

        access_block = (access_ctrl + circulation + perimeter + cameras + ids + pacs) / 6.0
        v_access = 1.0 - access_block

        response_block = (rt_police + rt_fire + rt_ems + le_cap + fire_ems_cap) / 5.0
        v_response = 1.0 - response_block

        # Weighted combination
        w_phys, w_access, w_resp = 0.3, 0.4, 0.3
        v_index = w_phys * v_phys + w_access * v_access + w_resp * v_response

        return clamp(v_index)

    except Exception as e:
        logging.warning(f"ASHER vulnerability calculation failed for {facility_id}: {e}")
        return 0.5


def calculate_asher_consequence(
    incident_type: str,
    facility_id: str,
    fsl_df: pd.DataFrame,
    lop_df: pd.DataFrame,
    services_df: pd.DataFrame,
    scenario_population: Optional[int] = None,
) -> float:
    """
    Calculate ASHER Consequence (C) using FSL factors, LOP factors, and services.
    
    Parameters
    ----------
    incident_type : str
        ASHER event type
    facility_id : str
        Facility identifier
    fsl_df : pd.DataFrame
        FSL factors from facility_profile.xlsx
    lop_df : pd.DataFrame
        LOP factors from facility_profile.xlsx
    services_df : pd.DataFrame
        Services data from facility_profile.xlsx
    scenario_population : int, optional
        Override population for scenario analysis
    
    Returns
    -------
    float
        Consequence score (0.0 to 1.0)
    """
    try:
        fsl_row = fsl_df[fsl_df["facility_id"] == facility_id].iloc[0]
        lop_row = lop_df[lop_df["facility_id"] == facility_id].iloc[0]
        svc_row = services_df[services_df["facility_id"] == facility_id].iloc[0]

        # FSL core consequence drivers
        mission = float(fsl_row.get("mission_criticality", 0.0))
        pop_factor = float(fsl_row.get("population_factor", 0.0))
        size_factor = float(fsl_row.get("facility_size_factor", 0.0))
        threat_factor = float(fsl_row.get("threat_factor", 0.0))
        symbolic = float(fsl_row.get("symbolic_factor", 0.0))
        cons_factor = float(fsl_row.get("consequence_factor", 0.0))

        fsl_core = (
            0.25 * mission
            + 0.20 * pop_factor
            + 0.15 * size_factor
            + 0.15 * threat_factor
            + 0.15 * symbolic
            + 0.10 * cons_factor
        )

        # LOP occupant-centric consequence
        asset_crit = float(lop_row.get("asset_criticality", 0.0))
        comm_crit = float(lop_row.get("community_criticality", 0.0))
        pop_density = float(lop_row.get("population_density", 0.0))
        pop_chars = float(lop_row.get("population_characteristics", 0.0))
        thr_comm = float(lop_row.get("threats_to_occupants_community", 0.0))
        thr_fac = float(lop_row.get("threats_to_occupants_facility", 0.0))
        thr_tenants = float(lop_row.get("threats_to_tenants_ideological", 0.0))

        lop_core = (
            0.20 * asset_crit
            + 0.20 * comm_crit
            + 0.15 * pop_density
            + 0.15 * pop_chars
            + 0.15 * thr_comm
            + 0.10 * thr_fac
            + 0.05 * thr_tenants
        )

        # Services amplifiers
        has_ed = int(svc_row.get("has_ED", 0))
        has_peds = int(svc_row.get("has_peds", 0))
        has_ld = int(svc_row.get("has_LD", 0))
        has_pharm = int(svc_row.get("has_pharmacy", 0))
        has_bh = int(svc_row.get("has_behavioral_health", 0))
        has_cash = int(svc_row.get("cash_over_1000", 0))

        svc_score = (
            0.25 * has_ed
            + 0.20 * has_peds
            + 0.15 * has_ld
            + 0.15 * has_pharm
            + 0.15 * has_bh
            + 0.10 * has_cash
        )

        svc_norm = svc_score / 1.0

        # Combine domains
        w_fsl, w_lop, w_svc = 0.45, 0.35, 0.20
        c_index = w_fsl * fsl_core + w_lop * lop_core + w_svc * svc_norm

        # Optional scenario population override
        if scenario_population is not None:
            pop_norm = min(scenario_population / 5000.0, 1.0)
            c_index = 0.15 * pop_norm + 0.85 * c_index

        return clamp(c_index)

    except Exception as e:
        logging.warning(f"ASHER consequence calculation failed for {facility_id}: {e}")
        return 0.5


def calculate_asher_risk(
    facility_id: str,
    incident_type: str,
    threat_context_df: pd.DataFrame,
    vulnerability_context_df: pd.DataFrame,
    fsl_df: pd.DataFrame,
    lop_df: pd.DataFrame,
    services_df: pd.DataFrame,
    scenario_population: Optional[int] = None,
) -> ASHERRiskResult:
    """
    Calculate complete ASHER risk assessment for a facility and incident type.
    
    Parameters
    ----------
    facility_id : str
        Facility identifier
    incident_type : str
        ASHER event type (ASE, IED, VBIED, VRA, IID)
    threat_context_df : pd.DataFrame
        Threat context data
    vulnerability_context_df : pd.DataFrame
        Vulnerability context data
    fsl_df : pd.DataFrame
        FSL factors
    lop_df : pd.DataFrame
        LOP factors
    services_df : pd.DataFrame
        Services data
    scenario_population : int, optional
        Override population for scenario
    
    Returns
    -------
    ASHERRiskResult
        Complete risk assessment result
    """
    threat = calculate_asher_threat(incident_type, facility_id, threat_context_df)
    vulnerability = calculate_asher_vulnerability(facility_id, vulnerability_context_df)
    consequence = calculate_asher_consequence(
        incident_type, facility_id, fsl_df, lop_df, services_df, scenario_population
    )
    
    risk_score = calculate_tvc_risk(threat, vulnerability, consequence)
    
    # Convert to 0-100 scale for risk level determination
    risk_score_100 = risk_score * 100
    risk_level = RiskLevel.from_score(risk_score_100)
    
    return ASHERRiskResult(
        facility_id=facility_id,
        incident_type=incident_type,
        threat=threat,
        vulnerability=vulnerability,
        consequence=consequence,
        risk_score=risk_score,
        risk_level=risk_level,
    )


def calculate_aggregated_asher_risk(
    facility_id: str,
    incident_list: List[str],
    threat_context_df: pd.DataFrame,
    vulnerability_context_df: pd.DataFrame,
    fsl_df: pd.DataFrame,
    lop_df: pd.DataFrame,
    services_df: pd.DataFrame,
) -> float:
    """
    Calculate aggregated risk index for any ASHER event at a facility.
    
    Parameters
    ----------
    facility_id : str
        Facility identifier
    incident_list : List[str]
        List of ASHER events to aggregate
    threat_context_df : pd.DataFrame
        Threat context data
    vulnerability_context_df : pd.DataFrame
        Vulnerability context data
    fsl_df : pd.DataFrame
        FSL factors
    lop_df : pd.DataFrame
        LOP factors
    services_df : pd.DataFrame
        Services data
    
    Returns
    -------
    float
        Aggregated risk score (0.0 to 1.0)
    """
    total_risk = 0.0
    
    for incident in incident_list:
        result = calculate_asher_risk(
            facility_id=facility_id,
            incident_type=incident,
            threat_context_df=threat_context_df,
            vulnerability_context_df=vulnerability_context_df,
            fsl_df=fsl_df,
            lop_df=lop_df,
            services_df=services_df,
        )
        total_risk += result.risk_score
    
    return clamp(total_risk)