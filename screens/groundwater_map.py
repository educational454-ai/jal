"""Groundwater Map screen implementation for BhujalDrishti."""
import pandas as pd
import streamlit as st

from services.data_loader import get_latest_per_station, get_depth_tier_category
from components.map_view import render_groundwater_map
from components.callouts import render_spatial_model_status_expander
from styles.theme import get_current_theme


def render_groundwater_map_screen(df: pd.DataFrame) -> None:
    """Render Screen 2: Groundwater Map."""
    # A. Page Heading (Restrained, scientific, consistent with Screen 1)
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">Purandar Groundwater Telemetry Map</div>
        <div class="sub-header">In-situ water level observations across 11 CGWB monitoring wells · Purandar Taluka</div>
    </div>
    """, unsafe_allow_html=True)
    
    latest_st = get_latest_per_station(df)
    active_theme = get_current_theme()
    
    # B. GIS Controls and Depth Tier Legend Toolbar
    c_legend, c_filter = st.columns([1.9, 1.1])
    with c_legend:
        st.markdown("""
        <div class="map-legend-bar">
            <span class="map-legend-title">Depth Tiers:</span>
            <span class="badge-shallow" title="Shallow: < 4.0 m MBGL">● Shallow (&lt; 4.0 m)</span>
            <span class="badge-moderate" title="Moderate: 4.0–8.0 m MBGL">● Moderate (4.0–8.0 m)</span>
            <span class="badge-deep" title="Deep: > 8.0 m MBGL">● Deep (&gt; 8.0 m)</span>
        </div>
        """, unsafe_allow_html=True)
        
    with c_filter:
        selected_zone_filter = st.selectbox(
            "Filter Stations by Depth Tier", 
            ["All Stations", "Shallow (< 4.0 m)", "Moderate (4.0–8.0 m)", "Deep (> 8.0 m)"],
            index=0,
            key="map_depth_filter_select",
            label_visibility="collapsed",
            help="Filter map markers to display all stations or only stations within a specific depth tier."
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
        
    # C. Interactive Map View (Full Width with comfortable 560px height)
    render_groundwater_map(filtered_stations, theme=active_theme)

    # D. Methodological Disclaimers and Spatial Layer Research Context
    st.caption("ℹ️ *Note: Station markers display physical in-situ measurements at fixed CGWB monitoring wells. Point color denotes observed water level in Meters Below Ground Level (MBGL). Reference bands (< 4.0 m, 4.0–8.0 m, > 8.0 m) are project-defined physical tiers, not official administrative categories.*")
    
    # Methodological findings on spatial interpolation and LOSO-CV
    render_spatial_model_status_expander()
