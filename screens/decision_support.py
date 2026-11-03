"""Conservation Decision Support screen implementation for BhujalDrishti."""
import pandas as pd
import streamlit as st

from services.data_loader import (
    get_latest_per_station,
    get_depth_tier_category,
    get_intervention_plan
)
from components.callouts import render_decision_support_advisory_notice


def render_decision_support_screen(df: pd.DataFrame) -> None:
    """Render Screen 4: Conservation Decision Support Dashboard."""
    # -------------------------------------------------------------
    # Section A: Page Heading
    # -------------------------------------------------------------
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">Conservation Decision Support</div>
        <div class="sub-header">Station-level groundwater assessment and conservation recommendations for Purandar Taluka</div>
    </div>
    """, unsafe_allow_html=True)
    
    render_decision_support_advisory_notice()

    # -------------------------------------------------------------
    # Section B: Taluka-wide Summary Cards (Dynamic)
    # -------------------------------------------------------------
    latest_st = get_latest_per_station(df)
    total_wells = len(latest_st)
    
    # Calculate canonical categories dynamically
    categories = latest_st['gw_level_mbgl'].apply(get_depth_tier_category)
    deep_count = int((categories == "Deep").sum())
    moderate_count = int((categories == "Moderate").sum())
    shallow_count = int((categories == "Shallow").sum())
    unknown_count = int((categories == "Unknown").sum())

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f'<div class="kpi-card kpi-card-total">'
            f'<div class="kpi-top">'
            f'<div class="kpi-label">Total Monitoring Stations</div>'
            f'<div class="kpi-value">{total_wells} Wells</div>'
            f'</div>'
            f'<div class="kpi-caption">CGWB monitoring stations represented in the historical dataset.</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f'<div class="kpi-card kpi-card-deep">'
            f'<div class="kpi-top">'
            f'<div class="kpi-label">Deep Tier Stations (&gt; 8.0 m)</div>'
            f'<div class="kpi-value" style="color: var(--badge-deep-text);">{deep_count} Stations</div>'
            f'</div>'
            f'<div class="kpi-caption">High vulnerability; prioritize recharge feasibility & pumping review.</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f'<div class="kpi-card kpi-card-moderate">'
            f'<div class="kpi-top">'
            f'<div class="kpi-label">Moderate Tier Stations (4.0–8.0 m)</div>'
            f'<div class="kpi-value" style="color: var(--badge-moderate-text);">{moderate_count} Stations</div>'
            f'</div>'
            f'<div class="kpi-caption">Precautionary stewardship; contour bunding & micro-irrigation.</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            f'<div class="kpi-card kpi-card-shallow">'
            f'<div class="kpi-top">'
            f'<div class="kpi-label">Shallow Tier Stations (&lt; 4.0 m)</div>'
            f'<div class="kpi-value" style="color: var(--badge-shallow-text);">{shallow_count} Stations</div>'
            f'</div>'
            f'<div class="kpi-caption">Safe equilibrium; regular vigilance & participatory budgeting.</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    if unknown_count > 0:
        st.warning(f"⚠️ **Incomplete Telemetry Alert**: {unknown_count} monitoring station(s) have unrecorded or missing depth measurements.")

    # -------------------------------------------------------------
    # Section C: Station Prioritization and Filters
    # -------------------------------------------------------------
    st.markdown("### Station Assessment & Conservation Planning")
    st.markdown(
        '<div class="station-assessment-note">'
        'ℹ️ <i>Station assessments are based on each station\'s latest available historical observation, not live measurements.</i>'
        '</div>',
        unsafe_allow_html=True
    )
    
    with st.container():
        f1, f2, f3 = st.columns([1.5, 1.3, 1.2])
        with f1:
            station_search = st.text_input(
                "Search Station",
                "",
                placeholder="Search by name (e.g. Saswad, Jejuri, Walha)...",
                key="ds_search_station",
                help="Filter the displayed stations by name."
            )
        with f2:
            tier_options = ["All Tiers", "Deep (> 8.0 m)", "Moderate (4.0–8.0 m)", "Shallow (< 4.0 m)"]
            if unknown_count > 0:
                tier_options.append("Unknown / Unclassified")
            tier_filter = st.selectbox(
                "Filter by Vulnerability Tier",
                tier_options,
                index=0,
                key="ds_tier_filter",
                help="Filter stations by their project-defined physical reference depth tier."
            )
        with f3:
            sort_option = st.selectbox(
                "Sort Stations",
                ["Vulnerability (Deepest First)", "Water Table (Shallowest First)", "Alphabetical (A–Z)"],
                index=0,
                key="ds_sort_option",
                help="Order stations to prioritize critical locations or organize alphabetically."
            )

    # Filter logic
    filtered_df = latest_st.copy()
    filtered_df['category'] = filtered_df['gw_level_mbgl'].apply(get_depth_tier_category)

    if "Deep" in tier_filter:
        filtered_df = filtered_df[filtered_df['category'] == "Deep"]
    elif "Moderate" in tier_filter:
        filtered_df = filtered_df[filtered_df['category'] == "Moderate"]
    elif "Shallow" in tier_filter:
        filtered_df = filtered_df[filtered_df['category'] == "Shallow"]
    elif "Unknown" in tier_filter:
        filtered_df = filtered_df[filtered_df['category'] == "Unknown"]

    if station_search.strip():
        query = station_search.strip()
        filtered_df = filtered_df[filtered_df['station'].str.contains(query, case=False, na=False)]

    # Sorting logic
    if "Deepest First" in sort_option:
        filtered_df = filtered_df.sort_values(by="gw_level_mbgl", ascending=False, na_position="last")
    elif "Shallowest First" in sort_option:
        filtered_df = filtered_df.sort_values(by="gw_level_mbgl", ascending=True, na_position="last")
    elif "Alphabetical" in sort_option:
        filtered_df = filtered_df.sort_values(by="station", ascending=True)

    st.markdown(
        f"<div class='results-count-bar'>Showing <b>{len(filtered_df)}</b> of <b>{total_wells}</b> monitoring stations</div>",
        unsafe_allow_html=True
    )

    # -------------------------------------------------------------
    # Section D & E: Station Details & Conservation Recommendations
    # -------------------------------------------------------------
    if filtered_df.empty:
        st.info(f"No monitoring stations match your search query '{station_search}' in the selected tier ({tier_filter}).")
    else:
        is_single = len(filtered_df) == 1
        for _, st_row in filtered_df.iterrows():
            st_name = st_row['station']
            depth = st_row['gw_level_mbgl']
            plan = get_intervention_plan(depth)

            icon = plan['icon']
            tier_label = plan['tier_label']
            priority = plan['priority']
            category = plan['category']
            badge_class = plan['badge']

            obs_date = st_row['date'].strftime('%d %b %Y') if pd.notna(st_row.get('date')) else 'N/A'
            season_tag = st_row.get('season_tag', 'N/A')
            rain_90 = f"{st_row['rain_90d']:.1f} mm" if pd.notna(st_row.get('rain_90d')) else "N/A"
            rain_365 = f"{st_row['rain_365d']:.1f} mm" if pd.notna(st_row.get('rain_365d')) else "N/A"
            is_extrapolated = bool(st_row.get('is_rainfall_extrapolated', 0))

            if pd.notna(depth) and isinstance(depth, (int, float)):
                depth_val_str = f"{depth:.2f}"
                depth_unit_str = "m MBGL"
            else:
                depth_val_str = "Unrecorded"
                depth_unit_str = ""

            extrap_badge_html = f'<span class="station-extrap-badge">⚠️ Spatially Extrapolated Rain</span>' if is_extrapolated else ""
            extrap_warning_html = f'<div class="station-extrap-warning">⚠️ <i>Station lies outside the 4-point IMD precipitation grid; rainfall lookbacks are spatially extrapolated from the nearest grid coordinates.</i></div>' if is_extrapolated else ""

            # Structured Station Card with zero CommonMark indentation hazards
            card_html = (
                f'<div class="decision-station-card tier-{category.lower()}">'
                f'<div class="station-card-top">'
                f'<div class="station-identity">'
                f'<span class="station-name">{st_name}</span>'
                f'<span class="{badge_class}">{tier_label}</span>'
                f'{extrap_badge_html}'
                f'</div>'
                f'<div class="station-depth-hero hero-{category.lower()}">'
                f'<span class="station-depth-val">{depth_val_str}</span>'
                f'<span class="station-depth-unit">{depth_unit_str}</span>'
                f'</div>'
                f'</div>'
                f'<div class="station-telemetry-grid">'
                f'<div class="telemetry-item"><span class="telemetry-lbl">Observation Date</span><span class="telemetry-val">{obs_date}</span></div>'
                f'<div class="telemetry-item"><span class="telemetry-lbl">Season</span><span class="telemetry-val">{season_tag}</span></div>'
                f'<div class="telemetry-item"><span class="telemetry-lbl">Past 90-Day Rain</span><span class="telemetry-val">{rain_90}</span></div>'
                f'<div class="telemetry-item"><span class="telemetry-lbl">Past 365-Day Rain</span><span class="telemetry-val">{rain_365}</span></div>'
                f'</div>'
                f'{extrap_warning_html}'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

            # Section E: Conservation Recommendations Expander Interaction
            with st.expander(f"📋 View Conservation Recommendations — {st_name} ({priority})", expanded=is_single):
                banner_html = (
                    f'<div class="decision-priority-banner priority-{category.lower()}">'
                    f'<span class="priority-banner-icon">{icon}</span>'
                    f'<div class="priority-banner-text">'
                    f'<div class="priority-banner-title">{priority}</div>'
                    f'<div class="priority-banner-sub">{plan["priority_level"]}</div>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(banner_html, unsafe_allow_html=True)

                actions_rows = "".join([
                    f'<div class="decision-action-item">'
                    f'<div class="action-num-badge">{idx + 1}</div>'
                    f'<div class="action-body">'
                    f'<div class="action-title">{title}</div>'
                    f'<div class="action-desc">{desc}</div>'
                    f'</div>'
                    f'</div>'
                    for idx, (title, desc) in enumerate(plan['actions'])
                ])
                actions_html = f'<div class="decision-actions-list">{actions_rows}</div>'
                st.markdown(actions_html, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # Section F: Scientific Limitations & Methodological Boundaries
    # -------------------------------------------------------------
    st.markdown("---")
    with st.expander("⚖️ **Scientific Assumptions, Methodological Boundaries & Limitations**", expanded=False):
        st.markdown("""
        1. **Physical Reference Tiers vs. Official Administrative Classifications**: Depth tiers (`< 4.0 m`, `4.0–8.0 m`, `> 8.0 m MBGL`) represent project-defined physical reference bands for instantaneous telemetry visualization. They do not constitute official Central Ground Water Board (CGWB) or Groundwater Estimation Committee (GEC) administrative classifications (*Safe, Semi-Critical, Critical, Over-Exploited*), which evaluate annual recharge vs. annual extraction budgets at the entire taluka level.
        2. **Groundwater Depth & Depletion Dynamics**: Water table depth alone does not prove aquifer depletion, identify localized root causes (e.g. localized pumping vs. seasonal recharge deficits), or prove the necessity of a specific engineering intervention at a site.
        3. **Site-Specific Feasibility Surveys**: Interventions presented are rule-based hydrogeological heuristics synthesized from standard CGWB and GSDA watershed conservation guidelines. All structural interventions (check dams, percolation tanks, injection wells) require on-site geophysical, lithological, and civil engineering surveys prior to execution.
        4. **Precipitation Grid Extrapolation**: Four peripheral monitoring stations (*Pimpri (Kh) Malvasti, Kamatwadi-Walha, Walha, Narayanpur*) lie outside the 4-point 0.25° IMD precipitation grid; antecedent rainfall metrics at these locations are spatially extrapolated.
        """)
