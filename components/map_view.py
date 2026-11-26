"""Interactive Leaflet map component with telemetry markers, rich popups, and reset controls."""
import json
import pandas as pd
import streamlit.components.v1 as components
from services.data_loader import get_status


def render_groundwater_map(
    filtered_stations: pd.DataFrame, 
    selected_station: str | None = None,
    center: tuple[float, float] = (18.28, 74.12), 
    zoom: int = 11, 
    theme: str = "light"
) -> None:
    """Render interactive Leaflet map with fixed circle markers, rich telemetry popups,
    hover tooltips, and interactive reset controls.
    """
    stations_json = []
    
    # Filter for valid numeric coordinates only
    valid_stations = filtered_stations.dropna(subset=['latitude', 'longitude']).copy()
    valid_stations = valid_stations[
        (valid_stations['latitude'] != 0) & (valid_stations['longitude'] != 0)
    ]

    for _, row in valid_stations.iterrows():
        status, color, _ = get_status(row['gw_level_mbgl'])
        depth = float(row['gw_level_mbgl'])
        date_str = row['date'].strftime('%d-%b-%Y')
        
        # Previous survey telemetry
        prev_depth = row.get('prev_gw_level_mbgl')
        prev_date = row.get('prev_date')
        change = row.get('depth_change_m')
        days = row.get('days_elapsed')
        
        prev_depth_str = f"{prev_depth:.2f} m" if pd.notnull(prev_depth) else "—"
        prev_date_str = prev_date.strftime('%d-%b-%Y') if pd.notnull(prev_date) else "—"
        
        # Change interpretation
        is_zendewadi = (row['station'] == 'Zendewadi')
        flag = " ⚠️" if is_zendewadi else ""
        if pd.isna(change):
            change_str = "— (Single record)"
            interpretation = "Single historical observation recorded in dataset; no prior survey available."
        elif change > 0:
            change_str = f"+{change:.2f} m (Deeper){flag}"
            interpretation = f"Water table deepened by +{change:.2f} m (water level fell) compared to previous historical observation."
        elif change < 0:
            change_str = f"{change:.2f} m (Shallower){flag}"
            interpretation = f"Water table became shallower by {abs(change):.2f} m (water level rose) compared to previous historical observation."
        else:
            change_str = f"0.00 m (Unchanged){flag}"
            interpretation = "Water table depth remained unchanged between observations."

        if pd.isna(days) or days is None:
            elapsed_str = "—"
        else:
            days_int = int(days)
            if is_zendewadi or days_int >= 2000:
                elapsed_str = f"{days_int:,} days ⚠️ (6.0-yr gap)"
                interpretation += " ⚠️ Spans 2,206-day (6.0-yr) observation gap."
            elif days_int > 365:
                yrs = days_int / 365.25
                elapsed_str = f"{days_int} days ({yrs:.1f}-yr gap)"
            else:
                elapsed_str = f"{days_int} days"

        is_selected = (selected_station is not None and str(row['station']) == selected_station)

        is_extrapolated = bool(row.get('is_rainfall_extrapolated', 0))
        if is_extrapolated:
            extrap_notice_html = (
                '<div class="popup-alert alert-warn"><span>⚠️</span>'
                '<div><b>Rainfall Lookback:</b> Station is outside the four-point rainfall grid spatial coverage; '
                'rainfall estimates require spatial inverse-distance weighting extrapolation.</div></div>'
            )
        else:
            extrap_notice_html = (
                '<div class="popup-alert alert-succ"><span>✓</span>'
                '<div><b>Rainfall Lookback:</b> Station is within the four-point rainfall grid spatial coverage; '
                'rainfall estimates interpolated from adjacent grid points.</div></div>'
            )

        stations_json.append({
            'name': str(row['station']),
            'lat': float(row['latitude']),
            'lon': float(row['longitude']),
            'depth': depth,
            'status': status,
            'color': color,
            'date': date_str,
            'season': str(row.get('season_tag', '—')),
            'prev_depth': prev_depth_str,
            'prev_date': prev_date_str,
            'change': change_str,
            'elapsed': elapsed_str,
            'interpretation': interpretation,
            'is_extrapolated': is_extrapolated,
            'extrap_notice': extrap_notice_html,
            'is_selected': is_selected
        })
        
    is_dark = (theme == "dark")
    map_border = "#23414B" if is_dark else "#DCE6E2"
    map_bg = "#0B2029" if is_dark else "#F5F7F4"
    
    popup_bg = "#102A35" if is_dark else "#FFFFFF"
    popup_text = "#EAF6F7" if is_dark else "#24343A"
    popup_muted = "#A5BEC5" if is_dark else "#647579"
    popup_border = "#23414B" if is_dark else "#DCE6E2"
    popup_close = "#A5BEC5" if is_dark else "#647579"
    
    alert_warn_bg = "rgba(245, 158, 11, 0.16)" if is_dark else "#FDF6ED"
    alert_warn_border = "#F59E0B" if is_dark else "#D99A45"
    alert_warn_text = "#FDE68A" if is_dark else "#8C5B17"
    
    alert_succ_bg = "rgba(16, 185, 129, 0.16)" if is_dark else "#D8EEE8"
    alert_succ_border = "#10B981" if is_dark else "#168C83"
    alert_succ_text = "#A7F3D0" if is_dark else "#168C83"

    marker_stroke = "#0B2029" if is_dark else "#FFFFFF"
    selected_stroke = "#35D0C1" if is_dark else "#123B46"
    
    dark_tile_filter = """
        .leaflet-tile-pane {
            filter: brightness(0.7) invert(1) contrast(2.6) hue-rotate(200deg) saturate(0.35) brightness(0.9);
        }
    """ if is_dark else ""
    
    leaflet_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            * {{
                box-sizing: border-box;
            }}
            body {{
                margin: 0;
                padding: 0;
                background-color: {map_bg};
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }}
            #map {{ 
                height: 560px; 
                width: 100%; 
                border-radius: 10px; 
                border: 1px solid {map_border}; 
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.10); 
                background-color: {map_bg};
            }}
            {dark_tile_filter}
            
            /* Styled Leaflet Popups */
            .leaflet-popup-content-wrapper {{
                background: {popup_bg} !important;
                color: {popup_text} !important;
                border-radius: 9px !important;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25) !important;
                border: 1px solid {popup_border} !important;
                padding: 0 !important;
                overflow: hidden !important;
            }}
            .leaflet-popup-content {{
                margin: 13px 15px !important;
                line-height: 1.45 !important;
                font-size: 12.5px !important;
            }}
            .leaflet-popup-tip {{
                background: {popup_bg} !important;
                border: 1px solid {popup_border} !important;
                box-shadow: none !important;
            }}
            .leaflet-container a.leaflet-popup-close-button {{
                color: {popup_close} !important;
                padding: 6px 8px 0 0 !important;
                font-size: 16px !important;
                font-weight: normal !important;
            }}
            .leaflet-container a.leaflet-popup-close-button:hover {{
                color: {popup_text} !important;
            }}

            /* Popup internal card layout */
            .popup-card {{
                min-width: 235px;
                max-width: 295px;
            }}
            .popup-eyebrow {{
                font-size: 9px;
                color: {popup_muted};
                text-transform: uppercase;
                letter-spacing: 0.06em;
                font-weight: 700;
                margin-bottom: 2px;
            }}
            .popup-title {{
                font-size: 15px;
                font-weight: 700;
                color: {popup_text};
                margin-bottom: 7px;
                padding-bottom: 5px;
                border-bottom: 1px solid {popup_border};
            }}
            .popup-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 4px;
                font-size: 12px;
            }}
            .popup-lbl {{
                color: {popup_muted};
            }}
            .popup-val {{
                color: {popup_text};
                font-weight: 600;
            }}
            .popup-tier-tag {{
                display: inline-block;
                padding: 1px 7px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 700;
            }}
            .popup-interpretation {{
                margin-top: 7px;
                padding: 6px 8px;
                background: {"rgba(53, 208, 193, 0.08)" if is_dark else "rgba(22, 140, 131, 0.08)"};
                border-left: 3px solid {"#35D0C1" if is_dark else "#168C83"};
                border-radius: 4px;
                font-size: 11px;
                color: {popup_text};
                line-height: 1.35;
            }}
            .popup-alert {{
                margin-top: 6px;
                padding: 5px 7px;
                border-radius: 4px;
                font-size: 10.5px;
                line-height: 1.35;
                display: flex;
                gap: 5px;
                align-items: flex-start;
            }}
            .alert-warn {{
                background-color: {alert_warn_bg};
                border-left: 3px solid {alert_warn_border};
                color: {alert_warn_text};
            }}
            .alert-succ {{
                background-color: {alert_succ_bg};
                border-left: 3px solid {alert_succ_border};
                color: {alert_succ_text};
            }}
            .popup-footer {{
                margin-top: 7px;
                font-size: 10px;
                color: {popup_muted};
                border-top: 1px dashed {popup_border};
                padding-top: 5px;
                font-style: italic;
            }}

            /* Hover Tooltips */
            .station-map-tooltip {{
                background: {popup_bg} !important;
                color: {popup_text} !important;
                border: 1px solid {popup_border} !important;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.18) !important;
                border-radius: 6px !important;
                font-size: 11.5px !important;
                padding: 3px 7px !important;
                font-weight: 500 !important;
            }}
            .station-map-tooltip::before {{
                border-top-color: {popup_border} !important;
            }}

            /* Custom Reset View Control Button */
            .leaflet-control-custom a {{
                background-color: {popup_bg} !important;
                color: {popup_text} !important;
                width: 30px !important;
                height: 30px !important;
                line-height: 30px !important;
                text-align: center !important;
                font-size: 16px !important;
                cursor: pointer !important;
                border-bottom: none !important;
            }}
            .leaflet-control-custom a:hover {{
                background-color: {"#163745" if is_dark else "#F0F5F2"} !important;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map', {{
                scrollWheelZoom: true
            }}).setView([{center[0]}, {center[1]}], {zoom});

            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 18,
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);

            var stations = {json.dumps(stations_json)};
            var markerList = [];
            var selectedMarker = null;

            stations.forEach(function(st) {{
                var radiusSize = st.is_selected ? 11.0 : 8.5;
                var markerWeight = st.is_selected ? 3.0 : 2.2;
                var strokeColor = st.is_selected ? '{selected_stroke}' : '{marker_stroke}';

                var marker = L.circleMarker([st.lat, st.lon], {{
                    radius: radiusSize,
                    fillColor: st.color,
                    color: strokeColor,
                    weight: markerWeight,
                    opacity: 1,
                    fillOpacity: 0.95
                }}).addTo(map);

                marker.bindTooltip(
                    '<b>' + st.name + '</b>: ' + st.depth.toFixed(2) + ' m MBGL',
                    {{
                        className: 'station-map-tooltip',
                        direction: 'top',
                        offset: [0, -9]
                    }}
                );

                marker.on('mouseover', function() {{
                    if (!st.is_selected) this.setRadius(10.5);
                }});
                marker.on('mouseout', function() {{
                    if (!st.is_selected) this.setRadius(8.5);
                }});

                var popupContent = `
                    <div class="popup-card">
                        <div class="popup-eyebrow">Observed CGWB Telemetry</div>
                        <div class="popup-title">${{st.name}}</div>
                        <div class="popup-row">
                            <span class="popup-lbl">Latest Depth:</span>
                            <span class="popup-val"><b>${{st.depth.toFixed(2)}} m</b> MBGL</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-lbl">Reference Tier:</span>
                            <span class="popup-tier-tag" style="color: ${{st.color}}; background: ${{st.color}}1A;">${{st.status}}</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-lbl">Observation Date:</span>
                            <span class="popup-val">${{st.date}}</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-lbl">Previous Survey:</span>
                            <span class="popup-val">${{st.prev_depth}} (${{st.prev_date}})</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-lbl">Observed Change:</span>
                            <span class="popup-val">${{st.change}}</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-lbl">Elapsed Time:</span>
                            <span class="popup-val">${{st.elapsed}}</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-lbl">Coordinates:</span>
                            <span class="popup-val">${{st.lat.toFixed(4)}}°N, ${{st.lon.toFixed(4)}}°E</span>
                        </div>
                        <div class="popup-interpretation">
                            ${{st.interpretation}}
                        </div>
                        ${{st.extrap_notice}}
                        <div class="popup-footer">
                            Historical in-situ manual CGWB observation, not live telemetry. Higher MBGL = deeper water table.
                        </div>
                    </div>
                `;
                marker.bindPopup(popupContent, {{
                    maxWidth: 300,
                    className: 'custom-cgwb-popup'
                }});

                if (st.is_selected) {{
                    selectedMarker = marker;
                }}
                markerList.push(marker);
            }});

            // Add Custom Reset Map View Button (Top-Left)
            var ResetControl = L.Control.extend({{
                options: {{ position: 'topleft' }},
                onAdd: function(map) {{
                    var container = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
                    container.innerHTML = '<a href="#" role="button" title="Reset Map View" style="display:flex;align-items:center;justify-content:center;">⟲</a>';
                    container.onclick = function(e) {{
                        e.preventDefault();
                        if (markerList.length > 0) {{
                            var networkGroup = L.featureGroup(markerList);
                            map.fitBounds(networkGroup.getBounds(), {{
                                padding: [45, 45],
                                maxZoom: 12
                            }});
                        }}
                    }};
                    return container;
                }}
            }});
            map.addControl(new ResetControl());

            // Center on selected station or set default network view
            if (selectedMarker) {{
                map.setView(selectedMarker.getLatLng(), 13);
                setTimeout(function() {{
                    map.invalidateSize();
                    selectedMarker.openPopup();
                }}, 250);
            }} else {{
                if (markerList.length > 0) {{
                    var networkGroup = L.featureGroup(markerList);
                    map.fitBounds(networkGroup.getBounds(), {{
                        padding: [45, 45],
                        maxZoom: 12
                    }});
                }}
                setTimeout(function() {{
                    map.invalidateSize();
                }}, 200);
            }}
        </script>
    </body>
    </html>
    """
    components.html(leaflet_html, height=575)
