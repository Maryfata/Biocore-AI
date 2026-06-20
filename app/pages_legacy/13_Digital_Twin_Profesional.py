"""
📊 DIGITAL TWIN PROFESIONAL — Gemelo Digital Multisistema

Representación computacional viva de la fisiología humana.
Integra 10 gemelos digitales interconectados con análisis clínico,
educativo y de investigación.
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from app.engines.digital_twin_multisystem import DigitalTwinMultisystem
    from app.supermodules import (
        generate_demo_ecg_signal,
        generate_demo_respiration_signal,
        generate_demo_spo2_signal,
    )
except ImportError as e:
    st.error(f"Error importando módulos: {e}")
    st.stop()


def init_session():
    """Inicializa variables de sesión"""
    if 'twin' not in st.session_state:
        st.session_state.twin = DigitalTwinMultisystem()
    if 'scenario' not in st.session_state:
        st.session_state.scenario = 'healthy'
    if 'history' not in st.session_state:
        st.session_state.history = []


def render_header():
    """Encabezado profesional"""
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='color: white; margin: 0;'>🧬 DIGITAL TWIN MULTISISTEMA</h1>
        <p style='color: #e0e0e0; margin: 5px 0 0 0;'>Representación Computacional Viva de la Fisiología Humana</p>
    </div>
    """, unsafe_allow_html=True)


def render_quick_scenario_selector():
    """Selector rápido de escenarios de paciente"""
    st.markdown("### 👥 Escenarios de Paciente")
    
    scenarios = {
        'healthy': '🟢 Paciente Sano',
        'hypertension': '🟡 Hipertensión',
        'copd': '🔴 EPOC',
        'arrhythmia': '⚠️ Arritmia',
        'sepsis': '🆘 Sepsis',
    }
    
    cols = st.columns(5)
    for idx, (key, label) in enumerate(scenarios.items()):
        with cols[idx]:
            if st.button(label, use_container_width=True):
                st.session_state.twin.create_patient_scenario(key)
                st.session_state.scenario = key
                st.success(f"✅ Escenario '{key}' cargado")
                st.rerun()


def render_cardiac_twin():
    """Visualiza el gemelo cardíaco"""
    st.markdown("### 🫀 Gemelo Cardíaco")
    
    twin = st.session_state.twin
    cardiac = twin.cardiac
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Frecuencia Cardíaca", f"{cardiac.heart_rate:.0f} bpm", 
                 delta=f"{cardiac.heart_rate - 72:.0f} vs normal")
        
    with col2:
        st.metric("Variabilidad (HRV)", f"{cardiac.hrv:.1f} ms")
        
    with col3:
        st.metric("Gasto Cardíaco", f"{cardiac.cardiac_output:.1f} L/min")
        
    with col4:
        st.metric("Estrés Miocárdico", f"{cardiac.myocardial_stress:.0f}%")

    # Gráfica de ritmo cardíaco simulado
    st.markdown("**Patrón Eléctrico:**")
    ecg_data = generate_demo_ecg_signal(fs=250, duration=10, hr=cardiac.heart_rate)
    st.line_chart(ecg_data[:2500], use_container_width=True)

    # Detalles técnicos
    with st.expander("📋 Detalles Técnicos"):
        col_tech1, col_tech2 = st.columns(2)
        with col_tech1:
            st.write(f"**Intervalo PR:** {cardiac.pr_interval:.3f} seg")
            st.write(f"**QRS Duration:** {cardiac.qrs_duration:.3f} seg")
            st.write(f"**Intervalo QT:** {cardiac.qt_interval:.3f} seg")
        with col_tech2:
            st.write(f"**Volumen Sistólico:** {cardiac.stroke_volume:.0f} ml")
            st.write(f"**Fracción de Eyección:** {cardiac.ventricular_ejection_fraction:.0f}%")
            st.write(f"**Estabilidad Ritmo:** {cardiac.rhythm_stability:.0f}%")


def render_respiratory_twin():
    """Visualiza el gemelo respiratorio"""
    st.markdown("### 💨 Gemelo Respiratorio")
    
    twin = st.session_state.twin
    respiratory = twin.respiratory
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Frecuencia Respiratoria", f"{respiratory.respiratory_rate:.0f} resp/min")
        
    with col2:
        st.metric("Ventilación", f"{respiratory.minute_ventilation:.1f} L/min")
        
    with col3:
        st.metric("Calidad Ventilación", f"{respiratory.ventilation_quality:.0f}%")
        
    with col4:
        st.metric("Riesgo Apnea", f"{respiratory.apnea_risk:.0f}%")

    # Gráfica respiratoria
    st.markdown("**Patrón Respiratorio:**")
    resp_data = generate_demo_respiration_signal(fs=250, duration=10, rr=respiratory.respiratory_rate)
    st.line_chart(resp_data[:2500], use_container_width=True)

    # Riesgos
    col_risk1, col_risk2 = st.columns(2)
    with col_risk1:
        if respiratory.apnea_risk > 30:
            st.warning(f"⚠️ Riesgo de apnea: {respiratory.apnea_risk:.0f}%")
    with col_risk2:
        if respiratory.hypoxia_risk > 30:
            st.warning(f"⚠️ Riesgo de hipoxia: {respiratory.hypoxia_risk:.0f}%")
