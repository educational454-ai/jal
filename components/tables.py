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
    display_df['Season'] = display_df['season_tag']
    display_df['Rainfall Status'] = display_df['is_rainfall_extrapolated'].apply(
        lambda x: "⚠️ Extrapolated" if x else "✓ IMD Grid"
    )
    display_df.rename(columns={'station': 'Station Name'}, inplace=True)
    
    st.dataframe(
        display_df[['Station Name', 'Observation Date', 'Water Depth (m MBGL)', 'Project Depth Tier', 'Season', 'Rainfall Status']],
        use_container_width=True,
        hide_index=True
    )
    st.caption("ℹ️ *Indicates the latest recorded in-situ manual CGWB observation for each of the 11 monitoring wells in Purandar Taluka.*")
