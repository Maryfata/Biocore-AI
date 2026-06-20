"""Home page - Main entry point for Biomedical Signal Platform."""

import os
import sys
import streamlit as st
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from app.supermodules import render_sidebar_navigation
except ImportError:
    import importlib.util
    utils_path = os.path.join(PROJECT_ROOT, 'app', 'utils.py')
    spec = importlib.util.spec_from_file_location('app_utils', utils_path)
    app_utils = importlib.util.module_from_spec(spec)
    sys.modules['app_utils'] = app_utils
    spec.loader.exec_module(app_utils)
    render_sidebar_navigation = app_utils.render_sidebar_navigation

st.set_page_config(
    page_title="Visualizador de Señales Biomédicas",
    page_icon="❤️",
    layout="wide"
)

render_sidebar_navigation()

st.markdown(
    """
    <style>
        .hero {
            background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%);
            color: white !important;
            padding: 40px 40px 20px 40px;
            border-radius: 24px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(31, 41, 55, 0.15);
        }
        .hero h1,
        .hero p,
        .hero .status-pill {
            color: white !important;
        }
        .hero h1 {
            font-size: 3rem;
            margin-bottom: 0.4rem;
        }
        .hero p {
            font-size: 1.05rem;
            line-height: 1.7;
            opacity: 0.9;
        }
        .feature-card {
            background: #111827;
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 18px;
            padding: 24px;
            color: #e2e8f0;
            min-height: 240px;
        }
        .feature-card h3 {
            color: #38bdf8;
            margin-bottom: 16px;
        }
        .feature-card ul {
            padding-left: 20px;
            margin: 0;
            opacity: 0.85;
        }
        .feature-card li {
            margin-bottom: 10px;
        }
        .status-pill {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 999px;
            background: rgba(56, 189, 248, 0.16);
            color: #bef264;
            font-weight: 600;
            margin-top: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='hero'>
        <h1>Visualizador de Señales Biomédicas</h1>
        <p>ECG clínico, análisis multisensorial, informes asistidos por IA y educación médica en un tablero moderno.</p>
        <p class='status-pill'>ECG demo MIT-BIH | Informes AI | Flujos de pacientes | Telemedicina lista</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Flujo clínico rápido")

col1, col2, col3, col4 = st.columns(4)
col1.metric("ECG demo MIT-BIH", "48 registros", "Compatible con PhysioNet")
col2.metric("Registros de pacientes", "+1.200", "Telemedicina segura")
col3.metric("Interpretaciones AI", "En desarrollo", "Perspectivas clínicas")
col4.metric("Casos educativos", "50+", "Dificultad adaptativa")

st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("### Por qué clínicos y educadores eligen esta plataforma")
    st.markdown(
        "- Tablero clínico unificado para ECG, PPG, SpO2, respiración y presión arterial."  
        "- Revisión interactiva de ECG demo MIT-BIH con métricas HRV anotadas."  
        "- Historial de telemedicina, generación de informes y formación clínica basada en casos."
    )
    st.markdown("### Novedades en esta versión")
    st.markdown(
        "- Interfaz y flujos de pacientes pulidos para entregas clínicas más rápidas."  
        "- Página AI integrada con análisis de pipeline y revisión de señales MIT-BIH."
    )

with col2:
    st.markdown("### Funciones destacadas")
    st.markdown("""
    <div class='feature-card'>
        <h3>📈 Revisión clínica de ECG</h3>
        <ul>
            <li>Verificación de calidad de señal</li>
            <li>Medición de picos R e intervalos</li>
            <li>Gráfico interactivo y vista previa de informe</li>
        </ul>
    </div>
    <div class='feature-card' style='margin-top: 20px;'>
        <h3>📚 Laboratorio de entrenamiento</h3>
        <ul>
            <li>Enseñanza de ECG basada en casos</li>
            <li>Evaluaciones en formato quiz</li>
            <li>Ejemplos clínicos reales</li>
        </ul>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

st.markdown("### Navega por la plataforma")

st.markdown(
    """
    - **📊 ECG Monitor**: Carga registros WFDB/MIT-BIH o sube ECG CSV.  
    - **🔗 Multisensor**: Correlaciona ECG con signos vitales y calcula índices de salud.  
    - **🎓 Educación**: Practica interpretación de ECG con casos clínicos interactivos.  
    - **👥 Pacientes**: Gestiona registros, genera informes y monitorea telemedicina.  
    - **🤖 AI Análisis**: Visualiza resultados del pipeline, clasificación ECG e informes clínicos.
    """
)

st.markdown("---")

st.markdown("### Fuentes de datos compatibles")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("**WFDB / MIT-BIH**")
    st.markdown("ECGs de investigación clínica, registros de arritmia y soporte PhysioNet.")
with col2:
    st.markdown("**EDF**")
    st.markdown("Grabaciones clínicas multicanal y señales de estudios de sueño.")
with col3:
    st.markdown("**CSV**")
    st.markdown("Exportaciones de sensores personalizados, wearables y fuentes ECG externas.")
with col4:
    st.markdown("**Wearables**")
    st.markdown("Telemetría de smartwatch y dispositivos para monitoreo en entorno real.")

st.sidebar.markdown("---")
st.sidebar.markdown("### Enlaces rápidos")
st.sidebar.markdown("- 📊 ECG Monitor\n- 🔗 Multisensor\n- 🎓 Educación\n- 👥 Pacientes\n- 🤖 AI Análisis")
st.sidebar.markdown("---")
st.sidebar.markdown("**Versión:** 2.1  \n**Estado:** Prototipo clínico  \n**Actualizado:** 2026")


def run():
    """Wrapper entrypoint compatible with importing as `run` from supermodules.

    Note: this module executes top-level Streamlit code on import, so `run()`
    is a no-op wrapper kept for API symmetry.
    """
    return None
