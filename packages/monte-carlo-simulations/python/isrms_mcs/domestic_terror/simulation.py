"""Domestic Terror Monte Carlo Simulation

Models domestic terrorism incidents for a facility or region using:
- PERT distributions for frequency and severity parameters
- Ideology-weighted probability adjustments
- Attack modality categorisation (lone actor, cell-based, etc.)

Migrated from: Domestic Terror MCS/
Changes from original:
- Removed hardcoded Windows paths
- Added type hints and dataclasses
- Replaced bare ``sys.path.append`` calls with package imports
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class AttackModality(str, Enum):
    """Categorisation of domestic terrorism attack types."""

    LONE_ACTOR = "lone_actor"
    CELL_BASED = "cell_based"
    CYBER_ENABLED = "cyber_enabled"
    COMBINED_ARMS = "combined_arms"


class IdeologyType(str, Enum):
    """Ideological motivation classification."""

    FAR_RIGHT = "far_right"
    FAR_LEFT = "far_left"
    RELIGIOUS_EXTREMISM = "religious_extremism"
    SINGLE_ISSUE = "single_issue"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class DomesticTerrorScenario:
    """Configuration for a domestic terrorism scenario.

    Parameters
    ----------
    scenario_id : str
        Unique identifier.
    incident_name : str
        Human-readable incident description.
    modality : AttackModality
        Type of attack modality.
    ideology : IdeologyType
        Ideological motivation.
    frequency_min : float
        Minimum annual frequency (incidents/year).
    frequency_mode : float
        Most-likely annual frequency.
    frequency_max : float
        Maximum annual frequency.
    casualty_min : float
        Minimum expected casualties per incident.
    casualty_mode : float
        Most-likely casualties per incident.
    casualty_max : float
        Maximum casualties per incident.
    financial_loss_per_casualty : float
        Estimated financial loss per casualty ($).
    property_damage_min : float
        Minimum property damage per incident ($).
    property_damage_mode : float
        Most-likely property damage ($).
    property_damage_max : float
        Maximum property damage ($).
    control_effectiveness : float
        Fraction by which controls reduce expected harm (0–1).
    ideology_weight : float
        Probability weight for ideological targeting of this facility (0–1).
    """

    scenario_id: str
    incident_name: str
    modality: AttackModality
    ideology: IdeologyType
    frequency_min: float
    frequency_mode: float
    frequency_max: float
    casualty_min: float
    casualty_mode: float
    casualty_max: float
    financial_loss_per_casualty: float = 500_000.0
    property_damage_min: float = 0.0
    property_damage_mode: float = 50_000.0
    property_damage_max: float = 500_000.0
    control_effectiveness: float = 0.0
    ideology_weight: float = 1.0
    tags: list[str] = field(default_factory=list)


@dataclass
class DomesticTerrorResult:
    """Results of a domestic terror Monte Carlo simulation."""

    scenario_id: str
    n_simulations: int
    annual_casualty_mean: float
    annual_casualty_p90: float
    annual_loss_mean: float
    annual_loss_p50: float
    annual_loss_p90: float
    annual_loss_p99: float
    residual_loss_mean: float
    probability_incident: float
    modality: AttackModality
    ideology: IdeologyType


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _pert_samples(
    minimum: float,
    mode: float,
    maximum: float,
    n: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Draw *n* PERT samples."""
    if minimum >= maximum:
        return np.full(n, mode)
    mean = (minimum + 4.0 * mode + maximum) / 6.0
    alpha = 6.0 * (mean - minimum) / (maximum - minimum)
    beta_ = 6.0 * (maximum - mean) / (maximum - minimum)
    alpha = max(alpha, 1e-6)
    beta_ = max(beta_, 1e-6)
    raw = rng.beta(alpha, beta_, size=n)
    return minimum + raw * (maximum - minimum)


# ---------------------------------------------------------------------------
# Public simulation function
# ---------------------------------------------------------------------------

def run_domestic_terror_simulation(
    scenario: DomesticTerrorScenario,
    n_simulations: int = 50_000,
    seed: Optional[int] = None,
) -> DomesticTerrorResult:
    """Run a Monte Carlo domestic terrorism simulation.

    Each iteration:
    1. Samples annual frequency from PERT distribution.
    2. Samples casualties and property damage per incident from PERT.
    3. Scales by ideology weight (facility targeting probability).
    4. Applies control effectiveness reduction.

    Parameters
    ----------
    scenario : DomesticTerrorScenario
        Scenario configuration.
    n_simulations : int
        Number of Monte Carlo iterations. Default: 50 000.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    DomesticTerrorResult
        Simulation statistics.
    """
    rng = np.random.default_rng(seed)

    # Sample frequencies (Poisson-lambda drawn from PERT)
    freq_samples = _pert_samples(
        scenario.frequency_min,
        scenario.frequency_mode,
        scenario.frequency_max,
        n_simulations,
        rng,
    )
    freq_samples = np.maximum(freq_samples * scenario.ideology_weight, 0.0)

    n_events = rng.poisson(freq_samples)

    # Sample casualties per event
    casualty_samples = _pert_samples(
        scenario.casualty_min,
        scenario.casualty_mode,
        scenario.casualty_max,
        n_simulations,
        rng,
    )
    casualty_samples = np.maximum(casualty_samples, 0.0)

    # Sample property damage per event
    damage_samples = _pert_samples(
        scenario.property_damage_min,
        scenario.property_damage_mode,
        scenario.property_damage_max,
        n_simulations,
        rng,
    )
    damage_samples = np.maximum(damage_samples, 0.0)

    annual_casualties = n_events * casualty_samples
    annual_loss = (
        annual_casualties * scenario.financial_loss_per_casualty
        + n_events * damage_samples
    )

    ce = max(0.0, min(float(scenario.control_effectiveness), 1.0))
    residual_loss = annual_loss * (1.0 - ce)

    return DomesticTerrorResult(
        scenario_id=scenario.scenario_id,
        n_simulations=n_simulations,
        annual_casualty_mean=float(np.mean(annual_casualties)),
        annual_casualty_p90=float(np.percentile(annual_casualties, 90)),
        annual_loss_mean=float(np.mean(annual_loss)),
        annual_loss_p50=float(np.percentile(annual_loss, 50)),
        annual_loss_p90=float(np.percentile(annual_loss, 90)),
        annual_loss_p99=float(np.percentile(annual_loss, 99)),
        residual_loss_mean=float(np.mean(residual_loss)),
        probability_incident=float(np.mean(n_events > 0)),
        modality=scenario.modality,
        ideology=scenario.ideology,
    )
