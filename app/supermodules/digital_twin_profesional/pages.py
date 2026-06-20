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

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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


def render_neurological_twin():
    """Visualiza el gemelo neurológico"""
    st.markdown("### 🧠 Gemelo Neurológico")
    
    twin = st.session_state.twin
    neuro = twin.neurological
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Atención", f"{neuro.attention:.0f}%")
        
    with col2:
        st.metric("Carga Cognitiva", f"{neuro.mental_workload:.0f}%")
        
    with col3:
        st.metric("Estrés", f"{neuro.stress_perception:.0f}%")
        
    with col4:
        st.metric("Somnolencia", f"{neuro.sleepiness:.0f}%")
    
    # Heatmap de actividad cortical
    st.markdown("**Actividad Cortical:**")
    cortical_activity = pd.DataFrame({
        'Región': ['Frontal', 'Parietal', 'Temporal', 'Occipital', 'Motor', 'Sensorial'],
        'Activación': [neuro.frontal_activity, neuro.parietal_activity, neuro.temporal_activity,
                      neuro.occipital_activity, neuro.motor_cortex_activation, neuro.sensory_integration]
    })
    st.bar_chart(cortical_activity.set_index('Región'), use_container_width=True)


def render_oxygenation_twin():
    """Visualiza el gemelo de oxigenación"""
    st.markdown("### 🫁 Gemelo de Oxigenación")
    
    twin = st.session_state.twin
    oxy = twin.oxygenation
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("SpO₂", f"{oxy.spo2:.1f}%", delta=f"{oxy.spo2 - 95:.1f}%" if oxy.spo2 < 95 else None)
        
    with col2:
        st.metric("Perfusión", f"{oxy.perfusion_index:.0f}%")
        
    with col3:
        st.metric("O₂ Arterial", f"{oxy.arterial_oxygen:.0f} mmHg")
        
    with col4:
        st.metric("O₂ Tisular", f"{oxy.tissue_oxygenation:.0f}%")
    
    # SpO2 simulado
    st.markdown("**Saturación en Tiempo Real:**")
    spo2_data = generate_demo_spo2_signal(fs=250, duration=10)
    spo2_normalized = (spo2_data / np.max(spo2_data) * 8) + (oxy.spo2 - 4)  # Scale to SpO2 values
    st.line_chart(spo2_normalized[:2500], use_container_width=True)


def render_autonomic_twin():
    """Visualiza el gemelo autonómico"""
    st.markdown("### 🔄 Gemelo Autonómico")
    
    twin = st.session_state.twin
    auto = twin.autonomic
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Actividad Simpática", f"{auto.sympathetic_activity:.0f}%")
        
    with col2:
        st.metric("Actividad Parasimpática", f"{auto.parasympathetic_activity:.0f}%")
        
    with col3:
        st.metric("Índice de Estrés", f"{auto.stress_index:.0f}%")
        
    with col4:
        st.metric("Flexibilidad Autonómica", f"{auto.autonomic_flexibility:.0f}%")
    
    # Balance simpático-parasimpático
    st.markdown("**Balance Autonómico:**")
    balance_data = {
        'Simpático': auto.sympathetic_activity,
        'Parasimpático': auto.parasympathetic_activity,
    }
    st.bar_chart(pd.Series(balance_data), use_container_width=True)


def render_intervention_controls():
    """Controles de intervenciones"""
    st.markdown("### 💊 Intervenciones Simuladas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🫁 Oxígeno"):
            intensity = st.slider("Intensidad O2", 0.0, 1.0, 0.7, key='o2_intensity')
            changes = st.session_state.twin.simulate_intervention("oxygen", intensity)
            st.success(f"✅ O₂ aplicado. SpO₂ → {changes.get('spo2', 'N/A'):.1f}%")
    
    with col2:
        if st.button("💤 Sedación"):
            intensity = st.slider("Intensidad sedación", 0.0, 1.0, 0.6, key='sed_intensity')
            changes = st.session_state.twin.simulate_intervention("sedation", intensity)
            st.info(f"✅ Sedación aplicada. Estrés → {changes.get('stress', 'N/A'):.0f}%")
    
    with col3:
        if st.button("🏃 Ejercicio"):
            intensity = st.slider("Intensidad ejercicio", 0.0, 1.0, 0.7, key='ex_intensity')
            changes = st.session_state.twin.simulate_intervention("exercise", intensity)
            st.warning(f"⚡ Ejercicio. FC → {changes.get('heart_rate', 'N/A'):.0f} bpm")
    
    with col4:
        if st.button("😴 Descanso"):
            intensity = st.slider("Intensidad descanso", 0.0, 1.0, 0.8, key='rest_intensity')
            changes = st.session_state.twin.simulate_intervention("rest", intensity)
            st.success(f"✅ Descanso. Recuperación → {changes.get('recovery', 'N/A'):.0f}%")


def render_predictions():
    """Predicciones fisiológicas"""
    st.markdown("### 🔮 Predicciones Fisiológicas (Próxima Hora)")
    
    twin = st.session_state.twin
    predictions = twin.predict_physiological_events(horizon_minutes=60)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        pred = predictions.get('fatigue', {})
        st.metric("Fatiga Predicha", f"{pred.get('predicted', 0):.0f}%",
                 help=f"Confianza: {pred.get('confidence', 0):.0%}")
    
    with col2:
        pred = predictions.get('recovery', {})
        st.metric("Recuperación Predicha", f"{pred.get('predicted', 0):.0f}%",
                 help=f"Confianza: {pred.get('confidence', 0):.0%}")
    
    with col3:
        pred = predictions.get('cardiovascular_instability', {})
        risk = pred.get('risk', 'N/A')
        color = '🔴' if risk == 'HIGH' else '🟢'
        st.metric("Riesgo Cardiovascular", risk,
                 help=f"{color} Confianza: {pred.get('confidence', 0):.0%}")


def render_clinical_summary():
    """Resumen clínico"""
    st.markdown("### 📋 Resumen Clínico Completo")
    
    twin = st.session_state.twin
    summary = twin.generate_clinical_summary()
    st.code(summary, language='text')
    
    # Exportar resumen
    col_export1, col_export2 = st.columns(2)
    with col_export1:
        if st.button("📥 Descargar Resumen (TXT)"):
            st.download_button(
                label="Descargar",
                data=summary,
                file_name=f"twin_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    with col_export2:
        if st.button("📥 Exportar Estado (JSON)"):
            json_data = twin.to_json()
            st.download_button(
                label="Descargar",
                data=json_data,
                file_name=f"twin_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


def render_education_mode():
    """Modo educativo"""
    st.markdown("### 📖 Modo Educativo")
    
    twin = st.session_state.twin
    
    st.markdown("""
    **Aprende sobre los 10 Gemelos Digitales:**
    
    El Digital Twin no es una visualización ni un avatar. Es una representación
    computacional viva de tu fisiología. Cada gemelo representa un sistema
    fisiológico diferente, y todos se comunican dinámicamente.
    """)
    
    education_content = {
        '🫀 Cardíaco': f"""
        **Función:** Modelar actividad eléctrica, mecánica y hemodinámica cardíaca.
        
        **Componentes:**
        - Nódulo SA: Genera impulsos (FC = {twin.cardiac.sa_node_rate:.0f} bpm)
        - Nódulo AV: Retraso de conducción ({twin.cardiac.av_conduction_delay:.3f} seg)
        - Ventrículos: Eyección (EF = {twin.cardiac.ventricular_ejection_fraction:.0f}%)
        
        **Estado Actual:**
        - FC: {twin.cardiac.heart_rate:.0f} bpm
        - HRV: {twin.cardiac.hrv:.1f} ms
        - Gasto Cardíaco: {twin.cardiac.cardiac_output:.1f} L/min
        """,
        
        '🧠 Neurológico': f"""
        **Función:** Modelar actividad cortical y estados cerebrales.
        
        **Regiones:**
        - Frontal: {twin.neurological.frontal_activity:.0f}% activa
        - Temporal: {twin.neurological.temporal_activity:.0f}% activa
        - Parietal: {twin.neurological.parietal_activity:.0f}% activa
        - Occipital: {twin.neurological.occipital_activity:.0f}% activa
        
        **Estado Cognitivo:**
        - Atención: {twin.neurological.attention:.0f}%
        - Carga Mental: {twin.neurological.mental_workload:.0f}%
        """,
        
        '💨 Respiratorio': f"""
        **Función:** Modelar ventilación e intercambio gaseoso.
        
        **Parámetros:**
        - FR: {twin.respiratory.respiratory_rate:.0f} resp/min
        - TV: {twin.respiratory.tidal_volume:.0f} ml
        - VE: {twin.respiratory.minute_ventilation:.1f} L/min
        - Patrón: {twin.respiratory.breathing_pattern}
        
        **Riesgos:**
        - Apnea: {twin.respiratory.apnea_risk:.0f}%
        - Hipoxia: {twin.respiratory.hypoxia_risk:.0f}%
        """,
    }
    
    selected_topic = st.selectbox("Selecciona un tema:", list(education_content.keys()))
    if selected_topic:
        st.info(education_content[selected_topic])


def main():
    """Función principal"""
    st.set_page_config(
        page_title="Digital Twin Profesional",
        page_icon="🧬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    init_session()
    render_header()
    
    # Tabs principales
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Resumen",
        "🫀 Sistemas Individuales",
        "💊 Intervenciones",
        "🔮 Predicciones",
        "📖 Educación"
    ])
    
    with tab1:
        st.markdown("## Dashboard Integral del Gemelo Digital")
        render_quick_scenario_selector()
        st.markdown("---")
        render_clinical_summary()
    
    with tab2:
        st.markdown("## Análisis de Sistemas Individuales")
        sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5 = st.tabs([
            "🫀 Cardíaco",
            "💨 Respiratorio",
            "🧠 Neurológico",
            "🫁 Oxigenación",
            "🔄 Autonómico"
        ])
        
        with sub_tab1:
            render_cardiac_twin()
        with sub_tab2:
            render_respiratory_twin()
        with sub_tab3:
            render_neurological_twin()
        with sub_tab4:
            render_oxygenation_twin()
        with sub_tab5:
            render_autonomic_twin()
    
    with tab3:
        st.markdown("## Simula Intervenciones Médicas")
        render_intervention_controls()
        st.markdown("---")
        st.info("💡 Las intervenciones simulan cambios reales en la fisiología del gemelo. Observa cómo responden todos los sistemas.")
    
    with tab4:
        st.markdown("## Predicciones Inteligentes")
        render_predictions()
        st.markdown("---")
        st.info("📊 Basadas en el estado actual del gemelo y tendencias fisiológicas.")
    
    with tab5:
        render_education_mode()
    
    # Sidebar con información
    with st.sidebar:
        st.markdown("### ℹ️ Sobre el Digital Twin")
        st.markdown("""
        El **Digital Twin Multisistema** es una representación computacional
        viva de tu fisiología. No es un gráfico - es un **sistema vivo** que:
        
        ✅ Integra 10 gemelos digitales  
        ✅ Modela interacciones fisiológicas  
        ✅ Simula intervenciones médicas  
        ✅ Predice eventos fisiológicos  
        ✅ Educa sobre sistemas corporales  
        
        **Escenario Actual:**
        """)
        st.metric("Paciente", st.session_state.scenario.upper())
        
        st.markdown("---")
        st.markdown("**🔗 Interacciones Fisiológicas Activadas:**")
        for interaction in st.session_state.twin.interactions:
            st.caption(f"• {interaction.description}")


if __name__ == "__main__" or True:
    try:
        main()
    except Exception as e:
        st.error(f"❌ Error en Digital Twin: {e}")
        import traceback
        st.code(traceback.format_exc())


def run():
    """Wrapper entrypoint compatible with importing as `run` from supermodules."""
    return main()
