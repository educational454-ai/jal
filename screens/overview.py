"""Overview Dashboard screen implementation for BhujalDrishti."""
import pandas as pd
import streamlit as st

from services.data_loader import (
    get_latest_per_station, 
    get_depth_tier_category,
    get_seasonal_matched_comparison,
    get_rainfall_groundwater_correlations
)
from components.metric_cards import (
    render_overview_kpis, 
    render_depth_distribution_summary,
    render_kpi_card
)
from components.tables import render_latest_stations_table
from components.charts import (
    render_regional_groundwater_chart, 
    render_compact_rainfall_chart,
    render_seasonal_comparison_chart,
    render_rainfall_groundwater_chart
)
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
    
    # F. Seasonal Groundwater Analysis (Collapsible Expander)
    render_seasonal_analysis_section(df, theme=active_theme)
    
    # G. Rainfall & Groundwater Relationship (Collapsible Expander)
    render_rainfall_relationship_section(df, theme=active_theme)


def render_seasonal_analysis_section(df: pd.DataFrame, theme: str = "light") -> None:
    """Render collapsible Seasonal Groundwater Analysis section using matched station-year pairs."""
    with st.expander("Seasonal Groundwater Analysis", expanded=False):
        seasonal_data = get_seasonal_matched_comparison(df)
        
        if not seasonal_data["has_data"] or seasonal_data["count"] < 2:
            st.info("ℹ️ Insufficient matched May and November observations available to compute seasonal paired statistics.")
            return

        count = seasonal_data["count"]
        y_min = seasonal_data["year_min"]
        y_max = seasonal_data["year_max"]
        mean_diff = seasonal_data["mean_change_m"]
        median_rise = seasonal_data["median_rise_m"]
        n_years = seasonal_data["yearly_summary"]["year"].nunique()
        
        # 1. 4 Metric Cards in Columns
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_kpi_card(
                label="Matched Station-Years",
                value=f"{count} Pairs",
                caption="Observations with both May & Nov records for same station and year."
            )
        with k2:
            render_kpi_card(
                label="Year Range Covered",
                value=f"{y_min}–{y_max}",
                caption=f"{n_years} distinct historical years with paired seasonal soundings."
            )
        with k3:
            render_kpi_card(
                label="Mean Depth Change (Nov − May)",
                value=f"{mean_diff:+.2f} m",
                caption="Negative change reflects water table moving closer to surface."
            )
        with k4:
            render_kpi_card(
                label="Median Water-Table Rise",
                value=f"+{median_rise:.2f} m",
                caption="Median seasonal recovery in water elevation following monsoon."
            )

        # 2. MBGL Explanation & Methodological Note Callout
        st.markdown(
            """
            <div class="info-callout" style="border-left-color: var(--teal-accent); margin-top: 14px; margin-bottom: 14px;">
                <b>Understanding MBGL & Seasonal Differences:</b>
                Groundwater levels are measured in <b>Meters Below Ground Level (MBGL)</b>:
                <ul style="margin: 4px 0 6px 18px; padding: 0;">
                    <li><b>Higher MBGL value:</b> Indicates a <i>deeper</i> water table (water level further below ground surface).</li>
                    <li><b>Lower MBGL value:</b> Indicates a <i>shallower</i> water table (water level closer to the surface).</li>
                    <li><b>Negative depth change (November − May &lt; 0):</b> Because November MBGL is lower than May MBGL, the net change is negative, indicating a <b>seasonal water-table rise</b> (recharge and elevation gain).</li>
                </ul>
                <span style="color: var(--callout-text-secondary); font-size: 0.83rem;">
                ℹ️ <b>Methodological Note:</b> This analysis is an empirical historical comparison of strictly matched station-year observations (1996–2022), <b>not a predictive model or forecast</b>. Seasonal water-table changes reflect net dynamic hydrological balance — monsoon precipitation infiltration and return flows minus baseflow discharges and local agricultural pumping extraction.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 3. May vs November Comparison Chart
        render_seasonal_comparison_chart(seasonal_data["yearly_summary"], theme=theme)


def render_rainfall_relationship_section(df: pd.DataFrame, theme: str = "light") -> None:
    """Render collapsible Rainfall & Groundwater Relationship section."""
    with st.expander("Rainfall & Groundwater Relationship", expanded=False):
        corr_data = get_rainfall_groundwater_correlations(df)
        
        if not corr_data["has_data"] or corr_data["n_obs"] < 5:
            st.info("ℹ️ Insufficient antecedent rainfall and groundwater observations available to compute relationship metrics.")
            return

        # 1. Interactive Lookback Window Selector
        c_sel, c_info = st.columns([1.6, 2.4])
        with c_sel:
            window_options = {
                "Preceding 365-Day Rainfall (Annual Cycle)": "rain_365d",
                "Preceding 180-Day Rainfall (Multi-Month Recharge)": "rain_180d",
                "Preceding 90-Day Rainfall (Seasonal Monsoon)": "rain_90d",
            }
            selected_window_label = st.selectbox(
                "Rainfall Accumulation Window",
                options=list(window_options.keys()),
                index=0,
                key="rain_gw_window_select",
                help="Select the antecedent precipitation accumulation window preceding each in-situ groundwater observation."
            )
            selected_window_col = window_options[selected_window_label]
            
        with c_info:
            w_info = corr_data["windows"].get(selected_window_col, {})
            p_val = w_info.get("pearson", 0.0)
            s_val = w_info.get("spearman", 0.0)
            st.caption(
                f"**Exploratory Pooled Correlation ({corr_data['n_obs']} observations across 11 stations):**  \n"
                f"• Spearman Rank: $\\rho = {s_val:+.3f}$ &nbsp;|&nbsp; • Pearson: $r = {p_val:+.3f}$  \n"
                f"*Pooled across stations and years (exploratory); may be influenced by station-level and temporal differences. Negative correlation reflects a regional tendency toward shallower water with higher rainfall, but is not consistent across all stations.* "
            )

        # 2. Dual-Axis Rainfall vs Groundwater Trend Chart
        render_rainfall_groundwater_chart(df, window_col=selected_window_col, theme=theme)

        # 3. Dynamic Correlation Summary (3-Column Metric Cards)
        st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
        w90 = corr_data["windows"].get("rain_90d", {})
        w180 = corr_data["windows"].get("rain_180d", {})
        w365 = corr_data["windows"].get("rain_365d", {})

        c1, c2, c3 = st.columns(3)
        with c1:
            render_kpi_card(
                label="90-Day Antecedent Lookback",
                value=f"ρ = {w90.get('spearman', 0.0):+.2f}",
                caption=f"Pearson r = {w90.get('pearson', 0.0):+.2f} (Mean: {w90.get('mean_mm', 0):.0f} mm). Seasonal monsoon window."
            )
        with c2:
            render_kpi_card(
                label="180-Day Antecedent Lookback",
                value=f"ρ = {w180.get('spearman', 0.0):+.2f}",
                caption=f"Pearson r = {w180.get('pearson', 0.0):+.2f} (Mean: {w180.get('mean_mm', 0):.0f} mm). Multi-month infiltration window."
            )
        with c3:
            render_kpi_card(
                label="365-Day Antecedent Lookback",
                value=f"ρ = {w365.get('spearman', 0.0):+.2f}",
                caption=f"Pearson r = {w365.get('pearson', 0.0):+.2f} (Mean: {w365.get('mean_mm', 0):.0f} mm). Annual hydrological recharge cycle."
            )

        # 4. Methodological Interpretation & Limitations Callout
        st.markdown(
            """
            <div class="info-callout" style="border-left-color: var(--blue-accent); margin-top: 14px; margin-bottom: 8px;">
                <b>Understanding the Rainfall–Groundwater Relationship:</b>
                <ul style="margin: 4px 0 6px 18px; padding: 0;">
                    <li><b>Measurement Orientation (MBGL):</b> Water levels are measured in <b>Meters Below Ground Level (MBGL)</b>. A lower MBGL value indicates a shallower water table (closer to ground surface), while a higher MBGL value indicates a deeper water table. Regionally, higher rainfall is associated with lower MBGL, producing an exploratory <b>negative correlation</b> (recharge tendency); however, this relationship is not uniform or consistent across individual stations.</li>
                    <li><b>Calculation & Alignment:</b> Antecedent accumulation windows (90d, 180d, 365d) are calculated by summing daily precipitation lookbacks over the exact N calendar days preceding each in-situ sounding date, aligning meteorological lookbacks with historical groundwater observations.</li>
                    <li><b>Correlation Does Not Imply Causation & Exploratory Nature:</b> Statistical correlation demonstrates temporal co-variation but does not prove direct causation or isolate absolute recharge volumes. Pooled correlations across 680 observations from 11 stations are exploratory and may be influenced by station-level and temporal differences. Observed water levels represent net dynamic aquifer storage — cumulative precipitation infiltration and surface runoff recharge minus baseflow discharge, natural evapotranspiration, and intensive agricultural borewell pumping.</li>
                    <li><b>Heterogeneous Hydrogeology & No Universal Lag:</b> Deccan basalt aquifers are compartmentalized into distinct lava flows, vesicular horizons, and fracture networks. Infiltration lag times and response magnitudes vary significantly from well to well; the observed negative correlation is not consistent across all stations, and there is no universal infiltration velocity or uniform lag across Purandar Taluka.</li>
                    <li><b>Observation Sparsity & Gridded Data Limitations:</b> Telemetry records consist of historical, irregularly spaced groundwater observations across 11 monitoring stations (a rough spatial average of approximately 1 monitoring station per 267 km², based on 11 stations across approximately 2,936 km²). Daily precipitation is derived from the coarse IMD 0.25° × 0.25° (~27 km) grid with only four grid centroids in the taluka, requiring inverse-distance spatial extrapolation for peripheral monitoring wells.</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
