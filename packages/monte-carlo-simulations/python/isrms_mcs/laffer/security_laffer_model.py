"""Security Laffer Model

Models the diminishing-returns relationship between security investment
and risk reduction. Analogous to the Laffer curve in taxation, excessive
security spending eventually yields marginal additional risk reduction.

The model uses a logistic (S-curve) function to represent:
- Initial rapid risk reduction at low spending levels
- Diminishing returns as spending increases
- A theoretical maximum risk reduction ceiling

Migrated from: Laffer_Security_Models/security_laffer_model.py
Changes from original:
- Removed hardcoded Windows paths
- Added type hints, dataclasses, and full docstrings
- Scipy-based curve fitting for empirical data
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

try:
    from scipy.optimize import minimize_scalar, curve_fit

    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False
    logger.warning(
        "scipy not available – curve fitting will use default parameters."
    )


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class SecurityLafferModel:
    """Parameters for the security investment Laffer model.

    The model uses a logistic function:

        risk_reduction(x) = max_reduction / (1 + exp(-k * (x - x0)))

    where *x* is investment as a fraction of the optimal budget.

    Parameters
    ----------
    model_id : str
        Unique identifier.
    facility_id : str
        Associated facility.
    baseline_risk : float
        Pre-investment risk score (0–1 or 0–100 scale).
    max_reduction : float
        Maximum achievable risk reduction fraction (0–1).
    optimal_investment : float
        Investment level ($) at which marginal returns begin diminishing.
    current_investment : float
        Current annual security investment ($).
    curve_steepness : float
        Steepness of the logistic S-curve (logistic *k* parameter;
        default 1e-5; higher = sharper transition at optimal_investment).
    """

    model_id: str
    facility_id: str
    baseline_risk: float
    max_reduction: float
    optimal_investment: float
    current_investment: float
    curve_steepness: float = 1e-5
    tags: list[str] = field(default_factory=list)


@dataclass
class LafferResult:
    """Output of a Laffer security model evaluation.

    Attributes
    ----------
    model_id : str
        Model identifier.
    current_risk_reduction : float
        Risk reduction at current investment level (0–1).
    residual_risk : float
        Remaining risk after current investment.
    optimal_risk_reduction : float
        Risk reduction at optimal investment level.
    marginal_return : float
        Marginal risk reduction per dollar at current investment.
    over_investment_flag : bool
        True if current investment exceeds optimal level.
    investment_gap : float
        Gap between optimal and current investment ($); negative = over-invested.
    roi : float
        Estimated ROI at current investment level.
    investment_curve : dict[str, list[float]]
        Sampled investment levels and corresponding risk reductions.
    """

    model_id: str
    current_risk_reduction: float
    residual_risk: float
    optimal_risk_reduction: float
    marginal_return: float
    over_investment_flag: bool
    investment_gap: float
    roi: float
    investment_curve: dict[str, list[float]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Logistic (S-curve) helpers
# ---------------------------------------------------------------------------

def _logistic(x: np.ndarray, max_r: float, k: float, x0: float) -> np.ndarray:
    """Logistic function for risk reduction vs. investment."""
    # Clip the exponent to avoid overflow
    exponent = np.clip(-k * (x - x0), -500, 500)
    return max_r / (1.0 + np.exp(exponent))


def _marginal_return(
    investment: float,
    max_r: float,
    k: float,
    x0: float,
) -> float:
    """Derivative of the logistic function (marginal return per dollar)."""
    exponent = float(np.clip(-k * (investment - x0), -500, 500))
    e = np.exp(exponent)
    denom = (1.0 + e) ** 2
    if denom == 0:
        return 0.0
    return float(max_r * k * e / denom)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def evaluate_laffer_model(model: SecurityLafferModel) -> LafferResult:
    """Evaluate the security Laffer model at the current investment level.

    Parameters
    ----------
    model : SecurityLafferModel
        Configured Laffer model parameters.

    Returns
    -------
    LafferResult
        Evaluation results including ROI, marginal return, and curve data.
    """
    k = model.curve_steepness
    x0 = model.optimal_investment

    # Investment curve (0 to 2× optimal)
    x_max = max(model.optimal_investment * 2.0, model.current_investment * 1.5)
    x_range = np.linspace(0.0, x_max, 300)
    y_range = _logistic(x_range, model.max_reduction, k, x0)

    current_reduction = float(
        _logistic(
            np.array([model.current_investment]),
            model.max_reduction,
            k,
            x0,
        )[0]
    )
    optimal_reduction = float(
        _logistic(
            np.array([model.optimal_investment]),
            model.max_reduction,
            k,
            x0,
        )[0]
    )

    marginal = _marginal_return(model.current_investment, model.max_reduction, k, x0)
    residual_risk = model.baseline_risk * (1.0 - current_reduction)
    investment_gap = model.optimal_investment - model.current_investment

    # ROI: value of risk reduced relative to investment
    risk_value = model.baseline_risk * current_reduction
    roi = (risk_value - model.current_investment) / model.current_investment if model.current_investment > 0 else 0.0

    return LafferResult(
        model_id=model.model_id,
        current_risk_reduction=current_reduction,
        residual_risk=residual_risk,
        optimal_risk_reduction=optimal_reduction,
        marginal_return=marginal,
        over_investment_flag=model.current_investment > model.optimal_investment,
        investment_gap=investment_gap,
        roi=roi,
        investment_curve={
            "investment": x_range.tolist(),
            "risk_reduction": y_range.tolist(),
        },
    )


def calculate_optimal_investment(
    baseline_risk: float,
    max_reduction: float,
    current_investment: float,
    curve_steepness: float = 1e-5,
    budget_range: tuple[float, float] = (0.0, 1_000_000.0),
) -> float:
    """Find the investment level that maximises risk-reduction ROI.

    Uses scalar minimisation over the budget range to find the inflection
    point of the marginal-return curve.

    Parameters
    ----------
    baseline_risk : float
        Pre-investment risk score.
    max_reduction : float
        Maximum achievable risk reduction fraction.
    current_investment : float
        Current investment level ($), used to initialise the search.
    curve_steepness : float
        Logistic S-curve steepness (*k* parameter).
    budget_range : tuple[float, float]
        (min, max) search bounds in dollars.

    Returns
    -------
    float
        Optimal investment level ($).
    """
    if not _SCIPY_AVAILABLE:
        # Fallback: return midpoint of budget range
        return float(sum(budget_range) / 2.0)

    # Maximise marginal return → find peak of derivative
    def neg_marginal(x: float) -> float:
        return -_marginal_return(x, max_reduction, curve_steepness, current_investment)

    result = minimize_scalar(
        neg_marginal,
        bounds=budget_range,
        method="bounded",
    )
    return float(result.x)


def fit_laffer_model(
    investment_data: list[float],
    risk_reduction_data: list[float],
    facility_id: str = "unknown",
) -> SecurityLafferModel:
    """Fit a Laffer model to empirical investment/risk-reduction observations.

    Requires scipy. Falls back to default parameters if not available.

    Parameters
    ----------
    investment_data : list[float]
        Historical investment levels ($).
    risk_reduction_data : list[float]
        Observed risk reductions corresponding to each investment level (0–1).
    facility_id : str
        Facility identifier for the fitted model.

    Returns
    -------
    SecurityLafferModel
        Fitted model parameters.
    """
    x = np.array(investment_data)
    y = np.array(risk_reduction_data)

    if _SCIPY_AVAILABLE and len(x) >= 3:
        try:
            p0 = [max(y), 1e-5, np.median(x)]
            popt, _ = curve_fit(
                _logistic,
                x,
                y,
                p0=p0,
                maxfev=10_000,
                bounds=([0, 0, 0], [1, np.inf, np.inf]),
            )
            max_r, k, x0 = popt
        except Exception as exc:
            logger.warning("Laffer curve fitting failed: %s – using defaults.", exc)
            max_r, k, x0 = 0.8, 1e-5, float(np.median(x))
    else:
        max_r, k, x0 = 0.8, 1e-5, float(np.median(x)) if len(x) > 0 else 100_000.0

    return SecurityLafferModel(
        model_id=f"{facility_id}_LAFFER_FITTED",
        facility_id=facility_id,
        baseline_risk=1.0,
        max_reduction=float(max_r),
        optimal_investment=float(x0),
        current_investment=float(x[-1]) if len(x) > 0 else 0.0,
        curve_steepness=float(k),
    )
