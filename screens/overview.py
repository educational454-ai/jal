"""Overview Dashboard screen implementation for BhujalDrishti."""
import pandas as pd
import streamlit as st

from services.data_loader import get_latest_per_station, get_depth_tier_category
from components.metric_cards import render_overview_kpis, render_depth_distribution_summary
from components.tables import render_latest_stations_table
from components.charts import render_regional_groundwater_chart, render_compact_rainfall_chart
from styles.theme import get_current_theme


def render_overview_screen(df: pd.DataFrame, models: dict) -> None:
    """Render Screen 1: Overview Dashboard."""
    # A. Page Heading (Restrained, scientific, no emojis)
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">Purandar Groundwater Overview</div>
        <div class="sub-header">Historical groundwater observations and rainfall patterns · 1996–2023</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate latest snapshot across the 11 monitoring stations
    latest_per_station = get_latest_per_station(df)
    avg_latest_mbgl = float(latest_per_station['gw_level_mbgl'].mean())
    station_count = int(df['station'].nunique())
    total_obs_records = int(len(df))
    
    categories = latest_per_station['gw_level_mbgl'].apply(get_depth_tier_category)
    deep_count = int((categories == "Deep").sum())
    moderate_count = int((categories == "Moderate").sum())
    shallow_count = int((categories == "Shallow").sum())
    
    active_theme = get_current_theme()
    
    # B. Three compact KPI cards (Held-out model MAE removed from Screen 1)
    render_overview_kpis(
        avg_mbgl=avg_latest_mbgl,
        station_count=station_count,
        total_records=total_obs_records
    )
    
    # C. Main Groundwater Chart (Full available content width)
    station_options = ["All Stations (Regional Mean Trend)"] + sorted(df['station'].unique().tolist())
    c_title, c_scope = st.columns([1.6, 1.0])
    with c_title:
        st.subheader("Historical Groundwater Trends")
    with c_scope:
        selected_scope = st.selectbox(
            "Station View Scope",
            options=station_options,
            index=0,
            key="overview_chart_station_scope",
            label_visibility="collapsed",
            help="Select 'All Stations' to view the regional min-max envelope, or isolate an individual monitoring well."
        )
        
    render_regional_groundwater_chart(df, station_filter=selected_scope, theme=active_theme)
    
    # D. Secondary Information (Balanced 2-Column Row)
    col_rain, col_dist = st.columns(2)
    
    with col_rain:
        st.subheader("Preceding 365d Rainfall History")
        render_compact_rainfall_chart(df, theme=active_theme)
        
    with col_dist:
        st.subheader("Groundwater Depth Distribution")
        render_depth_distribution_summary(
            shallow_count=shallow_count,
            moderate_count=moderate_count,
            deep_count=deep_count,
            total_count=station_count
        )
        
    # E. Latest Station Observations (Full Width)
    st.subheader("Latest Station Observations")
    render_latest_stations_table(latest_per_station)
