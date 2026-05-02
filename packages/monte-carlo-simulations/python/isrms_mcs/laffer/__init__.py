"""Laffer Security Models Module"""

from .security_laffer_model import (
    SecurityLafferModel,
    LafferResult,
    calculate_optimal_investment,
)

__all__ = [
    "SecurityLafferModel",
    "LafferResult",
    "calculate_optimal_investment",
]
