"""MCS Version 2 – Simulation Configuration

Centralised configuration for MCS v2 Monte Carlo runs. All data paths
are resolved via environment variables or relative to the package root –
no hardcoded absolute paths.

Migrated from: MCS Simulation Version 2/mcs_v2_config.py
Changes from original:
- Removed hardcoded Windows paths (``C:\\Users\\justi\\...``)
- Paths resolved via environment variables with package-relative fallbacks
- Added dataclasses for typed configuration objects
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path resolution helpers
# ---------------------------------------------------------------------------

def _env_path(env_var: str, default: Path) -> Path:
    """Return a Path from env var or fall back to *default*."""
    val = os.environ.get(env_var)
    return Path(val) if val else default


_DATA_DIR = _env_path(
    "ISRMS_MCS_DATA_DIR",
    Path(__file__).parents[5] / "data" / "mcs",
)


# ---------------------------------------------------------------------------
# Configuration dataclasses
# ---------------------------------------------------------------------------

@dataclass
class BundleConfig:
    """Configuration for a single mitigation bundle candidate.

    Parameters
    ----------
    bundle_id : str
        Unique identifier.
    name : str
        Human-readable bundle name.
    measures : list[str]
        List of measure IDs included in the bundle.
    estimated_cost : float
        Total estimated annual cost ($).
    expected_risk_reduction : float
        Expected aggregate risk reduction fraction (0–1).
    """

    bundle_id: str
    name: str
    measures: list[str]
    estimated_cost: float
    expected_risk_reduction: float
    tags: list[str] = field(default_factory=list)


@dataclass
class SimulationConfig:
    """Top-level configuration for an MCS v2 run.

    Parameters
    ----------
    run_id : str
        Unique identifier for this simulation run.
    n_simulations : int
        Number of Monte Carlo iterations.
    n_generations : int
        Number of genetic algorithm generations.
    population_size : int
        GA population size (number of candidate solutions).
    mutation_rate : float
        GA mutation probability (0–1).
    crossover_rate : float
        GA crossover probability (0–1).
    budget_constraint : float
        Maximum allowable annual spend ($).
    risk_target : float
        Target aggregate risk reduction fraction (0–1).
    seed : int, optional
        Random seed for reproducibility.
    data_dir : Path
        Directory containing input data files.
    output_dir : Path
        Directory for simulation output files.
    bundles : list[BundleConfig]
        Candidate mitigation bundles to evaluate.
    """

    run_id: str
    n_simulations: int = 10_000
    n_generations: int = 100
    population_size: int = 50
    mutation_rate: float = 0.05
    crossover_rate: float = 0.8
    budget_constraint: float = 500_000.0
    risk_target: float = 0.40
    seed: Optional[int] = None
    data_dir: Path = field(default_factory=lambda: _DATA_DIR)
    output_dir: Path = field(
        default_factory=lambda: _env_path(
            "ISRMS_MCS_OUTPUT_DIR",
            Path(__file__).parents[5] / "outputs" / "mcs",
        )
    )
    bundles: list[BundleConfig] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Default configuration factory
# ---------------------------------------------------------------------------

def default_config(run_id: str = "mcs_v2_default") -> SimulationConfig:
    """Return a sensible default :class:`SimulationConfig`.

    Parameters
    ----------
    run_id : str
        Identifier for this run.

    Returns
    -------
    SimulationConfig
        Default configuration.
    """
    return SimulationConfig(
        run_id=run_id,
        n_simulations=10_000,
        n_generations=50,
        population_size=30,
        mutation_rate=0.05,
        crossover_rate=0.8,
        budget_constraint=500_000.0,
        risk_target=0.40,
    )
