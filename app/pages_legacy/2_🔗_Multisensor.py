"""Multisensorial Biomedical Dashboard con análisis ML integrado."""

import os
import sys
import streamlit as st
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from src.ai.multisensor_analytics import MultisensorAnalyzer
    HAS_MULTISENSOR_ML = True
except ImportError:
    HAS_MULTISENSOR_ML = False

try:
    from app.supermodules import (
        safe_import_multisensor,
        generate_demo_ecg_signal,
        generate_demo_ppg_signal,
        generate_demo_spo2_signal,
        generate_demo_respiration_signal,
        generate_demo_temperature_signal,
        generate_demo_bp_signal,
        display_error_message,
        display_info_message,
        display_success_message,
        display_warning_message,
        render_sidebar_navigation,
        safe_import_plotly,
        init_session_state_key,
        validate_signal,
    )
except ImportError as import_error:
    import importlib.util
    utils_path = os.path.join(PROJECT_ROOT, 'app', 'utils.py')
    if not os.path.exists(utils_path):
        raise ImportError(f"Fallback a app.utils falló: no se encontró {utils_path}") from import_error

    spec = importlib.util.spec_from_file_location('app_utils', utils_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo crear un loader para {utils_path}") from import_error

    app_utils = importlib.util.module_from_spec(spec)
    sys.modules['app_utils'] = app_utils
    sys.modules['app.utils'] = app_utils
    spec.loader.exec_module(app_utils)

    safe_import_multisensor = app_utils.safe_import_multisensor
    generate_demo_ecg_signal = app_utils.generate_demo_ecg_signal
    generate_demo_ppg_signal = app_utils.generate_demo_ppg_signal
    generate_demo_spo2_signal = app_utils.generate_demo_spo2_signal
    generate_demo_respiration_signal = app_utils.generate_demo_respiration_signal
    generate_demo_temperature_signal = app_utils.generate_demo_temperature_signal
    generate_demo_bp_signal = app_utils.generate_demo_bp_signal
    display_error_message = app_utils.display_error_message
    display_info_message = app_utils.display_info_message
    display_success_message = app_utils.display_success_message
    display_warning_message = app_utils.display_warning_message
    render_sidebar_navigation = app_utils.render_sidebar_navigation
    safe_import_plotly = app_utils.safe_import_plotly
    init_session_state_key = app_utils.init_session_state_key
    validate_signal = app_utils.validate_signal

st.set_page_config(page_title="Panel Multisensor", layout="wide")
render_sidebar_navigation()

st.markdown("""
    <h1 id="panel-multisensorial" style="color: #1f77b4;">🔗 Panel Multisensorial</h1>
    <p>Integra ECG, PPG, SpO2, respiración, temperatura y presión arterial en un solo flujo clínico.</p>
""", unsafe_allow_html=True)

st.markdown(
    """
    ### Contenidos rápidos
    - [Introducción al panel multisensor](#introduccion-al-panel-multisensor)
    - [Cómo interpretar cada señal](#como-interpretar)
    - [Pasos para principiantes](#pasos-para-principiantes)
    - [Modo demo y datos sintéticos](#modo-demo)
    """
)

st.markdown('<a id="introduccion-al-panel-multisensor"></a>', unsafe_allow_html=True)
st.markdown("### Introducción al panel multisensor")
st.write(
    "Este panel integra varios tipos de datos biomédicos en un solo lugar. La idea es que puedas ver cómo cambian el ECG, la PPG, la SpO2, la respiración, la temperatura y la presión arterial de forma conjunta para tener un diagnóstico más completo."
)

st.markdown("<a id=\"como-interpretar\"></a>", unsafe_allow_html=True)
st.markdown("### Cómo interpretar cada señal")
st.markdown(
    "- ECG: observa el ritmo, los picos R y la regularidad del latido.\n"
    "- PPG: detecta frecuencia de pulso, amplitud y pulso irregular.\n"
    "- SpO2: verifica saturación de oxígeno y desaturaciones.\n"
    "- Respiración: revisa frecuencia, profundidad y posibles pausas.\n"
    "- Temperatura y presión arterial: aporta contexto clínico a los cambios en ritmo y oxigenación.\n"
)

st.markdown("### 📡 Configuración de sensores")

col1, col2, col3 = st.columns(3)

with col1:
    st.checkbox("ECG (Frecuencia cardíaca)", value=True, disabled=True)
    st.checkbox("PPG (Pulso)", value=False)
    st.checkbox("SpO2 (Oxígeno)", value=False)

with col2:
    st.checkbox("Respiración", value=False)
    st.checkbox("Temperatura", value=False)
    st.checkbox("Presión arterial", value=False)

st.markdown("""
    <h2 id="guia-de-interpretacion-de-senales">📖 Guía de interpretación de señales</h2>
    <p>Este panel ayuda a correlacionar signos vitales. Por ejemplo, una caída de SpO2 puede acompañarse de una respiración superficial y un ECG con taquicardia.</p>

    - ECG: muestra ritmo y arritmias.
    - PPG: mide pulso y amplitud de pulso.
    - SpO2: muestra saturación de oxígeno en sangre.
    - Respiración: permite detectar pausas o cambios de profundidad.
    - Temperatura y presión arterial: contexto vital para evaluación clínica.
""", unsafe_allow_html=True)

st.markdown('<a id="pasos-para-principiantes"></a>', unsafe_allow_html=True)
with st.expander("📘 Instrucciones para principiantes"):
    st.write("1. Selecciona los sensores que quieres simular o conectar.")
    st.write("2. Revisa el panel de señales en vivo o usa datos de ejemplo de demo.")
    st.write("3. Observa cómo cambian las señales en conjunto cuando hay un evento cardíaco o respiratorio.")
    st.write("4. Usa la guía de interpretación para identificar patrones de ECG, SpO2 y respiración.")

with col3:
    st.checkbox("EMG (Músculo)", value=False)
    st.checkbox("EEG (Cerebro)", value=False)
    st.checkbox("Glucosa", value=False)

st.markdown("---")

display_info_message("Crea señales de demostración para evaluar el panel multisensorial")

init_session_state_key("multisensor_demo", {})

if st.button("🎮 Generar señales de demostración"):
    try:
        BiosignalChannel, MultisensoralRecord, modules_available = safe_import_multisensor()

        fs = 250
        duration = 30

        with st.spinner("🔄 Generando señales..."):
            ecg_signal = generate_demo_ecg_signal(fs=fs, duration=duration)
            ppg_signal = generate_demo_ppg_signal(fs=fs, duration=duration)
            spo2_signal = generate_demo_spo2_signal(fs=fs, duration=duration)
            resp_signal = generate_demo_respiration_signal(fs=fs, duration=duration)
            temp_signal = generate_demo_temperature_signal(fs=fs, duration=duration)
            bp_sys = generate_demo_bp_signal(fs=fs, duration=duration)

        if not modules_available:
            display_warning_message("No se ha conectado el servicio de hardware. Usando señal demo local.")

        channels = [
            BiosignalChannel(name='ECG', signal=ecg_signal, fs=fs, unit='mV', signal_type='ecg'),
            BiosignalChannel(name='PPG', signal=ppg_signal, fs=fs, unit='AU', signal_type='ppg'),
            BiosignalChannel(name='SpO2', signal=spo2_signal, fs=1, unit='%', signal_type='spo2'),
            BiosignalChannel(name='Respiration', signal=resp_signal, fs=fs, unit='V', signal_type='respiration'),
            BiosignalChannel(name='Temperature', signal=temp_signal, fs=1, unit='°C', signal_type='temperature'),
            BiosignalChannel(name='BP_SYS', signal=bp_sys, fs=1, unit='mmHg', signal_type='bp_sys'),
        ]

        st.session_state.multisensor_demo = {
            'channels': channels,
            'fs': fs,
        }

    except Exception as e:
        display_error_message(e, "Panel multisensorial")

if st.session_state.multisensor_demo:
    demo_state = st.session_state.multisensor_demo
    channels = demo_state['channels']
    fs = demo_state['fs']

    record = MultisensoralRecord(channels, patient_id='DEMO_001')

    st.markdown("### 📊 Indicadores fisiológicos")
    col_hr, col_o2, col_temp, col_rr = st.columns(4)

    indices = record.compute_physiological_indices()
    col_hr.metric("Frecuencia cardíaca", f"{indices.get('heart_rate', 0):.0f}", "bpm")
    col_o2.metric("SpO2", f"{indices.get('spo2_mean', 0):.1f}", "%")
    col_temp.metric("Temperatura", f"{indices.get('temperature', 0):.1f}", "°C")
    col_rr.metric("Respiración", f"{indices.get('respiration_rate', 0):.1f}", "resp/min")

    st.markdown("---")
    st.markdown("### 📈 Panel de señales")

    go, sp, plotly_ok = safe_import_plotly()
    if plotly_ok:
        try:
            from visualization.medical.plotly_clinical import create_multisensor_dashboard

            channels_dict = {ch.name: ch.signal for ch in channels}
            fig = create_multisensor_dashboard(channels_dict, fs)
            st.plotly_chart(fig, use_container_width=True)
            display_success_message("Panel visualizado correctamente")
        except Exception as e:
            display_warning_message(f"La visualización Plotly falló: {e}")
            st.info("Mostrando solo métricas y vista general de la señal.")
    else:
        st.info("📊 Plotly no está disponible, mostrando solo métricas")

    st.markdown("### 🎯 Índice de salud integral")
    scores = record.health_score()

    col_cv, col_auto, col_o2, col_rec = st.columns(4)
    col_cv.metric("Cardiovascular", f"{scores['cardiovascular']:.0f}", "%")
    col_auto.metric("Autonómico", f"{scores['autonomic']:.0f}", "%")
    col_o2.metric("Oxigenación", f"{scores['oxygenation']:.0f}", "%")
    col_rec.metric("Recuperación", f"{scores['recovery']:.0f}", "%")

    st.markdown(f"### Puntuación general de salud: {scores['overall']:.0f}/100")
    st.markdown("**Nota:** El índice combina la función cardiovascular, el control autonómico, la oxigenación y la recuperación para ofrecer una visión clínica rápida del estado del paciente.")
    st.markdown("---")
    anomalies = record.detect_physiological_inconsistencies()
    if anomalies:
        display_warning_message(f"Anomalías detectadas: {', '.join(anomalies)}")
    else:
        display_success_message("Todas las señales dentro de rangos normales")

st.markdown("---")
with st.expander("📖 Guía de interpretación de señales"):
    st.markdown("""
    **ECG**: Actividad eléctrica del corazón
    - Normal: 60-100 bpm
    - Bradicardia: < 60 bpm
    - Taquicardia: > 100 bpm

    **PPG**: Fotopletismografía (pulso)
    - Refleja cambios de volumen sanguíneo
    - Se usa para confirmar frecuencia cardíaca

    **SpO2**: Saturación de oxígeno en sangre
    - Normal: > 95%
    - Hipoxemia: < 90%

    **Respiración**: Frecuencia respiratoria
    - Normal: 12-20 respiraciones/min
    - Taquipnea: > 20
    - Bradipnea: < 12

    **Temperatura**: Temperatura corporal
    - Normal: 36.5-37.5°C
    - Fiebre: > 38.5°C
    - Hipotermia: < 36°C

    **Presión arterial**: Sistólica/Diastólica
    - Normal: < 120/80 mmHg
    - Hipertensión: ≥ 130/80 mmHg
    """)
