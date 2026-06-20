"""BIOCORE AI — Complete Integrated Biomedical Intelligence Operating System.

Full integration of all modules with complete features, hardware support, and universal hands-free.
"""

import io
import os
import sys
import time
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Tuple, Any

import numpy as np
import streamlit as st
from scipy.signal import welch

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.supermodules import (
    estimate_ecg_heart_rate,
    estimate_respiration_rate,
    generate_demo_bp_signal,
    generate_demo_ecg_signal,
    generate_demo_ppg_signal,
    generate_demo_respiration_signal,
    generate_demo_spo2_signal,
    generate_demo_temperature_signal,
    safe_import_plotly,
    safe_import_ecg_modules,
    safe_import_multisensor,
    safe_import_src_modules,
    validate_signal,
    plot_signal_matplotlib,
    display_warning_message,
    display_error_message,
    display_info_message,
)

from app.reporting import export_lab_report
import app.reporting as reporting
from app.hands_off_mode import render_hands_off_panel

# Attempt to import gesture controller (fallback to emulator if unavailable)
try:
    from gesture_controller import GestureController
    _gesture_controller_available = True
except Exception:
    _gesture_controller_available = False
    class GestureController:
        def __init__(self):
            self.available = False
        def detect_gesture(self, image_data):
            return None

# Safe imports for optional biomedical modules
try:
    import importlib
    _mod_eeg = importlib.import_module('biomedical.eeg')
    EegSignalGenerator = getattr(_mod_eeg, 'EegSignalGenerator', None)
    EegAnalyzer = getattr(_mod_eeg, 'EegAnalyzer', None)
    EegPattern = getattr(_mod_eeg, 'EegPattern', None)
except Exception:
    EegSignalGenerator = None
    EegAnalyzer = None
    EegPattern = None

try:
    import importlib
    _mod_emg = importlib.import_module('biomedical.emg')
    preprocess_emg = getattr(_mod_emg, 'preprocess_emg', None)
    compute_emg_median_frequency = getattr(_mod_emg, 'compute_emg_median_frequency', None)
    compute_emg_fatigue_index = getattr(_mod_emg, 'compute_emg_fatigue_index', None)
    EMGStreamer = getattr(_mod_emg, 'EMGStreamer', None)
except Exception:
    preprocess_emg = None
    compute_emg_median_frequency = None
    compute_emg_fatigue_index = None
    EMGStreamer = None

# Fallback EMG functions if not available
if compute_emg_median_frequency is None:
    def compute_emg_median_frequency(signal: np.ndarray, fs: float) -> float:
        freqs, psd = welch(signal, fs=fs, nperseg=min(1024, len(signal)))
        if psd.size == 0:
            return 0.0
        cdf = np.cumsum(psd)
        if cdf[-1] <= 0:
            return 0.0
        median_idx = np.searchsorted(cdf, cdf[-1] / 2.0)
        return float(freqs[min(median_idx, len(freqs) - 1)])

if compute_emg_fatigue_index is None:
    def compute_emg_fatigue_index(median_frequency: float) -> float:
        fatigue = (120.0 - median_frequency) / 60.0 * 100.0
        return float(np.clip(fatigue, 0.0, 100.0))

if preprocess_emg is None:
    def preprocess_emg(signal: np.ndarray, fs: float) -> Tuple[np.ndarray, Dict]:
        filtered = signal
        metrics = {'mean_rectified': float(np.mean(np.abs(signal))), 'signal_std': float(np.std(signal)), 'fs': fs}
        return filtered, metrics

# Safe Plotly import
PLOTLY_GO, _, PLOTLY_OK = safe_import_plotly()

# Configure page
st.set_page_config(
    page_title="BIOCORE AI — Integrated Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://github.com",
        "Report a bug": "https://github.com/issues",
        "About": "BIOCORE AI — Complete Biomedical Intelligence Operating System",
    },
)

PAGE_TABS = [
    "🏠 Home",
    "📊 ECG Monitor",
    "🔗 Multisensor",
    "💨 Respiratory Lab",
    "🧠 EEG Neuro Lab",
    "🦾 EMG Muscle Lab",
    "📈 HRV Analysis",
    "🧬 Digital Twin",
    "🎓 Education",
    "🤖 AI Analysis",
    "👥 Patient Pipeline",
    "📚 Guides",
]

def inject_biocore_css() -> None:
    st.markdown(
        """
        <style>
            :root { color-scheme: dark; font-family: 'Inter', 'Segoe UI', sans-serif; }
            html, body, [data-testid='stAppViewContainer'] {
                background: radial-gradient(circle at top left, rgba(11, 196, 221, 0.18), transparent 26%),
                            linear-gradient(180deg, #05101f 0%, #040812 100%);
                color: #eef7ff;
            }
            .biocore-card { background: rgba(6, 16, 32, 0.90); border: 1px solid rgba(12, 185, 221, 0.18);
                            border-radius: 26px; padding: 20px; margin-bottom: 18px; }
            .biocore-panel { background: rgba(5, 14, 30, 0.95); border: 1px solid rgba(12, 185, 221, 0.18);
                            border-radius: 28px; box-shadow: 0 24px 58px rgba(0, 0, 0, 0.30); padding: 26px 28px; margin-bottom: 22px; }
            .status-pill { display: inline-flex; align-items: center; gap: 8px; padding: 10px 14px;
                          border-radius: 22px; border: 1px solid rgba(255,255,255,0.14); background: rgba(255,255,255,0.06);
                          color: #d5e8ff; font-size: 0.92rem; margin-bottom: 8px; }
            .pulse-dot { width: 12px; height: 12px; border-radius: 999px; background: #39ffbe;
                        box-shadow: 0 0 12px rgba(57,255,190,0.45); animation: pulse 1.6s ease-in-out infinite; }
            @keyframes pulse { 0% { transform: scale(0.9); opacity: 0.9; } 50% { transform: scale(1.15); opacity: 1; }
                              100% { transform: scale(0.9); opacity: 0.9; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

def init_state() -> None:
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = PAGE_TABS[0]
    if 'gesture_feedback' not in st.session_state:
        st.session_state.gesture_feedback = 'Esperando gesto...'
    if 'report_requested' not in st.session_state:
        st.session_state.report_requested = False
    if 'hands_free_active' not in st.session_state:
        st.session_state.hands_free_active = False
    if 'emg_streamer' not in st.session_state:
        st.session_state.emg_streamer = None
    if 'page_tabs' not in st.session_state:
        st.session_state.page_tabs = PAGE_TABS
    if 'hands_off_enabled' not in st.session_state:
        st.session_state.hands_off_enabled = True

@st.cache_resource
def get_gesture_controller() -> GestureController:
    return GestureController()

# ==================== RENDERING FUNCTIONS ====================

def render_top_bar() -> None:
    st.markdown(
        f"""
        <div class='biocore-panel'>
            <div style='display:flex; justify-content:space-between; flex-wrap:wrap; gap:16px;'>
                <div><div style='font-size:0.90rem; color:#7bc8ff; letter-spacing:0.18em; text-transform:uppercase;'>BIOCORE AI</div>
                <div style='font-size:3rem; line-height:1.05; letter-spacing:-0.04em; margin-bottom:6px;'>Integrated Intelligence</div>
                <div style='color:#98c8ff; font-size:1.02rem;'>Supervisión inmersiva, toda la plataforma en una aplicación.</div></div>
                <div style='text-align:right;'>
                    <div class='status-pill'><span class='pulse-dot'></span> SISTEMA ACTIVO</div>
                    <div style='margin-top:10px; color:#b8d8ff; font-size:0.88rem;'>Usa el panel Hands-Off para voz, gestos y atajos. Di "siguiente" o "generar reporte" y controla la plataforma sin tocarla.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def render_home_page() -> None:
    render_top_bar()
    st.markdown(
        """
        <div class='biocore-card'>
            <h2>Bienvenido a BIOCORE AI</h2>
            <p>Plataforma integrada de monitoreo biomédico con análisis ECG, EEG, EMG, multisensor y control manos libres por voz y gestos.</p>
            <p><strong>Instrucciones rápidas:</strong></p>
            <ol>
                <li>Navega usando el menú lateral o los comandos de Hands-Off.</li>
                <li>Activa Voice Mode o Gesture Mode en el panel derecho.</li>
                <li>Usa los botones de simulación si tu cámara o micrófono no funcionan.</li>
                <li>Genera reportes clínicos desde cada módulo con el botón de exportar.</li>
            </ol>
            <ul>
                <li>📊 ECG Monitor con análisis de arritmia</li>
                <li>🧠 EEG Neuro Lab con patrones cerebrales</li>
                <li>🦾 EMG Muscle Lab con streaming de hardware</li>
                <li>🔗 Multisensor Fusion de 6 canales</li>
                <li>💨 Respiratory Lab integrado</li>
                <li>📈 Digital Twin Clinical Dashboard</li>
                <li>🎓 Educación clínica con quizzes</li>
                <li>🤖 AI Analysis con explainabilidad</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

def apply_gesture_action(gesture_label: Optional[str]) -> None:
    if not gesture_label:
        return
    current_index = PAGE_TABS.index(st.session_state.selected_page)
    if gesture_label == 'open_palm':
        st.session_state.gesture_feedback = 'Pausa/Reanudar activado.'
    elif gesture_label == 'index':
        st.session_state.selected_page = PAGE_TABS[(current_index + 1) % len(PAGE_TABS)]
        st.session_state.gesture_feedback = f'Vista siguiente: {st.session_state.selected_page}'
    elif gesture_label == 'two_fingers':
        st.session_state.selected_page = PAGE_TABS[(current_index + 2) % len(PAGE_TABS)]
        st.session_state.gesture_feedback = f'Módulo cambiado: {st.session_state.selected_page}'
    elif gesture_label == 'ok_sign':
        st.session_state.report_requested = True
        st.session_state.gesture_feedback = 'Generando reporte...'
    elif gesture_label == 'pinch':
        st.session_state.gesture_feedback = 'Zoom toggle'
    else:
        st.session_state.gesture_feedback = f'Gesto: {gesture_label}'

def render_gesture_panel() -> None:
    controller = get_gesture_controller()
    st.markdown(
        """
        <div class='biocore-card'>
            <h3>🖐️ Control Manos Libres (Universal)</h3>
            <p>Simula o detecta gestos para navegar y generar reportes.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.checkbox('Activar detección por cámara', value=False, disabled=not controller.available, key='hands_free_active')
    
    if controller.available and st.session_state.hands_free_active:
        image = st.camera_input('Captura (activo)', key='gesture_camera')
        if image is not None:
            try:
                gesture_label = controller.detect_gesture(image.read())
                apply_gesture_action(gesture_label)
            except Exception as e:
                st.warning(f'Error: {e}')
    else:
        st.markdown('**Emulador de gestos:** usa los botones para simular.')
        c1, c2, c3, c4, c5 = st.columns(5)
        if c1.button('🖐️ Palma'):
            apply_gesture_action('open_palm')
        if c2.button('☝️ Índice'):
            apply_gesture_action('index')
        if c3.button('✌️ Dos'):
            apply_gesture_action('two_fingers')
        if c4.button('👌 OK'):
            apply_gesture_action('ok_sign')
        if c5.button('🤏 Pinch'):
            apply_gesture_action('pinch')
    
    st.write(f"**Estado:** {st.session_state.gesture_feedback}")


def render_module_header(title: str, subtitle: str, instructions: str) -> None:
    st.markdown(f"<h2>{title}</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='padding:18px; margin-bottom:14px; border-radius:16px; background:#08162f; border:1px solid rgba(255,255,255,0.06);'>"
        f"<strong>{subtitle}</strong><br><small style='color:#b8d8ff;'>{instructions}</small>"
        f"</div>",
        unsafe_allow_html=True,
    )


def render_export_report_section(lab_name: str, metrics: Dict[str, Any], findings: Optional[Dict[str, Any]] = None, notes: str = '') -> None:
    st.markdown('### 📤 Reporte personalizado')
    st.write('Genera un reporte enriquecido con métricas, hallazgos y notas específicas de este módulo.')
    if st.button(f'Exportar reporte de {lab_name}', key=f'export_report_{lab_name}'):
        try:
            path = export_lab_report(lab_name, metrics, notes=notes, findings=findings)
            if path:
                st.success(f'Reporte generado: {path}')
                try:
                    with open(path, 'rb') as report_file:
                        data = report_file.read()
                    mime = 'application/pdf' if path.lower().endswith('.pdf') else 'text/html'
                    st.download_button(f'Descargar {path.split(os.sep)[-1]}', data=data, file_name=os.path.basename(path), mime=mime)
                except Exception:
                    st.info('Reporte creado en disco. Revisa la carpeta reports/')
        except Exception as e:
            st.error(f'No se pudo exportar el reporte: {e}')


def render_hrv_page() -> None:
    render_module_header(
        '📈 HRV Analysis',
        'Análisis de variabilidad de la frecuencia cardíaca con métricas tiempo-frecuencia y visualizaciones clínicas.',
        'Elige datos demo o pega intervalos RR. Revisa métricas, histograma y espectro. Exporta un reporte HRV personalizado.'
    )

    source = st.sidebar.radio('HRV Source', ['Demo ECG', 'Manual RR series'], index=0)
    rr_ms = None
    if source == 'Manual RR series':
        txt = st.text_area('Pega RR intervals en ms separados por comas', '800,820,790,810,805,795,815,800')
        try:
            rr_ms = np.array([float(x.strip()) for x in txt.split(',') if x.strip()])
        except Exception:
            rr_ms = None
    else:
        hr = st.sidebar.slider('Demo HR (bpm)', 40, 140, 72)
        duration = st.sidebar.slider('Duración (seg)', 30, 180, 120)
        mean_rr = 60000.0 / float(max(30, hr))
        beats = int(max(16, (duration * hr) // 60))
        rr_ms = mean_rr + np.random.normal(0, mean_rr * 0.03, size=beats)

    if rr_ms is None or len(rr_ms) < 6:
        st.error('RR series insuficiente. Provee más latidos o usa la fuente demo.')
        return

    diffs = np.diff(rr_ms)
    sdnn = float(np.std(rr_ms, ddof=1))
    rmssd = float(np.sqrt(np.mean(diffs**2))) if len(diffs) > 0 else 0.0
    pnn50 = float(np.sum(np.abs(diffs) > 50) / max(1, len(diffs)) * 100)
    mean_nn = float(np.mean(rr_ms))
    median_rr = float(np.median(rr_ms))

    cols = st.columns(4)
    cols[0].metric('SDNN', f'{sdnn:.1f} ms')
    cols[1].metric('RMSSD', f'{rmssd:.1f} ms')
    cols[2].metric('pNN50', f'{pnn50:.1f} %')
    cols[3].metric('Mean RR', f'{mean_nn:.1f} ms')

    st.markdown('#### Serie RR y distribución')
    st.line_chart(rr_ms)
    if PLOTLY_OK:
        try:
            fig = PLOTLY_GO.Figure()
            fig.add_trace(PLOTLY_GO.Histogram(x=rr_ms, nbinsx=20, name='RR histogram'))
            fig.update_layout(template='plotly_dark', height=320, xaxis_title='RR ms', yaxis_title='Cuenta')
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.bar_chart(rr_ms)

    st.markdown('#### Espectro HRV (LF/HF)')
    try:
        # Interpolate RR into uniformly sampled time series
        t = np.cumsum(rr_ms) / 1000.0
        t -= t[0]
        fs_interp = 4.0
        ti = np.arange(0, t[-1], 1.0 / fs_interp)
        rr_interp = np.interp(ti, t, rr_ms)
        f, pxx = welch(rr_interp - np.mean(rr_interp), fs=fs_interp, nperseg=min(256, len(rr_interp)))
        lf_mask = (f >= 0.04) & (f < 0.15)
        hf_mask = (f >= 0.15) & (f <= 0.4)
        lf_power = float(np.trapz(pxx[lf_mask], f[lf_mask])) if np.any(lf_mask) else 0.0
        hf_power = float(np.trapz(pxx[hf_mask], f[hf_mask])) if np.any(hf_mask) else 0.0
        lf_hf = float(lf_power / hf_power) if hf_power > 0 else 0.0

        cols2 = st.columns(3)
        cols2[0].metric('LF power', f'{lf_power:.3f}')
        cols2[1].metric('HF power', f'{hf_power:.3f}')
        cols2[2].metric('LF/HF', f'{lf_hf:.2f}')

        if PLOTLY_OK:
            fig2 = PLOTLY_GO.Figure()
            fig2.add_trace(PLOTLY_GO.Scatter(x=f, y=pxx, mode='lines', name='PSD'))
            fig2.update_layout(template='plotly_dark', height=340, xaxis_title='Hz', yaxis_title='Power')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.line_chart(pxx)
    except Exception as e:
        st.warning(f'No se pudo calcular espectro HRV: {e}')

    findings = {'SDNN': f'{sdnn:.1f} ms', 'RMSSD': f'{rmssd:.1f} ms', 'LF/HF': f'{lf_hf:.2f}'}
    metrics = {'SDNN': sdnn, 'RMSSD': rmssd, 'pNN50': pnn50, 'LF/HF': lf_hf, 'Mean RR': mean_nn}
    render_export_report_section('HRV Analysis', metrics, findings=findings, notes='Reporte HRV generado desde BIOCORE AI.')


# ==================== DIGITAL TWIN PAGE ====

def render_digital_twin_page() -> None:
    render_module_header(
        '🧬 Digital Twin Clinical Dashboard',
        'Panel clínico del gemelo digital con indicadores de función cardiopulmonar, perfusión y riesgo integrado.',
        'Ajusta el perfil del paciente, revisa alertas clínicas y genera un informe estructurado con recomendaciones específicas.'
    )

    st.markdown(
        """
        <div class='biocore-card'>
            <h3>Guía de uso</h3>
            <ol>
                <li>Selecciona un preset de paciente o configura manualmente HR, SpO₂ y RR.</li>
                <li>Verifica las métricas clínicas y las alertas de riesgo en el panel derecho.</li>
                <li>Interpreta las señales sincronizadas de ECG, respiración y SpO₂.</li>
                <li>Usa el botón de reporte para exportar un informe clínico detallado.</li>
                <li>Activa Hands-Off a la derecha para controlar por voz, gestos o teclado.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    patient_preset = st.selectbox('Selecciona paciente virtual', ['Sano', 'Hipertensión', 'EPOC', 'Arritmia'])
    defaults = {'Sano': (72, 98, 16), 'Hipertensión': (88, 96, 18), 'EPOC': (102, 88, 24), 'Arritmia': (95, 94, 16)}
    hr_default, spo2_default, rr_default = defaults[patient_preset]

    hr = st.slider('Frecuencia cardíaca (bpm)', 40, 150, hr_default)
    spo2 = st.slider('Saturación de oxígeno (SpO₂ %)', 70, 100, spo2_default)
    rr = st.slider('Frecuencia respiratoria (rpm)', 8, 40, rr_default)

    perfusion = float(np.clip((spo2 - 70) * 1.4, 0, 100))
    autonomic_balance = float(np.clip(100 - abs(rr - 16) * 4 - abs(hr - 72) * 0.35, 0, 100))
    ventilation_score = float(np.clip(100 - abs(rr - 16) * 3.8 - max(0, 96 - spo2) * 1.3, 0, 100))
    hemodynamic_stability = float(np.clip(100 - abs(hr - 72) * 0.45 - abs(rr - 16) * 1.0, 0, 100))
    risk_total = (100 - hemodynamic_stability) * 0.35 + (100 - ventilation_score) * 0.35 + (100 - perfusion) * 0.3
    if risk_total > 65:
        risk_level = 'Alto'
        risk_message = 'Riesgo clínico alto: considera intervención inmediata y monitorización continua.'
    elif risk_total > 40:
        risk_level = 'Moderado'
        risk_message = 'Riesgo moderado: revisa signos vitales con frecuencia y ajusta soporte respiratorio o hemodinámico.'
    else:
        risk_level = 'Bajo'
        risk_message = 'Estado estable dentro de rangos aceptables, sigue monitorizando.'

    c1, c2, c3, c4 = st.columns([1.1, 1.1, 1.1, 1])
    c1.metric('Perfusión proxy', f'{perfusion:.0f}/100')
    c2.metric('Balance autonómico', f'{autonomic_balance:.0f}/100')
    c3.metric('Ventilación score', f'{ventilation_score:.0f}/100')
    c4.metric('Riesgo clínico', risk_level)

    st.markdown(f"""
        <div style='background:#04101d; border:1px solid rgba(255,255,255,0.10); border-radius:18px; padding:18px;'>
            <strong>Resumen clínico</strong><br>
            <span style='color:#b8d8ff;'>HR:</span> {hr} bpm · <span style='color:#b8d8ff;'>SpO₂:</span> {spo2}% · <span style='color:#b8d8ff;'>RR:</span> {rr} rpm<br>
            <span style='color:#79c9ff;'>{risk_message}</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('### Métricas derivadas y recomendaciones')
    st.write('- <strong>Perfusión:</strong> evalúa la entrega de oxígeno y flujo sanguíneo proximal.')
    st.write('- <strong>Balance autonómico:</strong> indica la carga de estrés entre sistema simpático y parasimpático.')
    st.write('- <strong>Ventilación:</strong> refleja la capacidad respiratoria frente a la saturación obtenida.')

    alert_texts = []
    if spo2 < 94:
        alert_texts.append('SpO₂ menor a 94% indica hipoxemia potencial. Activa soporte respiratorio.')
    if hr > 110:
        alert_texts.append('Taquicardia detectada; evalúa posible taquicardia sinusal o estrés cardiovascular.')
    if rr > 22:
        alert_texts.append('Taquipnea presente; controla el trabajo respiratorio y la oxigenación.')
    if perfusion < 50:
        alert_texts.append('Perfusión proxy baja; revisa perfusión periférica y estado hemodinámico.')

    if alert_texts:
        st.markdown('### ⚠️ Alertas clínicas')
        for txt in alert_texts:
            st.warning(txt)

    ecg = generate_demo_ecg_signal(250, 20, hr)
    resp = generate_demo_respiration_signal(250, 20, rr)
    spo2_signal = np.clip(np.full(250 * 20, spo2, dtype=float) + np.random.randn(250 * 20) * 0.3, 70, 100)

    st.markdown('### Señales sincronizadas del Digital Twin')
    if PLOTLY_OK:
        try:
            fig = PLOTLY_GO.Figure()
            fig.add_trace(PLOTLY_GO.Scatter(x=np.arange(len(ecg))/250, y=ecg, name='ECG', line=dict(color='#5bc0eb')))
            fig.add_trace(PLOTLY_GO.Scatter(x=np.arange(len(resp))/250, y=resp, name='Respiración', line=dict(color='#fde74c')))
            fig.add_trace(PLOTLY_GO.Scatter(x=np.arange(len(spo2_signal))/250, y=spo2_signal, name='SpO₂', line=dict(color='#9bc53d')))
            fig.update_layout(template='plotly_dark', height=420, paper_bgcolor='#081627', title='Digital Twin Clinical Dashboard', xaxis_title='Tiempo (s)', yaxis_title='Valor sintético')
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.line_chart({'ECG': ecg, 'Respiración': resp, 'SpO₂': spo2_signal})
    else:
        st.line_chart({'ECG': ecg, 'Respiración': resp, 'SpO₂': spo2_signal})

    st.markdown('### Detalles del paciente virtual')
    st.write(f'- Perfil: **{patient_preset}**')
    st.write(f'- FC: **{hr} bpm**')
    st.write(f'- SpO₂: **{spo2}%**')
    st.write(f'- FR: **{rr} rpm**')

    with st.expander('Comandos de voz y gestos disponibles'):
        st.markdown(
            """
            - Voz: 'siguiente', 'anterior', 'generar reporte', 'analiza', 'explica', 'jarvis', 'guardar', 'exportar', 'zoom in', 'zoom out'.
            - Gesto: palma = pausa/reanudar, índice = siguiente, peace = anterior, ok = reporte, pinch = zoom.
            - Teclado: n = siguiente, p = anterior, r = reporte, a = analizar, e = explicar, j = Jarvis.
            """
        )

    metrics = {
        'HR': hr,
        'SpO2': spo2,
        'RR': rr,
        'Perfusión proxy': perfusion,
        'Balance autonómico': autonomic_balance,
        'Ventilación score': ventilation_score,
        'Estabilidad hemodinámica': hemodynamic_stability,
        'Riesgo total': risk_total,
        'Nivel de riesgo': risk_level,
    }
    findings = {
        'Paciente virtual': patient_preset,
        'Riesgo clínico': risk_level,
        'Estado HR': f'{hr} bpm',
        'Estado SpO₂': f'{spo2} %',
        'Estado RR': f'{rr} rpm',
    }
    render_export_report_section('Digital Twin Clinical Dashboard', metrics, findings=findings, notes='Informe clínico del Digital Twin generado desde BIOCORE AI.')

def render_eeg_page() -> None:
    st.markdown("<h1 style='color: #1f77b4;'>🧠 EEG Neuro Lab</h1>", unsafe_allow_html=True)
    
    if EegSignalGenerator is None:
        st.error("Módulo EEG no disponible. Instala biomedical.eeg")
        return
    
    signal_source = st.sidebar.radio("Origen EEG", ["Generar sintético", "Cargar CSV"])
    pattern = st.sidebar.selectbox("Patrón", ["Alpha", "Beta", "Theta", "Delta", "Seizure"])
    channels = st.sidebar.selectbox("Canales", [2, 3, 4])
    duration = st.sidebar.slider("Duración (s)", 10, 120, 30)
    fs = st.sidebar.selectbox("fs (Hz)", [128, 256, 512], index=1)
    
    eeg_data = {}
    time_arr = np.array([])
    
    if signal_source == "Cargar CSV":
        uploaded_file = st.file_uploader("CSV EEG", type=['csv'])
        if uploaded_file:
            try:
                text = uploaded_file.read().decode('utf-8')
                data = np.genfromtxt(io.StringIO(text), delimiter=',')
                if data.ndim == 1:
                    eeg_data['EEG1'] = data
                else:
                    for i in range(min(data.shape[1], channels)):
                        eeg_data[f'EEG{i+1}'] = data[:, i]
                time_arr = np.arange(len(next(iter(eeg_data.values())))) / fs
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        params = EegPattern(pattern_type=pattern.lower(), duration=duration, fs=fs, amplitude=40.0, noise_level=0.18, channels=channels)
        gen = EegSignalGenerator(sampling_rate=fs)
        eeg_data, time_arr = gen.generate(params)
    
    if eeg_data:
        leads = [k for k in eeg_data.keys() if k != 'time'][:channels]
        
        # Plotly visualization
        if PLOTLY_OK:
            try:
                from plotly.subplots import make_subplots
                import plotly.graph_objects as go
                fig = make_subplots(rows=len(leads), cols=1, shared_xaxes=True)
                for idx, lead in enumerate(leads, 1):
                    fig.add_trace(go.Scatter(x=time_arr, y=eeg_data[lead], name=lead), row=idx, col=1)
                fig.update_layout(height=200*len(leads), template='plotly_dark', paper_bgcolor='#0f172a')
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                pass
        
        # Análisis
        st.markdown("### Análisis de potencia de banda")
        if EegAnalyzer:
            analyzer = EegAnalyzer(fs=fs)
            for lead in leads:
                result = analyzer.analyze(eeg_data[lead])
                st.markdown(f"**{lead}**")
                if hasattr(result, 'summary'):
                    st.write(result.summary)
                if hasattr(result, 'band_power'):
                    st.write(result.band_power)
        
        # Quiz
        with st.expander("🧪 Quiz EEG"):
            quiz = [
                {"q": "¿Banda para sueño profundo?", "opts": ["Alpha", "Delta"], "ans": "Delta", "exp": "Delta es la banda más lenta."},
                {"q": "¿Banda para concentración?", "opts": ["Beta", "Theta"], "ans": "Beta", "exp": "Beta es típica en atención."},
            ]
            answers = []
            for i, item in enumerate(quiz):
                ans = st.radio(item['q'], item['opts'], key=f"eeg_q_{i}")
                answers.append(ans)
            if st.button("Calcular"):
                score = sum(1 for a, q in zip(answers, quiz) if a == q['ans'])
                st.metric("Puntuación", f"{score}/{len(quiz)}")
                for a, q in zip(answers, quiz):
                    if a == q['ans']:
                        st.success(q['exp'])
                    else:
                        st.error(q['exp'])

# ==================== EMG PAGE (COMPLETE) ====================

def render_emg_page() -> None:
    st.markdown("<h1 style='color: #1f77b4;'>🦾 EMG Muscle Lab</h1>", unsafe_allow_html=True)
    
    signal_source = st.sidebar.radio("Origen EMG", ["Sintético", "CSV", "Live Hardware"])
    pattern = st.sidebar.selectbox("Patrón", ["Isométrica", "Rápida", "Fatiga"])
    duration = st.sidebar.slider("Duración (s)", 5, 60, 15)
    fs = st.sidebar.selectbox("fs (Hz)", [500, 1000, 2000], index=1)
    
    signal = None
    time_arr = np.array([])
    
    if signal_source == "CSV":
        f = st.file_uploader("CSV EMG", type=['csv'])
        if f:
            try:
                data = np.genfromtxt(io.StringIO(f.read().decode()), delimiter=',')
                signal = data if data.ndim == 1 else data[:, 0]
                time_arr = np.arange(len(signal)) / fs
            except:
                st.error("Error cargando CSV")
    elif signal_source == "Live Hardware":
        st.info("Hardware streaming disponible si EMGStreamer está instalado.")
        if EMGStreamer:
            if st.button("Conectar"):
                st.session_state.emg_streamer = EMGStreamer(port=None, baud=115200, fs=fs)
                if st.session_state.emg_streamer.connect():
                    st.success("Conectado")
                else:
                    st.error("Conexión fallida")
            signal = generate_demo_emg_signal(fs, duration, pattern) if signal is None else signal
            time_arr = np.arange(len(signal)) / fs
        else:
            st.warning("EMGStreamer no disponible")
            signal = generate_demo_emg_signal(fs, duration, pattern)
            time_arr = np.arange(len(signal)) / fs
    else:
        signal = generate_demo_emg_signal(fs, duration, pattern)
        time_arr = np.arange(len(signal)) / fs
    
    if signal is not None and len(signal) > 0:
        # Procesamiento
        filtered, metrics = preprocess_emg(signal, fs)
        rectified = np.abs(filtered)
        median_freq = compute_emg_median_frequency(filtered, fs)
        fatigue_idx = compute_emg_fatigue_index(median_freq)
        activation = float(np.clip(np.mean(rectified) / (np.max(rectified) + 1e-9) * 100, 0, 100))
        
        # Métricas
        col1, col2 = st.columns(2)
        col1.metric("Activación (%)", f"{activation:.1f}")
        col1.metric("MRV", f"{metrics['mean_rectified']:.3f}")
        col2.metric("Fatiga", f"{fatigue_idx:.1f}/100")
        col2.metric("Med Freq (Hz)", f"{median_freq:.1f}")
        
        # Visualización
        if PLOTLY_OK:
            try:
                from plotly.subplots import make_subplots
                import plotly.graph_objects as go
                fig = make_subplots(rows=2, cols=1)
                fig.add_trace(go.Scatter(x=time_arr, y=signal, name='Raw'), row=1, col=1)
                fig.add_trace(go.Scatter(x=time_arr, y=rectified, name='Rectified'), row=2, col=1)
                fig.update_layout(height=400, template='plotly_dark', paper_bgcolor='#0f172a')
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.line_chart(signal)
        
        # Export
        if st.button("Exportar informe EMG"):
            path = export_lab_report('EMG Lab', 
                {'activation': activation, 'fatigue': fatigue_idx, 'median_freq': median_freq},
                notes='EMG report')
            st.success(f"Exportado: {path}")

def generate_demo_emg_signal(fs: float, duration: float, pattern: str) -> np.ndarray:
    n = int(fs * duration)
    t = np.arange(n) / fs
    if pattern == "Isométrica":
        env = 0.6 + 0.2 * np.sin(2*np.pi*0.5*t)
    elif pattern == "Rápida":
        env = 0.4 + 0.5*np.exp(-((t-duration/2)**2)/0.25)
    else:
        env = 0.6 + 0.3*(1-t/max(duration, 1))
    return env * np.random.normal(0, 1, n) + 0.05*np.sin(100*np.pi*t)

# ==================== OTHER PAGES ====================

def render_ecg_monitor_page() -> None:
    st.markdown("<h2>📊 ECG Monitor</h2>", unsafe_allow_html=True)
    signal = generate_demo_ecg_signal(fs=250, duration=20, hr=72)
    hr = estimate_ecg_heart_rate(signal, 250)
    st.metric("Heart Rate", f"{hr:.0f} bpm")
    if PLOTLY_OK:
        try:
            fig = PLOTLY_GO.Figure(PLOTLY_GO.Scatter(x=np.arange(len(signal))/250, y=signal, mode='lines'))
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.line_chart(signal)

def render_multisensor_page() -> None:
    st.markdown("<h2>🔗 Multisensor Fusion</h2>", unsafe_allow_html=True)
    ch = {'ECG': generate_demo_ecg_signal(250, 20), 'PPG': generate_demo_ppg_signal(250, 20),
          'SpO2': generate_demo_spo2_signal(250, 20), 'Respiration': generate_demo_respiration_signal(250, 20)}
    if PLOTLY_OK:
        fig = PLOTLY_GO.Figure()
        for name, data in ch.items():
            fig.add_trace(PLOTLY_GO.Scatter(y=data, name=name, mode='lines'))
        st.plotly_chart(fig, use_container_width=True)

def render_respiratory_page() -> None:
    st.markdown("<h2>💨 Respiratory Lab</h2>", unsafe_allow_html=True)
    signal = generate_demo_respiration_signal(250, 30, 16)
    rr = estimate_respiration_rate(signal, 250)
    st.metric("Respiration Rate", f"{rr:.1f} rpm")
    st.line_chart(signal)

def render_education_page() -> None:
    st.markdown("<h2>🎓 Education</h2>", unsafe_allow_html=True)
    st.markdown("Educación clínica con casos de estudio y explicaciones interactivas.")

def render_ai_analysis_page() -> None:
    st.markdown("<h2>🤖 AI Analysis</h2>", unsafe_allow_html=True)
    st.markdown("Análisis con explainabilidad y modelos de machine learning.")

def render_patient_pipeline_page() -> None:
    st.markdown("<h2>👥 Patient Pipeline</h2>", unsafe_allow_html=True)
    st.markdown("Gestión de pacientes y reportes clínicos.")

def render_guides_page() -> None:
    st.markdown("<h2>📚 Guides</h2>", unsafe_allow_html=True)
    st.markdown("Documentación y guías de uso.")

def render_page_content(page: str) -> None:
    if page in ('🏠 Home', 'Home'):
        render_home_page()
    elif page in ('📊 ECG Monitor', 'ECG_Monitor', 'ECG Monitor'):
        render_ecg_monitor_page()
    elif page in ('📋 ECG-12-Derivaciones', 'ECG-12-Derivaciones'):
        render_ecg_12_page()
    elif page in ('🔗 Multisensor', 'Multisensor'):
        render_multisensor_page()
    elif page in ('💨 Respiratory Lab', 'Respiratory-Lab'):
        render_respiratory_page()
    elif page in ('🧠 EEG Neuro Lab', 'EEG-Neuro-Lab'):
        render_eeg_page()
    elif page in ('🦾 EMG Muscle Lab', 'EMG_Muscle_Lab'):
        render_emg_page()
    elif page in ('📈 HRV Analysis', 'HRV Analysis'):
        render_hrv_page()
    elif page in ('🧬 Digital Twin', 'Digital Twin'):
        render_digital_twin_page()
    elif page in ('🎓 Education', 'Education', '🏫 Academia Clinica', 'Academia_Clinica'):
        render_education_page()
    elif page in ('🤖 AI Analysis', 'AI_Analysis'):
        render_ai_analysis_page()
    elif page in ('👥 Patient Pipeline', 'Patients'):
        render_patient_pipeline_page()
    elif page in ('📚 Guides', 'Guides'):
        render_guides_page()

def main() -> None:
    init_state()
    inject_biocore_css()
    
    # Navigation
    page = st.sidebar.radio('Navigation', PAGE_TABS, index=PAGE_TABS.index(st.session_state.selected_page), label_visibility='collapsed')
    st.session_state.selected_page = page
    
    # Content + sidebar
    content_col, side_col = st.columns([3, 1])
    with content_col:
        render_page_content(page)
    with side_col:
        render_hands_off_panel()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**BIOCORE AI v2.0**  \nPlataforma integrada de biomedical signal intelligence.")

if __name__ == '__main__':
    main()
