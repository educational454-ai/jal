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
    active_theme = get_current_theme()
    
    # 1. Welcome / Hero Section (Clean introduction for visitors and academic reviewers)
    st.markdown("""
    <div class="overview-welcome-card">
        <div class="overview-welcome-eyebrow">Research Platform · Purandar Taluka, Maharashtra</div>
        <div class="overview-welcome-title">BhujalDrishti: Groundwater Monitoring & Decision Support</div>
        <div class="overview-welcome-desc">
            BhujalDrishti is a research-grade groundwater intelligence system studying hard-rock basalt aquifers across 
            <b>Purandar Taluka, Pune District, Maharashtra</b> (~2,936 km²). By integrating multi-decadal in-situ soundings 
            from the Central Ground Water Board (CGWB, 1996–2023), gridded precipitation from the India Meteorological 
            Department (IMD), GIS mapping, and machine learning, the platform analyzes aquifer recharge patterns and 
            forecasts future recorded monitoring events.
        </div>
        <div class="overview-explore-grid">
            <div class="overview-explore-item">
                <span class="overview-explore-badge">Overview (Active)</span>
                <span class="overview-explore-title">1. Overview Dashboard</span>
                <span class="overview-explore-desc">Regional historical trends, seasonal recharge recovery, rainfall correlations, and station soundings.</span>
            </div>
            <div class="overview-explore-item">
                <span class="overview-explore-badge">Explore Spatial</span>
                <span class="overview-explore-title">2. Groundwater Map</span>
                <span class="overview-explore-desc">Interactive GIS map showing monitoring well locations, depth stratification, and spatial distribution.</span>
            </div>
            <div class="overview-explore-item">
                <span class="overview-explore-badge">Explore Machine Learning</span>
                <span class="overview-explore-title">3. Next-Observation Forecast</span>
                <span class="overview-explore-desc">ML predictions for the next recorded CGWB survey event, with rainfall scenarios and prediction bands.</span>
            </div>
            <div class="overview-explore-item">
                <span class="overview-explore-badge">Explore Advisories</span>
                <span class="overview-explore-title">4. Decision Support</span>
                <span class="overview-explore-desc">Preliminary watershed conservation options, recharge heuristics, and AI-synthesized planning advisories.</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Calculate latest snapshot across the 11 monitoring stations
    latest_per_station = get_latest_per_station(df)
    station_count = int(df['station'].nunique())
    total_obs_records = int(len(df))
    
    categories = latest_per_station['gw_level_mbgl'].apply(get_depth_tier_category)
    deep_count = int((categories == "Deep").sum())
    moderate_count = int((categories == "Moderate").sum())
    shallow_count = int((categories == "Shallow").sum())

    # 2. Key Project Snapshot (3 easy-to-understand summary cards)
    st.markdown("### Project Monitoring Snapshot")
    st.caption("Key dimensions of the research monitoring dataset across Purandar Taluka.")
    render_overview_kpis(
        station_count=station_count,
        total_records=total_obs_records,
        coverage_km2="~2,936 km²"
    )
    st.caption("ℹ️ *Historical observations span 1996 through 2023. Discrete historical soundings reflect past monitoring rounds and do not represent live automated telemetry or current real-time groundwater conditions.*")

    # 3. Groundwater Depth Explanation (MBGL & Physical Depth Categories)
    st.markdown("""
    <div class="overview-mbgl-card">
        <div class="overview-mbgl-title">
            <span>💡</span>
            <span>Understanding Groundwater Depth (MBGL) & Physical Categories</span>
        </div>
        <div class="overview-mbgl-grid">
            <div class="overview-mbgl-text">
                Groundwater levels in this project are measured in <b>Metres Below Ground Level (MBGL)</b>, representing the physical distance from the ground surface down to the water table:
                <ul style="margin: 6px 0 8px 18px; padding: 0;">
                    <li><b>Smaller MBGL number (e.g., 2.5 m):</b> Water is <b>closer to the surface</b> (shallower / replenished).</li>
                    <li><b>Larger MBGL number (e.g., 10.5 m):</b> Water is <b>deeper underground</b> (deeper / drawn down).</li>
                </ul>
                <span style="font-size: 0.82rem; color: var(--text-muted);">
                ⚠️ <b>Classification Distinction:</b> Depth categories below are project-defined physical reference bands for visual interpretation. They are <b>not</b> official Central Ground Water Board (CGWB) administrative categorizations (Safe, Semi-Critical, Critical, Over-Exploited), which evaluate annual recharge vs. extraction budgets across the entire taluka.
                </span>
            </div>
            <div class="overview-mbgl-tiers">
                <div class="overview-mbgl-tier-row">
                    <span><span class="badge-shallow">● Shallow</span> (&lt; 4.0 m MBGL)</span>
                    <span style="color: var(--text-muted); font-size: 0.78rem;">Water table near surface</span>
                </div>
                <div class="overview-mbgl-tier-row">
                    <span><span class="badge-moderate">● Moderate</span> (4.0–8.0 m MBGL)</span>
                    <span style="color: var(--text-muted); font-size: 0.78rem;">Intermediate depth range</span>
                </div>
                <div class="overview-mbgl-tier-row">
                    <span><span class="badge-deep">● Deep</span> (&gt; 8.0 m MBGL)</span>
                    <span style="color: var(--text-muted); font-size: 0.78rem;">Significant water drawdown</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4. Detailed Hydrogeological Analysis (Progressive Disclosure via Tabs)
    st.markdown("### Detailed Hydrogeological Analysis")
    st.caption("Select a tab below to explore multi-decadal trends, seasonal monsoon recharge, or antecedent rainfall relationships.")
    
    tab_trends, tab_seasonal, tab_rainfall = st.tabs([
        "📈 Regional Groundwater Trends",
        "🌧️ Seasonal Recovery (May vs. Nov)",
        "📊 Rainfall & Groundwater Relationship"
    ])

    # Tab 1: Regional Groundwater Trends
    with tab_trends:
        st.markdown("#### Historical Groundwater Level Trajectory (1996–2023)")
        st.caption("Explore multi-decadal water table fluctuations across Purandar Taluka. Select 'All Stations' to view the regional envelope, or isolate an individual monitoring well.")
        
        station_options = ["All Stations (Regional Mean Trend)"] + sorted(df['station'].unique().tolist())
        c_scope, _ = st.columns([1.5, 1.5])
        with c_scope:
            selected_scope = st.selectbox(
                "Select Station View Scope",
                options=station_options,
                index=0,
                key="overview_chart_station_scope",
                help="Select 'All Stations' to view the regional min-max envelope, or isolate an individual monitoring well."
            )
            
        render_regional_groundwater_chart(df, station_filter=selected_scope, theme=active_theme)
        
        col_rain, col_dist = st.columns(2)
        with col_rain:
            st.markdown("#### Preceding 365d Rainfall History")
            st.caption("Annual precipitation accumulation lookback preceding each recorded groundwater survey date.")
            render_compact_rainfall_chart(df, theme=active_theme)
            
        with col_dist:
            st.markdown("#### Groundwater Depth Distribution")
            st.caption(f"Stratification of the latest recorded sounding per station ({station_count} wells).")
            render_depth_distribution_summary(
                shallow_count=shallow_count,
                moderate_count=moderate_count,
                deep_count=deep_count,
                total_count=station_count
            )

    # Tab 2: Seasonal Recovery (May vs. Nov)
    with tab_seasonal:
        render_seasonal_analysis_content(df, theme=active_theme)

    # Tab 3: Rainfall & Groundwater Relationship
    with tab_rainfall:
        render_rainfall_relationship_content(df, theme=active_theme)

    # 5. Station-Level Historical Data (Table with Non-Synoptic Caveat)
    st.markdown("### Monitoring Station Historical Data")
    st.caption("Latest recorded historical in-situ soundings for all 11 CGWB monitoring stations in Purandar Taluka.")
    
    st.markdown(
        """
        <div class="info-callout" style="border-left-color: var(--badge-moderate-border); margin-bottom: 14px;">
            <b>Observation Dates & Recency Notice:</b>
            The table below lists the <b>most recent recorded historical observation</b> for each of the 11 monitoring stations:
            <ul style="margin: 4px 0 6px 18px; padding: 0;">
                <li><b>7 stations</b> have observations recorded during the 2023 monitoring cycle (6 in May 2023, 1 in March 2023).</li>
                <li><b>4 stations</b> reflect older survey years in this research dataset (Zendewadi: May 2022, Saswad: Aug 2006, Waghapur: Aug 1997, Walha: Jan 1997).</li>
            </ul>
            <span style="color: var(--callout-text-secondary); font-size: 0.83rem;">
            ⚠️ <b>Non-Synoptic Warning:</b> Because soundings span 26 years (1997–2023) and multiple seasons, this table does <b>not</b> represent a single current regional water table. The arithmetic mean of these soundings (6.88 m MBGL) must not be interpreted as a current regional reading.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    render_latest_stations_table(latest_per_station)


def render_seasonal_analysis_content(df: pd.DataFrame, theme: str = "light") -> None:
    """Render Seasonal Groundwater Analysis content using strictly matched station-year pairs."""
    st.markdown("#### Seasonal Groundwater Recharge: Pre-Monsoon vs. Post-Monsoon")
    st.caption("Comparing pre-monsoon summer lows (May) to post-monsoon replenished depths (November) for the exact same station and calendar year to measure seasonal aquifer recovery.")
    
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
    
    # 4 Metric Cards in Columns
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

    # MBGL Explanation & Methodological Note Callout
    st.markdown(
        """
        <div class="info-callout" style="border-left-color: var(--teal-accent); margin-top: 14px; margin-bottom: 14px;">
            <b>Understanding MBGL Direction & Seasonal Recovery:</b>
            Groundwater levels are measured in <b>Meters Below Ground Level (MBGL)</b>:
            <ul style="margin: 4px 0 6px 18px; padding: 0;">
                <li><b>Higher MBGL value:</b> Indicates a <i>deeper</i> water table (water level further below ground surface).</li>
                <li><b>Lower MBGL value:</b> Indicates a <i>shallower</i> water table (water level closer to the surface).</li>
                <li><b>Negative depth change (November − May &lt; 0):</b> Because November MBGL is lower than May MBGL, the net change is negative, indicating a <b>seasonal water-table rise</b> (recharge and elevation gain).</li>
            </ul>
            <span style="color: var(--callout-text-secondary); font-size: 0.83rem;">
            ℹ️ <b>Methodological Note:</b> This analysis is an empirical historical comparison of strictly matched station-year observations (1996–2022), <b>not a predictive model or forecast</b>. Seasonal water-table changes reflect net dynamic hydrological balance — monsoon precipitation infiltration and return flows minus baseflow discharges and local unmetered agricultural pumping extraction.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # May vs November Comparison Chart
    render_seasonal_comparison_chart(seasonal_data["yearly_summary"], theme=theme)


def render_rainfall_relationship_content(df: pd.DataFrame, theme: str = "light") -> None:
    """Render Rainfall & Groundwater Relationship content."""
    st.markdown("#### Antecedent Rainfall & Groundwater Correlation")
    st.caption("Examine how antecedent precipitation accumulated over 90, 180, and 365 days correlates with recorded water table depths.")
    
    corr_data = get_rainfall_groundwater_correlations(df)
    
    if not corr_data["has_data"] or corr_data["n_obs"] < 5:
        st.info("ℹ️ Insufficient antecedent rainfall and groundwater observations available to compute relationship metrics.")
        return

    # Interactive Lookback Window Selector
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
            f"*Pooled across stations and years (exploratory); may be influenced by station-level and temporal differences. Negative correlation reflects a regional tendency toward shallower water with higher rainfall, but is not consistent across all stations.*"
        )

    # Dual-Axis Rainfall vs Groundwater Trend Chart
    render_rainfall_groundwater_chart(df, window_col=selected_window_col, theme=theme)

    # Dynamic Correlation Summary (3-Column Metric Cards)
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

    # Methodological Interpretation & Limitations Callout
    st.markdown(
        """
        <div class="info-callout" style="border-left-color: var(--blue-accent); margin-top: 14px; margin-bottom: 8px;">
            <b>Understanding the Rainfall–Groundwater Relationship:</b>
            <ul style="margin: 4px 0 6px 18px; padding: 0;">
                <li><b>Measurement Orientation (MBGL):</b> Water levels are measured in <b>Meters Below Ground Level (MBGL)</b>. A lower MBGL value indicates a shallower water table (closer to ground surface), while a higher MBGL value indicates a deeper water table. Regionally, higher rainfall is associated with lower MBGL, producing an exploratory <b>negative correlation</b> (recharge tendency); however, this relationship is not uniform or consistent across individual stations.</li>
                <li><b>Calculation & Alignment:</b> Antecedent accumulation windows (90d, 180d, 365d) are calculated by summing daily precipitation lookbacks over the exact N calendar days preceding each in-situ sounding date, aligning meteorological lookbacks with historical groundwater observations.</li>
                <li><b>Correlation Does Not Imply Causation & Exploratory Nature:</b> Statistical correlation demonstrates temporal co-variation but does not prove direct causation or isolate absolute recharge volumes. Pooled correlations across 680 observations from 11 stations are exploratory and may be influenced by station-level and temporal differences. Observed water levels represent net dynamic aquifer storage — cumulative precipitation infiltration and surface runoff recharge minus baseflow discharge, natural evapotranspiration, and unmetered agricultural borewell pumping.</li>
                <li><b>Heterogeneous Hydrogeology & No Universal Lag:</b> Deccan basalt aquifers are compartmentalized into distinct lava flows, vesicular horizons, and fracture networks. Infiltration lag times and response magnitudes vary significantly from well to well; the observed negative correlation is not consistent across all stations, and there is no universal infiltration velocity or uniform lag across Purandar Taluka.</li>
                <li><b>Observation Sparsity & Gridded Data Limitations:</b> Telemetry records consist of historical, irregularly spaced groundwater observations across 11 monitoring stations (a rough spatial average of approximately 1 monitoring station per 267 km², based on 11 stations across approximately 2,936 km²). Daily precipitation is derived from the coarse IMD 0.25° × 0.25° (~27 km) grid with only four grid centroids in the taluka, requiring inverse-distance spatial extrapolation for peripheral monitoring wells.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )


# Preserved backward compatibility wrappers for existing references or tests
def render_seasonal_analysis_section(df: pd.DataFrame, theme: str = "light") -> None:
    """Render collapsible Seasonal Groundwater Analysis section (backward compatibility wrapper)."""
    with st.expander("Seasonal Groundwater Analysis", expanded=False):
        render_seasonal_analysis_content(df, theme=theme)


def render_rainfall_relationship_section(df: pd.DataFrame, theme: str = "light") -> None:
    """Render collapsible Rainfall & Groundwater Relationship section (backward compatibility wrapper)."""
    with st.expander("Rainfall & Groundwater Relationship", expanded=False):
        render_rainfall_relationship_content(df, theme=theme)
