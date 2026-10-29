"""Groundwater Map screen implementation for BhujalDrishti."""
import pandas as pd
import streamlit as st

from services.data_loader import get_latest_per_station, get_depth_tier_category
from components.map_view import render_groundwater_map
from components.callouts import render_spatial_model_status_expander
from styles.theme import get_current_theme


def render_groundwater_map_screen(df: pd.DataFrame) -> None:
    """Render Screen 2: Groundwater Map."""
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">🗺️ Purandar Groundwater Telemetry Map</div>
        <div class="sub-header">Observed station telemetry across 11 CGWB monitoring wells with standardized depth color coding</div>
    </div>
    """, unsafe_allow_html=True)
    
    latest_st = get_latest_per_station(df)
    active_theme = get_current_theme()
    
    c_m1, c_m2 = st.columns([3, 1])
    with c_m2:
        st.markdown("#### **Map Controls & Legend**")
        st.markdown("""
        - 🟢 **Shallow Depth**: $< 4.0\\text{ m}$ MBGL *(water close to surface)*
        - 🟡 **Moderate Depth**: $4.0 - 8.0\\text{ m}$ MBGL
        - 🔴 **Deep Water Table**: $> 8.0\\text{ m}$ MBGL *(localized/seasonal drawdown)*
        """)
        st.caption("Fixed-size markers indicate observed in-situ water levels at CGWB stations. Color represents depth below ground surface based on physical reference bands.")
        
        selected_zone_filter = st.selectbox(
            "Filter by Depth Tier", 
            ["All Stations", "Shallow (< 4.0 m)", "Moderate (4.0–8.0 m)", "Deep (> 8.0 m)"]
        )
        
    filtered_stations = latest_st.copy()
    filter_category_map = {
        "Shallow (< 4.0 m)": "Shallow",
        "Moderate (4.0–8.0 m)": "Moderate",
        "Deep (> 8.0 m)": "Deep",
        "Shallow (< 4m)": "Shallow",
        "Moderate (4-8m)": "Moderate",
        "Deep (> 8m)": "Deep",
    }
    target_category = filter_category_map.get(selected_zone_filter)
    if target_category:
        filtered_stations = filtered_stations[
            filtered_stations['gw_level_mbgl'].apply(get_depth_tier_category) == target_category
        ]
        
    with c_m1:
        render_groundwater_map(filtered_stations, theme=active_theme)

    st.caption("ℹ️ *Note: Station markers display physical in-situ measurements at fixed CGWB monitoring wells. Point color denotes observed water level in Meters Below Ground Level (MBGL). Reference bands (<4m, 4–8m, >8m) are project-defined physical tiers, not official administrative categories.*")
    
    # Methodological findings on spatial interpolation and LOSO-CV
    render_spatial_model_status_expander()
