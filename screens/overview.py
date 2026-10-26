"""Overview Dashboard screen implementation for BhujalDrishti."""
import pandas as pd
import streamlit as st

from services.data_loader import get_latest_per_station
from services.metrics_service import get_model_metrics
from components.metric_cards import render_overview_kpis, render_depth_distribution_bar
from components.callouts import render_depth_tier_note
from components.tables import render_latest_stations_table
from components.charts import render_rainfall_groundwater_chart
from styles.theme import get_current_theme


def render_overview_screen(df: pd.DataFrame, models: dict) -> None:
    """Render Screen 1: Overview Dashboard."""
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">📊 Purandar Groundwater Overview</div>
        <div class="sub-header">Regional groundwater health, seasonal dynamics, and station alert indicators across Purandar Taluka</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate latest snapshot across the 11 monitoring stations
    latest_per_station = get_latest_per_station(df)
    avg_latest_mbgl = float(latest_per_station['gw_level_mbgl'].mean())
    station_count = int(df['station'].nunique())
    total_obs_records = int(len(df))
    
    # Retrieve held-out model accuracy dynamically from metadata
    meta = models.get('metadata', {})
    model_metrics = get_model_metrics(meta)
    rf_mae_eval = model_metrics['rf_mae']
    
    deep_count = int((latest_per_station['gw_level_mbgl'] > 8.0).sum())
    moderate_count = int(((latest_per_station['gw_level_mbgl'] >= 4.0) & (latest_per_station['gw_level_mbgl'] <= 8.0)).sum())
    shallow_count = int((latest_per_station['gw_level_mbgl'] < 4.0).sum())
    
    # Primary Dynamically Computed KPI Row
    render_overview_kpis(
        avg_mbgl=avg_latest_mbgl,
        station_count=station_count,
        total_records=total_obs_records,
        rf_mae=rf_mae_eval
    )
    
    # Depth Reference Tier Secondary Summary Pill Bar
    render_depth_distribution_bar(
        shallow_count=shallow_count,
        moderate_count=moderate_count,
        deep_count=deep_count,
        total_count=station_count
    )
    
    # Methodological Classification Callout
    render_depth_tier_note()
    
    # Two-column layout: Latest Station Table & Rainfall/Groundwater Correlation
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.subheader("📍 Latest Monitoring Station Status")
        render_latest_stations_table(latest_per_station)
        
    with col_right:
        st.subheader("🌧️ Taluka Rainfall vs. Water Table Trends")
        active_theme = get_current_theme()
        render_rainfall_groundwater_chart(df, theme=active_theme)
        
    st.info("💡 **Hydrogeological Insight**: Notice how years with higher rainfall (e.g., 2005, 2019, 2020) directly correspond to shallower water tables (water closer to the surface, appearing higher on the inverted axis).")
