"""Global research header banner and telemetry specifications component."""
import streamlit as st


def render_research_header(theme: str = "light") -> None:
    """Render the compact top research banner and collapsible telemetry specifications."""
    st.markdown("""
    <div class="research-header">
        <div class="header-left">
            <div class="header-icon-box">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>
                </svg>
            </div>
            <div class="header-titles">
                <div class="header-main-title">BhujalDrishti &nbsp;<span class="header-title-sep">| JalRakshak AI</span></div>
                <div class="header-subtitle">Multimodal GIS & Hydrological Forecasting Decision Support</div>
            </div>
        </div>
        <div class="header-badges">
            <span class="badge-prototype">Research Prototype</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Preserved Telemetry Network & Hydrogeological Specifications in clean collapsible format
    with st.expander("ℹ️ Telemetry Network & Hydrogeological Specifications", expanded=False):
        st.markdown("""
        <div class="telemetry-grid">
            <div class="telemetry-card">
                <div class="telemetry-card-label">Jurisdiction</div>
                <div class="telemetry-card-value">Purandar Taluka (Pune, MH)</div>
            </div>
            <div class="telemetry-card">
                <div class="telemetry-card-label">Administrative Area</div>
                <div class="telemetry-card-value">~1,105 km²</div>
            </div>
            <div class="telemetry-card">
                <div class="telemetry-card-label">Aquifer Formation</div>
                <div class="telemetry-card-value">Deccan Basalt Flows</div>
            </div>
            <div class="telemetry-card">
                <div class="telemetry-card-label">CGWB Monitoring</div>
                <div class="telemetry-card-value">11 In-situ Observation Wells</div>
            </div>
            <div class="telemetry-card">
                <div class="telemetry-card-label">Rainfall Grid</div>
                <div class="telemetry-card-value">4 IMD Points (0.25° resolution)</div>
            </div>
            <div class="telemetry-card">
                <div class="telemetry-card-label">Peripheral Stations</div>
                <div class="telemetry-card-value">4 Spatially Extrapolated</div>
            </div>
            <div class="telemetry-card telemetry-card-wide">
                <div class="telemetry-card-label">Validation Split</div>
                <div class="telemetry-card-value">Zero-Target-Leakage Chronological Split (Train: 1996–2017, Test: 2018–2023, n=124)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

