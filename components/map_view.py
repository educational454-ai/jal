"""Interactive Leaflet map component with telemetry markers and extrapolation warnings."""
import json
import pandas as pd
import streamlit.components.v1 as components
from services.data_loader import get_status


def render_groundwater_map(
    filtered_stations: pd.DataFrame, 
    center: tuple[float, float] = (18.28, 74.12), 
    zoom: int = 11, 
    theme: str = "light"
) -> None:
    """Render interactive Leaflet map with fixed circle markers and telemetry popups."""
    stations_json = []
    for _, row in filtered_stations.iterrows():
        status, color, _ = get_status(row['gw_level_mbgl'])
        stations_json.append({
            'name': str(row['station']),
            'lat': float(row['latitude']),
            'lon': float(row['longitude']),
            'depth': float(row['gw_level_mbgl']),
            'status': status,
            'color': color,
            'date': row['date'].strftime('%d %b %Y'),
            'season': str(row['season_tag']),
            'is_extrapolated': bool(row.get('is_rainfall_extrapolated', 0))
        })
        
    is_dark = (theme == "dark")
    map_border = "#23414B" if is_dark else "#D9E5E7"
    map_bg = "#0B2029" if is_dark else "#F4F8F8"
    
    popup_bg = "#102A35" if is_dark else "#FFFFFF"
    popup_text = "#EAF6F7" if is_dark else "#17313B"
    popup_muted = "#A5BEC5" if is_dark else "#617780"
    popup_border = "#23414B" if is_dark else "#E2E8F0"
    popup_close = "#A5BEC5" if is_dark else "#64748B"
    
    alert_warn_bg = "rgba(245, 158, 11, 0.16)" if is_dark else "#FEF3C7"
    alert_warn_border = "#F59E0B"
    alert_warn_text = "#FDE68A" if is_dark else "#92400E"
    
    alert_succ_bg = "rgba(16, 185, 129, 0.16)" if is_dark else "#D1FAE5"
    alert_succ_border = "#10B981"
    alert_succ_text = "#A7F3D0" if is_dark else "#065F46"

    marker_stroke = "#0B2029" if is_dark else "#FFFFFF"
    
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
                box-shadow: 0 4px 18px rgba(0, 0, 0, 0.22) !important;
                border: 1px solid {popup_border} !important;
                padding: 0 !important;
                overflow: hidden !important;
            }}
            .leaflet-popup-content {{
                margin: 12px 14px !important;
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
                min-width: 215px;
                max-width: 270px;
            }}
            .popup-eyebrow {{
                font-size: 9.5px;
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
                margin-bottom: 8px;
                padding-bottom: 6px;
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
            .popup-alert {{
                margin-top: 8px;
                padding: 6px 8px;
                border-radius: 5px;
                font-size: 11px;
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

            stations.forEach(function(st) {{
                // Fixed-size station marker with depth encoded by color
                var marker = L.circleMarker([st.lat, st.lon], {{
                    radius: 8.5,
                    fillColor: st.color,
                    color: '{marker_stroke}',
                    weight: 2.2,
                    opacity: 1,
                    fillOpacity: 0.95
                }}).addTo(map);

                marker.on('mouseover', function() {{
                    this.setRadius(10.5);
                }});
                marker.on('mouseout', function() {{
                    this.setRadius(8.5);
                }});

                var extrapNotice = st.is_extrapolated ? 
                    '<div class="popup-alert alert-warn"><span>⚠️</span><div><b>Precipitation Warning:</b> Station lies outside the 4-point IMD rainfall grid; rainfall lookback is spatially extrapolated.</div></div>' : 
                    '<div class="popup-alert alert-succ"><span>✓</span><div><b>Precipitation:</b> Station within IMD grid bounding box.</div></div>';

                var popupContent = `
                    <div class="popup-card">
                        <div class="popup-eyebrow">Observed CGWB Telemetry</div>
                        <div class="popup-title">${{st.name}}</div>
                        <div class="popup-row">
                            <span class="popup-lbl">Measured Depth:</span>
                            <span class="popup-val"><b>${{st.depth.toFixed(2)}} m</b> MBGL</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-lbl">Reference Tier:</span>
                            <span class="popup-tier-tag" style="color: ${{st.color}}; background: ${{st.color}}1A;">${{st.status}}</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-lbl">Season:</span>
                            <span class="popup-val">${{st.season}}</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-lbl">Observation Date:</span>
                            <span class="popup-val">${{st.date}}</span>
                        </div>
                        <div class="popup-row">
                            <span class="popup-lbl">Coordinates:</span>
                            <span class="popup-val">${{st.lat.toFixed(4)}}°N, ${{st.lon.toFixed(4)}}°E</span>
                        </div>
                        ${{extrapNotice}}
                    </div>
                `;
                marker.bindPopup(popupContent, {{
                    maxWidth: 290,
                    className: 'custom-cgwb-popup'
                }});
                markerList.push(marker);
            }});

            // Dynamically fit map bounds to the station network with comfortable padding
            if (markerList.length > 0) {{
                var networkGroup = L.featureGroup(markerList);
                map.fitBounds(networkGroup.getBounds(), {{
                    padding: [45, 45],
                    maxZoom: 12
                }});
            }}
        </script>
    </body>
    </html>
    """
    components.html(leaflet_html, height=575)
