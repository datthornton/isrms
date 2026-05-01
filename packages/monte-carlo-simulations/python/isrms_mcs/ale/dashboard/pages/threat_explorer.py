"""Threat Explorer Page

Streamlit page for exploring ALE threat scenarios with interactive filters
and Monte Carlo simulation results.

Migrated from: ALE/dashboard/pages/3_Threat_Explorer.py
Changes from original:
- Renamed to threat_explorer.py (snake_case, no numeric prefix)
- Removed hardcoded Windows paths
- Uses isrms_mcs package imports
- Refactored as a callable render function for integration with irms_ui.py
"""

from __future__ import annotations

import logging

import pandas as pd
import plotly.express as px
import streamlit as st

from isrms_mcs.ale.models.ale_equation import simulate_ale, calculate_ale_for_scenario
from isrms_mcs.ale.modules.load_ale_scenarios import load_ale_scenarios

logger = logging.getLogger(__name__)

N_SIMULATIONS = 10_000


@st.cache_data(show_spinner="Loading ALE scenarios…")
def _cached_scenarios() -> list:
    """Load and cache ALE scenarios from the configured workbook."""
    try:
        return load_ale_scenarios()
    except FileNotFoundError as exc:
        st.warning(str(exc))
        return []


def render_threat_explorer() -> None:
    """Render the Threat Explorer Streamlit page."""
    st.header("🔍 Threat Explorer")
    st.markdown(
        "Explore individual threat scenarios, their ALE distributions, and "
        "compare risk levels across your asset portfolio."
    )

    scenarios = _cached_scenarios()

    if not scenarios:
        st.info(
            "No ALE scenarios loaded. Configure `ISRMS_ALE_WORKBOOK` to point "
            "to your ALE workbook and reload the page."
        )
        return

    # -----------------------------------------------------------------------
    # Sidebar filters
    # -----------------------------------------------------------------------
    all_tags: set[str] = set()
    for s in scenarios:
        all_tags.update(s.tags)

    selected_tags = st.sidebar.multiselect(
        "Filter by tag", sorted(all_tags), default=[]
    )

    filtered = (
        [s for s in scenarios if any(t in s.tags for t in selected_tags)]
        if selected_tags
        else scenarios
    )

    st.subheader(f"Scenarios ({len(filtered)} of {len(scenarios)})")

    # -----------------------------------------------------------------------
    # Summary table
    # -----------------------------------------------------------------------
    rows = []
    for s in filtered:
        result = calculate_ale_for_scenario(s)
        rows.append(
            {
                "Scenario ID": s.scenario_id,
                "Threat": s.threat_name,
                "Asset Value ($)": f"{s.asset_value:,.0f}",
                "SLE ($)": f"{result.sle:,.0f}",
                "ARO": f"{result.aro:.4f}",
                "ALE ($)": f"{result.ale:,.0f}",
                "Residual ALE ($)": f"{result.ale_residual:,.0f}",
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    # -----------------------------------------------------------------------
    # Deep-dive: Monte Carlo for selected scenario
    # -----------------------------------------------------------------------
    st.subheader("Monte Carlo Deep-Dive")
    scenario_ids = [s.scenario_id for s in filtered]
    selected_id = st.selectbox("Select scenario", scenario_ids)

    if selected_id:
        scenario = next(s for s in filtered if s.scenario_id == selected_id)
        sim_result = simulate_ale(scenario, n_simulations=N_SIMULATIONS, seed=42)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean ALE", f"${sim_result.ale_mean:,.0f}")
        col2.metric("P50 ALE", f"${sim_result.ale_p50:,.0f}")
        col3.metric("P90 ALE", f"${sim_result.ale_p90:,.0f}")
        col4.metric("P95 ALE", f"${sim_result.ale_p95:,.0f}")

        fig = px.histogram(
            x=sim_result.ale_samples,
            nbins=100,
            title=f"ALE Distribution – {scenario.threat_name}",
            labels={"x": "ALE ($)", "y": "Frequency"},
            template="plotly_white",
        )
        fig.add_vline(
            x=sim_result.ale_p90,
            line_dash="dash",
            annotation_text="P90",
            line_color="red",
        )
        st.plotly_chart(fig, use_container_width=True)
