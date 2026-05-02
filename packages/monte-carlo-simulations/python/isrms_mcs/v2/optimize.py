"""MCS Version 2 – Genetic Algorithm Optimization Engine

Uses a genetic algorithm (GA) to find the optimal combination of security
mitigation bundles that maximises risk reduction within a budget constraint.

Migrated from: MCS Simulation Version 2/mcs_v2_optimize.py
Changes from original:
- Removed hardcoded Windows paths
- Added type hints and full docstrings
- Genetic algorithm operators implemented as pure functions
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from isrms_mcs.v2.config import SimulationConfig, BundleConfig

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class OptimizationResult:
    """Result of the genetic algorithm optimization.

    Attributes
    ----------
    run_id : str
        Simulation run identifier.
    best_bundle_ids : list[str]
        IDs of bundles in the optimal solution.
    best_cost : float
        Total cost of the optimal solution ($).
    best_risk_reduction : float
        Aggregate risk reduction of the optimal solution (0–1).
    roi : float
        Return on investment (risk_reduction_value / cost - 1).
    feasible : bool
        True if solution satisfies the budget constraint.
    generations_run : int
        Number of GA generations completed.
    fitness_history : list[float]
        Best fitness score per generation.
    pareto_front : list[dict]
        Non-dominated solutions (cost, risk_reduction pairs).
    """

    run_id: str
    best_bundle_ids: list[str]
    best_cost: float
    best_risk_reduction: float
    roi: float
    feasible: bool
    generations_run: int
    fitness_history: list[float] = field(default_factory=list)
    pareto_front: list[dict] = field(default_factory=list)


# ---------------------------------------------------------------------------
# GA helpers
# ---------------------------------------------------------------------------

def _evaluate_individual(
    individual: list[int],
    bundles: list[BundleConfig],
    budget: float,
    risk_target: float,
) -> float:
    """Compute fitness for a binary-encoded individual.

    Fitness = risk_reduction − penalty for exceeding budget.

    Parameters
    ----------
    individual : list[int]
        Binary vector; 1 = bundle selected, 0 = not selected.
    bundles : list[BundleConfig]
        Available bundles (same order as *individual*).
    budget : float
        Budget constraint ($).
    risk_target : float
        Target risk reduction fraction.

    Returns
    -------
    float
        Fitness score.
    """
    total_cost = sum(
        b.estimated_cost for b, sel in zip(bundles, individual) if sel
    )
    total_reduction = 1.0 - np.prod(
        [1.0 - b.expected_risk_reduction for b, sel in zip(bundles, individual) if sel]
        or [1.0]
    )

    # Heavy penalty for exceeding budget
    budget_penalty = max(0.0, (total_cost - budget) / budget) * 2.0
    fitness = total_reduction - budget_penalty
    return float(fitness)


def _tournament_select(
    population: list[list[int]],
    fitnesses: list[float],
    k: int = 3,
    rng: Optional[random.Random] = None,
) -> list[int]:
    """Tournament selection – pick the best of *k* random individuals."""
    rng = rng or random.Random()
    candidates = rng.choices(range(len(population)), k=k)
    best_idx = max(candidates, key=lambda i: fitnesses[i])
    return population[best_idx][:]


def _single_point_crossover(
    parent_a: list[int],
    parent_b: list[int],
    rng: Optional[random.Random] = None,
) -> tuple[list[int], list[int]]:
    """Single-point crossover."""
    rng = rng or random.Random()
    n = len(parent_a)
    point = rng.randint(1, n - 1)
    child_a = parent_a[:point] + parent_b[point:]
    child_b = parent_b[:point] + parent_a[point:]
    return child_a, child_b


def _mutate(
    individual: list[int],
    mutation_rate: float,
    rng: Optional[random.Random] = None,
) -> list[int]:
    """Bit-flip mutation."""
    rng = rng or random.Random()
    return [
        1 - gene if rng.random() < mutation_rate else gene
        for gene in individual
    ]


def _build_pareto_front(
    population: list[list[int]],
    bundles: list[BundleConfig],
) -> list[dict]:
    """Compute the cost–risk-reduction Pareto front."""
    points = []
    for individual in population:
        cost = sum(b.estimated_cost for b, sel in zip(bundles, individual) if sel)
        reduction = 1.0 - np.prod(
            [1.0 - b.expected_risk_reduction for b, sel in zip(bundles, individual) if sel]
            or [1.0]
        )
        points.append({"cost": cost, "risk_reduction": float(reduction), "individual": individual})

    # Non-dominated filter: a point is Pareto-optimal if no other point
    # dominates it (lower cost AND higher or equal reduction, or vice versa)
    pareto = []
    for p in points:
        dominated = False
        for q in points:
            if q["cost"] <= p["cost"] and q["risk_reduction"] >= p["risk_reduction"]:
                if q["cost"] < p["cost"] or q["risk_reduction"] > p["risk_reduction"]:
                    dominated = True
                    break
        if not dominated:
            pareto.append({"cost": p["cost"], "risk_reduction": p["risk_reduction"]})

    return sorted(pareto, key=lambda x: x["cost"])


# ---------------------------------------------------------------------------
# Public optimization function
# ---------------------------------------------------------------------------

def run_optimization(config: SimulationConfig) -> OptimizationResult:
    """Run genetic algorithm bundle optimization.

    Parameters
    ----------
    config : SimulationConfig
        Full simulation configuration including bundle definitions.

    Returns
    -------
    OptimizationResult
        Best solution found and convergence statistics.
    """
    bundles = config.bundles
    if not bundles:
        logger.warning("No bundles configured – returning empty result.")
        return OptimizationResult(
            run_id=config.run_id,
            best_bundle_ids=[],
            best_cost=0.0,
            best_risk_reduction=0.0,
            roi=0.0,
            feasible=True,
            generations_run=0,
        )

    rng_py = random.Random(config.seed)
    n_bundles = len(bundles)

    # Initialise random population
    population = [
        [rng_py.randint(0, 1) for _ in range(n_bundles)]
        for _ in range(config.population_size)
    ]

    fitness_history: list[float] = []
    best_individual: list[int] = population[0]
    best_fitness = float("-inf")

    for generation in range(config.n_generations):
        fitnesses = [
            _evaluate_individual(ind, bundles, config.budget_constraint, config.risk_target)
            for ind in population
        ]

        gen_best_fitness = max(fitnesses)
        gen_best_idx = fitnesses.index(gen_best_fitness)
        fitness_history.append(gen_best_fitness)

        if gen_best_fitness > best_fitness:
            best_fitness = gen_best_fitness
            best_individual = population[gen_best_idx][:]

        # Elitism: carry best individual into next generation
        new_population: list[list[int]] = [best_individual[:]]

        while len(new_population) < config.population_size:
            parent_a = _tournament_select(population, fitnesses, rng=rng_py)
            parent_b = _tournament_select(population, fitnesses, rng=rng_py)

            if rng_py.random() < config.crossover_rate:
                child_a, child_b = _single_point_crossover(parent_a, parent_b, rng=rng_py)
            else:
                child_a, child_b = parent_a[:], parent_b[:]

            new_population.append(_mutate(child_a, config.mutation_rate, rng=rng_py))
            if len(new_population) < config.population_size:
                new_population.append(_mutate(child_b, config.mutation_rate, rng=rng_py))

        population = new_population

    # Final evaluation of best individual
    best_cost = sum(
        b.estimated_cost for b, sel in zip(bundles, best_individual) if sel
    )
    best_reduction = float(
        1.0 - np.prod(
            [1.0 - b.expected_risk_reduction for b, sel in zip(bundles, best_individual) if sel]
            or [1.0]
        )
    )
    selected_bundle_ids = [
        b.bundle_id for b, sel in zip(bundles, best_individual) if sel
    ]
    feasible = best_cost <= config.budget_constraint
    # ROI: (risk_reduction_fraction - cost_fraction_of_budget) / cost_fraction_of_budget
    # Both terms are dimensionless fractions for a fair comparison.
    cost_fraction = best_cost / config.budget_constraint if config.budget_constraint > 0 else 0.0
    roi = (best_reduction - cost_fraction) / cost_fraction if cost_fraction > 0 else 0.0

    pareto_front = _build_pareto_front(population, bundles)

    logger.info(
        "Optimization complete: %d bundles selected, cost=$%.0f, "
        "risk_reduction=%.1f%%, feasible=%s",
        len(selected_bundle_ids),
        best_cost,
        best_reduction * 100,
        feasible,
    )

    return OptimizationResult(
        run_id=config.run_id,
        best_bundle_ids=selected_bundle_ids,
        best_cost=best_cost,
        best_risk_reduction=best_reduction,
        roi=roi,
        feasible=feasible,
        generations_run=config.n_generations,
        fitness_history=fitness_history,
        pareto_front=pareto_front,
    )
