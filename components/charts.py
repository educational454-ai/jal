"""Matplotlib chart components styled for Aqua Intelligence themes."""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import streamlit as st
from styles.theme import get_theme_palette


def render_regional_groundwater_chart(
    df: pd.DataFrame, 
    station_filter: str = "All Stations (Regional Mean Trend)", 
    theme: str = "light"
) -> None:
    """Render full-width primary groundwater observation chart across 1996–2023."""
    palette = get_theme_palette(theme)
    fig, ax = plt.subplots(figsize=(11.0, 3.4), dpi=120)
    
    # Theme-adaptive background & spines
    fig.patch.set_facecolor(palette['bg_surface'])
    ax.set_facecolor(palette['bg_secondary'])
    for spine in ax.spines.values():
        spine.set_color(palette['border'])

    # Ensure datetime format for reliable time-axis plotting
    plot_df = df.copy()
    plot_df['date'] = pd.to_datetime(plot_df['date'])

    # Group by discrete survey observation dates (104 rounds across 1996–2023)
    agg_dates = plot_df.groupby('date')['gw_level_mbgl'].agg(['mean', 'min', 'max', 'count']).reset_index()

    # Regional Min-Max observation envelope
    ax.fill_between(
        agg_dates['date'],
        agg_dates['min'],
        agg_dates['max'],
        color=palette['blue_accent'],
        alpha=0.18,
        label='Spread (Min–Max)'
    )

    if station_filter == "All Stations (Regional Mean Trend)":
        # Individual station soundings as subtle scatter (n=680 discrete measurements)
        ax.scatter(
            plot_df['date'],
            plot_df['gw_level_mbgl'],
            color=palette['text_secondary'],
            alpha=0.32,
            s=13,
            edgecolors='none',
            label='Soundings (n=680)'
        )
        # Regional mean line connecting discrete survey rounds
        ax.plot(
            agg_dates['date'],
            agg_dates['mean'],
            color=palette['blue_accent'],
            linewidth=2.0,
            marker='o',
            markersize=3.2,
            label='Regional Survey Mean'
        )
    else:
        # Single station selected
        st_data = plot_df[plot_df['station'] == station_filter].sort_values('date')
        # Background regional mean as subtle dashed reference line
        ax.plot(
            agg_dates['date'],
            agg_dates['mean'],
            color=palette['text_secondary'],
            linewidth=1.2,
            linestyle='--',
            alpha=0.55,
            label='Regional Survey Mean'
        )
        # Station specific soundings & line
        ax.plot(
            st_data['date'],
            st_data['gw_level_mbgl'],
            color=palette['teal_accent'],
            linewidth=2.0,
            marker='o',
            markersize=4.0,
            label=f'{station_filter} Depth'
        )

    # Reference Depth Thresholds (Project-defined physical reference bands)
    ax.axhline(4.0, color='#059669', linestyle='--', linewidth=1.1, label='Shallow Band (< 4.0 m)')
    ax.axhline(8.0, color='#DC2626', linestyle='--', linewidth=1.1, label='Deep Band (> 8.0 m)')

    ax.set_ylabel("Groundwater Depth (m MBGL)\n[Shallower ↑ / Deeper ↓]", color=palette['text_primary'], fontsize=8.8, labelpad=8)
    ax.set_xlabel("Observation Survey Date", color=palette['text_primary'], fontsize=8.8, labelpad=6)
    ax.tick_params(axis='both', labelcolor=palette['text_secondary'], labelsize=8.2)
    ax.grid(True, linestyle='--', alpha=0.45, color=palette['border'])

    # Format x-axis with 4-year major ticks for clean legibility
    ax.xaxis.set_major_locator(mdates.YearLocator(4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    # Inverted y-axis: shallower water tables closer to top (0 MBGL), deeper closer to bottom
    ax.invert_yaxis()

    # Unobstructed top legend positioned horizontally above plot area
    leg = ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.15),
        ncol=5,
        fontsize=8.0,
        frameon=True,
        facecolor=palette['bg_surface'],
        edgecolor=palette['border'],
        framealpha=0.95
    )
    for text in leg.get_texts():
        text.set_color(palette['text_primary'])

    fig.tight_layout(rect=[0, 0, 1, 0.90])
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.caption(
        "ℹ️ *Historical in-situ manual CGWB observations across 104 discrete survey rounds (1996–2023). "
        "The shaded envelope represents the empirical minimum-to-maximum range across reporting wells on each date; "
        "no daily values are interpolated.*"
    )


def render_compact_rainfall_chart(df: pd.DataFrame, theme: str = "light") -> None:
    """Render compact annual preceding 365d rainfall chart for Screen 1 secondary row."""
    palette = get_theme_palette(theme)
    annual_rain = df.groupby('year')['rain_365d'].mean().reset_index()
    long_term_mean = float(annual_rain['rain_365d'].mean())

    fig, ax = plt.subplots(figsize=(5.8, 3.2), dpi=120)
    fig.patch.set_facecolor(palette['bg_surface'])
    ax.set_facecolor(palette['bg_secondary'])
    for spine in ax.spines.values():
        spine.set_color(palette['border'])

    color_bar = palette['teal_accent']
    ax.bar(
        annual_rain['year'],
        annual_rain['rain_365d'],
        color=color_bar,
        alpha=0.70,
        edgecolor=color_bar,
        linewidth=0.8,
        width=0.72,
        label='Preceding 365d Rain'
    )
    ax.axhline(
        long_term_mean,
        color=palette['text_secondary'],
        linestyle='--',
        linewidth=1.2,
        label=f'Period Mean ({long_term_mean:.0f} mm)'
    )

    ax.set_xlabel('Calendar Year', fontsize=8.8, color=palette['text_primary'], labelpad=5)
    ax.set_ylabel('Preceding 365d Rain (mm)', fontsize=8.8, color=palette['text_primary'], labelpad=6)
    ax.tick_params(axis='both', labelcolor=palette['text_secondary'], labelsize=8.2)
    ax.grid(True, linestyle=':', alpha=0.55, color=palette['border'])
    ax.set_ylim(0, annual_rain['rain_365d'].max() * 1.10)

    # Align 4-year tick marks to match the groundwater observation chart
    years = [y for y in range(1996, 2024, 4)]
    ax.set_xticks(years)

    leg = ax.legend(loc='upper right', fontsize=8.0, facecolor=palette['bg_surface'], edgecolor=palette['border'], framealpha=0.92)
    for text in leg.get_texts():
        text.set_color(palette['text_primary'])

    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.caption("ℹ️ *Preceding 365-day cumulative rainfall lookback averaged across reporting stations per calendar year.*")


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
