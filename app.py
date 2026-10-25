import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import json
import streamlit.components.v1 as components
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# Configuration & Memory Optimization
# -------------------------------------------------------------
st.set_page_config(
    page_title="BhujalDrishti | Environmental Intelligence",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# Design System: Professional Environmental Research Theme
# Deep Navy, Teal, Muted Aqua, Soft Slate & Neutral White
# -------------------------------------------------------------
st.markdown("""
<style>
    /* CSS Variables & Global Typography */
    :root {
        --navy-950: #090D16;
        --navy-900: #0F172A;
        --navy-800: #1E293B;
        --navy-700: #334155;
        --teal-700: #0F766E;
        --teal-600: #0D9488;
        --teal-500: #14B8A6;
        --teal-100: #CCFBF1;
        --teal-50:  #F0FDFA;
        --slate-50: #F8FAFC;
        --slate-100: #F1F5F9;
        --slate-200: #E2E8F0;
        --slate-300: #CBD5E1;
        --slate-500: #64748B;
        --slate-600: #475569;
        --slate-700: #334155;
    }

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        color: #0F172A;
        -webkit-font-smoothing: antialiased;
    }

    /* Container Spacing */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1400px;
    }

    /* Platform Branded Header Banner */
    .research-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 16px 20px;
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 10px;
        border: 1px solid #334155;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.12), 0 2px 4px -2px rgba(15, 23, 42, 0.08);
    }
    .header-left {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .header-icon-box {
        width: 44px;
        height: 44px;
        background: rgba(13, 148, 136, 0.2);
        border: 1px solid rgba(20, 184, 166, 0.4);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #2DD4BF;
    }
    .header-titles {
        display: flex;
        flex-direction: column;
    }
    .header-main-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.025em;
        line-height: 1.2;
    }
    .header-subtitle {
        font-size: 0.82rem;
        color: #94A3B8;
        font-weight: 400;
        margin-top: 2px;
    }
    .header-badges {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .badge-prototype {
        background-color: rgba(13, 148, 136, 0.25);
        color: #5EEAD4;
        border: 1px solid rgba(45, 212, 191, 0.4);
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .badge-jurisdiction {
        background-color: rgba(255, 255, 255, 0.08);
        color: #E2E8F0;
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.74rem;
        font-weight: 500;
    }

    /* Screen Title Block */
    .screen-header-block {
        margin-bottom: 1.1rem;
    }
    .main-header {
        font-size: 1.65rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        line-height: 1.25;
        margin-bottom: 3px;
    }
    .sub-header {
        font-size: 0.92rem;
        color: #475569;
        margin-bottom: 0px;
        line-height: 1.5;
    }

    /* Premium Metric & KPI Cards */
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04), 0 1px 2px 0 rgba(15, 23, 42, 0.02);
        margin-bottom: 10px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.04);
    }
    .kpi-label {
        font-size: 0.74rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748B;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 1.65rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.15;
        margin-bottom: 3px;
    }
    .kpi-caption {
        font-size: 0.76rem;
        color: #64748B;
        line-height: 1.35;
    }

    /* Evaluation Result Metric Card */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        line-height: 1.5;
        font-size: 0.88rem;
    }

    /* Depth Reference Tier Badges */
    .badge-shallow, .badge-safe {
        background-color: #F0FDFA;
        color: #0F766E;
        border: 1px solid #99F6E4;
        padding: 3px 9px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-moderate, .badge-semi {
        background-color: #FEFCE8;
        color: #854D0E;
        border: 1px solid #FDE047;
        padding: 3px 9px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }
    .badge-deep, .badge-critical {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
        padding: 3px 9px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.8rem;
        display: inline-block;
    }

    /* Structured Callout Banners */
    .info-callout {
        background-color: #F8FAFC;
        border-left: 4px solid #0D9488;
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 0.86rem;
        color: #334155;
        line-height: 1.55;
        margin-bottom: 1.1rem;
    }
    .warning-callout {
        background-color: #FFFBEB;
        border-left: 4px solid #D97706;
        border-top: 1px solid #FEF3C7;
        border-right: 1px solid #FEF3C7;
        border-bottom: 1px solid #FEF3C7;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 0.84rem;
        color: #92400E;
        line-height: 1.45;
        margin-bottom: 0.8rem;
    }

    /* Sidebar Clean Styling */
    .sidebar-brand {
        padding-bottom: 12px;
        margin-bottom: 10px;
        border-bottom: 1px solid #E2E8F0;
    }
    .sidebar-brand-name {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
    }
    .sidebar-brand-tagline {
        font-size: 0.8rem;
        font-weight: 600;
        color: #0D9488;
    }
    .telemetry-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
        font-size: 0.78rem;
        color: #475569;
        line-height: 1.5;
    }

    /* Reduced Motion Safety */
    @media (prefers-reduced-motion: reduce) {
        .kpi-card {
            transition: none !important;
            transform: none !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Cached Loaders
# -------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/purandar_groundwater_features.csv")
    df['date'] = pd.to_datetime(df['date'])
    if 'is_rainfall_extrapolated' not in df.columns:
        extrap_stations = {'Pimpri (Kh) Malvasti', 'Kamatwadi-Walha', 'Walha', 'Narayanpur'}
        df['is_rainfall_extrapolated'] = df['station'].apply(lambda s: 1 if s in extrap_stations else 0)
    return df

@st.cache_resource
def load_models():
    models = {}
    if os.path.exists("models/rf_forecast_model.joblib"):
        models['forecast'] = joblib.load("models/rf_forecast_model.joblib")
    if os.path.exists("models/forecast_q10.joblib"):
        models['q10'] = joblib.load("models/forecast_q10.joblib")
    if os.path.exists("models/forecast_q90.joblib"):
        models['q90'] = joblib.load("models/forecast_q90.joblib")
    if os.path.exists("reports/model_evaluation.json"):
        with open("reports/model_evaluation.json", "r", encoding="utf-8") as f:
            models['metadata'] = json.load(f)
    return models

df = load_data()
if 'is_rainfall_extrapolated' not in df.columns:
    extrap_stations = {'Pimpri (Kh) Malvasti', 'Kamatwadi-Walha', 'Walha', 'Narayanpur'}
    df['is_rainfall_extrapolated'] = df['station'].apply(lambda s: 1 if s in extrap_stations else 0)
models = load_models()

# -------------------------------------------------------------
# Project-Defined Depth Reference Tiers
# (Explicitly distinguished from official CGWB administrative extraction categories)
# -------------------------------------------------------------
def get_depth_tier(mbgl):
    if mbgl < 4.0:
        return "Shallow (< 4.0 m)", "#0F766E", "badge-shallow"
    elif mbgl <= 8.0:
        return "Moderate (4.0–8.0 m)", "#854D0E", "badge-moderate"
    else:
        return "Deep (> 8.0 m)", "#991B1B", "badge-deep"

def get_status(mbgl):
    # Backward compatible wrapper for legacy helper references
    return get_depth_tier(mbgl)

# -------------------------------------------------------------
# Reusable UI Component: Research Header
# -------------------------------------------------------------
def render_research_header():
    st.markdown("""
    <div class="research-header">
        <div class="header-left">
            <div class="header-icon-box">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>
                </svg>
            </div>
            <div class="header-titles">
                <div class="header-main-title">BhujalDrishti &nbsp;<span style="font-weight: 400; font-size: 1.05rem; color: #94A3B8;">| JalRakshak AI</span></div>
                <div class="header-subtitle">Multimodal GIS & Hydrological Next-Observation Forecasting Decision Support</div>
            </div>
        </div>
        <div class="header-badges">
            <span class="badge-prototype">Research Prototype</span>
            <span class="badge-jurisdiction">Purandar Taluka (~1,105 km²)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------
# Sidebar Navigation & Context
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-name">💧 BhujalDrishti</div>
        <div class="sidebar-brand-tagline">Environmental Intelligence System</div>
    </div>
    """, unsafe_allow_html=True)
    
    screen = st.radio(
        "Navigation",
        [
            "📊 Screen 1: Overview Dashboard",
            "🗺️ Screen 2: Groundwater Map",
            "🔮 Screen 3: Next-Observation Forecast",
            "🛡️ Screen 4: Decision Support"
        ],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("##### **Telemetry Network Context**")
    st.markdown("""
    <div class="telemetry-box">
        • <b>Jurisdiction:</b> Purandar Taluka (Pune, MH)<br>
        • <b>Administrative Area:</b> ~1,105 km²<br>
        • <b>Aquifer Formation:</b> Deccan Basalt Flows<br>
        • <b>CGWB Monitoring:</b> 11 In-situ Observation Wells<br>
        • <b>Rainfall Grid:</b> 4 IMD Points (0.25° resolution)<br>
        • <b>Extrapolated Wells:</b> 4 Southern/Western Stations<br>
        • <b>Validation Split:</b> Zero-Target-Leakage Chronological Split (Train: 1996–2017, Test: 2018–2023)
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("ℹ️ *Academic research decision-support prototype. Predictions are statistical estimates, not physical measurements.*")

# Render Top Global Branded Header
render_research_header()

# =============================================================
# SCREEN 1: OVERVIEW DASHBOARD
# =============================================================
if screen == "📊 Screen 1: Overview Dashboard":
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">📊 Purandar Groundwater Overview</div>
        <div class="sub-header">Regional groundwater health, seasonal dynamics, and station alert indicators across Purandar Taluka</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate latest snapshot across the 11 monitoring stations
    latest_per_station = df.sort_values('date').groupby('station').last().reset_index()
    avg_latest_mbgl = float(latest_per_station['gw_level_mbgl'].mean())
    station_count = int(df['station'].nunique())
    total_obs_records = int(len(df))
    
    # Retrieve held-out model accuracy dynamically from metadata
    meta = models.get('metadata', {})
    rf_mae_eval = meta.get('results_fc', {}).get('Random Forest Regressor', {}).get('MAE', 2.092)
    
    deep_count = int((latest_per_station['gw_level_mbgl'] > 8.0).sum())
    moderate_count = int(((latest_per_station['gw_level_mbgl'] >= 4.0) & (latest_per_station['gw_level_mbgl'] <= 8.0)).sum())
    shallow_count = int((latest_per_station['gw_level_mbgl'] < 4.0).sum())
    
    # Primary Dynamically Computed KPI Row
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Mean Water Table Depth</div>
                <div class="kpi-value">{avg_latest_mbgl:.2f} m</div>
                <div class="kpi-caption">Meters Below Ground Level (MBGL) across {station_count} stations at latest record.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Monitoring Network</div>
                <div class="kpi-value">{station_count} Wells</div>
                <div class="kpi-caption">Active CGWB in-situ manual monitoring stations (~1 well per 100 km²).</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Historical Time Series</div>
                <div class="kpi-value">{total_obs_records} Records</div>
                <div class="kpi-caption">Quality-verified quarterly observations spanning 1996 through 2023.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with k4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">Held-Out Model MAE</div>
                <div class="kpi-value">{rf_mae_eval:.3f} m</div>
                <div class="kpi-caption">Random Forest next-observation forecast error on 2018–2023 test set (n=124).</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    # Depth Reference Tier Secondary Summary Pill Bar
    st.markdown(
        f"""
        <div style="background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px 16px; margin-bottom: 1rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
            <span style="font-size: 0.82rem; font-weight: 600; color: #334155;">Latest Observation Depth Distribution:</span>
            <div style="display: flex; gap: 10px; align-items: center;">
                <span class="badge-shallow">Shallow (&lt; 4m): {shallow_count} / {station_count} wells</span>
                <span class="badge-moderate">Moderate (4–8m): {moderate_count} / {station_count} wells</span>
                <span class="badge-deep">Deep (&gt; 8m): {deep_count} / {station_count} wells</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
        
    st.markdown(
        """
        <div class="info-callout">
            <b>Depth Reference Tier Classification Note</b>: Tiers displayed above (&lt;4.0 m, 4.0–8.0 m, &gt;8.0 m) represent project-defined physical reference bands for instantaneous telemetry visualization. They do not constitute official Central Ground Water Board (CGWB) groundwater exploitation categories. Official CGWB administrative categorizations (Safe, Semi-Critical, Critical, Over-Exploited) are assessed at the entire taluka level based on annual groundwater extraction versus annual replenishable recharge budgets, not single-well point measurements.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Two-column layout: Latest Station Table & Rainfall/Groundwater Correlation
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.subheader("📍 Latest Monitoring Station Status")
        if 'is_rainfall_extrapolated' not in latest_per_station.columns:
            extrap_stations = {'Pimpri (Kh) Malvasti', 'Kamatwadi-Walha', 'Walha', 'Narayanpur'}
            latest_per_station['is_rainfall_extrapolated'] = latest_per_station['station'].apply(
                lambda s: 1 if s in extrap_stations else 0
            )
        display_df = latest_per_station[['station', 'date', 'gw_level_mbgl', 'season_tag', 'is_rainfall_extrapolated']].copy()
        display_df['Observation Date'] = display_df['date'].dt.strftime('%d-%b-%Y')
        display_df['Water Depth (m MBGL)'] = display_df['gw_level_mbgl'].apply(lambda x: f"{x:.2f}")
        display_df['Project Depth Tier'] = display_df['gw_level_mbgl'].apply(lambda x: get_depth_tier(x)[0])
        display_df['Season'] = display_df['season_tag']
        display_df['Rainfall Status'] = display_df['is_rainfall_extrapolated'].apply(lambda x: "⚠️ Extrapolated" if x else "✓ IMD Grid")
        display_df.rename(columns={'station': 'Station Name'}, inplace=True)
        
        st.dataframe(
            display_df[['Station Name', 'Observation Date', 'Water Depth (m MBGL)', 'Project Depth Tier', 'Season', 'Rainfall Status']],
            use_container_width=True,
            hide_index=True
        )
        st.caption("ℹ️ *Indicates the latest recorded in-situ manual CGWB observation for each of the 11 monitoring wells in Purandar Taluka.*")
        
    with col_right:
        st.subheader("🌧️ Taluka Rainfall vs. Water Table Trends")
        # Aggregated annual groundwater depth vs antecedent rainfall
        annual_summary = df.groupby('year').agg({
            'gw_level_mbgl': 'mean',
            'rain_365d': 'mean'
        }).reset_index()
        
        fig, ax1 = plt.subplots(figsize=(6.4, 3.9), dpi=115)
        fig.patch.set_facecolor('#FFFFFF')
        ax1.set_facecolor('#FAFAFA')
        
        # Rainfall Bar Chart (Left Axis)
        color_rain = '#0D9488'
        ax1.set_xlabel('Calendar Year', fontsize=8.5, color='#334155', labelpad=6)
        ax1.set_ylabel('Mean Preceding 365d Rainfall (mm)', color=color_rain, fontsize=8.5)
        ax1.bar(
            annual_summary['year'], 
            annual_summary['rain_365d'], 
            color=color_rain, 
            alpha=0.38, 
            edgecolor=color_rain, 
            linewidth=0.8,
            width=0.65, 
            label='Preceding 365d Rain (mm)'
        )
        ax1.tick_params(axis='y', labelcolor=color_rain, labelsize=8)
        ax1.tick_params(axis='x', labelsize=8, colors='#334155')
        ax1.grid(True, linestyle=':', alpha=0.55, color='#CBD5E1')
        
        # Groundwater Line (Right Inverted Axis)
        ax2 = ax1.twinx()
        color_gw = '#1E3A8A'
        ax2.set_ylabel('Mean Groundwater Depth (m MBGL) [Shallower ↑ / Deeper ↓]', color=color_gw, fontsize=8.5)
        ax2.plot(
            annual_summary['year'], 
            annual_summary['gw_level_mbgl'], 
            color=color_gw, 
            linewidth=2.0, 
            marker='o', 
            markersize=3.5, 
            label='Mean Depth (m MBGL)'
        )
        ax2.tick_params(axis='y', labelcolor=color_gw, labelsize=8)
        ax2.invert_yaxis() # Invert so shallower water table appears higher
        
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
        st.caption("ℹ️ *Methodological Note: Rainfall bars represent the station-averaged 365-day cumulative antecedent precipitation lookbacks preceding observation dates in each calendar year. Water table fluctuations reflect net hydrological balance (precipitation infiltration, baseflow, and seasonal agricultural pumping extraction), rather than natural recharge alone.*")

    st.info("💡 **Hydrogeological Insight**: Notice how years with higher rainfall (e.g., 2005, 2019, 2020) directly correspond to shallower water tables (water closer to the surface, appearing higher on the inverted axis).")

# =============================================================
# SCREEN 2: GROUNDWATER MAP
# =============================================================
elif screen == "🗺️ Screen 2: Groundwater Map":
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">🗺️ Purandar Groundwater Telemetry Map</div>
        <div class="sub-header">Observed station telemetry across 11 CGWB monitoring wells with standardized depth color coding</div>
    </div>
    """, unsafe_allow_html=True)
    
    latest_st = df.sort_values('date').groupby('station').last().reset_index()
    
    c_m1, c_m2 = st.columns([3, 1])
    with c_m2:
        st.markdown("#### **Map Controls & Legend**")
        st.markdown("""
        - 🟢 **Shallow Depth**: $< 4.0\\text{ m}$ MBGL *(water close to surface)*
        - 🟡 **Moderate Depth**: $4.0 - 8.0\\text{ m}$ MBGL
        - 🔴 **Deep Water Table**: $> 8.0\\text{ m}$ MBGL *(localized/seasonal drawdown)*
        """)
        st.caption("Fixed-size markers indicate observed in-situ water levels at CGWB stations. Color represents depth below ground surface.")
        
        selected_zone_filter = st.selectbox(
            "Filter by Risk Level", 
            ["All Stations", "Safe (< 4m)", "Semi-Critical (4-8m)", "Critical (> 8m)"]
        )
        
    filtered_stations = latest_st.copy()
    if selected_zone_filter == "Safe (< 4m)":
        filtered_stations = filtered_stations[filtered_stations['gw_level_mbgl'] < 4.0]
    elif selected_zone_filter == "Semi-Critical (4-8m)":
        filtered_stations = filtered_stations[(filtered_stations['gw_level_mbgl'] >= 4.0) & (filtered_stations['gw_level_mbgl'] <= 8.0)]
    elif selected_zone_filter == "Critical (> 8m)":
        filtered_stations = filtered_stations[filtered_stations['gw_level_mbgl'] > 8.0]
        
    # Generate Leaflet HTML
    stations_json = []
    for _, row in filtered_stations.iterrows():
        status, color, _ = get_status(row['gw_level_mbgl'])
        stations_json.append({
            'name': str(row['station']),
            'lat': float(row['latitude']),
            'lon': float(row['longitude']),
            'depth': float(row['gw_level_mbgl']),
            'status': status,
            'color': color,
            'date': row['date'].strftime('%d %b %Y'),
            'season': str(row['season_tag']),
            'is_extrapolated': bool(row.get('is_rainfall_extrapolated', 0))
        })
        
    leaflet_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            #map {{ height: 505px; width: 100%; border-radius: 8px; border: 1px solid #CBD5E1; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
            .info-box {{
                background: white; padding: 10px 14px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); font-family: sans-serif;
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0;">
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([18.28, 74.12], 11);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 18,
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);

            var stations = {json.dumps(stations_json)};

            stations.forEach(function(st) {{
                // Fixed-size station marker with depth encoded by color
                var marker = L.circleMarker([st.lat, st.lon], {{
                    radius: 9,
                    fillColor: st.color,
                    color: '#ffffff',
                    weight: 2.5,
                    opacity: 1,
                    fillOpacity: 0.92
                }}).addTo(map);

                var extrapNotice = st.is_extrapolated ? 
                    '<div style="color: #92400E; font-size: 11px; margin-top: 6px; background: #FEF3C7; padding: 4px 6px; border-radius: 4px; border-left: 3px solid #F59E0B;">⚠️ <b>Precipitation Warning:</b> Station lies outside the 4-point IMD rainfall grid; rainfall is spatially extrapolated.</div>' : 
                    '<div style="color: #065F46; font-size: 11px; margin-top: 6px; background: #D1FAE5; padding: 4px 6px; border-radius: 4px; border-left: 3px solid #10B981;">✓ <b>Precipitation:</b> Station within IMD grid bounding box.</div>';

                var popupContent = `
                    <div style="font-family: Arial, sans-serif; min-width: 190px; line-height: 1.45;">
                        <div style="font-size: 10px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; font-weight: bold;">Observed CGWB Telemetry</div>
                        <h4 style="margin: 2px 0 6px 0; color: #1E3A8A; font-size: 14px;">${{st.name}}</h4>
                        <b>Measured Water Depth:</b> ${{st.depth.toFixed(2)}} m MBGL<br>
                        <b>Classification:</b> <span style="color: ${{st.color}}; font-weight: bold;">${{st.status}}</span><br>
                        <b>Season:</b> ${{st.season}}<br>
                        <b>Observation Date:</b> ${{st.date}}
                        ${{extrapNotice}}
                    </div>
                `;
                marker.bindPopup(popupContent);
            }});
        </script>
    </body>
    </html>
    """
    with c_m1:
        components.html(leaflet_html, height=520)

    st.caption("ℹ️ *Note: Station markers display physical in-situ measurements at fixed CGWB monitoring wells. Point color denotes observed water level in Meters Below Ground Level (MBGL).*")
    
    with st.expander("🔬 **Spatial Prediction Layer Status (Why continuous heatmap interpolation is withheld)**"):
        st.markdown("""
        **Investigation Findings on `rf_mapping_model.joblib`:**
        - **Evaluation Deflation via Spatial Leave-One-Station-Out Validation**: While standard temporal evaluation on known station locations indicated $R^2 = 0.59$, rigorous **Leave-One-Station-Out Cross-Validation (LOSO-CV)** revealed an overall $R^2 = 0.022$ and severely negative $R^2$ values for individual stations (e.g., Pimpri: $R^2 = -8.79$, Saswad: $R^2 = -3.14$, Kamatwadi-Walha: $R^2 = -1.13$).
        - **Data Density Limitation**: With only 11 monitoring stations across $\\sim 1,105\\text{ km}^2$ (~1 well per $100\\text{ km}^2$), decision tree ensembles with raw latitude and longitude memorize coordinates rather than learning transferable spatial physical relationships.
        - **Basaltic Hydrogeology**: Groundwater in Deccan basalt flows is compartmentalized by fractured zones, compact massive basalt layers, weathered vesicular horizons, and lineaments that cannot be reliably interpolated without fine-scale digital elevation models (DEM), lithological logs, and geomorphic slope covariates.
        - **Integrity Decision**: To prevent presenting unvalidated or misleading spatial heatmaps as scientific predictions, the map displays verified station observations only until adequate spatial covariates and denser sensor networks are integrated.
        """)

# =============================================================
# SCREEN 3: NEXT-OBSERVATION FORECASTING
# =============================================================
elif screen == "🔮 Screen 3: Next-Observation Forecast":
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">🔮 Next-Observation Groundwater Forecast</div>
        <div class="sub-header">Predicting the next recorded CGWB groundwater monitoring event per station with uncalibrated q10–q90 prediction bands</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("ℹ️ **Understanding Groundwater Measurements (MBGL)**: Water levels are measured in **Meters Below Ground Level (MBGL)**. A lower value (e.g., 2.5 m) means water is close to the surface, while a higher value (e.g., 10.5 m) indicates a deeper water table. **Note**: Forecasts displayed here are statistical machine-learning estimates based on antecedent rainfall and prior water levels, not actual future physical measurements.")
    
    # Station Selector
    valid_stations = [s for s in df['station'].unique() if (df['station'] == s).sum() >= 10]
    c_s1, c_s2 = st.columns([1.2, 1.8])
    
    with c_s1:
        station_sel = st.selectbox("Select Monitoring Station", sorted(valid_stations), index=0)
        station_df = df[df['station'] == station_sel].sort_values('date').copy()
        latest_record = station_df.iloc[-1]
        
        st.markdown("#### **Latest Known Conditions**")
        st.markdown(f"- **Station**: `{station_sel}`")
        st.markdown(f"- **Observation Date**: {latest_record['date'].strftime('%d %b %Y')}")
        st.markdown(f"- **Recorded Level**: `{latest_record['gw_level_mbgl']:.2f} m MBGL`")
        st.markdown(f"- **Preceding 90-Day Rain**: `{latest_record['rain_90d']:.1f} mm`")
        st.markdown(f"- **Preceding 365-Day Rain**: `{latest_record['rain_365d']:.1f} mm`")
        if latest_record.get('is_rainfall_extrapolated', 0):
            st.caption("⚠️ *Station is outside the 4-point IMD rainfall grid; rainfall is spatially extrapolated.*")
        
        st.markdown("---")
        st.markdown("#### **Rainfall Scenario Simulation**")
        rain_factor = st.slider("Simulate Antecedent Rainfall Adjustment", -50, 50, 0, 5, format="%d%%",
                                help="Adjust rainfall to simulate a drought year (-30%) or high-recharge year (+30%)")
        st.caption("*Applies proportional scaling to antecedent 30d–365d cumulative rainfall features.*")
        
    with c_s2:
        # Forecast computation
        if 'forecast' in models and 'q10' in models and 'q90' in models and 'metadata' in models:
            meta = models['metadata']
            feature_cols_fc = meta['feature_cols_fc']
            
            # Prepare feature vector based on latest record
            feat_dict = {}
            for col in feature_cols_fc:
                feat_dict[col] = latest_record[col]
                
            # Apply what-if simulation to rain features
            multiplier = 1.0 + (rain_factor / 100.0)
            feat_dict['rain_30d'] *= multiplier
            feat_dict['rain_60d'] *= multiplier
            feat_dict['rain_90d'] *= multiplier
            feat_dict['rain_180d'] *= multiplier
            feat_dict['rain_365d'] *= multiplier
            
            # Predict
            X_input = pd.DataFrame([feat_dict])
            pred_val = float(models['forecast'].predict(X_input)[0])
            pred_q10 = float(models['q10'].predict(X_input)[0])
            pred_q90 = float(models['q90'].predict(X_input)[0])
            
            # Logical bounds without truncating valid artesian readings
            lower_b = min(pred_q10, pred_val)
            upper_b = max(pred_val, pred_q90)
            
            # Retrieve exact evaluation metrics dynamically from metadata
            rf_res = meta.get('results_fc', {}).get('Random Forest Regressor', {})
            rf_mae = rf_res.get('MAE', 2.092)
            rf_rmse = rf_res.get('RMSE', 2.899)
            rf_r2 = rf_res.get('R2', 0.247)
            
            pers_res = meta.get('results_fc', {}).get('Baseline (Persistence: gw_now)', {})
            pers_mae = pers_res.get('MAE', 2.744)
            pers_rmse = pers_res.get('RMSE', 3.709)
            
            unc_info = meta.get('uncertainty_intervals', {})
            emp_cov = unc_info.get('empirical_test_coverage_pct', 57.26)
            avg_width = unc_info.get('average_interval_width_meters', 4.36)
            
            test_h = meta.get('horizon_statistics', {}).get('test_population', {
                'mean_days': 109.4, 'median_days': 92.0, 'min_days': 41.0, 'max_days': 233.0
            })
            overall_h = meta.get('horizon_statistics', {}).get('overall_population', {
                'mean_days': 106.9, 'median_days': 102.0, 'min_days': 41.0, 'max_days': 2206.0
            })
            
            st.markdown("#### **🔮 Next-Observation Groundwater Forecast**")
            k1, k2, k3 = st.columns(3)
            with k1:
                st.metric("Projected Depth", f"{pred_val:.2f} m", 
                          delta=f"{pred_val - latest_record['gw_level_mbgl']:+.2f} m vs current",
                          delta_color="inverse")
            with k2:
                st.metric("Uncalibrated q10–q90 Prediction Band", f"{lower_b:.2f} m – {upper_b:.2f} m", 
                          help=f"Nominal 80% interval. Measured empirical test coverage: {emp_cov:.1f}% (below nominal 80% target; miss rate: {100.0 - emp_cov:.1f}%). Average test width: {avg_width:.2f} m. Does not guarantee future coverage.")
            with k3:
                status, color, badge = get_status(pred_val)
                st.markdown(f"**Estimated Status:**<br><span class='{badge}'>{status}</span>", unsafe_allow_html=True)
                
            st.markdown("##### **⏱️ Forecast Horizon Context (Next-Observation Schedule)**")
            st.markdown(
                f"""
                <div style="background-color: #F8FAFC; border-left: 4px solid #3B82F6; padding: 10px 14px; border-radius: 6px; font-size: 0.88rem; margin-bottom: 12px; border-top: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0; border-bottom: 1px solid #E2E8F0;">
                    <b>Evaluation Population Forecast Horizon</b> (Held-out test set, 2018–2023, <i>n</i> = 124):<br>
                    • <b>Median:</b> {test_h['median_days']:.1f} days &nbsp;|&nbsp; 
                    • <b>Mean:</b> {test_h['mean_days']:.1f} days &nbsp;|&nbsp; 
                    • <b>Min:</b> {test_h['min_days']:.1f} days &nbsp;|&nbsp; 
                    • <b>Max:</b> {test_h['max_days']:.1f} days<br>
                    <span style="color: #64748B; font-size: 0.81rem;">
                    *Predicts the next recorded CGWB observation date, not groundwater exactly 90 days in the future. For comparison, full historical population (1996–2023, n=658): Median = {overall_h['median_days']:.1f}d, Mean = {overall_h['mean_days']:.1f}d, Min = {overall_h['min_days']:.1f}d, Max = {overall_h['max_days']:.1f}d.*
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("##### **📊 Held-Out Test Evaluation Results (2018–2023, n=124 events)**")
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<b>Random Forest Model</b><br>"
                    f"• MAE: <b>{rf_mae:.3f} m</b><br>"
                    f"• RMSE: <b>{rf_rmse:.3f} m</b><br>"
                    f"• R²: <b>{rf_r2:.3f}</b>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with m_col2:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<b>Persistence Baseline</b><br>"
                    f"• MAE: <b>{pers_mae:.3f} m</b><br>"
                    f"• RMSE: <b>{pers_rmse:.3f} m</b><br>"
                    f"• Error Reduction: <b>{((pers_mae - rf_mae)/pers_mae)*100:.1f}%</b> lower MAE"
                    f"</div>",
                    unsafe_allow_html=True
                )
            with m_col3:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<b>Uncalibrated q10–q90 Prediction Band</b><br>"
                    f"• Empirical Test Coverage: <b>{emp_cov:.2f}%</b><br>"
                    f"• Nominal Target: 80.0% (Undercoverage)<br>"
                    f"• Measured Average Width: <b>{avg_width:.2f} m</b><br>"
                    f"<span style='color: #991B1B; font-size: 0.78rem;'>*Does not guarantee future coverage*</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
        else:
            st.warning("Forecasting models and evaluation metadata are loading or unavailable.")
            
    # Historical Curve Plot
    st.markdown("---")
    st.subheader(f"📈 Historical Groundwater Depletion & Recharge Curve: {station_sel}")
    
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.plot(station_df['date'], station_df['gw_level_mbgl'], color='#2563EB', marker='o', markersize=3, label='Observed Level (MBGL)', linewidth=1.8)
    
    # Invert axis so water closer to surface is at the top
    ax.set_ylabel("Depth Below Ground Level (m MBGL)\n[Shallower ↑ / Deeper ↓]")
    ax.set_xlabel("Year")
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Draw reference thresholds
    ax.axhline(4.0, color='#10B981', linestyle=':', label='Safe Reference (<4m)')
    ax.axhline(8.0, color='#EF4444', linestyle=':', label='Critical Reference (>8m)')
    ax.invert_yaxis()
    ax.legend(loc='lower left')
    
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    with st.expander("📐 **Prediction Interval Calibration & Conformal Prediction Analysis**"):
        st.markdown("""
        **Uncalibrated Quantile Model Status:**
        - The current `q10` and `q90` Gradient Boosting models target nominal 80% coverage (10th to 90th percentiles).
        - On held-out test data (2018–2023, $n=124$), empirical coverage is **57.26%** (a **42.74% miss rate**), confirming significant out-of-sample undercoverage.
        - Measured average prediction interval width is **4.36 m**.
        
        **Conformalized Quantile Regression (CQR) Calibration Investigation:**
        - Investigated using an independent chronological calibration period (2014–2017) without tuning against the 2018–2023 test set:
          - A nonconformity score adjustment $Q = 1.543\\text{ m}$ was calculated on 97 calibration events.
          - Applying this adjustment achieved **85.5% empirical coverage** on the 2018–2023 test set, widening the average prediction interval from $4.04\\text{ m}$ to $7.13\\text{ m}$.
          
        **Assumptions & Limitations of Conformal Prediction in Hydrogeology:**
        1. **Exchangeability Violation**: Standard conformal prediction assumes exchangeable (i.i.d.) data. Time-series groundwater levels exhibit strong autocorrelation and non-stationary distribution shifts (e.g. changing multi-year rainfall regimes, expanding borewell extraction). Conformal prediction does not guarantee $\\ge 80\\%$ coverage on every future dataset when distribution shifts occur.
        2. **Interval Width Trade-off**: Achieving empirical coverage above $80\\%$ required widening the average interval to $\\sim 7.1\\text{ m}$, which spans most of the typical dynamic range of local shallow dugwells, limiting actionable decision utility.
        3. **Academic Baseline**: We retain the uncalibrated `q10`–`q90` model, clearly report its 57.3% measured test coverage and 4.36 m width, and explicitly state that calibration remains an unresolved research topic.
        """)

# =============================================================
# SCREEN 4: CONSERVATION DECISION SUPPORT
# =============================================================
elif screen == "🛡️ Screen 4: Decision Support":
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">🛡️ Conservation Decision Support System</div>
        <div class="sub-header">Actionable, evidence-backed watershed and farm-level groundwater conservation interventions</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="info-callout">
            <b>Decision-Support Advisory Notice</b>: Interventions presented below are rule-based hydrogeological guidelines synthesized from standard Central Ground Water Board (CGWB) and Groundwater Surveys and Development Agency (GSDA) watershed conservation handbooks. They represent preliminary decision-support heuristics, <b>not validated site-specific engineering designs</b>. All structural interventions require detailed on-site hydrogeological, geophysical, and civil surveys prior to construction.
        </div>
        """,
        unsafe_allow_html=True
    )
    
    latest_st = df.sort_values('date').groupby('station').last().reset_index()
    
    st.markdown("### 📋 Station-wise Vulnerability & Prescribed Interventions")
    
    for _, st_row in latest_st.iterrows():
        st_name = st_row['station']
        depth = st_row['gw_level_mbgl']
        status, color, badge = get_status(depth)
        
        with st.expander(f"{'🔴' if status=='Critical' else '🟡' if status=='Semi-Critical' else '🟢'} **{st_name}** — Level: {depth:.2f} m MBGL ({status})"):
            c1, c2 = st.columns([1, 1.5])
            with c1:
                st.markdown(f"**Latest Reading Date:** {st_row['date'].strftime('%d %b %Y')}")
                st.markdown(f"**Season:** {st_row['season_tag']}")
                st.markdown(f"**Past 90-Day Rain:** `{st_row['rain_90d']:.1f} mm`")
                st.markdown(f"**Past 365-Day Rain:** `{st_row['rain_365d']:.1f} mm`")
                if st_row.get('is_rainfall_extrapolated', 0):
                    st.caption("⚠️ *Station is outside the 4-point IMD rainfall grid; rainfall lookbacks are spatially extrapolated.*")
                
            with c2:
                st.markdown("**Recommended Conservation Actions:**")
                if status == "Critical":
                    st.error("🚨 **High Priority Intervention Required**")
                    st.markdown("""
                    - **Artificial Recharge Structures**: Fast-track construction of percolation tanks and cement check dams across local nalas.
                    - **Borewell Regulation**: Suspend permits for new commercial extraction borewells until post-monsoon recovery.
                    - **Crop Shift Advisory**: Transition summer crops away from sugarcane towards drought-hardy pulses, millets, and drip-irrigated horticulture (custard apple, pomegranate).
                    - **Farm Ponds (Shet-Tale)**: Line farm ponds with plastic sheeting to prevent percolation loss in storage ponds.
                    """)
                elif status == "Semi-Critical":
                    st.warning("⚠️ **Moderate Depletion Precaution**")
                    st.markdown("""
                    - **Continuous Contour Trenches (CCT)**: Implement ridge-to-valley soil moisture conservation on upper slope lands.
                    - **Micro-Irrigation Incentives**: Promote 100% drip irrigation for fig and vegetable orchards.
                    - **Rooftop Rainwater Harvesting**: Mandate injection well recharge for large institutional/panchayat buildings.
                    """)
                else:
                    st.success("✅ **Sustainable Level Maintained**")
                    st.markdown("""
                    - **Aquifer Maintenance**: Continue monitored seasonal pumping.
                    - **Community Water Budgeting**: Conduct bi-annual village water audits at Gram Sabha meetings before the rabi planting season.
                    """)
                    
    st.markdown("---")
    st.info("📌 **Disclaimer**: *BhujalDrishti provides decision-support advisories based on CGWB/GSDA hydrogeological guidelines and statistical model outputs. Interventions should be validated with local site inspections by hydrogeologists prior to civil execution.*")
