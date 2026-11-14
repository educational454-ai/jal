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
    # A. Page Heading (Restrained, scientific, consistent with shared design system)
    st.markdown("""
    <div class="screen-header-block">
        <div class="main-header">Purandar Groundwater Telemetry Map</div>
        <div class="sub-header">Geographical distribution and station-level water table observations · 11 CGWB monitoring stations</div>
    </div>
    """, unsafe_allow_html=True)
    
    latest_st = get_latest_per_station(df)
    active_theme = get_current_theme()
    
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

    # B. Station Summary KPI Cards (Section 6)
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
            caption=f"Physical reference tiers: {n_shallow_all} Shallow, {n_moderate_all} Moderate, {n_deep_all} Deep."
        )
    with k4:
        render_kpi_card(
            label="Latest Observation Coverage",
            value="1997–2023",
            caption="7 stations observed in 2023; 4 stations reflect earlier historical rounds."
        )

    # C. Interactive Controls Toolbar (Section 5)
    c_tier, c_search, c_reset = st.columns([1.6, 1.6, 0.8])
    
    # Initialize session state for filters if not present
    if "map_depth_filter_select" not in st.session_state:
        st.session_state["map_depth_filter_select"] = "All Depth Tiers"
    if "map_station_search_select" not in st.session_state:
        st.session_state["map_station_search_select"] = "All Stations"

    # Reset button handler
    with c_reset:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Reset Filters", use_container_width=True, help="Clear active depth tier and station search filters."):
            st.session_state["map_depth_filter_select"] = "All Depth Tiers"
            st.session_state["map_station_search_select"] = "All Stations"
            st.rerun()

    with c_tier:
        depth_filter_options = [
            "All Depth Tiers", 
            "Shallow (< 4.0 m)", 
            "Moderate (4.0–8.0 m)", 
            "Deep (> 8.0 m)"
        ]
        selected_tier = st.selectbox(
            "Filter by Depth Category",
            options=depth_filter_options,
            key="map_depth_filter_select",
            help="Filter map markers to display all stations or only stations within a specific depth tier."
        )

    # Apply depth tier filtering
    filtered_stations = latest_st.copy()
    filter_category_map = {
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
            help="Focus on an individual monitoring station to zoom directly and inspect its telemetry popup."
        )

    # D. Map Legend Toolbar
    st.markdown("""
    <div class="map-legend-bar" style="margin-bottom: 6px;">
        <span class="map-legend-title">Depth Tiers:</span>
        <span class="badge-shallow" title="Shallow: < 4.0 m MBGL">● Shallow (&lt; 4.0 m)</span>
        <span class="badge-moderate" title="Moderate: 4.0–8.0 m MBGL">● Moderate (4.0–8.0 m)</span>
        <span class="badge-deep" title="Deep: > 8.0 m MBGL">● Deep (&gt; 8.0 m)</span>
        <span style="color: var(--text-secondary); font-size: 0.76rem; margin-left: 8px;">
            • Click any marker to view telemetry popup & historical changes &nbsp;|&nbsp; ⟲ Reset View button on top-left of map
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

    # E. Interactive Leaflet Map View (Section 3 & 4)
    target_station_focus = None if selected_station_option == "All Stations" else selected_station_option
    render_groundwater_map(
        valid_coords, 
        selected_station=target_station_focus, 
        theme=active_theme
    )

    # Boundary notice (Section 7)
    st.caption(
        "ℹ️ *Geographical Boundary Note: Official Purandar Taluka administrative boundary GeoJSON is not available in the repository. "
        "The map displays verified in-situ monitoring stations at their recorded coordinates without unvalidated boundary approximations.*"
    )

    # F. Station Information & Telemetry Table (Section 6)
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.subheader(f"Station Telemetry Details ({len(filtered_stations)} Stations)")
    
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

    st.caption("ℹ️ *Historical in-situ manual CGWB observations (1996–2023), not live monitoring. Negative depth values (if any) reflect artesian/overflow conditions. Reference bands (< 4.0 m, 4.0–8.0 m, > 8.0 m) are project-defined physical tiers, not official CGWB administrative categories. Stations outside the four-point rainfall grid's spatial coverage require extrapolated rainfall estimates; grid coverage does not imply uniform or dense rain-gauge coverage.*")
    
    # G. Methodological Findings on Spatial Prediction & LOSO-CV (Section 8)
    render_spatial_model_status_expander()
