"""Matplotlib chart components styled for Aqua Intelligence themes."""
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from styles.theme import get_theme_palette


def render_rainfall_groundwater_chart(df: pd.DataFrame, theme: str = "light") -> None:
    """Render dual-axis chart showing 365d antecedent rainfall vs groundwater level."""
    palette = get_theme_palette(theme)
    annual_summary = df.groupby('year').agg({
        'gw_level_mbgl': 'mean',
        'rain_365d': 'mean'
    }).reset_index()
    
    fig, ax1 = plt.subplots(figsize=(6.4, 3.9), dpi=115)
    
    # Theme-adaptive background & spines
    fig.patch.set_facecolor(palette['bg_surface'])
    ax1.set_facecolor(palette['bg_secondary'])
    for spine in ax1.spines.values():
        spine.set_color(palette['border'])
        
    color_rain = palette['teal_accent']
    ax1.set_xlabel('Calendar Year', fontsize=8.5, color=palette['text_primary'], labelpad=6)
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
    ax1.tick_params(axis='x', labelcolor=palette['text_secondary'], labelsize=8)
    ax1.grid(True, linestyle=':', alpha=0.55, color=palette['border'])
    
    # Groundwater Line (Right Inverted Axis)
    ax2 = ax1.twinx()
    for spine in ax2.spines.values():
        spine.set_color(palette['border'])
        
    color_gw = palette['blue_accent']
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
    ax2.invert_yaxis()
    
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    
    st.caption(
        "ℹ️ *Methodological Note: Rainfall bars represent the station-averaged 365-day cumulative antecedent precipitation lookbacks "
        "preceding observation dates in each calendar year. Water table fluctuations reflect net dynamic hydrological balance "
        "(precipitation infiltration, baseflow, and seasonal agricultural pumping extraction), rather than natural recharge alone.*"
    )


def render_station_history_chart(station_df: pd.DataFrame, station_name: str, theme: str = "light") -> None:
    """Render historical water table fluctuation time series for a single monitoring well."""
    palette = get_theme_palette(theme)
    fig, ax = plt.subplots(figsize=(10, 3.8), dpi=115)
    
    fig.patch.set_facecolor(palette['bg_surface'])
    ax.set_facecolor(palette['bg_secondary'])
    for spine in ax.spines.values():
        spine.set_color(palette['border'])
        
    color_line = palette['blue_accent']
    ax.plot(
        station_df['date'], 
        station_df['gw_level_mbgl'], 
        color=color_line, 
        marker='o', 
        markersize=3, 
        label='Observed Level (MBGL)', 
        linewidth=1.8
    )
    
    ax.set_ylabel("Depth Below Ground Level (m MBGL)\n[Shallower ↑ / Deeper ↓]", color=palette['text_primary'], fontsize=8.5)
    ax.set_xlabel("Year", color=palette['text_primary'], fontsize=8.5)
    ax.tick_params(axis='both', labelcolor=palette['text_secondary'], labelsize=8)
    ax.grid(True, linestyle='--', alpha=0.5, color=palette['border'])
    
    # Reference thresholds
    ax.axhline(4.0, color='#10B981', linestyle=':', label='Shallow Reference Band (<4m)')
    ax.axhline(8.0, color='#EF4444', linestyle=':', label='Deep Reference Band (>8m)')
    ax.invert_yaxis()
    
    leg = ax.legend(loc='lower left', facecolor=palette['bg_surface'], edgecolor=palette['border'])
    for text in leg.get_texts():
        text.set_color(palette['text_primary'])
        
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
