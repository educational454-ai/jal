"""Interactive Leaflet map component with telemetry markers and extrapolation warnings."""
import json
import pandas as pd
import streamlit.components.v1 as components
from services.data_loader import get_status


def render_groundwater_map(filtered_stations: pd.DataFrame, center: tuple[float, float] = (18.28, 74.12), zoom: int = 11, theme: str = "light") -> None:
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
        
    map_border = "#23414B" if theme == "dark" else "#CBD5E1"
    dark_tile_filter = """
        .leaflet-tile-pane {
            filter: brightness(0.7) invert(1) contrast(2.6) hue-rotate(200deg) saturate(0.35) brightness(0.9);
        }
    """ if theme == "dark" else ""
    
    leaflet_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            #map {{ 
                height: 505px; 
                width: 100%; 
                border-radius: 8px; 
                border: 1px solid {map_border}; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.12); 
            }}
            {dark_tile_filter}
            .info-box {{
                background: white; padding: 10px 14px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); font-family: sans-serif;
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0;">
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([{center[0]}, {center[1]}], {zoom});
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 18,
                attribution: '© OpenStreetMap contributors'
            }}).addTo(map);

            var stations = {json.dumps(stations_json)};

            stations.forEach(function(st) {{
                // Fixed-size station marker with depth encoded by color
                var marker = L.circleMarker([st.lat, st.lon], {{
                    radius: 9,
                    fillColor: st.color,
                    color: '#ffffff',
                    weight: 2.5,
                    opacity: 1,
                    fillOpacity: 0.92
                }}).addTo(map);

                var extrapNotice = st.is_extrapolated ? 
                    '<div style="color: #92400E; font-size: 11px; margin-top: 6px; background: #FEF3C7; padding: 4px 6px; border-radius: 4px; border-left: 3px solid #F59E0B;">⚠️ <b>Precipitation Warning:</b> Station lies outside the 4-point IMD rainfall grid; rainfall is spatially extrapolated.</div>' : 
                    '<div style="color: #065F46; font-size: 11px; margin-top: 6px; background: #D1FAE5; padding: 4px 6px; border-radius: 4px; border-left: 3px solid #10B981;">✓ <b>Precipitation:</b> Station within IMD grid bounding box.</div>';

                var popupContent = `
                    <div style="font-family: Arial, sans-serif; min-width: 190px; line-height: 1.45; color: #1E293B;">
                        <div style="font-size: 10px; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px; font-weight: bold;">Observed CGWB Telemetry</div>
                        <h4 style="margin: 2px 0 6px 0; color: #0F172A; font-size: 14px;">${{st.name}}</h4>
                        <b>Measured Water Depth:</b> ${{st.depth.toFixed(2)}} m MBGL<br>
                        <b>Classification:</b> <span style="color: ${{st.color}}; font-weight: bold;">${{st.status}}</span><br>
                        <b>Season:</b> ${{st.season}}<br>
                        <b>Observation Date:</b> ${{st.date}}
                        ${{extrapNotice}}
                    </div>
                `;
                marker.bindPopup(popupContent);
            }});
        </script>
    </body>
    </html>
    """
    components.html(leaflet_html, height=520)
