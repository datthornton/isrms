"""ALE Equation - Annual Loss Estimation Core Model

Implements the standard ALE calculation framework:
    SLE  = Asset Value × Exposure Factor
    ARO  = Annualized Rate of Occurrence
    ALE  = SLE × ARO

Monte Carlo extensions allow probabilistic ALE estimation using
triangular or PERT distributions for SLE components and ARO.

Migrated from: ALE/ALE _Demonstrator/ALE_Equation.py
Changes from original:
- Removed hardcoded Windows paths
- Added type hints and docstrings
- Extracted Monte Carlo simulation into separate function
- Used numpy for vectorised simulation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ALEScenario:
    """A single ALE threat scenario.

    Parameters
    ----------
    scenario_id : str
        Unique identifier for the scenario.
    threat_name : str
        Human-readable threat description.
    asset_value : float
        Total asset value in dollars.
    exposure_factor_min : float
        Minimum asset exposure fraction (0–1) under the threat.
    exposure_factor_mode : float
        Most-likely asset exposure fraction.
    exposure_factor_max : float
        Maximum asset exposure fraction.
    aro_min : float
        Minimum annualised rate of occurrence (events / year).
    aro_mode : float
        Most-likely annualised rate of occurrence.
    aro_max : float
        Maximum annualised rate of occurrence.
    control_effectiveness : float
        Fraction by which controls reduce ALE (0–1).
    """

    scenario_id: str
    threat_name: str
    asset_value: float
    exposure_factor_min: float
    exposure_factor_mode: float
    exposure_factor_max: float
    aro_min: float
    aro_mode: float
    aro_max: float
    control_effectiveness: float = 0.0
    tags: list[str] = field(default_factory=list)


@dataclass
class ALEResult:
    """Result of a single deterministic ALE calculation."""

    scenario_id: str
    sle: float
    aro: float
    ale: float
    ale_residual: float  # ALE after control effectiveness


@dataclass
class ALESimulationResult:
    """Result of a Monte Carlo ALE simulation."""

    scenario_id: str
    ale_samples: np.ndarray
    ale_mean: float
    ale_p50: float
    ale_p90: float
    ale_p95: float
    ale_residual_mean: float


def calculate_sle(asset_value: float, exposure_factor: float) -> float:
    """Calculate Single Loss Expectancy.

    Parameters
    ----------
    asset_value : float
        Total value of the asset in dollars.
    exposure_factor : float
        Fraction of asset value lost in a single event (0.0–1.0).

    Returns
    -------
    float
        Single Loss Expectancy in dollars.
    """
    ef = max(0.0, min(float(exposure_factor), 1.0))
    return float(asset_value) * ef


def calculate_aro(events_per_year: float) -> float:
    """Return the Annualised Rate of Occurrence.

    Parameters
    ----------
    events_per_year : float
        Expected number of events per year.

    Returns
    -------
    float
        Annualised Rate of Occurrence (non-negative).
    """
    return max(0.0, float(events_per_year))


def calculate_ale(
    asset_value: float,
    exposure_factor: float,
    aro: float,
    control_effectiveness: float = 0.0,
) -> float:
    """Calculate Annual Loss Expectancy (deterministic).

    ALE = SLE × ARO × (1 - control_effectiveness)

    Parameters
    ----------
    asset_value : float
        Total value of the asset in dollars.
    exposure_factor : float
        Fraction of asset value lost per event (0.0–1.0).
    aro : float
        Annualised rate of occurrence.
    control_effectiveness : float
        Fraction by which security controls reduce ALE (0.0–1.0).

    Returns
    -------
    float
        Annual Loss Expectancy in dollars.
    """
    sle = calculate_sle(asset_value, exposure_factor)
    aro_val = calculate_aro(aro)
    ce = max(0.0, min(float(control_effectiveness), 1.0))
    return sle * aro_val * (1.0 - ce)


def _pert_samples(
    minimum: float,
    mode: float,
    maximum: float,
    n: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Draw samples from a PERT (beta-variant) distribution.

    Uses the standard PERT parameterisation:
        mean = (min + 4*mode + max) / 6
        variance governed by lambda=4 (default)

    Parameters
    ----------
    minimum, mode, maximum : float
        Distribution parameters.
    n : int
        Number of samples.
    rng : numpy.random.Generator
        Random number generator for reproducibility.

    Returns
    -------
    numpy.ndarray
        Array of *n* samples scaled to [minimum, maximum].
    """
    if minimum >= maximum:
        return np.full(n, mode)
    mean = (minimum + 4.0 * mode + maximum) / 6.0
    # Beta parameters
    alpha = 6.0 * (mean - minimum) / (maximum - minimum)
    beta = 6.0 * (maximum - mean) / (maximum - minimum)
    alpha = max(alpha, 1e-6)
    beta = max(beta, 1e-6)
    raw = rng.beta(alpha, beta, size=n)
    return minimum + raw * (maximum - minimum)


def simulate_ale(
    scenario: ALEScenario,
    n_simulations: int = 10_000,
    seed: Optional[int] = None,
) -> ALESimulationResult:
    """Run a Monte Carlo ALE simulation for a single scenario.

    Both Exposure Factor and ARO are drawn from PERT distributions
    parameterised by their (min, mode, max) values.

    Parameters
    ----------
    scenario : ALEScenario
        The threat scenario to simulate.
    n_simulations : int
        Number of Monte Carlo iterations.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    ALESimulationResult
        Simulation statistics.
    """
    rng = np.random.default_rng(seed)

    ef_samples = _pert_samples(
        scenario.exposure_factor_min,
        scenario.exposure_factor_mode,
        scenario.exposure_factor_max,
        n_simulations,
        rng,
    )
    ef_samples = np.clip(ef_samples, 0.0, 1.0)

    aro_samples = _pert_samples(
        scenario.aro_min,
        scenario.aro_mode,
        scenario.aro_max,
        n_simulations,
        rng,
    )
    aro_samples = np.maximum(aro_samples, 0.0)

    sle_samples = scenario.asset_value * ef_samples
    ale_samples = sle_samples * aro_samples

    ce = max(0.0, min(float(scenario.control_effectiveness), 1.0))
    ale_residual_samples = ale_samples * (1.0 - ce)

    return ALESimulationResult(
        scenario_id=scenario.scenario_id,
        ale_samples=ale_samples,
        ale_mean=float(np.mean(ale_samples)),
        ale_p50=float(np.percentile(ale_samples, 50)),
        ale_p90=float(np.percentile(ale_samples, 90)),
        ale_p95=float(np.percentile(ale_samples, 95)),
        ale_residual_mean=float(np.mean(ale_residual_samples)),
    )


def calculate_ale_for_scenario(scenario: ALEScenario) -> ALEResult:
    """Deterministic ALE calculation for a scenario using mode values.

    Parameters
    ----------
    scenario : ALEScenario
        The threat scenario.

    Returns
    -------
    ALEResult
        Deterministic ALE result using modal parameter values.
    """
    sle = calculate_sle(scenario.asset_value, scenario.exposure_factor_mode)
    aro = calculate_aro(scenario.aro_mode)
    ale = sle * aro
    ale_residual = ale * (1.0 - max(0.0, min(scenario.control_effectiveness, 1.0)))
    return ALEResult(
        scenario_id=scenario.scenario_id,
        sle=sle,
        aro=aro,
        ale=ale,
        ale_residual=ale_residual,
    )
