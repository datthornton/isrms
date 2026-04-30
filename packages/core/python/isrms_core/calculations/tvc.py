"""TVC (Threat × Vulnerability × Consequence) Risk Calculation

Standardized TVC calculation used across NIBRS and ASHER modules.
"""

from typing import Dict, Optional


def calculate_tvc_risk(
    threat: float,
    vulnerability: float,
    consequence: float,
    scaling_factor: Optional[float] = None,
) -> float:
    """
    Calculate TVC risk score.
    
    Risk = T × V × C × S (optional scaling)
    
    Parameters
    ----------
    threat : float
        Threat score (0.0 to 1.0)
    vulnerability : float
        Vulnerability score (0.0 to 1.0)
    consequence : float
        Consequence score (0.0 to 1.0)
    scaling_factor : float, optional
        Additional scaling factor
    
    Returns
    -------
    float
        Risk score
    """
    risk = threat * vulnerability * consequence
    
    if scaling_factor is not None:
        risk *= scaling_factor
    
    return risk


def calculate_vulnerability(
    population: int,
    square_footage: int,
    security_measures: Dict[str, bool],
) -> float:
    """
    Calculate vulnerability score based on facility characteristics.
    
    Parameters
    ----------
    population : int
        Facility population
    square_footage : int
        Facility size
    security_measures : dict
        {measure_name: is_implemented}
    
    Returns
    -------
    float
        Vulnerability score (0.0 to 1.0)
    """
    # Base vulnerability from density
    density = population / square_footage if square_footage > 0 else 0
    base_v = min(density / 0.1, 1.0)  # Normalize to [0, 1]
    
    # Reduction from security measures
    security_reduction = 0.0
    security_weights = {
        "access_control": 0.15,
        "cameras": 0.10,
        "guards": 0.20,
        "barriers": 0.15,
        "alarms": 0.10,
    }
    
    for measure, implemented in security_measures.items():
        if implemented and measure in security_weights:
            security_reduction += security_weights[measure]
    
    final_v = max(0.0, base_v - security_reduction)
    return min(final_v, 1.0)


def calculate_consequence(
    population: int,
    critical_services: int,
    incident_type: str,
) -> float:
    """
    Calculate consequence score.
    
    Parameters
    ----------
    population : int
        Facility population
    critical_services : int
        Number of critical services
    incident_type : str
        Type of incident (for consequence weighting)
    
    Returns
    -------
    float
        Consequence score (0.0 to 1.0)
    """
    # Population-based consequence
    pop_consequence = min(population / 10000, 1.0)
    
    # Service criticality
    service_consequence = min(critical_services / 10, 1.0)
    
    # Incident type weight
    incident_weights = {
        "Murder": 1.0,
        "ASE": 1.0,  # Active Shooter
        "IED": 1.0,
        "Rape": 0.9,
        "Aggravated Assault": 0.8,
        "Robbery": 0.6,
        "Burglary": 0.4,
    }
    
    weight = incident_weights.get(incident_type, 0.5)
    
    return (pop_consequence + service_consequence) / 2 * weight