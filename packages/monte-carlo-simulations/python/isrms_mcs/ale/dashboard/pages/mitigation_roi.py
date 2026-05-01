"""Mitigation ROI Page

Streamlit page for comparing the return-on-investment of security
mitigation measures across ALE threat scenarios.

Migrated from: ALE/dashboard/pages/4_Mitigation_ROI.py
Changes from original:
- Renamed to mitigation_roi.py (snake_case, no numeric prefix)
- Removed hardcoded Windows paths
- Uses isrms_mcs package imports
- Refactored as a callable render function
"""

from __future__ import annotations

import logging

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from isrms_mcs.ale.models.ale_equation import (
    ALEScenario,
    simulate_ale,
    calculate_ale_for_scenario,
)
from isrms_mcs.ale.modules.load_ale_scenarios import load_ale_scenarios

logger = logging.getLogger(__name__)

N_SIMULATIONS = 10_000


@st.cache_data(show_spinner="Loading ALE scenarios…")
def _cached_scenarios() -> list:
    """Load and cache ALE scenarios."""
    try:
        return load_ale_scenarios()
    except FileNotFoundError as exc:
        st.warning(str(exc))
        return []


def _calculate_roi(ale_before: float, ale_after: float, control_cost: float) -> float:
    """Calculate ROI for a mitigation measure.

    ROI = (Risk Reduction – Control Cost) / Control Cost

    Parameters
    ----------
    ale_before : float
        ALE before the control is applied.
    ale_after : float
        Residual ALE after the control is applied.
    control_cost : float
        Annual cost of implementing the control.

    Returns
    -------
    float
        ROI as a decimal (e.g. 1.5 = 150 % return).
    """
    risk_reduction = ale_before - ale_after
    if control_cost <= 0:
        return 0.0
    return (risk_reduction - control_cost) / control_cost


def render_mitigation_roi() -> None:
    """Render the Mitigation ROI Streamlit page."""
    st.header("💰 Mitigation ROI Analysis")
    st.markdown(
        "Compare the cost-effectiveness of security controls by measuring the "
        "reduction in Annual Loss Expectancy (ALE) relative to implementation cost."
    )

    scenarios = _cached_scenarios()

    if not scenarios:
        st.info(
            "No ALE scenarios loaded. Configure `ISRMS_ALE_WORKBOOK` and reload."
        )
        return

    # -----------------------------------------------------------------------
    # Sidebar: control cost inputs
    # -----------------------------------------------------------------------
    st.sidebar.subheader("Control Cost Inputs")
    st.sidebar.markdown("Enter the **annual cost** for each mitigation control.")

    control_costs: dict[str, float] = {}
    for scenario in scenarios:
        default_cost = 5_000.0
        cost = st.sidebar.number_input(
            f"{scenario.scenario_id} – Control Cost ($)",
            min_value=0.0,
            value=default_cost,
            step=500.0,
            key=f"cost_{scenario.scenario_id}",
        )
        control_costs[scenario.scenario_id] = cost

    # -----------------------------------------------------------------------
    # Build comparison table
    # -----------------------------------------------------------------------
    rows = []
    for scenario in scenarios:
        base = calculate_ale_for_scenario(scenario)
        ale_before = base.ale
        ale_after = base.ale_residual
        cost = control_costs.get(scenario.scenario_id, 0.0)
        roi = _calculate_roi(ale_before, ale_after, cost)
        rows.append(
            {
                "Scenario": scenario.threat_name,
                "ALE Before ($)": ale_before,
                "ALE After ($)": ale_after,
                "Risk Reduction ($)": ale_before - ale_after,
                "Control Cost ($)": cost,
                "ROI": roi,
            }
        )

    df = pd.DataFrame(rows)

    # Format for display
    fmt_df = df.copy()
    for col in ["ALE Before ($)", "ALE After ($)", "Risk Reduction ($)", "Control Cost ($)"]:
        fmt_df[col] = fmt_df[col].map("${:,.0f}".format)
    fmt_df["ROI"] = df["ROI"].map("{:.1%}".format)

    st.subheader("ROI Summary Table")
    st.dataframe(fmt_df, use_container_width=True)

    # -----------------------------------------------------------------------
    # Bar chart: ROI by scenario
    # -----------------------------------------------------------------------
    st.subheader("ROI by Scenario")
    fig = go.Figure(
        data=[
            go.Bar(
                x=df["Scenario"],
                y=df["ROI"] * 100,
                marker_color=[
                    "green" if v > 0 else "red" for v in df["ROI"]
                ],
                text=[f"{v:.1%}" for v in df["ROI"]],
                textposition="outside",
            )
        ]
    )
    fig.update_layout(
        yaxis_title="ROI (%)",
        xaxis_title="Threat Scenario",
        template="plotly_white",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------------------------
    # Waterfall: ALE before vs after
    # -----------------------------------------------------------------------
    st.subheader("ALE Before vs After Controls")
    fig2 = go.Figure(
        data=[
            go.Bar(name="ALE Before", x=df["Scenario"], y=df["ALE Before ($)"]),
            go.Bar(name="ALE After", x=df["Scenario"], y=df["ALE After ($)"]),
        ]
    )
    fig2.update_layout(
        barmode="group",
        yaxis_title="ALE ($)",
        template="plotly_white",
    )
    st.plotly_chart(fig2, use_container_width=True)
