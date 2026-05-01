"""ALE (Annual Loss Estimation) Module

Provides models and dashboard components for Annual Loss Estimation,
threat exploration, and mitigation ROI analysis.

Sub-packages
-----------
models
    Core ALE equation and calculation engine.
modules
    Data loading utilities for ALE scenarios.
dashboard
    Streamlit dashboard components.
"""

from .models.ale_equation import calculate_ale, calculate_sle, calculate_aro

__all__ = [
    "calculate_ale",
    "calculate_sle",
    "calculate_aro",
]
