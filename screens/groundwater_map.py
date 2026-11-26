"""Groundwater Map screen implementation for BhujalDrishti."""
import pandas as pd
import streamlit as st

from services.data_loader import (
    get_latest_per_station, 
    get_depth_tier_category,
    get_depth_tier
)
from components.map_view import render_groundwater_map
from components.metric_cards import render_kpi_card
from components.callouts import render_spatial_model_status_expander
from styles.theme import get_current_theme


def render_groundwater_map_screen(df: pd.DataFrame) -> None:
    """Render Screen 2: Groundwater Map GIS Dashboard."""
    active_theme = get_current_theme()
    latest_st = get_latest_per_station(df)

    # Check spatial coordinates validity across the monitoring network
    valid_coord_mask = (
        latest_st['latitude'].notna() & 
        latest_st['longitude'].notna() & 
        (latest_st['latitude'] != 0) & 
        (latest_st['longitude'] != 0)
    )
    mapped_count = int(valid_coord_mask.sum())
    total_stations = len(latest_st)

    # Depth categories count for the entire network
    all_categories = latest_st['gw_level_mbgl'].apply(get_depth_tier_category)
    n_shallow_all = int((all_categories == "Shallow").sum())
    n_moderate_all = int((all_categories == "Moderate").sum())
    n_deep_all = int((all_categories == "Deep").sum())

    # 1. Welcome & Study Area Header Card
    st.markdown("""
    <div class="map-welcome-card">
        <div class="map-welcome-eyebrow">GIS Spatial Layer · Purandar Taluka, Maharashtra</div>
        <div class="map-welcome-title">Purandar Groundwater Telemetry Map</div>
        <div class="map-welcome-desc">
            Interactive geographical visualization of the 11 Central Ground Water Board (CGWB) in-situ monitoring stations 
            distributed across <b>Purandar Taluka, Pune District, Maharashtra</b> (~2,936 km²). Each marker represents 
            a discrete observation well color-coded by its latest recorded physical depth category.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Interactive Map Controls Toolbar
    c_tier, c_search, c_reset = st.columns([1.6, 1.6, 0.8])

    depth_filter_options = [
        "All Depth Categories", 
        "Shallow (< 4 m MBGL)", 
        "Moderate (4–8 m MBGL)", 
        "Deep (> 8 m MBGL)"
    ]

    # Initialize session state for filters if not present or outdated
    if "map_depth_filter_select" not in st.session_state or st.session_state["map_depth_filter_select"] not in depth_filter_options:
        st.session_state["map_depth_filter_select"] = "All Depth Categories"
    if "map_station_search_select" not in st.session_state:
        st.session_state["map_station_search_select"] = "All Stations"

    # Reset button handler
    with c_reset:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Reset Filters", use_container_width=True, help="Clear active depth category and station search filters."):
            st.session_state["map_depth_filter_select"] = "All Depth Categories"
            st.session_state["map_station_search_select"] = "All Stations"
            st.rerun()

    with c_tier:
        selected_tier = st.selectbox(
            "Filter by Depth Category",
            options=depth_filter_options,
            key="map_depth_filter_select",
            help="Filter map markers to display all stations or only stations within a specific physical depth category."
        )

    # Apply depth tier filtering using existing canonical classification logic
    filtered_stations = latest_st.copy()
    filter_category_map = {
        "Shallow (< 4 m MBGL)": "Shallow",
        "Moderate (4–8 m MBGL)": "Moderate",
        "Deep (> 8 m MBGL)": "Deep",
        "Shallow (< 4.0 m)": "Shallow",
        "Moderate (4.0–8.0 m)": "Moderate",
        "Deep (> 8.0 m)": "Deep"
    }
    target_category = filter_category_map.get(selected_tier)
    if target_category:
        filtered_stations = filtered_stations[
            filtered_stations['gw_level_mbgl'].apply(get_depth_tier_category) == target_category
        ]

    # Station search options dynamically restricted to tier-filtered stations
    station_options = ["All Stations"] + sorted(filtered_stations['station'].unique().tolist())

    # Ensure current search select value is valid in options
    current_search = st.session_state.get("map_station_search_select", "All Stations")
    if current_search not in station_options:
        current_search = "All Stations"
        st.session_state["map_station_search_select"] = "All Stations"

    with c_search:
        selected_station_option = st.selectbox(
            "Search / Select Monitoring Station",
            options=station_options,
            key="map_station_search_select",
            help="Focus on an individual monitoring station to zoom directly and inspect its telemetry details."
        )

    # 3. Map Legend Toolbar
    st.markdown("""
    <div class="map-legend-bar" style="margin-bottom: 8px;">
        <span class="map-legend-title">Depth Categories:</span>
        <span class="badge-shallow" title="Shallow: MBGL < 4 m">● Shallow (&lt; 4 m MBGL)</span>
        <span class="badge-moderate" title="Moderate: 4–8 m MBGL">● Moderate (4–8 m MBGL)</span>
        <span class="badge-deep" title="Deep: MBGL > 8 m">● Deep (&gt; 8 m MBGL)</span>
        <span style="color: var(--text-secondary); font-size: 0.78rem; margin-left: 8px;">
            • Click any marker or select a station from the dropdown to view its telemetry details &nbsp;|&nbsp; ⟲ Reset View button on top-left of map
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Check for invalid coordinates in filtered set (defensive handling)
    valid_coords = filtered_stations[
        filtered_stations['latitude'].notna() & 
        filtered_stations['longitude'].notna() & 
        (filtered_stations['latitude'] != 0) & 
        (filtered_stations['longitude'] != 0)
    ]
    invalid_coords = filtered_stations[
        filtered_stations['latitude'].isna() | 
        filtered_stations['longitude'].isna() | 
        (filtered_stations['latitude'] == 0) | 
        (filtered_stations['longitude'] == 0)
    ]
    if len(invalid_coords) > 0:
        st.warning(
            f"⚠️ **Spatial Data Quality Notice:** {len(invalid_coords)} station(s) "
            f"({', '.join(invalid_coords['station'].tolist())}) have unrecorded or invalid coordinates "
            f"and are excluded from map rendering to preserve spatial integrity. Their telemetry is listed in the table below."
        )

    # 4. Interactive Leaflet Map View (Prominent near top)
    target_station_focus = None if selected_station_option == "All Stations" else selected_station_option
    render_groundwater_map(
        valid_coords, 
        selected_station=target_station_focus, 
        theme=active_theme
    )

    # Boundary notice
    st.caption(
        "ℹ️ *Geographical Boundary Note: Official Purandar Taluka administrative boundary GeoJSON is not available in the repository. "
        "The map displays verified in-situ monitoring stations at their recorded coordinates without unvalidated boundary approximations.*"
    )

    # 5. Station Selection Details Panel
    if selected_station_option != "All Stations":
        st_row = latest_st[latest_st['station'] == selected_station_option].iloc[0]
        depth_val = float(st_row['gw_level_mbgl'])
        tier_label, tier_color, tier_badge = get_depth_tier(depth_val)
        obs_date_str = st_row['date'].strftime('%d-%b-%Y')
        lat_str = f"{st_row['latitude']:.4f}°N" if pd.notnull(st_row['latitude']) else "Unrecorded"
        lon_str = f"{st_row['longitude']:.4f}°E" if pd.notnull(st_row['longitude']) else "Unrecorded"
        
        prev_depth = st_row.get('prev_gw_level_mbgl')
        prev_date = st_row.get('prev_date')
        change = st_row.get('depth_change_m')
        days = st_row.get('days_elapsed')
        
        prev_depth_str = f"{prev_depth:.2f} m MBGL" if pd.notnull(prev_depth) else "—"
        prev_date_str = prev_date.strftime('%d-%b-%Y') if pd.notnull(prev_date) else "—"
        
        is_zendewadi = (selected_station_option == 'Zendewadi')
        flag = " ⚠️" if is_zendewadi else ""
        if pd.isna(change):
            change_display = "— (Single historical record)"
            narrative = f"Station <b>{selected_station_option}</b> has a single recorded historical sounding of {depth_val:.2f} m MBGL on {obs_date_str}. No prior survey is available in the dataset."
        elif change > 0:
            change_display = f"↑ +{change:.2f} m (Deeper){flag}"
            narrative = f"The water table at <b>{selected_station_option}</b> was measured at <b>{depth_val:.2f} m MBGL</b> on <b>{obs_date_str}</b> ({tier_label}). Compared to the previous survey on {prev_date_str} ({prev_depth_str}), the water table deepened by <b>+{change:.2f} m</b> (water level fell)."
        elif change < 0:
            change_display = f"↓ {change:.2f} m (Shallower){flag}"
            narrative = f"The water table at <b>{selected_station_option}</b> was measured at <b>{depth_val:.2f} m MBGL</b> on <b>{obs_date_str}</b> ({tier_label}). Compared to the previous survey on {prev_date_str} ({prev_depth_str}), the water table rose closer to the surface by <b>{abs(change):.2f} m</b> (water level ascended)."
        else:
            change_display = f"~ 0.00 m (Stable){flag}"
            narrative = f"The water table at <b>{selected_station_option}</b> was measured at <b>{depth_val:.2f} m MBGL</b> on <b>{obs_date_str}</b> ({tier_label}), remaining approximately unchanged from the prior survey."

        if pd.isna(days) or days is None:
            elapsed_display = "—"
        else:
            days_int = int(days)
            if is_zendewadi or days_int >= 2000:
                elapsed_display = f"{days_int:,} days ⚠️ (6.0-yr gap)"
                narrative += " ⚠️ <i>Note: Zendewadi's observed change spans a 2,206-day (6.0-year) observation gap (2016–2022) and must not be compared directly to seasonal 57-day intervals.</i>"
            elif days_int > 365:
                yrs = days_int / 365.25
                elapsed_display = f"{days_int} days ({yrs:.1f}-yr gap)"
            else:
                elapsed_display = f"{days_int} days"

        is_extrap = bool(st_row.get('is_rainfall_extrapolated', 0))
        rain_status = "⚠️ Extrapolated (Outside 4-Point Grid)" if is_extrap else "✓ Within 4-Point IMD Grid"

        st.markdown(f"""
        <div class="map-station-detail-card">
            <div class="map-station-header">
                <div class="map-station-title-group">
                    <span class="map-station-name">{selected_station_option}</span>
                    <span class="map-station-coords">{lat_str}, {lon_str}</span>
                </div>
                <div>
                    <span class="{tier_badge}">● {tier_label}</span>
                </div>
            </div>
            <div class="map-station-grid">
                <div class="map-station-metric">
                    <span class="map-station-metric-label">Latest Measured Depth</span>
                    <span class="map-station-metric-val">{depth_val:.2f} m MBGL</span>
                    <span class="map-station-metric-sub">In-situ manual tape sounding</span>
                </div>
                <div class="map-station-metric">
                    <span class="map-station-metric-label">Observation Date</span>
                    <span class="map-station-metric-val">{obs_date_str}</span>
                    <span class="map-station-metric-sub">Historical survey · Not live telemetry</span>
                </div>
                <div class="map-station-metric">
                    <span class="map-station-metric-label">Observed Change</span>
                    <span class="map-station-metric-val">{change_display}</span>
                    <span class="map-station-metric-sub">vs. prior recorded observation</span>
                </div>
                <div class="map-station-metric">
                    <span class="map-station-metric-label">Previous Survey Date</span>
                    <span class="map-station-metric-val">{prev_date_str}</span>
                    <span class="map-station-metric-sub">Elapsed time: {elapsed_display}</span>
                </div>
                <div class="map-station-metric">
                    <span class="map-station-metric-label">Geographic Coordinates</span>
                    <span class="map-station-metric-val" style="font-size: 1.05rem;">{lat_str}, {lon_str}</span>
                    <span class="map-station-metric-sub">Purandar Taluka, Maharashtra</span>
                </div>
                <div class="map-station-metric">
                    <span class="map-station-metric-label">IMD Rainfall Grid Status</span>
                    <span class="map-station-metric-val" style="font-size: 0.95rem;">{rain_status}</span>
                    <span class="map-station-metric-sub">Regional precipitation lookback alignment</span>
                </div>
            </div>
            <div class="map-station-narrative">
                {narrative}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="map-all-summary-card">
            <div class="map-all-summary-text">
                <div class="map-all-summary-title">Network Overview · 11 Monitoring Stations</div>
                <div class="map-all-summary-sub">
                    Showing all 11 CGWB monitoring stations across Purandar Taluka (~2,936 km²). Select any station from the dropdown above or click a marker on the map to inspect its individual depth, observation date, and prior survey changes.
                </div>
            </div>
            <div class="map-all-badges">
                <span class="badge-shallow">● {n_shallow_all} Shallow (&lt; 4 m MBGL)</span>
                <span class="badge-moderate">● {n_moderate_all} Moderate (4–8 m MBGL)</span>
                <span class="badge-deep">● {n_deep_all} Deep (&gt; 8 m MBGL)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 6. Scientific Explanation & Spatial Scope Card
    st.markdown("""
    <div class="map-spatial-explainer-card">
        <div class="map-spatial-explainer-title">
            <span>💡</span>
            <span>Scientific Hydrogeology & Spatial Scope</span>
        </div>
        <div class="map-spatial-explainer-grid">
            <div class="map-spatial-explainer-item">
                <span class="map-spatial-explainer-heading">What Each Marker Represents</span>
                <span class="map-spatial-explainer-body">
                    Each colored dot marks a discrete in-situ monitoring station (borewell or open dugwell) surveyed historically by the Central Ground Water Board (CGWB) in Purandar Taluka. Markers indicate the station's latest recorded physical depth category.
                </span>
            </div>
            <div class="map-spatial-explainer-item">
                <span class="map-spatial-explainer-heading">Understanding MBGL (Metres Below Ground Level)</span>
                <span class="map-spatial-explainer-body">
                    Groundwater depth measures down from the ground surface. A <b>lower MBGL number</b> (e.g. 2.9 m) means water is <b>closer to the surface</b> (shallower/replenished). A <b>higher MBGL number</b> (e.g. 12.1 m) means water is <b>deep underground</b> (depleted/drawn down).
                </span>
            </div>
            <div class="map-spatial-explainer-item">
                <span class="map-spatial-explainer-heading">Why Discrete Points Instead of a Continuous Heatmap?</span>
                <span class="map-spatial-explainer-body">
                    Purandar Taluka covers ~2,936 km² with 11 monitoring stations (~1 station per 267 km²). In regional hard-rock terrain, groundwater distribution can be spatially heterogeneous across short distances due to localized sub-surface variations. Without dense, site-specific borehole lithological records and unmetered abstraction data, continuous spatial interpolation across sparse points is scientifically unreliable and would produce unsupported contours.
                </span>
            </div>
            <div class="map-spatial-explainer-item">
                <span class="map-spatial-explainer-heading">Spatial Generalization Status (LOSO-CV R² = 0.022)</span>
                <span class="map-spatial-explainer-body">
                    Rigorous spatial Leave-One-Station-Out cross-validation (LOSO-CV) demonstrates that predicting groundwater depths at unmonitored locations achieves an <b>R² of 0.022</b> (near-zero spatial generalizability). This empirical validation confirms that groundwater levels cannot be extrapolated reliably between sparse monitoring points in this hard-rock setting, justifying the decision to display discrete station observations only.
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 7. Station Telemetry Data Table
    st.subheader(f"Monitoring Station Historical Data Table ({len(filtered_stations)} Stations)")
    
    st.markdown(
        """
        <div class="info-callout" style="border-left-color: var(--badge-moderate-border); margin-bottom: 12px;">
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

    # Format table for display
    display_df = pd.DataFrame()
    display_df['Station Name'] = filtered_stations['station']
    display_df['Observation Date'] = filtered_stations['date'].dt.strftime('%d-%b-%Y')
    display_df['Water Depth (m MBGL)'] = filtered_stations['gw_level_mbgl'].apply(lambda x: f"{x:.2f}")
    display_df['Project Depth Tier'] = filtered_stations['gw_level_mbgl'].apply(lambda x: get_depth_tier(x)[0])

    def format_change(row) -> str:
        diff = row.get('depth_change_m')
        st_name = row.get('station', '')
        if pd.isna(diff):
            return "— (Single record)"
        flag = " ⚠️" if st_name == 'Zendewadi' else ""
        if diff > 0:
            return f"+{diff:.2f} m (Deeper){flag}"
        elif diff < 0:
            return f"{diff:.2f} m (Shallower){flag}"
        else:
            return f"0.00 m (Unchanged){flag}"

    display_df['Observed Change'] = filtered_stations.apply(format_change, axis=1)

    display_df['Previous Survey Date'] = filtered_stations['prev_date'].apply(
        lambda x: x.strftime('%d-%b-%Y') if pd.notnull(x) else "—"
    )

    def format_elapsed(row) -> str:
        days = row.get('days_elapsed')
        st_name = row.get('station', '')
        if pd.isna(days) or days is None:
            return "—"
        days_int = int(days)
        if st_name == 'Zendewadi' or days_int >= 2000:
            return f"{days_int:,} days ⚠️ (6.0-yr gap)"
        elif days_int > 365:
            yrs = days_int / 365.25
            return f"{days_int} days ({yrs:.1f}-yr gap)"
        else:
            return f"{days_int} days"

    display_df['Elapsed Days'] = filtered_stations.apply(format_elapsed, axis=1)

    display_df['Coordinates'] = filtered_stations.apply(
        lambda r: f"{r['latitude']:.4f}°N, {r['longitude']:.4f}°E" if pd.notnull(r['latitude']) else "Unrecorded", axis=1
    )

    display_df['Rainfall Status'] = filtered_stations['is_rainfall_extrapolated'].apply(
        lambda x: "⚠️ Extrapolated (Outside 4-Point Grid)" if x else "✓ Within Grid Coverage"
    )

    col_config = {
        "Station Name": st.column_config.TextColumn("Station Name", width="medium"),
        "Observation Date": st.column_config.TextColumn("Observation Date", width="small"),
        "Water Depth (m MBGL)": st.column_config.TextColumn("Water Depth (m MBGL)", width="small"),
        "Project Depth Tier": st.column_config.TextColumn("Project Depth Tier", width="medium"),
        "Observed Change": st.column_config.TextColumn("Observed Change", width="medium"),
        "Previous Survey Date": st.column_config.TextColumn("Previous Survey Date", width="small"),
        "Elapsed Days": st.column_config.TextColumn("Elapsed Days", width="medium"),
        "Coordinates": st.column_config.TextColumn("Coordinates", width="medium"),
        "Rainfall Status": st.column_config.TextColumn("Rainfall Status", width="small"),
    }

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config=col_config
    )

    st.caption("ℹ️ *Historical in-situ manual CGWB observations (1996–2023), not live monitoring. Negative depth values (if any) reflect artesian/overflow conditions. Reference categories (Shallow: < 4 m, Moderate: 4–8 m, Deep: > 8 m MBGL) are project-defined physical reference bands, not official CGWB administrative categories. Stations outside the four-point rainfall grid's spatial coverage require extrapolated rainfall estimates; grid coverage does not imply uniform or dense rain-gauge coverage.*")

    # 8. Network Monitoring Snapshot & Research Findings (Collapsible Expander)
    with st.expander("ℹ️ Network Monitoring Snapshot & Spatial Model Findings", expanded=False):
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_kpi_card(
                label="Monitoring Network",
                value=f"{total_stations} Stations",
                caption="CGWB observation stations represented in historical dataset."
            )
        with k2:
            render_kpi_card(
                label="Stations with Valid Coordinates",
                value=f"{mapped_count} / {total_stations}",
                caption="Recorded non-null station coordinates; validity does not establish positional accuracy."
            )
        with k3:
            render_kpi_card(
                label="Latest Recorded Depth Distribution",
                value=f"{n_shallow_all}S · {n_moderate_all}M · {n_deep_all}D",
                caption=f"Physical reference tiers (MBGL): {n_shallow_all} Shallow (< 4 m), {n_moderate_all} Moderate (4–8 m), {n_deep_all} Deep (> 8 m)."
            )
        with k4:
            render_kpi_card(
                label="Latest Observation Coverage",
                value="1997–2023",
                caption="7 stations observed in 2023; 4 stations reflect earlier historical rounds."
            )
        
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        render_spatial_model_status_expander()
