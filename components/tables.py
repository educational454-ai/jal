"""Station telemetry table formatting component."""
import pandas as pd
import streamlit as st
from services.data_loader import get_depth_tier


def render_latest_stations_table(latest_per_station: pd.DataFrame) -> None:
    """Render formatted telemetry table showing latest snapshot and station-wise changes."""
    display_df = pd.DataFrame()
    display_df['Station Name'] = latest_per_station['station']
    display_df['Observation Date'] = latest_per_station['date'].dt.strftime('%d-%b-%Y')
    display_df['Water Depth (m MBGL)'] = latest_per_station['gw_level_mbgl'].apply(lambda x: f"{x:.2f}")
    display_df['Project Depth Tier'] = latest_per_station['gw_level_mbgl'].apply(lambda x: get_depth_tier(x)[0])
    
    # Dynamic calculation of depth change formatting
    def format_change(row) -> str:
        diff = row.get('depth_change_m')
        st_name = row.get('station', '')
        if pd.isna(diff):
            return "— (Insufficient data)"
        flag = " ⚠️" if st_name == 'Zendewadi' else ""
        if diff > 0:
            return f"+{diff:.2f} m (Deeper){flag}"
        elif diff < 0:
            return f"{diff:.2f} m (Shallower){flag}"
        else:
            return f"0.00 m (Unchanged){flag}"

    display_df['Observed Change'] = latest_per_station.apply(format_change, axis=1)

    # Previous survey date formatting
    display_df['Previous Survey Date'] = latest_per_station['prev_date'].apply(
        lambda x: x.strftime('%d-%b-%Y') if pd.notnull(x) else "—"
    )

    # Elapsed days formatting with Zendewadi gap flag
    def format_elapsed_days(row) -> str:
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

    display_df['Elapsed Days'] = latest_per_station.apply(format_elapsed_days, axis=1)

    col_config = {
        "Station Name": st.column_config.TextColumn("Station Name", width="medium"),
        "Observation Date": st.column_config.TextColumn("Observation Date", width="small"),
        "Water Depth (m MBGL)": st.column_config.TextColumn("Water Depth (m MBGL)", width="small"),
        "Project Depth Tier": st.column_config.TextColumn("Project Depth Tier", width="medium"),
        "Observed Change": st.column_config.TextColumn(
            "Observed Change", 
            width="medium",
            help="Change in groundwater depth between latest and immediately preceding observation (latest MBGL − previous MBGL). "
                 "Positive = Deeper water table (water level fell); Negative = Shallower water table (water level rose)."
        ),
        "Previous Survey Date": st.column_config.TextColumn(
            "Previous Survey Date", 
            width="small",
            help="Date of the immediately preceding recorded in-situ groundwater measurement."
        ),
        "Elapsed Days": st.column_config.TextColumn(
            "Elapsed Days", 
            width="medium",
            help="Calendar days between preceding and latest recorded groundwater observations."
        ),
    }

    # Render all 11 stations with comfortable row height to avoid vertical clipping
    table_height = int((len(display_df) + 1) * 35.5 + 10)

    # Primary clean view: 7 well-structured columns
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=table_height,
        column_config=col_config
    )

    # Observation recency and interval context note
    st.caption(
        "ℹ️ **Observation Recency & Interval Context:** 7 monitoring stations have telemetry observations recorded in the 2023 cycle (6 through May 2023, 1 through March 2023). "
        "4 stations have older latest observations in this research dataset (Zendewadi: May 2022, Saswad: Aug 2006, Waghapur: Aug 1997, Walha: Jan 1997). "
        "Absence of recent observations reflects the temporal period of record in the dataset, not physical well operational status. "
        "⚠️ Zendewadi's observed change (+0.67 m) spans a 2,206-day (6.0-year) gap (2016–2022) and must not be compared directly to 57-day seasonal intervals."
    )

    # Secondary technical information enclosed in a collapsed detail expander
    with st.expander("ℹ️ Telemetry Technical Details & Extrapolation Status"):
        tech_df = display_df[['Station Name', 'Observation Date', 'Previous Survey Date']].copy()
        tech_df['Season'] = latest_per_station['season_tag'].values
        
        # Add Previous Depth
        tech_df['Previous Depth (m)'] = latest_per_station['prev_gw_level_mbgl'].apply(
            lambda x: f"{x:.2f} m" if pd.notnull(x) else "—"
        )
        
        # Total historical observations handling limited records safely
        tech_df['Total Records'] = latest_per_station['total_station_records'].apply(
            lambda x: f"{int(x)} (Limited history)" if int(x) < 10 else f"{int(x)}"
        )
        
        # Dataset Recency classification
        def classify_recency(d):
            yr = pd.to_datetime(d).year
            return "2023 Monitoring Series" if yr == 2023 else f"Historical Record ({yr})"
            
        tech_df['Dataset Recency'] = latest_per_station['date'].apply(classify_recency)
        
        tech_df['Rainfall Status'] = latest_per_station['is_rainfall_extrapolated'].apply(
            lambda x: "⚠️ Extrapolated (outside 0.25° IMD grid)" if x else "✓ Inside IMD Grid"
        ).values
        
        if 'latitude' in latest_per_station.columns and 'longitude' in latest_per_station.columns:
            tech_df['Coordinates'] = latest_per_station.apply(
                lambda r: f"{r['latitude']:.4f}°N, {r['longitude']:.4f}°E", axis=1
            ).values
            cols = [
                'Station Name', 'Observation Date', 'Season', 'Previous Survey Date', 
                'Previous Depth (m)', 'Coordinates', 'Total Records', 'Dataset Recency', 'Rainfall Status'
            ]
        else:
            cols = [
                'Station Name', 'Observation Date', 'Season', 'Previous Survey Date', 
                'Previous Depth (m)', 'Total Records', 'Dataset Recency', 'Rainfall Status'
            ]
            
        tech_col_config = {
            "Station Name": st.column_config.TextColumn("Station Name", width="medium"),
            "Observation Date": st.column_config.TextColumn("Observation Date", width="small"),
            "Season": st.column_config.TextColumn("Season", width="medium"),
            "Previous Survey Date": st.column_config.TextColumn("Previous Survey Date", width="small"),
            "Previous Depth (m)": st.column_config.TextColumn("Previous Depth (m)", width="small"),
            "Coordinates": st.column_config.TextColumn("Coordinates", width="medium"),
            "Total Records": st.column_config.TextColumn("Total Records", width="small"),
            "Dataset Recency": st.column_config.TextColumn("Dataset Recency", width="medium"),
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
            "This reflects rainfall data grid geometry, not administrative taluka boundary discrepancies. "
            "Station record depth reflects observations contained in this research dataset.*"
        )
        
    st.caption("ℹ️ *Historical in-situ manual CGWB observations (1996–2023), not live monitoring. Negative depth values (if any) reflect artesian/overflow conditions.*")
