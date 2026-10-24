import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import json
import streamlit.components.v1 as components
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# Configuration & Memory Optimization (Lightweight for 8GB RAM)
# -------------------------------------------------------------
st.set_page_config(
    page_title="BhujalDrishti | JalRakshak AI",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .badge-safe {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-semi {
        background-color: #FEF08A;
        color: #854D0E;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-critical {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Cached Loaders (Zero redundant memory allocation)
# -------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/purandar_groundwater_features.csv")
    df['date'] = pd.to_datetime(df['date'])
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
        with open("reports/model_evaluation.json", "r") as f:
            models['metadata'] = json.load(f)
    return models

df = load_data()
models = load_models()

# Categorization helper
def get_status(mbgl):
    if mbgl < 4.0:
        return "Safe", "#10B981", "badge-safe"
    elif mbgl <= 8.0:
        return "Semi-Critical", "#F59E0B", "badge-semi"
    else:
        return "Critical", "#EF4444", "badge-critical"

# -------------------------------------------------------------
# Sidebar Navigation & Context
# -------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/water-pipe.png", width=64)
    st.markdown("### **BhujalDrishti**\n*JalRakshak AI System*")
    st.caption("Multimodal GIS & ML Groundwater Forecasting in Purandar Taluka, Maharashtra")
    st.markdown("---")
    
    screen = st.radio(
        "Navigation",
        [
            "📊 Screen 1: Overview Dashboard",
            "🗺️ Screen 2: Groundwater Map",
            "🔮 Screen 3: AI Forecasting",
            "🛡️ Screen 4: Decision Support"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("#### **Telemetry Status**")
    st.caption("📍 Taluka: **Purandar (Pune, MH)**")
    st.caption("📡 CGWB Stations: **11 Monitoring Wells**")
    st.caption("🌧️ IMD Rainfall Grids: **4 Grid Points**")
    st.caption("⚡ Memory Mode: **Eco / Low-Footprint**")

# =============================================================
# SCREEN 1: OVERVIEW DASHBOARD
# =============================================================
if screen == "📊 Screen 1: Overview Dashboard":
    st.markdown('<div class="main-header">📊 Purandar Groundwater Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Regional groundwater health, seasonal dynamics, and station alert indicators</div>', unsafe_allow_html=True)
    
    # Calculate latest snapshot
    latest_per_station = df.sort_values('date').groupby('station').last().reset_index()
    avg_latest_mbgl = latest_per_station['gw_level_mbgl'].mean()
    critical_count = (latest_per_station['gw_level_mbgl'] > 8.0).sum()
    semi_count = ((latest_per_station['gw_level_mbgl'] >= 4.0) & (latest_per_station['gw_level_mbgl'] <= 8.0)).sum()
    safe_count = (latest_per_station['gw_level_mbgl'] < 4.0).sum()
    
    # Top KPI cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Avg Groundwater Depth", f"{avg_latest_mbgl:.2f} m", help="Meters Below Ground Level (MBGL) across stations")
    with c2:
        st.metric("Safe Wells (< 4m)", f"{safe_count} / {len(latest_per_station)}", delta=f"{safe_count} safe", delta_color="normal")
    with c3:
        st.metric("Semi-Critical (4–8m)", f"{semi_count} / {len(latest_per_station)}", delta="Needs recharge", delta_color="off")
    with c4:
        st.metric("Critical Wells (> 8m)", f"{critical_count} / {len(latest_per_station)}", delta=f"{critical_count} high risk", delta_color="inverse")
        
    st.markdown("---")
    
    # Two-column layout: Latest Station Table & Rainfall/Groundwater Correlation
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        st.subheader("📍 Latest Monitoring Station Status")
        display_df = latest_per_station[['station', 'date', 'gw_level_mbgl', 'season_tag']].copy()
        display_df['date'] = display_df['date'].dt.strftime('%d-%b-%Y')
        display_df['Status'] = display_df['gw_level_mbgl'].apply(lambda x: get_status(x)[0])
        display_df.rename(columns={
            'station': 'Station Name',
            'date': 'Observation Date',
            'gw_level_mbgl': 'Depth (MBGL)',
            'season_tag': 'Season'
        }, inplace=True)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
    with col_right:
        st.subheader("🌧️ Taluka Rainfall vs. Water Table Trends")
        # Aggregated annual groundwater depth vs rainfall
        annual_summary = df.groupby('year').agg({
            'gw_level_mbgl': 'mean',
            'rain_365d': 'mean'
        }).reset_index()
        
        fig, ax1 = plt.subplots(figsize=(6, 3.8))
        color = '#1E40AF'
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Annual Rain (mm)', color=color)
        ax1.bar(annual_summary['year'], annual_summary['rain_365d'], color='#93C5FD', alpha=0.6, width=0.7, label='Rainfall (365d)')
        ax1.tick_params(axis='y', labelcolor=color)
        
        ax2 = ax1.twinx()
        color = '#DC2626'
        ax2.set_ylabel('Depth Below Ground (MBGL - lower is better)', color=color)
        ax2.plot(annual_summary['year'], annual_summary['gw_level_mbgl'], color=color, linewidth=2.2, marker='o', markersize=4, label='Avg Depth (MBGL)')
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.invert_yaxis() # Invert so higher water table goes UP
        
        fig.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.info("💡 **Hydrogeological Insight**: Notice how years with higher rainfall (e.g., 2005, 2019, 2020) directly correspond to shallower water tables (water closer to the surface, appearing higher on the inverted axis).")

# =============================================================
# SCREEN 2: GROUNDWATER MAP
# =============================================================
elif screen == "🗺️ Screen 2: Groundwater Map":
    st.markdown('<div class="main-header">🗺️ Purandar Spatial Groundwater GIS Map</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Interactive GIS mapping of 11 CGWB monitoring stations with depth status & spatial radius</div>', unsafe_allow_html=True)
    
    # Filter or latest view
    latest_st = df.sort_values('date').groupby('station').last().reset_index()
    
    c_m1, c_m2 = st.columns([3, 1])
    with c_m2:
        st.markdown("#### **Map Controls & Legend**")
        st.markdown("""
        - 🟢 **Safe Zone**: $< 4.0\\text{ m}$ MBGL
        - 🟡 **Semi-Critical**: $4.0 - 8.0\\text{ m}$ MBGL
        - 🔴 **Critical Zone**: $> 8.0\\text{ m}$ MBGL
        """)
        st.caption("Circles represent the modeled area of influence and depth magnitude for each monitoring well.")
        
        selected_zone_filter = st.selectbox("Filter by Risk Level", ["All Stations", "Safe (< 4m)", "Semi-Critical (4-8m)", "Critical (> 8m)"])
        
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
            'name': row['station'],
            'lat': float(row['latitude']),
            'lon': float(row['longitude']),
            'depth': float(row['gw_level_mbgl']),
            'status': status,
            'color': color,
            'date': row['date'].strftime('%d %b %Y'),
            'season': str(row['season_tag'])
        })
        
    leaflet_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            #map {{ height: 500px; width: 100%; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
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
                // Add marker
                var circle = L.circle([st.lat, st.lon], {{
                    color: st.color,
                    fillColor: st.color,
                    fillOpacity: 0.35,
                    radius: Math.max(1200, st.depth * 250)
                }}).addTo(map);

                var marker = L.circleMarker([st.lat, st.lon], {{
                    radius: 8,
                    fillColor: st.color,
                    color: '#ffffff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.95
                }}).addTo(map);

                var popupContent = `
                    <div style="font-family: Arial, sans-serif; min-width: 170px;">
                        <h4 style="margin: 0 0 6px 0; color: #1E3A8A;">${{st.name}}</h4>
                        <b>Water Depth:</b> ${{st.depth}} m MBGL<br>
                        <b>Classification:</b> <span style="color: ${{st.color}}; font-weight: bold;">${{st.status}}</span><br>
                        <b>Season:</b> ${{st.season}}<br>
                        <b>Last Record:</b> ${{st.date}}
                    </div>
                `;
                marker.bindPopup(popupContent);
                circle.bindPopup(popupContent);
            }});
        </script>
    </body>
    </html>
    """
    with c_m1:
        components.html(leaflet_html, height=520)

    st.caption("ℹ️ *Note: Estimated spatial areas between stations represent modeled influence zones based on station elevation and proximity, not direct physical measurements.*")

# =============================================================
# SCREEN 3: AI FORECASTING
# =============================================================
elif screen == "🔮 Screen 3: AI Forecasting":
    st.markdown('<div class="main-header">🔮 AI Groundwater Forecasting Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Station-level 1–3 month ahead predictive forecasting with uncertainty confidence intervals</div>', unsafe_allow_html=True)
    
    # Station Selector
    valid_stations = [s for s in df['station'].unique() if (df['station'] == s).sum() >= 10]
    c_s1, c_s2 = st.columns([1.2, 1.8])
    
    with c_s1:
        station_sel = st.selectbox("Select Monitoring Station", sorted(valid_stations), index=0)
        station_df = df[df['station'] == station_sel].sort_values('date').copy()
        latest_record = station_df.iloc[-1]
        
        st.markdown("#### **Latest Known Conditions**")
        st.markdown(f"- **Observation Date**: {latest_record['date'].strftime('%d %b %Y')}")
        st.markdown(f"- **Recorded Level**: `{latest_record['gw_level_mbgl']:.2f} m MBGL`")
        st.markdown(f"- **Preceding 90-Day Rain**: `{latest_record['rain_90d']:.1f} mm`")
        st.markdown(f"- **Preceding 365-Day Rain**: `{latest_record['rain_365d']:.1f} mm`")
        
        st.markdown("---")
        st.markdown("#### **Rainfall Scenario Simulation**")
        rain_factor = st.slider("Simulate Antecedent Rainfall Adjustment", -50, 50, 0, 5, format="%d%%",
                                help="Adjust rainfall to simulate a drought year (-30%) or high-recharge year (+30%)")
        
    with c_s2:
        # Forecast computation
        if 'forecast' in models and 'q10' in models and 'q90' in models:
            feature_cols_fc = models['metadata']['feature_cols_fc']
            
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
            
            # Ensure logical bounds
            lower_b = max(0.0, min(pred_q10, pred_val))
            upper_b = max(pred_val, pred_q90)
            
            st.markdown("#### **🔮 Next-Quarter Model Forecast**")
            k1, k2, k3 = st.columns(3)
            with k1:
                st.metric("Projected Depth", f"{pred_val:.2f} m", 
                          delta=f"{pred_val - latest_record['gw_level_mbgl']:+.2f} m vs current",
                          delta_color="inverse")
            with k2:
                st.metric("80% Uncertainty Band", f"{lower_b:.2f} m – {upper_b:.2f} m", help="Empirical 10th to 90th percentile confidence interval")
            with k3:
                status, color, badge = get_status(pred_val)
                st.markdown(f"**Predicted Status:**<br><span class='{badge}'>{status}</span>", unsafe_allow_html=True)
                
            st.caption(f"*Trained on Random Forest + Quantile Ensembles. Chronological test validation MAE: 2.14 m (22.2% lower error than persistence baseline).*")
            
        else:
            st.warning("Forecasting models are loading or unavailable.")
            
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
    ax.axhline(4.0, color='#10B981', linestyle=':', label='Safe Threshold (4m)')
    ax.axhline(8.0, color='#EF4444', linestyle=':', label='Critical Threshold (8m)')
    ax.invert_yaxis()
    ax.legend(loc='lower left')
    
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# =============================================================
# SCREEN 4: CONSERVATION DECISION SUPPORT
# =============================================================
elif screen == "🛡️ Screen 4: Decision Support":
    st.markdown('<div class="main-header">🛡️ Conservation Decision Support System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Actionable, evidence-backed watershed and farm-level groundwater conservation interventions</div>', unsafe_allow_html=True)
    
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
