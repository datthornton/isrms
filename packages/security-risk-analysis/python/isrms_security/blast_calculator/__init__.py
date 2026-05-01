"""Blast Effects Calculator

Calculates injury and damage ranges for IED charges.

Status: Template - In Development
"""

from dataclasses import dataclass
from typing import Literal
import math


@dataclass
class BlastEffects:
    """Blast effects calculation result"""
    charge_weight_kg: float
    standoff_distance_m: float
    building_type: str
    
    lethal_radius_m: float
    severe_injury_radius_m: float
    minor_injury_radius_m: float
    structural_damage_radius_m: float
    
    peak_overpressure_psi: float
    impulse_psi_ms: float


def calculate_blast_effects(
    charge_weight_kg: float,
    standoff_distance_m: float,
    building_type: Literal["concrete", "steel", "wood"] = "concrete",
) -> BlastEffects:
    """
    Calculate blast effects for an IED charge.
    
    Uses simplified Kingery-Bulmash equations.
    
    Parameters
    ----------
    charge_weight_kg : float
        TNT equivalent charge weight in kg
    standoff_distance_m : float
        Distance from charge to target in meters
    building_type : str
        Type of construction (concrete, steel, wood)
    
    Returns
    -------
    BlastEffects
        Calculated blast effects
    
    Notes
    -----
    This is a simplified implementation. For operational use,
    integrate with validated blast modeling software.
    """
    # Convert to scaled distance
    scaled_distance = standoff_distance_m / (charge_weight_kg ** (1/3))
    
    # Calculate peak overpressure (simplified Kingery-Bulmash)
    if scaled_distance < 0.1:
        peak_overpressure_psi = 10000  # Near-field approximation
    else:
        peak_overpressure_psi = (
            1772 / scaled_distance**3 
            - 114 / scaled_distance**2 
            + 108 / scaled_distance
        )
    
    # Calculate impulse (simplified)
    impulse_psi_ms = peak_overpressure_psi * 0.05 * scaled_distance
    
    # Injury radii (based on overpressure thresholds)
    lethal_threshold_psi = 60  # 50% lethality
    severe_threshold_psi = 30  # Severe injuries
    minor_threshold_psi = 5    # Minor injuries/eardrum rupture
    
    lethal_radius = _calculate_radius_for_pressure(
        charge_weight_kg, lethal_threshold_psi
    )
    severe_radius = _calculate_radius_for_pressure(
        charge_weight_kg, severe_threshold_psi
    )
    minor_radius = _calculate_radius_for_pressure(
        charge_weight_kg, minor_threshold_psi
    )
    
    # Structural damage radius (building-type dependent)
    damage_thresholds = {
        "concrete": 10,  # psi
        "steel": 7,
        "wood": 3,
    }
    
    structural_radius = _calculate_radius_for_pressure(
        charge_weight_kg, damage_thresholds[building_type]
    )
    
    return BlastEffects(
        charge_weight_kg=charge_weight_kg,
        standoff_distance_m=standoff_distance_m,
        building_type=building_type,
        lethal_radius_m=lethal_radius,
        severe_injury_radius_m=severe_radius,
        minor_injury_radius_m=minor_radius,
        structural_damage_radius_m=structural_radius,
        peak_overpressure_psi=peak_overpressure_psi,
        impulse_psi_ms=impulse_psi_ms,
    )


def _calculate_radius_for_pressure(charge_kg: float, target_psi: float) -> float:
    """
    Calculate standoff distance for a given overpressure.
    
    Uses iterative solver on simplified Kingery-Bulmash.
    """
    # Simple iterative solver
    min_r = 0.1
    max_r = 1000.0
    
    for _ in range(50):  # Max 50 iterations
        mid_r = (min_r + max_r) / 2
        scaled = mid_r / (charge_kg ** (1/3))
        
        if scaled < 0.1:
            pressure = 10000
        else:
            pressure = (
                1772 / scaled**3 
                - 114 / scaled**2 
                + 108 / scaled
            )
        
        if abs(pressure - target_psi) < 0.1:
            return mid_r
        
        if pressure > target_psi:
            min_r = mid_r
        else:
            max_r = mid_r
    
    return mid_r