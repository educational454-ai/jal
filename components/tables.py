"""Station telemetry table formatting component."""
import pandas as pd
import streamlit as st
from services.data_loader import get_depth_tier


def render_latest_stations_table(latest_per_station: pd.DataFrame) -> None:
    """Render formatted telemetry table showing the latest snapshot for all monitoring stations."""
    display_df = latest_per_station[['station', 'date', 'gw_level_mbgl', 'season_tag', 'is_rainfall_extrapolated']].copy()
    display_df['Observation Date'] = display_df['date'].dt.strftime('%d-%b-%Y')
    display_df['Water Depth (m MBGL)'] = display_df['gw_level_mbgl'].apply(lambda x: f"{x:.2f}")
    display_df['Project Depth Tier'] = display_df['gw_level_mbgl'].apply(lambda x: get_depth_tier(x)[0])
    display_df.rename(columns={'station': 'Station Name'}, inplace=True)
    
    col_config = {
        "Station Name": st.column_config.TextColumn("Station Name", width="medium"),
        "Observation Date": st.column_config.TextColumn("Observation Date", width="small"),
        "Water Depth (m MBGL)": st.column_config.TextColumn("Water Depth (m MBGL)", width="small"),
        "Project Depth Tier": st.column_config.TextColumn("Project Depth Tier", width="medium"),
    }
    
    # Render all 11 stations with comfortable row height to avoid vertical clipping
    table_height = int((len(display_df) + 1) * 35.5 + 10)
    
    # Primary clean view: exactly the four most useful default columns
    st.dataframe(
        display_df[['Station Name', 'Observation Date', 'Water Depth (m MBGL)', 'Project Depth Tier']],
        use_container_width=True,
        hide_index=True,
        height=table_height,
        column_config=col_config
    )
    
    # Secondary technical information enclosed in a collapsed detail expander
    with st.expander("ℹ️ Telemetry Technical Details & Extrapolation Status"):
        tech_df = display_df.copy()
        tech_df['Season'] = latest_per_station['season_tag'].values
        tech_df['Rainfall Status'] = latest_per_station['is_rainfall_extrapolated'].apply(
            lambda x: "⚠️ Extrapolated (outside 0.25° IMD grid)" if x else "✓ Inside IMD Grid"
        ).values
        
        if 'latitude' in latest_per_station.columns and 'longitude' in latest_per_station.columns:
            tech_df['Coordinates'] = latest_per_station.apply(
                lambda r: f"{r['latitude']:.4f}°N, {r['longitude']:.4f}°E", axis=1
            ).values
            cols = ['Station Name', 'Observation Date', 'Season', 'Coordinates', 'Rainfall Status']
        else:
            cols = ['Station Name', 'Observation Date', 'Season', 'Rainfall Status']
            
        tech_col_config = {
            "Station Name": st.column_config.TextColumn("Station Name", width="medium"),
            "Observation Date": st.column_config.TextColumn("Observation Date", width="small"),
            "Season": st.column_config.TextColumn("Season", width="medium"),
            "Coordinates": st.column_config.TextColumn("Coordinates", width="medium"),
            "Rainfall Status": st.column_config.TextColumn("Rainfall Status", width="medium"),
        }
            
        st.dataframe(
            tech_df[cols], 
            use_container_width=True, 
            hide_index=True,
            height=table_height,
            column_config=tech_col_config
        )
        st.caption(
            "ℹ️ *Extrapolation status indicates monitoring stations located near the taluka periphery where antecedent "
            "precipitation lookbacks are derived via inverse-distance weighting from adjacent IMD 0.25° grid centroids. "
            "This reflects rainfall data grid geometry, not administrative taluka boundary discrepancies.*"
        )
        
    st.caption("ℹ️ *Historical in-situ manual CGWB observations (1996–2023), not live monitoring. Negative depth values (if any) reflect artesian/overflow conditions.*")
