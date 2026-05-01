"""MCS Version 2 – Run Profiler

Profiles the performance of the MCS v2 optimization engine across
varying configuration parameters. Useful for calibrating n_simulations
and population_size for production runs.

Migrated from: MCS Simulation Version 2/run_profile.py
Changes from original:
- Removed hardcoded Windows paths
- Added type hints and structured output
- Uses cProfile for Python-native profiling
"""

from __future__ import annotations

import cProfile
import io
import logging
import pstats
import time
from dataclasses import dataclass, field
from typing import Optional

from isrms_mcs.v2.config import SimulationConfig, BundleConfig, default_config
from isrms_mcs.v2.optimize import run_optimization, OptimizationResult

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ProfileResult:
    """Result of a profiling run.

    Attributes
    ----------
    run_id : str
        Simulation run identifier.
    elapsed_seconds : float
        Wall-clock time in seconds.
    n_simulations : int
        Number of MC iterations used.
    n_generations : int
        Number of GA generations.
    population_size : int
        GA population size.
    optimization_result : OptimizationResult
        The underlying optimization result.
    profile_stats : str
        Formatted cProfile output (top functions by cumulative time).
    """

    run_id: str
    elapsed_seconds: float
    n_simulations: int
    n_generations: int
    population_size: int
    optimization_result: OptimizationResult
    profile_stats: str = ""


# ---------------------------------------------------------------------------
# Profiling function
# ---------------------------------------------------------------------------

def profile_optimization(
    config: Optional[SimulationConfig] = None,
    top_n: int = 20,
) -> ProfileResult:
    """Run the MCS v2 optimizer under cProfile and return timing statistics.

    Parameters
    ----------
    config : SimulationConfig, optional
        Configuration to profile. Uses ``default_config()`` if not provided.
    top_n : int
        Number of top functions to include in the profile summary.

    Returns
    -------
    ProfileResult
        Profiling result with elapsed time and cProfile stats.
    """
    if config is None:
        config = _make_sample_config()

    profiler = cProfile.Profile()

    start = time.perf_counter()
    profiler.enable()
    opt_result = run_optimization(config)
    profiler.disable()
    elapsed = time.perf_counter() - start

    # Format cProfile statistics
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats("cumulative")
    stats.print_stats(top_n)
    profile_output = stream.getvalue()

    logger.info(
        "Profile run '%s': %.3fs elapsed, %d generations, pop=%d",
        config.run_id,
        elapsed,
        config.n_generations,
        config.population_size,
    )

    return ProfileResult(
        run_id=config.run_id,
        elapsed_seconds=elapsed,
        n_simulations=config.n_simulations,
        n_generations=config.n_generations,
        population_size=config.population_size,
        optimization_result=opt_result,
        profile_stats=profile_output,
    )


def sweep_profile(
    n_generations_list: tuple[int, ...] = (20, 50, 100),
    population_sizes: tuple[int, ...] = (20, 50, 100),
) -> list[ProfileResult]:
    """Sweep over GA parameter combinations and profile each.

    Parameters
    ----------
    n_generations_list : list[int]
        GA generation counts to test.
    population_sizes : list[int]
        Population sizes to test.

    Returns
    -------
    list[ProfileResult]
        One result per (n_generations, population_size) combination.
    """
    results: list[ProfileResult] = []
    for n_gen in n_generations_list:
        for pop_size in population_sizes:
            cfg = _make_sample_config(
                run_id=f"profile_g{n_gen}_p{pop_size}",
                n_generations=n_gen,
                population_size=pop_size,
            )
            result = profile_optimization(cfg)
            results.append(result)
            logger.info(
                "Sweep: gen=%d pop=%d → %.3fs",
                n_gen,
                pop_size,
                result.elapsed_seconds,
            )
    return results


def _make_sample_config(
    run_id: str = "profile_run",
    n_generations: int = 50,
    population_size: int = 30,
) -> SimulationConfig:
    """Build a small sample config for profiling."""
    bundles = [
        BundleConfig(
            bundle_id=f"B{i:02d}",
            name=f"Bundle {i}",
            measures=[f"M{i}A", f"M{i}B"],
            estimated_cost=float(20_000 * i),
            expected_risk_reduction=min(0.05 * i, 0.50),
        )
        for i in range(1, 11)
    ]
    return SimulationConfig(
        run_id=run_id,
        n_simulations=1_000,
        n_generations=n_generations,
        population_size=population_size,
        budget_constraint=200_000.0,
        risk_target=0.40,
        seed=42,
        bundles=bundles,
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = profile_optimization()
    print(f"Elapsed: {result.elapsed_seconds:.3f}s")
    print(result.profile_stats[:2000])
