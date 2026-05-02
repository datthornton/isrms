"""ALE Dashboard – IRMS UI

Main Streamlit entry-point for the Annual Loss Estimation dashboard.
Provides navigation to sub-pages:
  - Threat Explorer
  - Mitigation ROI

Migrated from: ALE/dashboard/irms_ui.py
Changes from original:
- Removed hardcoded Windows paths
- Uses isrms_mcs package imports
- Streamlit multi-page navigation via st.navigation / st.sidebar
"""

from __future__ import annotations

import streamlit as st

from isrms_mcs.ale.modules.load_ale_scenarios import load_ale_scenarios


def main() -> None:
    """Run the ALE IRMS dashboard."""
    st.set_page_config(
        page_title="IRMS – Annual Loss Estimation",
        page_icon="📊",
        layout="wide",
    )

    st.title("IRMS Annual Loss Estimation (ALE) Dashboard")
    st.markdown(
        """
        This dashboard provides Annual Loss Estimation analysis tools for security
        risk management. Use the sidebar to navigate between modules.
        """
    )

    # -----------------------------------------------------------------------
    # Sidebar navigation
    # -----------------------------------------------------------------------
    page = st.sidebar.selectbox(
        "Navigate to",
        ["Home", "Threat Explorer", "Mitigation ROI"],
    )

    if page == "Home":
        _render_home()
    elif page == "Threat Explorer":
        from isrms_mcs.ale.dashboard.pages.threat_explorer import render_threat_explorer

        render_threat_explorer()
    elif page == "Mitigation ROI":
        from isrms_mcs.ale.dashboard.pages.mitigation_roi import render_mitigation_roi

        render_mitigation_roi()


def _render_home() -> None:
    """Render the home / overview page."""
    st.header("Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Module", "ALE")
    with col2:
        st.metric("Status", "Active")
    with col3:
        st.metric("Version", "0.1.0")

    st.markdown(
        """
        ### What is ALE?

        **Annual Loss Expectancy (ALE)** is the expected monetary loss for an asset
        due to a risk over a one-year period.

        ```
        SLE  = Asset Value × Exposure Factor
        ALE  = SLE × Annualised Rate of Occurrence (ARO)
        ```

        Monte Carlo simulation is used to produce probabilistic ALE estimates when
        exact values for Exposure Factor and ARO are uncertain.

        ### Getting Started

        1. Ensure `ALE_workbook.xlsx` is available and `ISRMS_ALE_WORKBOOK` is set.
        2. Navigate to **Threat Explorer** to review loaded scenarios.
        3. Navigate to **Mitigation ROI** to compare mitigation options.
        """
    )


if __name__ == "__main__":
    main()
