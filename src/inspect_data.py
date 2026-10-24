import pandas as pd
import numpy as np
import os
import json

def load_and_inspect():
    gw_path = "data/raw/purandhar_groundwater_level_merged.csv"
    rf_path = "data/raw/purandar_rainfall_1991_2023.csv"
    
    print(f"Loading {gw_path}...")
    df_gw = pd.read_csv(gw_path)
    print(f"Groundwater shape: {df_gw.shape}")
    print(f"Columns: {list(df_gw.columns)}")
    
    print(f"\nLoading {rf_path}...")
    df_rf = pd.read_csv(rf_path)
    print(f"Rainfall shape: {df_rf.shape}")
    print(f"Rainfall columns: {list(df_rf.columns)}")

    # Groundwater details
    target_col = "Groundwater Level Quarterly Manual (meter)"
    print("\n--- Groundwater Summary ---")
    print("Stations count and distribution:")
    print(df_gw['Station'].value_counts())
    
    # Parse dates
    # '05-01-1996 6:00' -> DD-MM-YYYY HH:MM
    df_gw['date'] = pd.to_datetime(df_gw['Data Acquisition Time'], format='%d-%m-%Y %H:%M', errors='coerce')
    # If any NaT, fallback to general parse
    if df_gw['date'].isna().any():
        df_gw['date'] = pd.to_datetime(df_gw['Data Acquisition Time'], dayfirst=True, errors='coerce')
        
    print(f"\nValid date parsed: {df_gw['date'].notna().sum()} / {len(df_gw)}")
    print(f"Date range: {df_gw['date'].min()} to {df_gw['date'].max()}")
    
    print("\nWater Level Stats (MBGL):")
    print(df_gw[target_col].describe())
    
    negative_readings = df_gw[df_gw[target_col] < 0]
    print(f"\nNegative readings count: {len(negative_readings)}")
    if len(negative_readings) > 0:
        print(negative_readings[['Station', 'date', target_col]])

    # Rainfall details
    print("\n--- Rainfall Summary ---")
    df_rf['date'] = pd.to_datetime(df_rf['time'], format='%d-%m-%Y', errors='coerce')
    if df_rf['date'].isna().any():
        df_rf['date'] = pd.to_datetime(df_rf['time'], dayfirst=True, errors='coerce')
    print(f"Rainfall date range: {df_rf['date'].min()} to {df_rf['date'].max()}")
    print("Rainfall Grid Points:")
    print(df_rf.groupby(['latitude', 'longitude']).size())
    print("\nRainfall stats:")
    print(df_rf['rainfall'].describe())

if __name__ == "__main__":
    load_and_inspect()
