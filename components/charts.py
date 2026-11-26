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
    ax.axhline(4.0, color='#168C83', linestyle='--', linewidth=1.1, label='Shallow Band (< 4.0 m)')
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


def render_rainfall_groundwater_chart(
    df: pd.DataFrame, 
    window_col: str = "rain_365d", 
    theme: str = "light"
) -> None:
    """Render dual-axis chart showing antecedent rainfall vs groundwater level."""
    palette = get_theme_palette(theme)
    window_labels = {
        "rain_90d": "Preceding 90-Day Rainfall",
        "rain_180d": "Preceding 180-Day Rainfall",
        "rain_365d": "Preceding 365-Day Rainfall",
    }
    label_text = window_labels.get(window_col, "Preceding Rainfall")
    
    # Defensive check for window_col presence
    actual_col = window_col if window_col in df.columns else "rain_365d"
    
    annual_summary = df.groupby('year').agg({
        'gw_level_mbgl': 'mean',
        actual_col: 'mean'
    }).reset_index()
    
    fig, ax1 = plt.subplots(figsize=(10.5, 3.8), dpi=120)
    
    # Theme-adaptive background & spines
    fig.patch.set_facecolor(palette['bg_surface'])
    ax1.set_facecolor(palette['bg_secondary'])
    for spine in ax1.spines.values():
        spine.set_color(palette['border'])
        
    color_rain = palette['teal_accent']
    ax1.set_xlabel('Calendar Year', fontsize=8.8, color=palette['text_primary'], labelpad=6)
    ax1.set_ylabel(f'Mean {label_text} (mm)', color=color_rain, fontsize=8.8, labelpad=8)
    bars = ax1.bar(
        annual_summary['year'], 
        annual_summary[actual_col], 
        color=color_rain, 
        alpha=0.45, 
        edgecolor=color_rain, 
        linewidth=0.8,
        width=0.68, 
        label=f'{label_text} (mm, left axis)'
    )
    ax1.tick_params(axis='y', labelcolor=color_rain, labelsize=8.2)
    ax1.tick_params(axis='x', labelcolor=palette['text_secondary'], labelsize=8.2)
    ax1.grid(True, linestyle=':', alpha=0.50, color=palette['border'])
    
    years = [y for y in range(1996, 2024, 2)]
    ax1.set_xticks(years)
    ax1.set_xlim(1995.2, 2023.8)
    
    # Groundwater Line (Right Inverted Axis)
    ax2 = ax1.twinx()
    for spine in ax2.spines.values():
        spine.set_color(palette['border'])
        
    color_gw = palette['blue_accent']
    ax2.set_ylabel('Mean Groundwater Depth (m MBGL)\n[Shallower ↑ / Deeper ↓]', color=color_gw, fontsize=8.8, labelpad=8)
    line = ax2.plot(
        annual_summary['year'], 
        annual_summary['gw_level_mbgl'], 
        color=color_gw, 
        linewidth=2.2, 
        marker='o', 
        markersize=4.2, 
        label='Mean Water Table Depth (m MBGL, right inverted axis)'
    )
    ax2.tick_params(axis='y', labelcolor=color_gw, labelsize=8.2)
    ax2.invert_yaxis()
    
    # Combined legend above plot area
    handles = [bars, line[0]]
    labels = [f'{label_text} (mm, left axis)', 'Groundwater Depth (m MBGL, right inverted axis)']
    leg = ax1.legend(
        handles, labels,
        loc='upper center',
        bbox_to_anchor=(0.5, 1.18),
        ncol=2,
        fontsize=8.0,
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
        f"ℹ️ *Annual historical comparison (1996–2023). Bars depict the station-averaged {label_text.lower()} "
        "accumulated prior to observation dates in each calendar year. Line depicts the regional mean in-situ groundwater depth (inverted axis: top is shallower).* "
    )


def render_station_history_chart(
    station_df: pd.DataFrame, 
    station_name: str,
    pred_val: float | None = None,
    lower_b: float | None = None,
    upper_b: float | None = None,
    pred_date: pd.Timestamp | None = None,
    scenario_val: float | None = None,
    rain_factor: int = 0,
    theme: str = "light"
) -> None:
    """Render historical water table fluctuation time series for a single monitoring well,
    with distinct machine-learning next-observation forecast and uncalibrated prediction bands.
    """
    palette = get_theme_palette(theme)
    fig, ax = plt.subplots(figsize=(10.5, 4.2), dpi=120)
    
    # Theme-adaptive background & spines
    fig.patch.set_facecolor(palette['bg_surface'])
    ax.set_facecolor(palette['bg_secondary'])
    for spine in ax.spines.values():
        spine.set_color(palette['border'])
        
    sorted_df = station_df.sort_values('date').copy()
    color_line = palette['blue_accent']
    
    # 1. Historical Observed Readings
    ax.plot(
        sorted_df['date'], 
        sorted_df['gw_level_mbgl'], 
        color=color_line, 
        marker='o', 
        markersize=3.6, 
        label='Observed In-Situ Level (CGWB)', 
        linewidth=1.9,
        zorder=3
    )
    
    # 2. Predicted Next Observation (if available)
    if pred_val is not None and not sorted_df.empty:
        last_date = sorted_df['date'].iloc[-1]
        last_val = float(sorted_df['gw_level_mbgl'].iloc[-1])
        
        # If prediction date not provided, estimate using median horizon (~92 days)
        if pred_date is None:
            pred_date = last_date + pd.Timedelta(days=92)
            
        color_pred = '#D99A45' if theme == 'light' else '#F59E0B'
        
        # A. Dashed trajectory connector from latest observation to next prediction
        ax.plot(
            [last_date, pred_date], 
            [last_val, pred_val], 
            color=color_pred, 
            linestyle='--', 
            linewidth=1.9, 
            label='Forecast Step (Next Observation)',
            zorder=4
        )
        
        # B. Uncalibrated q10–q90 Prediction Band Error Bar
        if lower_b is not None and upper_b is not None:
            yerr_lower = max(0.0, pred_val - lower_b)
            yerr_upper = max(0.0, upper_b - pred_val)
            ax.errorbar(
                [pred_date], 
                [pred_val], 
                yerr=[[yerr_lower], [yerr_upper]], 
                fmt='none', 
                ecolor='#B87A28' if theme == 'light' else '#FBBF24', 
                elinewidth=2.2, 
                capsize=5, 
                capthick=1.8, 
                alpha=0.90, 
                label=f'Uncalibrated q10–q90 Band ({lower_b:.2f}–{upper_b:.2f} m)',
                zorder=4
            )
            
        # C. Distinct Diamond Marker for Point Estimate
        ax.plot(
            [pred_date], 
            [pred_val], 
            marker='D', 
            markersize=8.0, 
            color=color_pred, 
            markeredgecolor=palette['text_primary'], 
            markeredgewidth=1.2, 
            label=f'Predicted Next Obs: {pred_val:.2f} m MBGL',
            zorder=6
        )
        
        # D. Informative Annotation Callout
        diff = pred_val - last_val
        direction_txt = "Deeper" if diff > 0.05 else ("Shallower" if diff < -0.05 else "Stable")
        annot_text = f"Predicted Next Obs\n{pred_val:.2f} m MBGL ({diff:+.2f} m {direction_txt})\nest. {pred_date.strftime('%b %Y')}"
        y_offset = -24 if pred_val < last_val else 22
        ax.annotate(
            annot_text,
            xy=(pred_date, pred_val),
            xytext=(14, y_offset),
            textcoords='offset points',
            fontsize=7.8,
            fontweight='600',
            color=palette['text_primary'],
            bbox=dict(
                boxstyle='round,pad=0.35', 
                facecolor=palette['bg_surface'], 
                edgecolor=color_pred, 
                alpha=0.92,
                linewidth=1.1
            ),
            arrowprops=dict(
                arrowstyle='->', 
                connectionstyle='arc3,rad=0.15', 
                color=color_pred, 
                lw=1.2
            ),
            zorder=7
        )
        
        # E. Simulated Scenario Marker (if rainfall factor != 0 and scenario provided)
        if scenario_val is not None and rain_factor != 0:
            color_scen = '#168C83' if theme == 'light' else '#2DD4BF'
            ax.plot(
                [last_date, pred_date], 
                [last_val, scenario_val], 
                color=color_scen, 
                linestyle=':', 
                linewidth=1.7, 
                label=f'Simulated ({rain_factor:+d}% Rain)',
                zorder=4
            )
            ax.plot(
                [pred_date], 
                [scenario_val], 
                marker='s', 
                markersize=7.5, 
                color=color_scen, 
                markeredgecolor=palette['text_primary'], 
                markeredgewidth=1.1, 
                label=f'Simulated Scenario: {scenario_val:.2f} m MBGL',
                zorder=6
            )
    
    # 3. Project-Defined Physical Depth Reference Lines
    ax.axhline(4.0, color='#168C83', linestyle=':', linewidth=1.2, label='Shallow Reference (< 4.0 m)')
    ax.axhline(8.0, color='#EF4444', linestyle=':', linewidth=1.2, label='Deep Reference (> 8.0 m)')
    
    # 4. MBGL Axis Orientation: Inverted (0 at surface, deeper at bottom)
    ax.invert_yaxis()
    
    ax.set_ylabel("Depth Below Ground Level (m MBGL)\n[Shallower ↑ / Deeper ↓]", color=palette['text_primary'], fontsize=8.6, labelpad=8)
    ax.set_xlabel("Survey Date / Historical Timeline", color=palette['text_primary'], fontsize=8.6, labelpad=6)
    ax.tick_params(axis='both', labelcolor=palette['text_secondary'], labelsize=8.2)
    ax.grid(True, linestyle='--', alpha=0.45, color=palette['border'])
    
    # 5. Clean Theme-Aware Multi-Column Legend
    leg = ax.legend(
        loc='lower left', 
        ncol=2,
        fontsize=7.8,
        facecolor=palette['bg_surface'], 
        edgecolor=palette['border'],
        framealpha=0.92
    )
    for text in leg.get_texts():
        text.set_color(palette['text_primary'])
        
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_seasonal_comparison_chart(yearly_summary: pd.DataFrame, theme: str = "light") -> None:
    """Render May (Pre-Monsoon) vs November (Post-Monsoon) paired groundwater comparison chart."""
    palette = get_theme_palette(theme)
    fig, ax = plt.subplots(figsize=(10.5, 3.6), dpi=120)
    
    # Theme-adaptive background & spines
    fig.patch.set_facecolor(palette['bg_surface'])
    ax.set_facecolor(palette['bg_secondary'])
    for spine in ax.spines.values():
        spine.set_color(palette['border'])
        
    color_may = '#E67E22' if theme == 'dark' else '#D99A45'
    color_nov = palette['teal_accent']
    color_fill = palette['blue_accent']
    
    # Fill between May and Nov to show the net seasonal rise
    ax.fill_between(
        yearly_summary['year'],
        yearly_summary['may_mean'],
        yearly_summary['nov_mean'],
        color=color_fill,
        alpha=0.22,
        label='Seasonal Water-Table Rise'
    )
    
    # May line (Pre-Monsoon)
    ax.plot(
        yearly_summary['year'],
        yearly_summary['may_mean'],
        color=color_may,
        linewidth=2.0,
        marker='o',
        markersize=4.5,
        label='Pre-Monsoon (May Mean MBGL)'
    )
    
    # November line (Post-Monsoon)
    ax.plot(
        yearly_summary['year'],
        yearly_summary['nov_mean'],
        color=color_nov,
        linewidth=2.0,
        marker='s',
        markersize=4.5,
        label='Post-Monsoon (Nov Mean MBGL)'
    )
    
    # Project-defined reference depth bands
    ax.axhline(4.0, color='#168C83', linestyle='--', linewidth=1.1, alpha=0.75, label='Shallow Band (< 4.0 m)')
    ax.axhline(8.0, color='#EF4444', linestyle='--', linewidth=1.1, alpha=0.75, label='Deep Band (> 8.0 m)')
    
    ax.set_ylabel("Groundwater Depth (m MBGL)\n[Shallower ↑ / Deeper ↓]", color=palette['text_primary'], fontsize=8.8, labelpad=8)
    ax.set_xlabel("Calendar Year (Matched Observations)", color=palette['text_primary'], fontsize=8.8, labelpad=6)
    ax.tick_params(axis='both', labelcolor=palette['text_secondary'], labelsize=8.2)
    ax.grid(True, linestyle='--', alpha=0.45, color=palette['border'])
    
    # Set 2-year ticks across the historical span
    years = [y for y in range(1996, 2024, 2)]
    ax.set_xticks(years)
    ax.set_xlim(1995.5, 2022.5)
    
    # Invert Y-axis so shallower water is at the top
    ax.invert_yaxis()
    
    leg = ax.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.18),
        ncol=5,
        fontsize=7.8,
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
        "ℹ️ *Pre-Monsoon (May) vs Post-Monsoon (November) annual mean water table depths across strictly matched station-year observations (n=137 pairs, 1996–2022). "
        "The shaded band depicts net seasonal water-table elevation gain following monsoon infiltration.*"
    )
