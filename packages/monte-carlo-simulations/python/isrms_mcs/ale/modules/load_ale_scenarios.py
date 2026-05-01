"""ALE Scenario Loader

Loads threat scenarios from an Excel workbook (ALE_workbook.xlsx) into
:class:`~isrms_mcs.ale.models.ale_equation.ALEScenario` objects.

The workbook path is resolved in the following order:
1. Explicit ``workbook_path`` argument passed to :func:`load_ale_scenarios`.
2. ``ISRMS_ALE_WORKBOOK`` environment variable.
3. ``<repo-root>/data/ALE_workbook.xlsx`` (development fallback).

Migrated from: ALE/modules/load_ale_scenarios.py
Changes from original:
- Removed hardcoded Windows path (``C:\\Users\\justi\\...``)
- Path resolved via environment variable or relative to package root
- Uses pandas for Excel parsing
- Added type hints and docstrings
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

import pandas as pd

from isrms_mcs.ale.models.ale_equation import ALEScenario

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default workbook location (overridable via environment variable)
# ---------------------------------------------------------------------------
_DEFAULT_WORKBOOK = Path(__file__).parents[5] / "data" / "ALE_workbook.xlsx"

# Required columns in the "Scenarios" sheet
_REQUIRED_COLUMNS = {
    "scenario_id",
    "threat_name",
    "asset_value",
    "exposure_factor_min",
    "exposure_factor_mode",
    "exposure_factor_max",
    "aro_min",
    "aro_mode",
    "aro_max",
}

_OPTIONAL_COLUMNS = {
    "control_effectiveness",
    "tags",
}


def _resolve_workbook_path(workbook_path: Optional[Path | str]) -> Path:
    """Return the resolved workbook path from argument, env var, or default."""
    if workbook_path is not None:
        return Path(workbook_path)
    env_path = os.environ.get("ISRMS_ALE_WORKBOOK")
    if env_path:
        return Path(env_path)
    return _DEFAULT_WORKBOOK


def load_ale_scenarios(
    workbook_path: Optional[Path | str] = None,
    sheet_name: str = "Scenarios",
) -> list[ALEScenario]:
    """Load ALE threat scenarios from an Excel workbook.

    Parameters
    ----------
    workbook_path : str or Path, optional
        Path to the ALE workbook. Falls back to the ``ISRMS_ALE_WORKBOOK``
        environment variable, then to the repository-level default.
    sheet_name : str
        Name of the worksheet containing scenario data. Default: ``"Scenarios"``.

    Returns
    -------
    list[ALEScenario]
        List of parsed scenario objects.

    Raises
    ------
    FileNotFoundError
        If the workbook cannot be found at the resolved path.
    ValueError
        If required columns are missing from the sheet.
    """
    path = _resolve_workbook_path(workbook_path)

    if not path.exists():
        raise FileNotFoundError(
            f"ALE workbook not found at '{path}'. "
            "Set the ISRMS_ALE_WORKBOOK environment variable or pass an explicit path."
        )

    logger.info("Loading ALE scenarios from %s (sheet: %s)", path, sheet_name)
    df = pd.read_excel(path, sheet_name=sheet_name)

    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing = _REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"ALE workbook sheet '{sheet_name}' is missing required columns: {missing}"
        )

    scenarios: list[ALEScenario] = []
    for _, row in df.iterrows():
        try:
            tags_raw = row.get("tags", "")
            tags = (
                [t.strip() for t in str(tags_raw).split(",") if t.strip()]
                if pd.notna(tags_raw)
                else []
            )

            scenario = ALEScenario(
                scenario_id=str(row["scenario_id"]),
                threat_name=str(row["threat_name"]),
                asset_value=float(row["asset_value"]),
                exposure_factor_min=float(row["exposure_factor_min"]),
                exposure_factor_mode=float(row["exposure_factor_mode"]),
                exposure_factor_max=float(row["exposure_factor_max"]),
                aro_min=float(row["aro_min"]),
                aro_mode=float(row["aro_mode"]),
                aro_max=float(row["aro_max"]),
                control_effectiveness=float(row.get("control_effectiveness", 0.0)),
                tags=tags,
            )
            scenarios.append(scenario)
        except Exception as exc:
            logger.warning("Skipping malformed scenario row: %s – %s", dict(row), exc)

    logger.info("Loaded %d ALE scenarios", len(scenarios))
    return scenarios
