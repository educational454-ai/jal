import pandas as pd
import numpy as np
import datetime

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2.0) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def engineer_features():
    print("--- 1. Loading Datasets ---")
    gw_path = "data/raw/purandhar_groundwater_level_merged.csv"
    rf_path = "data/raw/purandar_rainfall_1991_2023.csv"
    
    df_gw = pd.read_csv(gw_path)
    df_rf = pd.read_csv(rf_path)
    
    # Clean groundwater columns
    df_gw['date'] = pd.to_datetime(df_gw['Data Acquisition Time'], dayfirst=True)
    df_gw['date_only'] = df_gw['date'].dt.date
    target_col = 'Groundwater Level Quarterly Manual (meter)'
    df_gw['gw_level_mbgl'] = df_gw[target_col]
    
    # Preserve original negative readings (e.g. -0.40m at Narayanpur on 05-11-2009).
    # In hydrogeology, negative MBGL indicates artesian / overflow conditions where the
    # piezometric surface rises above ground level. We keep the true physical observation
    # and provide 'is_overflow' as an explicit indicator.
    df_gw['is_overflow'] = (df_gw['gw_level_mbgl'] < 0).astype(int)
    # Do NOT clip to 0.0m; preserve authentic water level
    
    # Clean rainfall
    df_rf['date'] = pd.to_datetime(df_rf['time'], dayfirst=True)
    df_rf['date_only'] = df_rf['date'].dt.date
    
    # Grid coordinates
    grid_coords = df_rf[['latitude', 'longitude']].drop_duplicates().values
    print(f"Rainfall grid points: {grid_coords}")
    grid_lat_min, grid_lat_max = grid_coords[:, 0].min(), grid_coords[:, 0].max()
    grid_lon_min, grid_lon_max = grid_coords[:, 1].min(), grid_coords[:, 1].max()
    print(f"Rainfall grid bounds: Lat [{grid_lat_min}, {grid_lat_max}], Lon [{grid_lon_min}, {grid_lon_max}]")
    
    # Station coordinates & spatial grid validity check
    stations = df_gw.groupby('Station')[['Latitude', 'Longitude']].first().reset_index()
    stations['is_rainfall_extrapolated'] = (
        (stations['Latitude'] < grid_lat_min) | (stations['Latitude'] > grid_lat_max) |
        (stations['Longitude'] < grid_lon_min) | (stations['Longitude'] > grid_lon_max)
    ).astype(int)
    print(f"Stations ({len(stations)}):")
    for _, row in stations.iterrows():
        extra_note = " [EXTRAPOLATED RAINFALL]" if row['is_rainfall_extrapolated'] else " [INTERPOLATED]"
        print(f"  {row['Station']}: ({row['Latitude']:.4f}, {row['Longitude']:.4f}){extra_note}")
        
    print("\n--- 2. Computing Spatially Weighted Rainfall per Station ---")
    # For each station, compute IDW weights from the 4 grid points
    station_weights = {}
    for _, st in stations.iterrows():
        s_lat, s_lon = st['Latitude'], st['Longitude']
        dists = []
        for g_lat, g_lon in grid_coords:
            d = haversine_distance(s_lat, s_lon, g_lat, g_lon)
            dists.append(max(d, 0.1)) # avoid div by zero
        inv_dists = [1.0 / (d ** 2) for d in dists]
        weights = [w / sum(inv_dists) for w in inv_dists]
        station_weights[st['Station']] = list(zip(grid_coords, weights))
        
    # Pivot rainfall: index=date_only, columns=(lat, lon)
    rf_pivot = df_rf.pivot(index='date_only', columns=['latitude', 'longitude'], values='rainfall').sort_index()
    
    # Precompute daily rainfall series for each station
    station_daily_rf = {}
    # Also compute taluka-wide mean daily rainfall
    rf_pivot['taluka_mean'] = rf_pivot.mean(axis=1)
    
    for st_name, g_weights in station_weights.items():
        daily_series = pd.Series(0.0, index=rf_pivot.index)
        for (g_lat, g_lon), w in g_weights:
            daily_series += rf_pivot[(g_lat, g_lon)] * w
        station_daily_rf[st_name] = daily_series
        
    print("--- 3. Merging Antecedent Rainfall Windows to Groundwater Observations ---")
    records = []
    
    # Sort groundwater by station and date
    df_gw = df_gw.sort_values(by=['Station', 'date']).reset_index(drop=True)
    
    for idx, row in df_gw.iterrows():
        st_name = row['Station']
        obs_date = row['date_only']
        rf_series = station_daily_rf[st_name]
        
        # Calculate windows leading up to obs_date
        # Temporal alignment convention: Groundwater observations are recorded at 06:00 AM IST.
        # To strictly prevent same-day leakage (rainfall occurring between 06:00 AM and 23:59 IST on obs_date),
        # antecedent rainfall lookback windows end on (obs_date - 1 day).
        # For an exact N-day window [obs_date - N, obs_date - 1], the count of inclusive calendar days is:
        # (obs_date - 1) - (obs_date - N) + 1 = N days.
        end_idx = obs_date - datetime.timedelta(days=1)
        start_30 = obs_date - datetime.timedelta(days=30)
        start_60 = obs_date - datetime.timedelta(days=60)
        start_90 = obs_date - datetime.timedelta(days=90)
        start_180 = obs_date - datetime.timedelta(days=180)
        start_365 = obs_date - datetime.timedelta(days=365)
        
        sub_30 = rf_series.loc[start_30:end_idx]
        sub_60 = rf_series.loc[start_60:end_idx]
        sub_90 = rf_series.loc[start_90:end_idx]
        sub_180 = rf_series.loc[start_180:end_idx]
        sub_365 = rf_series.loc[start_365:end_idx]

        # Verify window length exactness
        assert len(sub_30) == 30, f"Expected 30 days, got {len(sub_30)} for {obs_date}"
        assert len(sub_60) == 60, f"Expected 60 days, got {len(sub_60)} for {obs_date}"
        assert len(sub_90) == 90, f"Expected 90 days, got {len(sub_90)} for {obs_date}"
        assert len(sub_180) == 180, f"Expected 180 days, got {len(sub_180)} for {obs_date}"
        assert len(sub_365) == 365, f"Expected 365 days, got {len(sub_365)} for {obs_date}"
        
        rain_30d = sub_30.sum() if len(sub_30) > 0 else np.nan
        rain_60d = sub_60.sum() if len(sub_60) > 0 else np.nan
        rain_90d = sub_90.sum() if len(sub_90) > 0 else np.nan
        rain_180d = sub_180.sum() if len(sub_180) > 0 else np.nan
        rain_365d = sub_365.sum() if len(sub_365) > 0 else np.nan
        
        rain_dry_days_30d = (sub_30 < 0.1).sum() if len(sub_30) > 0 else np.nan
        rain_max_1d_30d = sub_30.max() if len(sub_30) > 0 else np.nan
        
        # Season identification
        m = row['date'].month
        if m in [4, 5]:
            season_tag = 'Pre-Monsoon (May)'
            season_code = 1
        elif m in [6, 7, 8]:
            season_tag = 'Monsoon (Aug)'
            season_code = 2
        elif m in [9, 10, 11]:
            season_tag = 'Post-Monsoon (Nov)'
            season_code = 3
        else: # 12, 1, 2, 3
            season_tag = 'Rabi/Winter (Jan)'
            season_code = 4
            
        is_extrap = int(stations.loc[stations['Station'] == st_name, 'is_rainfall_extrapolated'].values[0])

        records.append({
            'station': st_name,
            'latitude': row['Latitude'],
            'longitude': row['Longitude'],
            'date': row['date'].strftime('%Y-%m-%d'),
            'year': row['date'].year,
            'month': row['date'].month,
            'day': row['date'].day,
            'quarter': (row['date'].month - 1) // 3 + 1,
            'season_tag': season_tag,
            'season_code': season_code,
            'gw_level_mbgl': row['gw_level_mbgl'],
            'is_overflow': row['is_overflow'],
            'is_rainfall_extrapolated': is_extrap,
            'rain_30d': round(rain_30d, 2),
            'rain_60d': round(rain_60d, 2),
            'rain_90d': round(rain_90d, 2),
            'rain_180d': round(rain_180d, 2),
            'rain_365d': round(rain_365d, 2),
            'rain_dry_days_30d': rain_dry_days_30d,
            'rain_max_1d_30d': round(rain_max_1d_30d, 2)
        })
        
    df_features = pd.DataFrame(records)
    
    # Compute station-level temporal lags and forward target (lead)
    print("--- 4. Computing Lags & Next-Observation Target ---")
    df_features['date_dt'] = pd.to_datetime(df_features['date'])
    df_features = df_features.sort_values(by=['station', 'date_dt']).reset_index(drop=True)
    
    # Lag 1 (previous measured level at this station)
    df_features['gw_level_lag1'] = df_features.groupby('station')['gw_level_mbgl'].shift(1)
    df_features['gw_level_lag2'] = df_features.groupby('station')['gw_level_mbgl'].shift(2)
    
    # Days elapsed since previous observation (known at observation time)
    df_features['days_since_prev_obs'] = (
        df_features['date_dt'] - df_features.groupby('station')['date_dt'].shift(1)
    ).dt.days
    
    # Forward target: gw_level_next (for forecasting the next recorded observation)
    df_features['gw_level_next'] = df_features.groupby('station')['gw_level_mbgl'].shift(-1)
    df_features['target_date'] = df_features.groupby('station')['date'].shift(-1)
    df_features['days_to_next_obs'] = (
        df_features.groupby('station')['date_dt'].shift(-1) - df_features['date_dt']
    ).dt.days
    
    df_features.drop(columns=['date_dt'], inplace=True)
    
    # Save processed features
    out_path = "data/processed/purandar_groundwater_features.csv"
    df_features.to_csv(out_path, index=False)
    print(f"\nSaved processed analytical dataset: {out_path} ({df_features.shape[0]} rows, {df_features.shape[1]} cols)")
    
    # Print sample
    print("\nFeature Summary:")
    print(df_features[['gw_level_mbgl', 'rain_30d', 'rain_90d', 'rain_365d', 'gw_level_lag1']].describe())
    
    # Check Pearson correlation with groundwater depth
    corr = df_features[['gw_level_mbgl', 'rain_30d', 'rain_60d', 'rain_90d', 'rain_180d', 'rain_365d', 'gw_level_lag1']].corr()
    print("\nCorrelation Matrix with gw_level_mbgl (MBGL):")
    print(corr['gw_level_mbgl'])

if __name__ == '__main__':
    engineer_features()
