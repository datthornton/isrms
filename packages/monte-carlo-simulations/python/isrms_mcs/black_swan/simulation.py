"""Black Swan Monte Carlo Simulation

Models rare, high-impact security events (black swan events) using PERT
distributions for frequency and severity. Calculates blast injury ranges,
control effectiveness adjustments, and produces probability-weighted loss
distributions.

Migrated from: Black Swan Simulation/Black_Swan_MCS.py
Changes from original:
- Removed hardcoded Windows paths
- Added type hints and dataclasses
- Replaced bare ``sys.path.append`` calls with package imports
- PERT sampling extracted into reusable helper
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class BlackSwanScenario:
    """Configuration for a black swan event scenario.

    Parameters
    ----------
    scenario_id : str
        Unique identifier.
    event_name : str
        Human-readable event description.
    frequency_min : float
        Minimum annual frequency (events/year).
    frequency_mode : float
        Most-likely annual frequency.
    frequency_max : float
        Maximum annual frequency.
    severity_min : float
        Minimum financial severity per event ($).
    severity_mode : float
        Most-likely financial severity per event ($).
    severity_max : float
        Maximum financial severity per event ($).
    control_effectiveness : float
        Fraction by which controls reduce expected loss (0–1).
    blast_charge_kg : float, optional
        TNT-equivalent charge mass in kg (for blast injury modelling).
    """

    scenario_id: str
    event_name: str
    frequency_min: float
    frequency_mode: float
    frequency_max: float
    severity_min: float
    severity_mode: float
    severity_max: float
    control_effectiveness: float = 0.0
    blast_charge_kg: Optional[float] = None
    tags: list[str] = field(default_factory=list)


@dataclass
class BlastInjuryRanges:
    """Estimated injury distances for an explosive event.

    All distances in metres.
    """

    severe_injury_m: float
    moderate_injury_m: float
    minor_injury_m: float
    lethal_range_m: float


@dataclass
class BlackSwanResult:
    """Results of a black swan Monte Carlo simulation."""

    scenario_id: str
    n_simulations: int
    annual_loss_mean: float
    annual_loss_p50: float
    annual_loss_p90: float
    annual_loss_p99: float
    residual_loss_mean: float
    probability_nonzero: float
    blast_injury_ranges: Optional[BlastInjuryRanges] = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _pert_samples(
    minimum: float,
    mode: float,
    maximum: float,
    n: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Draw *n* samples from a PERT distribution.

    Parameters
    ----------
    minimum, mode, maximum : float
        PERT distribution parameters.
    n : int
        Number of samples.
    rng : numpy.random.Generator
        Seeded generator.

    Returns
    -------
    numpy.ndarray
        Samples scaled to [minimum, maximum].
    """
    if minimum >= maximum:
        return np.full(n, mode)
    mean = (minimum + 4.0 * mode + maximum) / 6.0
    alpha = 6.0 * (mean - minimum) / (maximum - minimum)
    beta_ = 6.0 * (maximum - mean) / (maximum - minimum)
    alpha = max(alpha, 1e-6)
    beta_ = max(beta_, 1e-6)
    raw = rng.beta(alpha, beta_, size=n)
    return minimum + raw * (maximum - minimum)


def _blast_injury_ranges(charge_kg: float) -> BlastInjuryRanges:
    """Estimate injury ranges from Hopkinson-Cranz scaling.

    Uses simplified empirical coefficients derived from Kingery-Bulmash
    data for TNT-equivalent charges in open air.

    Parameters
    ----------
    charge_kg : float
        TNT-equivalent mass in kilograms.

    Returns
    -------
    BlastInjuryRanges
        Estimated injury distances in metres.
    """
    if charge_kg <= 0:
        return BlastInjuryRanges(
            severe_injury_m=0.0,
            moderate_injury_m=0.0,
            minor_injury_m=0.0,
            lethal_range_m=0.0,
        )
    # Cube-root scaling: R = k * W^(1/3)
    cbrt_w = charge_kg ** (1.0 / 3.0)
    return BlastInjuryRanges(
        lethal_range_m=round(2.2 * cbrt_w, 1),
        severe_injury_m=round(4.5 * cbrt_w, 1),
        moderate_injury_m=round(9.0 * cbrt_w, 1),
        minor_injury_m=round(18.0 * cbrt_w, 1),
    )


# ---------------------------------------------------------------------------
# Public simulation function
# ---------------------------------------------------------------------------

def run_black_swan_simulation(
    scenario: BlackSwanScenario,
    n_simulations: int = 50_000,
    seed: Optional[int] = None,
) -> BlackSwanResult:
    """Run a Monte Carlo black swan event simulation.

    For each iteration, samples event frequency and severity from PERT
    distributions, computes annual loss, then applies control effectiveness.

    Parameters
    ----------
    scenario : BlackSwanScenario
        Scenario configuration.
    n_simulations : int
        Number of Monte Carlo iterations. Default: 50 000.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    BlackSwanResult
        Simulation statistics including loss percentiles.
    """
    rng = np.random.default_rng(seed)

    freq_samples = _pert_samples(
        scenario.frequency_min,
        scenario.frequency_mode,
        scenario.frequency_max,
        n_simulations,
        rng,
    )
    freq_samples = np.maximum(freq_samples, 0.0)

    sev_samples = _pert_samples(
        scenario.severity_min,
        scenario.severity_mode,
        scenario.severity_max,
        n_simulations,
        rng,
    )
    sev_samples = np.maximum(sev_samples, 0.0)

    # Poisson-realised number of events per year, then sum severities
    n_events = rng.poisson(freq_samples)
    annual_loss = n_events * sev_samples

    ce = max(0.0, min(float(scenario.control_effectiveness), 1.0))
    residual_loss = annual_loss * (1.0 - ce)

    blast_ranges: Optional[BlastInjuryRanges] = None
    if scenario.blast_charge_kg is not None:
        blast_ranges = _blast_injury_ranges(scenario.blast_charge_kg)

    return BlackSwanResult(
        scenario_id=scenario.scenario_id,
        n_simulations=n_simulations,
        annual_loss_mean=float(np.mean(annual_loss)),
        annual_loss_p50=float(np.percentile(annual_loss, 50)),
        annual_loss_p90=float(np.percentile(annual_loss, 90)),
        annual_loss_p99=float(np.percentile(annual_loss, 99)),
        residual_loss_mean=float(np.mean(residual_loss)),
        probability_nonzero=float(np.mean(annual_loss > 0)),
        blast_injury_ranges=blast_ranges,
    )
