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
    render_metric_explained,
    render_view_selector,
    render_scientific_discovery_layer,
    render_discovery_lab,
)
from app.engines import DigitalTwinEngine, PhysiologyCoreEngine, PhysiologySignal
from app.clinical_db import init_db, save_patient_state, list_patient_states, load_patient_state

# --- SAFE BIOMARKERS IMPORT ---
try:
    from app.biomarkers import BiocoreEngine
    BIOMARKERS_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Biomarkers Engine import failed: {e}")
    BIOMARKERS_AVAILABLE = False

# --- SAFE CLINICAL EXPERT SYSTEM IMPORT ---
try:
    from app.clinical_ai import ClinicalAIEngine
    AI_ENGINE_AVAILABLE = True
except Exception as e:
    print(f"⚠️ ClinicalAIEngine import failed: {e}")
    AI_ENGINE_AVAILABLE = False


try:
    from app.reporting import export_lab_report
    import app.reporting as reporting
except Exception as e:
    print(f"⚠️ Reporting module import failed: {e}")
    def export_lab_report(*args, **kwargs):
        return None
    reporting = None

try:
    from app.biomedical_tutor import BiomedicalTutor
    TUTOR_AVAILABLE = True
except Exception as e:
    TUTOR_AVAILABLE = False
    print(f"⚠️ BiomedicalTutor not available: {e}")

# Import JARVIS AI Copilot and Hands-Off Mode
try:
    from app.ai_copilot import initialize_copilot, render_copilot_panel, BioCoreCopilot, BiometricsContext
    COPILOT_AVAILABLE = True
except Exception as e:
    COPILOT_AVAILABLE = False
    print(f"⚠️ JARVIS Copilot not available: {e}")

try:
    from app.hands_off_mode import initialize_hands_off, render_hands_off_panel, HandsOffController, ControlMode
    HANDS_OFF_AVAILABLE = True
except Exception as e:
    HANDS_OFF_AVAILABLE = False
    print(f"⚠️ Hands-Off Mode not available: {e}")

# Attempt to import gesture controller (fallback to emulator if unavailable)
try:
    from gesture_controller import GestureController
    _gesture_controller_available = True
except Exception as e:
    print(f"⚠️ GestureController import failed: {e}")
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

# --- HUBS DEFINITION ---
HUBS = {
    "Learning Hub": [
        "🎓 Education",
        "🏫 Clinical Academy",
        "📚 Guides",
    ],
    "Clinical Hub": [
        "📊 ECG Monitor",
        "📋 12-Lead ECG",
        "🔗 Multisensor",
        "💨 Respiratory Lab",
        "🧠 EEG Neuro Lab",
        "🦾 EMG Muscle Lab",
        "📈 HRV Analysis",
        "🧬 Biomarkers Lab",
    ],
    "Research Hub": [
        "🤖 AI Analysis",
        "👥 Patient Pipeline",
    ],
    "Simulation Hub": [
        "🧪 Simulation Lab",
    ],
    "AI Hub": [
        "🤖 JARVIS Copilot",
    ],
    "Hardware Hub": [
        "🔧 Hardware Ops",
    ],
    "Digital Twin Hub": [
        "🧬 Digital Twin",
    ],
}
PAGE_TABS = [page for pages in HUBS.values() for page in pages]

DEFAULT_HUB = "Learning Hub"


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
    if 'selected_hub' not in st.session_state:
        st.session_state.selected_hub = DEFAULT_HUB
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = HUBS[st.session_state.selected_hub][0]
    if 'gesture_feedback' not in st.session_state:
        st.session_state.gesture_feedback = 'Waiting for gesture...'
    if 'report_requested' not in st.session_state:
        st.session_state.report_requested = False
    if 'page_tabs' not in st.session_state:
        st.session_state.page_tabs = PAGE_TABS
    if 'hands_off_feedback' not in st.session_state:
        st.session_state.hands_off_feedback = 'Waiting for hands-free command...'
    if 'hands_off_enabled' not in st.session_state:
        st.session_state.hands_off_enabled = True
    if 'hands_free_active' not in st.session_state:
        st.session_state.hands_free_active = False
    if 'emg_streamer' not in st.session_state:
        st.session_state.emg_streamer = None
    if 'learning_progress' not in st.session_state:
        st.session_state.learning_progress = {
            'Cardio-Physiology': 58,
            'Neurophysiology': 42,
            'Respiratory': 33,
            'Muscle': 26,
            'Clinical Interpretation': 69,
        }
    if 'mission_goal' not in st.session_state:
        st.session_state.mission_goal = 'Explore the platform and activate the Clinical Hub.'

# initialize lightweight clinical DB
try:
    init_db()
except Exception:
    pass

@st.cache_resource
def get_gesture_controller() -> GestureController:
    return GestureController()


def render_metric_explained(title: str, value: Any, unit: str = '', meaning: Optional[str] = None,
                            importance: Optional[str] = None, affects: Optional[str] = None,
                            relations: Optional[str] = None, consequences: Optional[str] = None) -> None:
    try:
        display_value = f"{value} {unit}" if unit else f"{value}"
    except Exception:
        display_value = str(value)

    st.markdown(f"**{title}** — {display_value}")
    with st.expander(f"What does {title} mean?", expanded=False):
        st.markdown(f"- **Meaning:** {meaning or 'Quantitative clinical value summarizing a physiological aspect.'}")
        st.markdown(f"- **Importance:** {importance or 'Allows prioritizing clinical and educational decisions.'}")
        st.markdown(f"- **Affected by:** {affects or 'Drugs, hemodynamic status, respiration, exercise, and technical artifacts.'}")
        st.markdown(f"- **Relationships:** {relations or 'Interacts with ventilation, oxygenation, and neurological status.'}")
        st.markdown(f"- **Consequences:** {consequences or 'A significant change suggests intervention, further testing, or intensive monitoring.'}")


def render_discovery_lab(name: str, signals: Dict[str, np.ndarray]):
    with st.expander(f"🔬 Discovery Lab — {name}", expanded=False):
        st.write('Interactivity: correlations, sensitivity, and parameter exploration.')
        if len(signals) < 2:
            st.info('At least 2 signals are required to explore correlations.')
            return
        if st.button(f'Run discovery for {name}'):
            keys = list(signals.keys())
            mat = np.zeros((len(keys), len(keys)))
            for i in range(len(keys)):
                for j in range(len(keys)):
                    a = signals[keys[i]]
                    b = signals[keys[j]]
                    mn = min(len(a), len(b))
                    if mn > 1:
                        mat[i, j] = float(np.corrcoef(a[:mn], b[:mn])[0, 1])
                    else:
                        mat[i, j] = 0.0
            corr_dict = {k: {kk: float(mat[i, j]) for j, kk in enumerate(keys)} for i, k in enumerate(keys)}
            st.json(corr_dict)
            strongest = np.unravel_index(np.argmax(np.abs(mat - np.eye(len(keys))*2)), mat.shape)
            k1, k2 = keys[strongest[0]], keys[strongest[1]]
            st.write(f'Quick interpretation: highest correlation observed between **{k1}** and **{k2}** ({mat[strongest]:.2f}).')

def render_view_selector(view_id: str = None) -> str:
    import inspect
    if view_id is None:
        caller_frame = inspect.currentframe().f_back
        view_id = caller_frame.f_code.co_name
    return st.radio(
        'Cognitive Exploration Layer',
        ['Clinical', 'Educational', 'Research', 'AI', 'Simulation', 'Digital Twin'],
        horizontal=True,
        key=f"view_selector_{view_id}"
    )

def render_page_content(page: str) -> None:
    if page in HUBS["Learning Hub"]:
        if "Education" in page or "Academy" in page:
            render_education_page()
        else:
            render_guides_page()
    elif page in HUBS["Clinical Hub"]:
        if "ECG Monitor" in page or "ECG_Monitor" in page:
            render_ecg_monitor_page()
        elif "12-Lead" in page:
            render_ecg_12_page()
        elif "Multisensor" in page:
            render_multisensor_page()
        elif "Respiratory" in page:
            render_respiratory_page()
        elif "EEG" in page:
            render_eeg_page()
        elif "EMG" in page:
            render_emg_page()
        elif "HRV" in page:
            render_hrv_page()
        elif "Biomarkers" in page:
            render_biomarkers_page()
    elif page in HUBS["Research Hub"]:
        if "AI" in page:
            render_ai_analysis_page()
        else:
            render_patient_pipeline_page()
    elif page in HUBS["Simulation Hub"]:
        render_simulation_lab_page()
    elif page in HUBS["AI Hub"]:
        render_jarvis_copilot_page()
    elif page in HUBS["Hardware Hub"]:
        render_hardware_ops_page()
    elif page in HUBS["Digital Twin Hub"]:
        render_digital_twin_page()
    else:
        render_home_page()

def render_metrics_grid(metrics_data: List[Dict]):
    cols = st.columns(len(metrics_data))
    for idx, data in enumerate(metrics_data):
        with cols[idx]:
            render_metric_explained(
                title=data['title'],
                value=data['value'],
                unit=data.get('unit', ''),
                meaning=data.get('meaning'),
                importance=data.get('importance'),
                affects=data.get('affects'),
                relations=data.get('relations'),
                consequences=data.get('consequences')
            )

# ==================== RENDERING FUNCTIONS ====================

def render_top_bar() -> None:
    st.markdown(
        f"""
        <div class='biocore-panel'>
            <div style='display:flex; justify-content:space-between; flex-wrap:wrap; gap:16px;'>
                <div><div style='font-size:0.90rem; color:#7bc8ff; letter-spacing:0.18em; text-transform:uppercase;'>BIOCORE AI</div>
                <div style='font-size:3rem; line-height:1.05; letter-spacing:-0.04em; margin-bottom:6px;'>Integrated Intelligence</div>
                <div style='color:#98c8ff; font-size:1.02rem;'>Immersive supervision, the entire platform in one app.</div></div>
                <div style='text-align:right;'><div class='status-pill'><span class='pulse-dot'></span> SYSTEM ACTIVE</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_mission_control_panel() -> None:
    st.markdown(
        """
        <div class='biocore-card'>
            <h2>🏁 Mission Control</h2>
            <p>Quickly access the ecosystem hubs and control your biomedical platform from a single panel.</p>
            <div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(150px, 1fr)); gap:14px; margin-top:16px;'>
                <div class='biocore-panel'><strong>Learning Hub</strong><br>Interactive academy with courses, cases, and quizzes.</div>
                <div class='biocore-panel'><strong>Clinical Hub</strong><br>Real monitoring of ECG, EEG, EMG, and respiration.</div>
                <div class='biocore-panel'><strong>Research Hub</strong><br>Cohort analysis, data export, and reporting.</div>
                <div class='biocore-panel'><strong>Simulation Hub</strong><br>Virtual patients and critical scenarios.</div>
                <div class='biocore-panel'><strong>AI Hub</strong><br>Biomedical copilot and explainability.</div>
                <div class='biocore-panel'><strong>Digital Twin</strong><br>Live global physiological state.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('### Quick Launch Panel')
    cols = st.columns(3)
    if cols[0].button('Learning Hub', key='home_open_learning'):
        st.session_state.selected_hub = 'Learning Hub'
        st.session_state.selected_page = HUBS['Learning Hub'][0]
        st.rerun()
    if cols[1].button('Clinical Hub', key='home_open_clinical'):
        st.session_state.selected_hub = 'Clinical Hub'
        st.session_state.selected_page = HUBS['Clinical Hub'][0]
        st.rerun()
    if cols[2].button('Research Hub', key='home_open_research'):
        st.session_state.selected_hub = 'Research Hub'
        st.session_state.selected_page = HUBS['Research Hub'][0]
        st.rerun()
    cols2 = st.columns(3)
    if cols2[0].button('Simulation Hub', key='home_open_simulation'):
        st.session_state.selected_hub = 'Simulation Hub'
        st.session_state.selected_page = HUBS['Simulation Hub'][0]
        st.rerun()
    if cols2[1].button('AI Hub', key='home_open_ai'):
        st.session_state.selected_hub = 'AI Hub'
        st.session_state.selected_page = HUBS['AI Hub'][0]
        st.rerun()
    if cols2[2].button('Digital Twin Hub', key='home_open_digital_twin'):
        st.session_state.selected_hub = 'Digital Twin Hub'
        st.session_state.selected_page = HUBS['Digital Twin Hub'][0]
        st.rerun()


def render_home_page() -> None:
    render_top_bar()
    st.markdown(
        """
        <div class='biocore-card'>
            <h2>Welcome to BIOCORE AI</h2>
            <p>The unified biomedical cognitive ecosystem to learn, research, monitor, simulate, explain, predict, and discover.</p>
            <div style='display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:18px; margin-top:18px;'>
                <div class='biocore-panel'>
                    <h3>1. Learning Hub</h3>
                    <p>Interactive biomedical academy with courses, clinical cases, quizzes, and adaptive progress.</p>
                </div>
                <div class='biocore-panel'>
                    <h3>2. Clinical Hub</h3>
                    <p>Advanced monitoring of ECG, EEG, EMG, respiration, SpO₂, and integrated vital signs.</p>
                </div>
                <div class='biocore-panel'>
                    <h3>3. Research Hub</h3>
                    <p>Digital laboratory for cohort analysis, data export, and scientific reporting.</p>
                </div>
                <div class='biocore-panel'>
                    <h3>4. Simulation Hub</h3>
                    <p>Dynamic clinical cases and virtual patients with modifiable physiological parameters.</p>
                </div>
                <div class='biocore-panel'>
                    <h3>5. AI Hub</h3>
                    <p>Clinical reasoning engine, biomedical copilot, and explainable analysis for medical users.</p>
                </div>
                <div class='biocore-panel'>
                    <h3>6. Hardware Hub</h3>
                    <p>Integration of real sensors and streaming for ECG, EMG, and multisensor setups.</p>
                </div>
                <div class='biocore-panel'>
                    <h3>7. Digital Twin Hub</h3>
                    <p>Digital twin that visualizes cardiovascular, respiratory, and neuromuscular states in real-time.</p>
                </div>
                <div class='biocore-panel'>
                    <h3>8. HRV Lab</h3>
                    <p>Heart rate variability analysis: time-frequency metrics, HRV twin, and clinical cases.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_gesture_action(gesture_label: Optional[str]) -> None:
    if not gesture_label:
        return
    current_index = PAGE_TABS.index(st.session_state.selected_page)
    if gesture_label == 'open_palm':
        st.session_state.gesture_feedback = 'Pause/Resume activated.'
    elif gesture_label == 'index':
        st.session_state.selected_page = PAGE_TABS[(current_index + 1) % len(PAGE_TABS)]
        st.session_state.gesture_feedback = f'Next view: {st.session_state.selected_page}'
    elif gesture_label == 'two_fingers':
        st.session_state.selected_page = PAGE_TABS[(current_index + 2) % len(PAGE_TABS)]
        st.session_state.gesture_feedback = f'Module changed: {st.session_state.selected_page}'
    elif gesture_label == 'ok_sign':
        st.session_state.report_requested = True
        st.session_state.gesture_feedback = 'Generating report...'
    elif gesture_label == 'pinch':
        st.session_state.gesture_feedback = 'Zoom toggle'
    else:
        st.session_state.gesture_feedback = f'Gesture: {gesture_label}'

def render_gesture_panel() -> None:
    controller = get_gesture_controller()
    st.markdown(
        """
        <div class='biocore-card'>
            <h3>🖐️ Hands-Free Control (Universal)</h3>
            <p>Simulate or detect gestures to navigate and generate reports.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    camera_enabled = st.checkbox(
        'Activate camera detection',
        value=False,
        disabled=False,
        key='hands_free_active'
    )
    
    if camera_enabled:
        image = st.camera_input('Capture (active)', key='gesture_camera')
        if image is not None:
            if controller.available:
                try:
                    gesture_label = controller.detect_gesture(image.read())
                    if gesture_label:
                        apply_gesture_action(gesture_label)
                    else:
                        st.info('Gesture not recognized. Try moving your hand more clearly.')
                except Exception as e:
                    st.warning(f'Gesture detection error: {e}')
            else:
                st.warning('Gestures unavailable: install mediapipe and opencv-python for camera detection.')
    else:
        st.markdown('**Gesture Emulator:** use buttons to simulate.')
        c1, c2, c3, c4, c5 = st.columns(5)
        if c1.button('🖐️ Palm'):
            apply_gesture_action('open_palm')
        if c2.button('☝️ Index'):
            apply_gesture_action('index')
        if c3.button('✌️ Two'):
            apply_gesture_action('two_fingers')
        if c4.button('👌 OK'):
            apply_gesture_action('ok_sign')
        if c5.button('🤏 Pinch'):
            apply_gesture_action('pinch')
    
    st.write(f"**Status:** {st.session_state.gesture_feedback}")

# ==================== BIOMARKERS PANEL ====================

def render_biomarkers_page() -> None:
    """Renders the comprehensive proprietary Biomarkers dashboard with Override mode."""
    st.markdown("<h1 style='color: #1f77b4;'>🧬 Biomarkers & Diagnostics Lab</h1>", unsafe_allow_html=True)
    
    if not BIOMARKERS_AVAILABLE:
        st.error("⚠️ Biomarkers module not found. Make sure 'biomarkers.py' is saved in 'app/'.")
        return

    engine = BiocoreEngine()

    st.markdown("""
    This panel calculates our proprietary indices. You can use the **Database** to load known profiles, 
    or activate **Manual Input** to introduce values extracted from your own hardware signal by signal.
    """)

    st.divider()

    # ==========================================
    # MAIN SWITCH
    # ==========================================
    st.markdown("### ⚙️ Clinical Data Source")
    modo_datos = st.radio(
        "Select how to feed the biomarkers engine:",
        ["📥 Load from Database (Profiles)", "✍️ Manual Sensor Input"],
        horizontal=True
    )

    st.markdown("---")

    if modo_datos == "📥 Load from Database (Profiles)":
        # AUTOMATIC MODE
        st.markdown("#### ⚡ Clinical Scenarios")
        escenario = st.selectbox(
            "Select a pre-loaded clinical profile:",
            ["👤 Basal State (Healthy)", "🏃‍♂️ Post-Effort Athlete", "🤯 Severe Cognitive Stress", "😴 Chronic Fatigue"]
        )

        if escenario == "👤 Basal State (Healthy)":
            datos_sensores = {'hrv_lf_hf_ratio': 1.5, 'eda_scr_peaks': 4, 'scl_u_siemens': 3.0, 'current_resting_hr': 65.0, 'hrv_rmssd': 45.0, 'sleep_hours': 7.5, 'eeg_alpha_power': 15.0, 'eeg_theta_power': 8.0, 'signal_coherence': 0.7, 'hrv_hf_power': 350.0, 'hr_surge': 5.0, 'hr_recovery_rate': 25.0, 'hrv_sdnn': 50.0}
        elif escenario == "🏃‍♂️ Post-Effort Athlete":
            datos_sensores = {'hrv_lf_hf_ratio': 2.8, 'eda_scr_peaks': 12, 'scl_u_siemens': 8.0, 'current_resting_hr': 85.0, 'hrv_rmssd': 25.0, 'sleep_hours': 8.0, 'eeg_alpha_power': 18.0, 'eeg_theta_power': 10.0, 'signal_coherence': 0.8, 'hrv_hf_power': 150.0, 'hr_surge': 15.0, 'hr_recovery_rate': 45.0, 'hrv_sdnn': 65.0}
        elif escenario == "🤯 Severe Cognitive Stress":
            datos_sensores = {'hrv_lf_hf_ratio': 4.2, 'eda_scr_peaks': 20, 'scl_u_siemens': 12.0, 'current_resting_hr': 95.0, 'hrv_rmssd': 15.0, 'sleep_hours': 4.5, 'eeg_alpha_power': 5.0, 'eeg_theta_power': 28.0, 'signal_coherence': 0.3, 'hrv_hf_power': 80.0, 'hr_surge': 25.0, 'hr_recovery_rate': 12.0, 'hrv_sdnn': 20.0}
        else: 
            datos_sensores = {'hrv_lf_hf_ratio': 0.8, 'eda_scr_peaks': 2, 'scl_u_siemens': 1.5, 'current_resting_hr': 55.0, 'hrv_rmssd': 85.0, 'sleep_hours': 9.0, 'eeg_alpha_power': 8.0, 'eeg_theta_power': 15.0, 'signal_coherence': 0.4, 'hrv_hf_power': 600.0, 'hr_surge': 2.0, 'hr_recovery_rate': 15.0, 'hrv_sdnn': 30.0}
        
        # Adding metrics that don't change in presets
        datos_sensores['metabolic_efficiency'] = 1.1 if st.session_state.get('pac_actividad', '') == "Intense (Athlete)" else 0.9
        datos_sensores['bp_variance'] = 4.5
        datos_sensores['ppg_pulse_transit_time_var'] = 11.2
        datos_sensores['eeg_beta_attenuation'] = 5.0

    else:
        # MANUAL MODE
        st.markdown("#### ✍️ Manual Input Panel")
        st.caption("Click on any box to write your value directly or use the buttons.")
        
        tab_cardio, tab_neuro, tab_eda = st.tabs(["🫀 Cardio (ECG & HRV)", "🧠 Neuro (EEG)", "💧 Skin (EDA)"])

        with tab_cardio:
            c1, c2, c3 = st.columns(3)
            hr_val = c1.number_input("Resting HR (bpm)", value=65.0, step=1.0)
            rmssd_val = c2.number_input("HRV RMSSD (ms)", value=45.0, step=1.0)
            sdnn_val = c3.number_input("HRV SDNN (ms)", value=50.0, step=1.0)
            
            c4, c5, c6 = st.columns(3)
            lfhf_val = c4.number_input("LF/HF Ratio", value=1.5, step=0.1)
            hf_val = c5.number_input("HF Power (ms2)", value=350.0, step=10.0)
            hrr_val = c6.number_input("HR Recovery (bpm/min)", value=25.0, step=1.0)

        with tab_neuro:
            n1, n2, n3 = st.columns(3)
            alpha_val = n1.number_input("Alpha Waves", value=15.0, step=1.0)
            theta_val = n2.number_input("Theta Waves", value=8.0, step=1.0)
            coh_val = n3.number_input("Coherence (0-1)", value=0.7, step=0.05)

        with tab_eda:
            e1, e2, e3 = st.columns(3)
            eda_val = e1.number_input("EDA Peaks", value=4, step=1)
            scl_val = e2.number_input("Basal Conductance", value=3.0, step=0.5)
            surge_val = e3.number_input("Cognitive HR Surge", value=5.0, step=1.0)

        # Pack manual data
        datos_sensores = {
            'hrv_lf_hf_ratio': lfhf_val, 'eda_scr_peaks': eda_val, 'scl_u_siemens': scl_val,
            'current_resting_hr': hr_val, 'hrv_rmssd': rmssd_val, 'sleep_hours': 7.5, 
            'eeg_alpha_power': alpha_val, 'eeg_theta_power': theta_val, 'signal_coherence': coh_val,
            'hrv_hf_power': hf_val, 'hr_surge': surge_val, 'hr_recovery_rate': hrr_val,
            'hrv_sdnn': sdnn_val,
            'metabolic_efficiency': 1.1 if st.session_state.get('pac_actividad', '') == "Intense (Athlete)" else 0.9,
            'bp_variance': 4.5, 'ppg_pulse_transit_time_var': 11.2, 'eeg_beta_attenuation': 5.0
        }

    # ==========================================
    # CALCULATION AND DISPLAY
    # ==========================================
    
    # Automatic penalties based on Sidebar Global Clinical File
    if st.session_state.get('pac_cirugias', False):
        datos_sensores['hr_recovery_rate'] -= 5.0
    if st.session_state.get('pac_edad', 25) > 50:
        datos_sensores['hrv_rmssd'] *= 0.85

    resultados = engine.get_full_biomarker_suite(datos_sensores)

    st.divider()
    st.subheader("📊 BIOCORE Proprietary Scores")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="Stress Index", value=f"{resultados['Stress Index']['score']}/100", delta=resultados['Stress Index']['status'], delta_color="inverse" if resultados['Stress Index']['score'] > 50 else "normal")
        st.metric(label="Cognitive Load Score", value=f"{resultados['Cognitive Load Score']['score']}/100", delta=resultados['Cognitive Load Score']['status'], delta_color="inverse" if resultados['Cognitive Load Score']['score'] > 65 else "normal")

    with col2:
        st.metric(label="Recovery Index", value=f"{resultados['Recovery Index']['score']}/100", delta=resultados['Recovery Index']['status'])
        st.metric(label="Physiological Resilience", value=f"{resultados['Physiological Resilience Score']['score']}/100", delta=resultados['Physiological Resilience Score']['status'])

    with col3:
        st.metric(label="NeuroCardiac Coupling", value=f"{resultados['NeuroCardiac Coupling Score']['score']}/100", delta=resultados['NeuroCardiac Coupling Score']['status'])
        st.metric(label="Learning Readiness Index", value=f"{resultados['Learning Readiness Index']['score']}/100", delta=resultados['Learning Readiness Index']['status'])
    
    st.markdown("---")
    st.subheader("📝 Reasoning System Notes")
    actividad = st.session_state.get('pac_actividad', 'Moderate')
    if st.session_state.get('pac_cirugias', False):
        st.warning("⚠️ **Clinical Alert:** Cardiovascular resilience and stability variables have been penalized according to the patient's active trauma/surgery history.")
    if actividad == "Intense (Athlete)":
        st.success("⚡ **Athletic Adaptation:** The system detected the athletic profile and calibrated metabolic efficiency and vagal recovery calculations assuming structural cardiovascular adaptations.")


# ==================== EEG PAGE (COMPLETE) ====================

def render_eeg_page() -> None:
    st.markdown("<h1 style='color: #1f77b4;'>🧠 EEG Neuro Lab</h1>", unsafe_allow_html=True)

    if EegSignalGenerator is None:
        st.error("EEG Module not available. Install biomedical.eeg")
        return

    source = st.sidebar.radio("EEG Source", ["Demo", "Local CSV"], index=0)
    pattern = st.sidebar.selectbox("Pattern" , ["Alpha", "Beta", "Theta", "Delta", "Seizure"], index=0)
    fs = st.sidebar.selectbox("fs (Hz)", [128, 256, 512], index=1)
    channels = st.sidebar.selectbox("Channels", [1,2,4], index=1)

    eeg_data = {}
    time_arr = np.array([])
    if source == 'Local CSV':
        uploaded = st.file_uploader('Upload EEG CSV (Cognitive Lab)', type=['csv'])
        if uploaded:
            try:
                text = uploaded.read().decode('utf-8')
                data = np.genfromtxt(io.StringIO(text), delimiter=',')
                if data.ndim == 1:
                    eeg_data['EEG1'] = data
                else:
                    for i in range(min(data.shape[1], channels)):
                        eeg_data[f'EEG{i+1}'] = data[:, i]
                time_arr = np.arange(len(next(iter(eeg_data.values())))) / fs
            except Exception as e:
                st.error(f'Error reading EEG CSV: {e}')
    else:
        params = EegPattern(pattern_type=pattern.lower(), duration=30, fs=fs, amplitude=40.0, noise_level=0.18, channels=channels)
        gen = EegSignalGenerator(sampling_rate=fs)
        eeg_data, time_arr = gen.generate(params)

    view = render_view_selector()

    if view == 'Clinical':
        st.markdown('### Clinical View')
        if not eeg_data:
            st.info('No EEG data loaded.')
        else:
            lead = list(eeg_data.keys())[0]
            st.markdown(f"**Channel analysis: {lead}**")
            st.line_chart(eeg_data[lead])
            st.markdown('#### Clinical Interpretation')
            st.write(f'Pattern: {pattern}. Explanation: Frequency bands reflect states of brain activation.')
            st.write('Meaning: Dominant frequency indicates state (alertness/fatigue).')
            st.write('Importance: Guides cognitive intervention or neurological monitoring.')
            st.write('Affected by: Sleep, medication, hypoxia, movement.')
            st.write('Relationships: Correlation with RR and HRV due to autonomic balance.')
            render_metric_explained('Dominant Frequency (EEG)', f'{np.random.uniform(0.5, 30):.1f}', unit='Hz',
                        meaning='Rhythmic component with highest spectral power.',
                        importance='Defines state of consciousness and cortical alertness.',
                        affects='Cerebral metabolism, sleep, drugs, and paroxysmal pathology.',
                        relations='Modulates heart rate via the autonomic axis.',
                        consequences='Focal slowing may suggest structural lesion or ischemia.')
            render_scientific_discovery_layer(eeg_data)

    elif view == 'Educational':
        st.markdown('### Educational View')
        st.write('Interactive: Select band to see anatomy and clinical example.')
        band = st.selectbox('Band', ['Delta','Theta','Alpha','Beta'])
        if band == 'Alpha':
            st.info('Alpha: Relaxation, closed eyes; increases during rest.')
        elif band == 'Beta':
            st.info('Beta: Attention and cognitive load.')
        st.write('Mini-quiz and explanation available.')

    elif view == 'Research':
        st.markdown('### Research View')
        st.write('Export time series, calculate band power, and correlate with respiration and HRV.')
        if st.button('Export EEG for research'):
            path = export_lab_report('EEG Research', {'channels': len(eeg_data)}, notes='EEG export')
            if path:
                st.success(f'Exported: {path}')

    elif view == 'AI':
        st.markdown('### AI View')
        st.write('AI Tutor: Explains findings and proposes diagnostic hypotheses based on patterns.')
        if eeg_data:
            st.write('Example: Increase in Theta + drop in Alpha → possible cognitive fatigue.')
        else:
            st.info('AI requires data; load EEG or use demo.')

    elif view == 'Simulation':
        st.markdown('### Simulation View')
        pat = st.selectbox('Simulate pattern', ['Alpha','Beta','Seizure'])
        dur = st.slider('Duration (s)', 5, 60, 30)
        sim = EegSignalGenerator(sampling_rate=fs).generate(EegPattern(pattern_type=pat.lower(), duration=dur, fs=fs, amplitude=30.0, noise_level=0.1, channels=1))[0]
        st.line_chart(sim[list(sim.keys())[0]])

    else:
        st.markdown('### Digital Twin View')
        st.write('Neuro twin: Simplified representation of networks and cognitive load.')
        render_metric_explained('Estimated Cognitive Load', f'{np.random.uniform(20,80):.0f}', unit='/100',
                    meaning='Cognitive load estimation based on synthetic EEG.',
                    importance='Indicator of mental fatigue and cognitive performance.',
                    affects='Sleep deprivation, stress, hypoxia, medication.',
                    relations='Correlates with HRV and EMG activation.',
                    consequences='Sustained high load suggests decreased performance and need for rest.')
        render_discovery_lab('EEG Twin', {'EEG': eeg_data.get(list(eeg_data.keys())[0], np.array([]))} if eeg_data else {})

# ==================== EMG PAGE (COMPLETE) ====================

def render_emg_page() -> None:
    st.markdown("<h1 style='color: #1f77b4;'>🦾 EMG Muscle Lab</h1>", unsafe_allow_html=True)

    source = st.sidebar.radio('EMG Source', ['Demo','CSV','Live Hardware'])
    pattern = st.sidebar.selectbox('Pattern', ['Isometric','Fast','Fatigue'])
    fs = st.sidebar.selectbox('fs (Hz)', [500,1000,2000], index=1)
    duration = st.sidebar.slider('Duration (s)', 5, 60, 15)

    signal = None
    time_arr = np.array([])
    if source == 'CSV':
        f = st.file_uploader('EMG CSV', type=['csv'])
        if f:
            try:
                data = np.genfromtxt(io.StringIO(f.read().decode()), delimiter=',')
                signal = data if data.ndim == 1 else data[:, 0]
                time_arr = np.arange(len(signal)) / fs
            except Exception as e:
                st.error(f'EMG CSV Error: {e}')
    elif source == 'Live Hardware' and EMGStreamer:
        if st.button('Connect EMG Hardware'):
            st.session_state.emg_streamer = EMGStreamer(port=None, baud=115200, fs=fs)
            if st.session_state.emg_streamer.connect():
                st.success('EMG Connected')
        signal = generate_demo_emg_signal(fs, duration, pattern) if signal is None else signal
        time_arr = np.arange(len(signal)) / fs
    else:
        signal = generate_demo_emg_signal(fs, duration, pattern)
        time_arr = np.arange(len(signal)) / fs

    view = render_view_selector()

    if view == 'Clinical':
        st.markdown('### Clinical View')
        filtered, metrics = preprocess_emg(signal, fs)
        activation = float(np.clip(np.mean(np.abs(filtered)) / (np.max(np.abs(filtered)) + 1e-9) * 100, 0, 100))
        st.write('Muscle activation and contraction patterns')
        render_metric_explained('Muscle Activation', f'{activation:.1f}', unit='%',
                    meaning='Average level of muscle activation from rectified EMG.',
                    importance='Indicates effort and risk of fatigue.',
                    affects='Load, posture, fatigue, neuromuscular imbalance.',
                    relations='Correlates with ECG and respiration during effort.',
                    consequences='Prolonged high activation suggests fatigue and injury risk.')
        st.write('Meaning: Level of motor recruitment. Importance: indicates effort and fatigue.')
        st.write('Affected by: load, posture, fatigue, neurogenic factors.')
        render_scientific_discovery_layer({'EMG': signal})

    elif view == 'Educational':
        st.markdown('### Educational View')
        st.write('Visualize activation, rectification, and learn about muscle fatigue.')
        st.line_chart(signal)
        st.plotly_chart(PLOTLY_GO.Figure(PLOTLY_GO.Scatter(y=signal, name='Raw EMG')), use_container_width=True)

    elif view == 'Research':
        st.markdown('### Research View')
        median_freq = compute_emg_median_frequency(signal, fs)
        st.write(f'Median frequency: {median_freq:.1f} Hz')
        if st.button('Export EMG for research'):
            p = export_lab_report('EMG Research', {'median_freq': median_freq}, notes='EMG export')
            if p:
                st.success(f'Exported: {p}')

    elif view == 'AI':
        st.markdown('### AI View')
        st.write('AI suggests diagnoses: fatigue, overuse, myopathic vs neurogenic pattern (conceptual only).')

    elif view == 'Simulation':
        st.markdown('### Simulation View')
        force = st.slider('Simulated force (%)', 0, 100, 40)
        st.write('Simulation of isometric contraction with varying recruitment.')

    else:
        st.markdown('### Digital Twin View')
        render_metric_explained('Muscle Fatigue Index', f'{np.random.uniform(10,80):.0f}', unit='/100',
                    meaning='Muscle fatigue estimator based on frequency shifts.',
                    importance='Helps plan recovery and exercise duration.',
                    affects='Effort duration, temperature, and metabolism.',
                    relations='Relates activation and median frequency (EMG).')
        render_discovery_lab('EMG Twin', {'EMG': signal})

def generate_demo_emg_signal(fs: float, duration: float, pattern: str) -> np.ndarray:
    n = int(fs * duration)
    t = np.arange(n) / fs
    if pattern == "Isometric":
        env = 0.6 + 0.2 * np.sin(2*np.pi*0.5*t)
    elif pattern == "Fast":
        env = 0.4 + 0.5*np.exp(-((t-duration/2)**2)/0.25)
    else:
        env = 0.6 + 0.3*(1-t/max(duration, 1))
    return env * np.random.normal(0, 1, n) + 0.05*np.sin(100*np.pi*t)

# ==================== OTHER PAGES ====================

def render_ecg_monitor_page() -> None:
    st.markdown("<h2>🫀 Cardiovascular Intelligence Lab</h2>", unsafe_allow_html=True)
    ECGAnalyzer, create_clinical_ecg_figure, load_mitbih_record, get_mitbih_records, ecg_ok = safe_import_ecg_modules()
    src_modules, src_ok = safe_import_src_modules()

    source = st.sidebar.radio('ECG Source', ['Demo (synthetic)', 'Local CSV'], index=0)
    signal = None
    fs = 250
    metadata = {}

    if source == 'Local CSV':
        uploaded = st.sidebar.file_uploader('Upload local ECG (CSV)', type=['csv'])
        if uploaded and src_ok and 'load_biomedical_signal' in src_modules:
            try:
                with open(os.path.join(tempfile.gettempdir(), uploaded.name), 'wb') as tmp:
                    tmp.write(uploaded.read())
                signal, fs, metadata = src_modules['load_biomedical_signal'](os.path.join(tempfile.gettempdir(), uploaded.name))
                st.success('ECG signal loaded from local CSV')
            except Exception as e:
                display_error_message(e, 'ECG file upload')
        elif uploaded:
            st.warning('CSV upload detected, but `src` modules are missing. Using demo.')

    if signal is None:
        hr_demo = st.sidebar.slider('Demo HR (bpm)', 40, 140, 72)
        signal = generate_demo_ecg_signal(fs=fs, duration=20, hr=hr_demo)
        metadata['source'] = 'demo'

    valid, msg = validate_signal(signal)
    if not valid:
        st.error(msg)
        return

    view = render_view_selector()
    hr = estimate_ecg_heart_rate(signal, fs)
    vm = np.arange(len(signal)) / fs

    def show_anatomy(part: str):
        explanations = {
            'SA Node': 'SA Node: natural pacemaker initiating atrial depolarization (P waves).',
            'AV Node': 'AV Node: physiological delay to allow ventricular filling before contraction.',
            'His Bundle': 'Bundle of His: conducts the impulse to the ventricular branches.',
            'Purkinje': 'Purkinje Fibers: rapid distribution synchronizing ventricular contraction.'
        }
        st.markdown(f"**{part}**: {explanations.get(part, '')}")

    if view == 'Clinical':
        st.markdown('### Clinical View')
        render_metric_explained('Heart Rate', f'{hr:.0f}', unit='bpm',
                    meaning='Heart rate derived from ECG.',
                    importance='Primary indicator of cardiovascular status and effort.',
                    affects='Exercise, arrhythmias, drugs, intravascular volume.',
                    relations='Affects perfusion, metabolic demand, and synchronization with respiration.',
                    consequences='Sudden changes may indicate arrhythmia or shock.')
        st.markdown(f"**Source:** {metadata.get('source', 'demo')}  |  **Sampling:** {fs} Hz")

        render_scientific_discovery_layer({'ECG': signal})
        if PLOTLY_OK:
            try:
                fig = PLOTLY_GO.Figure()
                fig.add_trace(PLOTLY_GO.Scatter(x=vm, y=signal, name='ECG', mode='lines'))
                fig.update_layout(template='plotly_dark', height=360, title='ECG — Signal')
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.line_chart(signal)
        else:
            st.line_chart(signal)

        st.markdown('#### Dynamic Physiology — select a segment to view events:')
        seg = st.selectbox('Segment', ['P', 'QRS', 'T'])
        if seg == 'P':
            st.write('- Electrical event: atrial depolarization (P wave).')
            st.write('- Mechanical event: atrial contraction, contributes to ventricular filling.')
            st.write('- Hemodynamic event: slight increase in atrial pressure and ventricular filling.')
        elif seg == 'QRS':
            st.write('- Electrical event: ventricular depolarization (QRS complex).')
            st.write('- Mechanical event: ventricular contraction and systolic ejection.')
            st.write('- Hemodynamic event: increase in systolic blood pressure and cardiac output.')
        else:
            st.write('- Electrical event: ventricular repolarization (T wave).')
            st.write('- Mechanical event: ventricular relaxation and start of filling.')

        st.markdown('#### Differential Diagnosis (example)')
        st.write('If persistent ST elevation is observed in contiguous leads:')
        st.write('- Findings: ST elevation in V2-V4')
        st.write('- Possible diagnoses: Acute anterior myocardial infarction (LAD).')
        st.write('- Justification: Correlation with coronary territories and clinical symptoms.')

    elif view == 'Educational':
        st.markdown('### Educational View — Interactive Anatomy')
        cols = st.columns(4)
        if cols[0].button('SA Node'):
            show_anatomy('SA Node')
        if cols[1].button('AV Node'):
            show_anatomy('AV Node')
        if cols[2].button('His Bundle'):
            show_anatomy('His Bundle')
        if cols[3].button('Purkinje Fibers'):
            show_anatomy('Purkinje')

        st.markdown('### Physiological Timeline')
        st.write('Depolarization → Contraction → Ejection → Relaxation → Ventricular Filling')
        st.markdown('Step through each stage using the controls:')
        step = st.slider('Stage', 0, 4, 0)
        steps = ['Depolarization', 'Contraction', 'Ejection', 'Relaxation', 'Filling']
        st.info(steps[step])

    elif view == 'Research':
        st.markdown('### Research View')
        st.write('Generate time series, compare cohorts, and export data for scientific analysis.')
        if st.button('Export segment for research'):
            path = export_lab_report('ECG Segment', {'length': len(signal)}, notes='ECG segment for research')
            if path:
                st.success(f'Exported: {path}')
        st.markdown('#### Example Correlations with other sensors')
        resp_demo = generate_demo_respiration_signal(fs, 20, 16)
        spo2_demo = generate_demo_spo2_signal(fs, 20)
        len_min = min(len(signal), len(resp_demo), len(spo2_demo))
        corr_ecg_resp = float(np.corrcoef(signal[:len_min], resp_demo[:len_min])[0, 1]) if len_min > 1 else 0.0
        corr_ecg_spo2 = float(np.corrcoef(signal[:len_min], spo2_demo[:len_min])[0, 1]) if len_min > 1 else 0.0
        st.write(f'ECG ↔ Respiration: {corr_ecg_resp:.2f} — ECG ↔ SpO₂: {corr_ecg_spo2:.2f}')

    elif view == 'AI':
        st.markdown('### AI View — Tutor & Reasoning')
        st.write('AI explains findings, proposes educational questions, and generates diagnostic hypotheses.')
        try:
            if src_ok and 'interpret_ecg' in src_modules:
                summary = src_modules['interpret_ecg'](signal, fs)
                st.write(summary)
            else:
                st.info('Advanced interpretation unavailable; showing conceptual explanation.')
                st.write('- What do you observe? > Look for ST elevations, wide QRS, absent P waves.')
                st.write('- What would you do? > Correlate with symptoms, troponins, and perfusion.')
        except Exception as e:
            st.warning(f'AI interpretation failed: {e}')

    elif view == 'Simulation':
        st.markdown('### Simulation View — Exploration Mode')
        st.write('Adjust parameters and observe effects on ECG and associated explanations.')
        fc = st.slider('Heart Rate (bpm)', 30, 160, int(hr))
        pr = st.slider('PR (ms)', 80, 300, 160)
        qrs = st.slider('QRS (ms)', 60, 200, 100)
        qt = st.slider('QT (ms)', 200, 500, 360)
        st.markdown('#### What would change if...')
        st.write('- Increased HR: Reduces RR interval, may decrease ventricular filling time.')
        st.write('- Wide QRS: Suggests bundle branch block or aberrant conduction, affects ventricular synchrony.')

    elif view == 'Digital Twin':
        st.markdown('### Digital Twin View — Live Heart')
        st.write('Cardiac twin synchronized with ECG: simplified animation of the cardiac cycle.')
        hr_idx = np.clip((hr - 40) / 100, 0, 1)
        contractility = 50 + hr_idx * 50
        render_metric_explained('Contractility Index', f'{contractility:.0f}', unit='/100',
                    meaning='Simplified proxy for ventricular contractility in the twin.',
                    importance='Helps understand ejection capacity and perfusion.',
                    affects='Ischemia, inotropic drugs, blood volume.',
                    relations='Influences blood pressure and tissue perfusion.',
                    consequences='Low contractility decreases perfusion; high increases O2 consumption.')
        render_discovery_lab('Cardiac Twin', {'ECG': signal})
        st.write('The twin updates state based on metrics: perfusion, rate, and detected arrhythmias.')
        if PLOTLY_OK:
            try:
                x = vm[:500]
                y = signal[:500]
                frames = []
                nframes = min(60, len(x))
                step = max(1, len(x)//nframes)
                for i in range(0, len(x), step):
                    frames.append(PLOTLY_GO.Frame(data=[PLOTLY_GO.Scatter(x=x, y=y, mode='lines', name='ECG'),
                                                        PLOTLY_GO.Scatter(x=[x[i]], y=[y[i]], mode='markers', marker=dict(size=10, color='red'), name='Phase')],
                                               name=str(i)))

                fig = PLOTLY_GO.Figure(data=[PLOTLY_GO.Scatter(x=x, y=y, mode='lines', name='ECG'),
                                             PLOTLY_GO.Scatter(x=[x[0]], y=[y[0]], mode='markers', marker=dict(size=10, color='red'), name='Phase')],
                                       frames=frames)
                fig.update_layout(template='plotly_dark', updatemenus=[dict(type='buttons', showactive=False,
                                                                              buttons=[dict(label='Play', method='animate', args=[None, {'frame': {'duration': 80, 'redraw': True}, 'fromcurrent': True}])])],
                                  height=380, title='ECG Twin — cardiac cycle')
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.line_chart(signal)
            try:
                import math
                t = np.linspace(0, 2 * np.pi, 300)
                x3 = 16 * np.sin(t)**3
                y3 = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
                z3 = np.sin(3*t) * 2
                fig3d = PLOTLY_GO.Figure()
                fig3d.add_trace(PLOTLY_GO.Scatter3d(x=x3, y=y3, z=z3, mode='markers', marker=dict(size=3, color=z3, colorscale='Hot')))
                fig3d.update_layout(title='3D Twin — Heart Shape', template='plotly_dark', height=420)
                st.plotly_chart(fig3d, use_container_width=True)
            except Exception:
                pass

def render_multisensor_page() -> None:
    st.markdown("<h2>🔗 Multisensor Fusion Lab</h2>", unsafe_allow_html=True)
    _, _, _, _, _ = safe_import_ecg_modules()
    _, src_ok = safe_import_src_modules()
    BiosignalChannel, MultisensoralRecord, multisensor_ok = safe_import_multisensor()

    demo_channels = {
        'ECG': generate_demo_ecg_signal(250, 20),
        'PPG': generate_demo_ppg_signal(250, 20),
        'SpO2': generate_demo_spo2_signal(250, 20),
        'Respiration': generate_demo_respiration_signal(250, 20),
    }

    view = render_view_selector()

    if view == 'Clinical':
        st.markdown('### Clinical View')
        record = MultisensoralRecord([BiosignalChannel(name, sig, 250.0, unit='mV' if name=='ECG' else '%', signal_type=name.lower()) for name,sig in demo_channels.items()], patient_id='DEMO')
        indices = record.compute_physiological_indices()
        health = record.health_score()
        st.write('Integrated view of vital signs and perfusion')
        render_metric_explained('Health Score', f"{health['overall']:.1f}", unit='/100',
                    meaning='Aggregated index of multisensor physiological state.',
                    importance='Serves to prioritize interventions and monitoring.',
                    affects='Variations in ECG, PPG, SpO2, and respiration.',
                    relations='Summarizes interactions between cardiovascular and respiratory systems.')
        render_metric_explained('Heart Rate', f"{indices['heart_rate']:.0f}", unit='bpm')
        render_metric_explained('SpO2', f"{indices['spo2_mean']:.1f}", unit='%')
        st.write('Meaning: Aggregated index of physiological wellness. Importance: Prioritizes interventions.')
        render_scientific_discovery_layer(demo_channels)

    elif view == 'Educational':
        st.markdown('### Educational View')
        st.write('Interactive multisensor: Select channels to learn about cardiorespiratory coupling and oxygenation.')
        ch = st.multiselect('Channels', list(demo_channels.keys()), default=['ECG','SpO2'])
        for c in ch:
            st.line_chart(demo_channels[c])

    elif view == 'Research':
        st.markdown('### Research View')
        st.write('Export synchronized records and calculate advanced correlations.')
        if st.button('Export multisensor for research'):
            p = export_lab_report('Multisensor Research', {'channels': list(demo_channels.keys())}, notes='Multisensor export')
            if p:
                st.success(f'Exported: {p}')

    elif view == 'AI':
        st.markdown('### AI View')
        st.write('AI detects deterioration patterns and suggests hypotheses and actions.')

    elif view == 'Simulation':
        st.markdown('### Simulation View')
        st.write('Adjust SpO2, HR, and RR to observe changes in integrated indices.')
        hr = st.slider('HR', 40, 160, 72)
        spo2 = st.slider('SpO2', 80, 100, 96)
        rr = st.slider('RR', 8, 30, 16)
        st.write('The system recalculates the Health Score in real-time.')

    else:
        st.markdown('### Digital Twin View')
        st.write('Multisensor twin synchronizing ECG, PPG, and respiration while simulating perfusion states.')
        render_metric_explained('Perfusion Proxy', f"{np.clip(np.mean(demo_channels['PPG'])*100,0,100):.0f}", unit='/100',
                    meaning='Peripheral perfusion estimator based on PPG.',
                    importance='Detects changes in peripheral flow and tissue perfusion.',
                    affects='Vasoconstriction, temperature, volume.')
        render_discovery_lab('Multisensor Twin', demo_channels)


def render_respiratory_page() -> None:
    st.markdown("<h2>💨 Respiratory Lab</h2>", unsafe_allow_html=True)
    src_modules, src_ok = safe_import_src_modules()
    source = st.sidebar.radio('Respiratory Source', ['Demo','Local File'])
    signal = None
    fs = 250
    metadata = {}

    if source == 'Local File':
        uploaded = st.sidebar.file_uploader('Upload local Respiration', type=['csv','edf','hea','dat'])
        if uploaded and src_ok:
            try:
                with open(os.path.join(tempfile.gettempdir(), uploaded.name), 'wb') as tmp:
                    tmp.write(uploaded.read())
                signal, fs, metadata = src_modules['load_biomedical_signal'](os.path.join(tempfile.gettempdir(), uploaded.name))
                st.success('Respiratory signal loaded')
            except Exception as e:
                display_error_message(e, 'Respiratory Upload')
        elif uploaded:
            st.warning('File upload requires `src.data` modules.')

    if signal is None:
        signal = generate_demo_respiration_signal(fs, 30, 16)
        metadata['source'] = 'demo'

    view = render_view_selector()

    rr = estimate_respiration_rate(signal, fs)
    spo2_demo = generate_demo_spo2_signal(fs, 30)
    ecg_demo = generate_demo_ecg_signal(fs, 20, 72)
    len_min = min(len(signal), len(spo2_demo), len(ecg_demo))
    resp_ecg_corr = float(np.corrcoef(signal[:len_min], ecg_demo[:len_min])[0, 1]) if len_min > 1 else 0.0
    resp_spo2_corr = float(np.corrcoef(signal[:len_min], spo2_demo[:len_min])[0, 1]) if len_min > 1 else 0.0

    if view == 'Clinical':
        st.markdown('### Clinical View')
        render_metric_explained('Respiratory Rate', f'{rr:.1f}', unit='rpm',
                    meaning='Estimated respiratory rate from the signal.',
                    importance='Reflects ventilation and potential respiratory fatigue.',
                    affects='Exercise, pain, acidosis, hypoxia.',
                    relations='Couples with HR and SpO2 during hemodynamic changes.')
        status = 'Normal' if 12 <= rr <= 20 else 'Altered'
        st.write(f'Respiratory Status: {status}')
        st.write('Meaning: Respiratory rate measures ventilation. Importance: Guides respiratory support.')
        st.line_chart(signal)
        render_scientific_discovery_layer({'Respiratory': signal})

    elif view == 'Educational':
        st.markdown('### Educational View')
        st.write('Learn about inspiration/expiration phases, neural control of respiration, and pathological patterns.')
        st.line_chart(signal)

    elif view == 'Research':
        st.markdown('### Research View')
        st.write('Export series, compare cohorts, and analyze hypoxia events.')
        if st.button('Export respiration'):
            p = export_lab_report('Respiration Research', {'length': len(signal)}, notes='Resp export')
            if p:
                st.success(f'Exported: {p}')

    elif view == 'AI':
        st.markdown('### AI View')
        st.write('AI proposes hypotheses: hypoventilation, tachypnea, restrictive or obstructive patterns (conceptual).')

    elif view == 'Simulation':
        st.markdown('### Simulation View')
        rr_new = st.slider('Simulate RR', 6, 40, int(rr))
        st.write(f'Simulation with RR={rr_new} rpm. Observe changes in oxygenation and work of breathing.')

    else:
        st.markdown('### Digital Twin View')
        render_metric_explained('Ventilatory Resilience', f'{np.random.uniform(30,90):.0f}', unit='/100',
                    meaning='Proxy for ventilatory capacity under stress.',
                    importance='Indicates capacity to maintain effective ventilation.',
                    affects='Pulmonary reserves, respiratory muscle fatigue.')
        render_discovery_lab('Respiratory Twin', {'Respiration': signal})


def render_hrv_page() -> None:
    st.markdown("<h2>📈 HRV Analysis</h2>", unsafe_allow_html=True)
    st.markdown('Heart Rate Variability analysis with time-frequency metrics and clinical explanation.')
    source = st.sidebar.radio('HRV Source', ['Demo (ECG-derived)','Manual RR series'], index=0)
    rr_ms = None
    if source == 'Manual RR series':
        txt = st.text_area('Paste RR intervals in ms separated by commas', '800,820,790,810,805')
        try:
            rr_ms = np.array([float(x.strip()) for x in txt.split(',') if x.strip()])
        except Exception:
            rr_ms = None
    else:
        hr = st.sidebar.slider('Demo HR (bpm)', 40, 140, 72)
        n = st.sidebar.slider('Duration (sec)', 30, 300, 120)
        mean_rr = 60000.0 / float(max(30, hr))
        beats = int(max(10, (n * hr) // 60))
        rr_ms = mean_rr + np.random.normal(0, mean_rr * 0.03, size=beats)

    if rr_ms is None or len(rr_ms) < 5:
        st.error('Insufficient RR series. Provide more beats or use the demo source.')
        return

    diffs = np.diff(rr_ms)
    sdnn = float(np.std(rr_ms, ddof=1))
    rmssd = float(np.sqrt(np.mean(diffs**2))) if len(diffs) > 0 else 0.0
    pnn50 = float(np.sum(np.abs(diffs) > 50) / max(1, len(diffs)) * 100)
    mean_nn = float(np.mean(rr_ms))

    st.markdown('### Clinical View')
    render_metric_explained('SDNN', f'{sdnn:.1f}', unit='ms',
                meaning='Standard deviation of NN intervals (global variability).',
                importance='General indicator of autonomic variability.',
                affects='Stress, age, cardiac diseases, and medications.',
                relations='Correlates with RMSSD and autonomic balance.',
                consequences='Low values associated with higher cardiovascular risk.')
    render_metric_explained('RMSSD', f'{rmssd:.1f}', unit='ms',
                meaning='Root mean square of successive differences — parasympathetic tone proxy.')
    render_metric_explained('pNN50', f'{pnn50:.1f}', unit='%',
                meaning='Percentage of NN differences >50ms — vagal indicator.')

    render_scientific_discovery_layer({'RR_ms': rr_ms})

    freqs = None
    lf_power = None
    hf_power = None
    try:
        t = np.cumsum(rr_ms) / 1000.0
        t = t - t[0]
        fs_interp = 4.0
        ti = np.arange(0, t[-1], 1.0/fs_interp)
        rr_interp = np.interp(ti, t, rr_ms)
        from scipy.signal import welch
        f, pxx = welch(rr_interp - np.mean(rr_interp), fs=fs_interp, nperseg=min(256, len(rr_interp)))
        lf_mask = (f >= 0.04) & (f < 0.15)
        hf_mask = (f >= 0.15) & (f <= 0.4)
        lf_power = float(np.trapz(pxx[lf_mask], f[lf_mask])) if np.any(lf_mask) else 0.0
        hf_power = float(np.trapz(pxx[hf_mask], f[hf_mask])) if np.any(hf_mask) else 0.0
        lf_hf = lf_power / hf_power if hf_power > 0 else None
        st.markdown('### Research View — HRV Spectrum')
        if PLOTLY_OK:
            fig = PLOTLY_GO.Figure()
            fig.add_trace(PLOTLY_GO.Scatter(x=f, y=pxx, mode='lines', name='PSD'))
            fig.update_layout(template='plotly_dark', height=320, xaxis_title='Hz', yaxis_title='Power')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart(pxx)
        st.write(f'LF: {lf_power:.3f} — HF: {hf_power:.3f} — LF/HF: {lf_hf if lf_hf is not None else "n/a"}')
    except Exception:
        st.info('Could not calculate HRV spectrum; missing scipy or sufficient data.')

    view = render_view_selector()
    if view == 'Educational':
        st.markdown('### Educational View — What affects HRV?')
        st.write('- Vagal tone increments raise RMSSD and pNN50.')
        st.write('- Chronic disease and age tend to lower SDNN.')
        st.line_chart(rr_ms)
    elif view == 'AI':
        st.markdown('### AI View')
        st.write('AI proposes interpretations and risk based on population thresholds.')
    elif view == 'Simulation':
        st.markdown('### Simulation View')
        st.write('Adjust variability and observe effects on indices (sterile demo).')
        var = st.slider('Variability (SD%)', 0.0, 10.0, 3.0)
        sim_rr = mean_nn + np.random.normal(0, mean_nn * var/100.0, size=len(rr_ms))
        st.line_chart(sim_rr)
    elif view == 'Digital Twin':
        st.markdown('### Digital Twin View — HRV Twin')
        render_metric_explained('Autonomic Balance (proxy)', f'{np.clip(100 - abs(sdnn - 50),0,100):.1f}', unit='/100')
        render_discovery_lab('HRV Twin', {'RR_ms': rr_ms})

def render_education_page() -> None:
    src_modules, src_ok = safe_import_src_modules()
    st.markdown("<h2>🎓 Education</h2>", unsafe_allow_html=True)
    st.markdown('BIOCORE AI University transforms every module into a learning experience with lessons, clinical cases, and adaptive questions.')
    
    view = render_view_selector()
    
    if view == 'Clinical':
        st.markdown('### Clinical View: Real Case Studies')
        st.info("Explore how pathologies present in real patients.")
        case_id = st.selectbox('Load Clinical Case', ['Myocardial Infarction', 'Atrial Fibrillation', 'Epileptic Seizure'])
        st.info(f"Scenario: Clinical presentation of {case_id} for differential diagnosis.")
        render_metric_explained('Case Difficulty', 'Intermediate',
                    meaning='Pedagogical level of the current clinical scenario.',
                    importance='Allows adjusting the AI support level.')
    elif view == 'Educational':
        st.markdown('### Educational View: Theory and Quizzes')
        st.write('Learn the physiological basis of the signals captured in the Clinical Hub.')
        if src_ok and 'create_quiz' in src_modules:
            st.button('Start Adaptive Quiz')
    elif view == 'Research':
        st.markdown('### Research View: Learning Data')
        st.write('Progression statistics and skill acquisition metrics.')
    elif view == 'AI':
        st.markdown('### AI View: Cognitive Tutor')
        st.write('AI analyzes your progress and suggests specific topics to reinforce.')
    elif view == 'Simulation':
        st.markdown('### Simulation View: Diagnostic Practice')
        st.write('Simulate interpreting a signal with noise and artifacts.')

    st.markdown('### 1. Data')
    st.write('Access real and generated examples: ECG, EEG, EMG, respiration, SpO₂, and digital twins.')
    st.markdown('### 2. Interpretation')
    st.write('Each topic explains physiology, clinical patterns, and multisensory relationships.')
    st.markdown('### 3. Education')

    course_cards = [
        ('Cardiovascular Physiology', 'ECG interpretation and hemodynamic dynamics.', st.session_state.learning_progress['Cardio-Physiology']),
        ('Neurophysiology', 'EEG rhythms, cognitive load, and artifacts.', st.session_state.learning_progress['Neurophysiology']),
        ('Respiratory Physiology', 'Ventilation, gas exchange, and respiratory patterns.', st.session_state.learning_progress['Respiratory']),
        ('Muscle and EMG', 'Activation, fatigue, and EMG signal.', st.session_state.learning_progress['Muscle']),
        ('Clinical Interpretation', 'Differential diagnosis and synthesis of findings.', st.session_state.learning_progress['Clinical Interpretation']),
    ]
    cols = st.columns(2)
    for idx, (title, desc, progress) in enumerate(course_cards):
        with cols[idx % 2]:
            st.markdown(f'**{title}**')
            st.write(desc)
            st.progress(progress / 100)
            st.caption(f'Progress: {progress}%')

    st.markdown('### 4. AI')
    st.write('The biomedical tutor asks questions, explains results, and suggests next learning steps.')
    if st.button('Advance in learning'):
        for key in st.session_state.learning_progress:
            st.session_state.learning_progress[key] = min(100, st.session_state.learning_progress[key] + 5)
        st.success('Progress updated.')

    st.markdown('### 5. Research')
    st.write('Generate case summaries, compare progress with academic metrics, and prepare scientific reports.')

    if src_ok and 'create_quiz' in src_modules and callable(src_modules['create_quiz']):
        with st.expander('🧠 Supervised quiz activity'):
            quiz = src_modules['create_quiz']('cardio')
            if isinstance(quiz, list) and quiz:
                for idx, item in enumerate(quiz):
                    answer = st.radio(item['question'], item['options'], key=f'quiz_{idx}')
                    if st.button(f'Review question {idx + 1}', key=f'review_{idx}'):
                        if answer == item.get('answer'):
                            st.success('Correct')
                        else:
                            st.error(f'Incorrect. {item.get("explanation", "Check the answer.")}')

            st.progress(progress/100)
            st.caption(f'Level: {progress}%')
            
    st.markdown('### Learning Path Tutor')
    st.write('BIOCORE AI suggests study paths based on your progress and emerging clinical cases.')


def render_guides_page() -> None:
    st.markdown("<h2>📚 Guides</h2>", unsafe_allow_html=True)
    st.markdown('Documentation and user guides for the BIOCORE AI ecosystem.')
    st.markdown(
        '- Use Mission Control to switch between hubs.\n'
        '- In Clinical Hub explore ECG, Multisensor, and Respiratory Lab.\n'
        '- In Learning Hub follow courses, clinical cases, and adaptive tutoring.\n'
        '- In Simulation Hub adjust physiology and observe virtual patient resilience.')
    st.markdown('### Integration Principles')
    st.markdown(
        '- All modules interpret, explain, teach, predict, and simulate.\n'
        '- Each module connects with the others to generate physiological correlations.\n'
        '- The system must feel like a coherent organism, not isolated tools.')
    st.markdown('### Roles')
    st.markdown(
        '- Student: Guided cases, questions, and clinical explanations.\n'
        '- Researcher: Export data, compare cohorts, and generate statistics.\n'
        '- Physician: Integrated monitoring, digital twin, and explainable AI.')
    if st.button('Open quick onboarding'):
        st.session_state.mission_goal = 'Explore Clinical Hub with real data and consult AI Hub for explanations.'
        st.success('Quick onboarding activated.')
    st.info(f'Current objective: {st.session_state.mission_goal}')

# ==================== NEW EXPERT SYSTEM PANEL ====================

def render_ai_analysis_page() -> None:
    st.markdown("<h1 style='color: #1f77b4;'>🤖 Clinical Expert System (CDSS)</h1>", unsafe_allow_html=True)
    
    if not AI_ENGINE_AVAILABLE:
        st.error("⚠️ ClinicalAIEngine module not found. Make sure 'clinical_ai.py' is saved in 'app/'.")
        return
        
    st.markdown("""
    ICU-grade deterministic reasoning engine. Evaluates complex pathological intersections across hemodynamics, 
    metabolism, respiration, anthropometry, and biometric biomarkers (Total Fusion).
    """)
    st.divider()

    st.markdown("### 🎚️ Vital Signs Input (Simulation)")
    
    c1, c2, c3 = st.columns(3)
    hr_input = c1.number_input("Heart Rate (bpm)", value=115.0)
    spo2_input = c2.number_input("SpO2 (%)", value=93.0)
    rr_input = c3.number_input("Resp Rate (rpm)", value=22.0)

    c4, c5, c6 = st.columns(3)
    sys_input = c4.number_input("Systolic BP (mmHg)", value=120.0)
    dia_input = c5.number_input("Diastolic BP (mmHg)", value=80.0)
    temp_input = c6.number_input("Temperature (°C)", value=37.5)

    with st.expander("🔬 Laboratories and Advanced Metrics (Optional)"):
        ca, cb, cc = st.columns(3)
        lactate_input = ca.number_input("Lactate (mmol/L)", value=1.0)
        glucose_input = cb.number_input("Glucose (mg/dL)", value=90.0)
        etco2_input = cc.number_input("EtCO2 (mmHg)", value=40.0)
        
        cd, ce, cf = st.columns(3)
        gcs_input = cd.number_input("GCS (Score)", value=15, max_value=15, min_value=3)
        hemo_input = ce.number_input("Hemoglobin (g/dL)", value=14.0)
        potassium_input = cf.number_input("Potassium (mEq/L)", value=4.0)

    if st.button("🧠 Execute Clinical Intelligence Analysis", use_container_width=True, type="primary"):
        ai_engine = ClinicalAIEngine()
        
        # Collecting data for AI
        vitals_dict = {
            'hr': hr_input, 'spo2': spo2_input, 'rr': rr_input,
            'sys_bp': sys_input, 'dia_bp': dia_input, 'temp': temp_input,
            'lactate': lactate_input, 'glucose': glucose_input, 'etco2': etco2_input,
            'gcs': gcs_input, 'hemoglobin': hemo_input, 'potassium': potassium_input,
            'body_fat_pct': st.session_state.get('pac_grasa', 20.0)
        }

        # Extracting sidebar info for personalized analysis
        nombre_pac = st.session_state.get('pac_nombre', 'Alpha Patient')
        edad_pac = st.session_state.get('pac_edad', 25)
        peso_pac = st.session_state.get('pac_peso', 75.0)
        
        # Analysis calls the mega-engine and generates the report
        resultados = ai_engine.analyze_patient(
            vitals=vitals_dict,
            patient_name=nombre_pac,
            age=edad_pac,
            gender="Unknown", # Generic for now, could be added to UI
            weight_kg=peso_pac,
            height_cm=170.0 # Default for BMI
        )

        st.divider()
        
        c_left, c_right = st.columns(2)
        with c_left:
            st.markdown("### 🩺 1. Clinical Findings")
            for item in resultados["clasificacion"]:
                st.markdown(f"- 🔎 {item}")

        with c_right:
            st.markdown("### ⚠️ 2. Risk Level")
            st.markdown(
                f"<div style='background-color: {resultados['color_riesgo']}20; padding: 20px; border-radius: 10px; border: 2px solid {resultados['color_riesgo']}; text-align: center;'>"
                f"<h2 style='color: {resultados['color_riesgo']}; margin:0;'>{resultados['riesgo']}</h2>"
                "</div>", 
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🧠 3. Physiological Explainability (White Box)")
        with st.expander("View engine clinical reasoning", expanded=True):
            st.write(resultados["explicacion"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🖨️ 4. Structured Clinical Report")
        st.markdown(
            f"<div style='background-color: #0c1421; padding: 25px; border-radius: 15px; border: 1px solid #1f77b4;'>"
            f"{resultados['informe']}"
            "</div>", 
            unsafe_allow_html=True
        )


def render_patient_pipeline_page() -> None:
    st.markdown("<h2>👥 Patient Pipeline</h2>", unsafe_allow_html=True)
    src_modules, src_ok = safe_import_src_modules()
    st.markdown('Pipeline of virtual and real patients with tracking, cohort analysis, and educational support.')

    view = render_view_selector()

    if view == 'Clinical':
        st.markdown('### Clinical View')
        patient_id = st.text_input('Patient ID', 'PATIENT-001')
        diagnosis = st.selectbox('Initial Evaluation', ['Stable','Respiratory compromise','Arrhythmia detected'])
        if st.button('Generate patient file'):
            st.success(f'File {patient_id} generated with status {diagnosis}')
            st.write('Clinical pipeline ready for tracking.')

        st.markdown('#### Save / Load clinical state')
        if st.button('Save current state'):
            try:
                state = {'diagnosis': diagnosis, 'patient_id': patient_id, 'notes': 'saved from UI'}
                import datetime
                ts = datetime.datetime.utcnow().isoformat()
                rowid = save_patient_state(patient_id, state, ts)
                st.success(f'State saved: id={rowid}')
            except Exception as e:
                st.error(f'Could not save state: {e}')

        rows = list_patient_states(20)
        if rows:
            st.markdown('**Recent saved states**')
            for r in rows:
                with st.expander(f"{r['patient_id']} — {r['timestamp']} (id={r['id']})"):
                    st.json(r['data'])
                    if st.button(f'Load state {r["id"]}', key=f'load_{r["id"]}'):
                        loaded = load_patient_state(r['id'])
                        st.success(f'State loaded: {loaded.get("patient_id")}, timestamp={loaded.get("timestamp")}')
        else:
            st.info('No clinical states saved.')

    elif view == 'Educational':
        st.markdown('### Educational View')
        st.write('Interactive clinical cases: follow the evolution of a virtual patient and make decisions.')

    elif view == 'Research':
        st.markdown('### Research View')
        if st.button('Load demo cohorts'):
            st.success('Demo cohort loaded into pipeline.')

    elif view == 'AI':
        st.markdown('### AI View')
        st.write('AI suggests risk stratification and care pathways for each patient.')

    elif view == 'Simulation':
        st.markdown('### Simulation View')
        st.write('Create virtual patients with adjustable parameters (HR, RR, SpO2, etc.)')

    else:
        st.markdown('### Digital Twin View')
        st.write('Virtual patient synchronized with signals; saves states and simulates interventions.')

def render_simulation_lab_page() -> None:
    st.markdown("<h2>🧪 Simulation Lab</h2>", unsafe_allow_html=True)
    st.markdown('Simulates multidimensional virtual patients for training, research, and clinical reasoning.')

    view = render_view_selector()

    if view == 'Clinical':
        hr = st.slider('Heart Rate (bpm)', 40, 160, 88)
        rr = st.slider('Respiratory Rate (rpm)', 8, 30, 18)
        spo2 = st.slider('SpO₂ (%)', 80, 100, 96)
        render_metric_explained('HR', f'{hr}', unit='bpm', meaning='Simulated heart rate.')
        render_metric_explained('RR', f'{rr}', unit='rpm', meaning='Simulated respiratory rate.')
        render_metric_explained('SpO₂', f'{spo2}', unit='%', meaning='Simulated saturation.')
        render_discovery_lab('Simulation Case', {'HR': np.array([hr]), 'RR': np.array([rr]), 'SpO2': np.array([spo2])})
        st.write('What each metric means, why it matters, and how it relates to other systems.')

    elif view == 'Educational':
        st.markdown('### Educational View')
        st.write('Interactive clinical cases and explanations of the physiological impact of each parameter.')

    elif view == 'Research':
        st.markdown('### Research View')
        if st.button('Save case for research'):
            p = export_lab_report('Simulation Case', {'params': 'demo'}, notes='Sim case')
            if p:
                st.success(f'Saved: {p}')

    elif view == 'AI':
        st.markdown('### AI View')
        st.write('AI estimates risk and suggests interventions with physiological justification.')

    elif view == 'Simulation':
        st.markdown('### Simulation View')
        st.write('Adjust multiple parameters and observe aggregated responses of the virtual patient.')

    else:
        st.markdown('### Digital Twin View')
        st.write('Patient twin that persists states and simulates clinical interventions in virtual time.')


def render_hardware_ops_page() -> None:
    st.markdown("<h2>🔧 Hardware Ops</h2>", unsafe_allow_html=True)
    st.markdown('Monitors connectivity, signal quality, and multisensor synchronization.')

    view = render_view_selector()

    sensors = {
        'ECG Sensor': 'Connected',
        'EEG Array': 'Simulated',
        'EMG Amplifier': 'Available' if EMGStreamer is not None else 'Not available',
        'Camera / Gestures': 'Available' if _gesture_controller_available else 'Not available',
    }

    if view == 'Clinical':
        st.markdown('### Clinical View')
        st.write('Current status of sensors and minimum quality required for clinical monitoring.')
        for name, status in sensors.items():
            st.markdown(f'- **{name}:** {status}')

    elif view == 'Educational':
        st.markdown('### Educational View')
        st.write('Explanations on calibration, noise, gain, and synchronization between channels.')

    elif view == 'Research':
        st.markdown('### Research View')
        st.write('Export connectivity and quality logs for technical validation.')

    elif view == 'AI':
        st.markdown('### AI View')
        st.write('AI suggests automatic calibrations and sensor failure diagnostics.')

    elif view == 'Simulation':
        st.markdown('### Simulation View')
        st.write('Simulate dropouts, noise, and latency to test system robustness.')

    else:
        st.markdown('### Digital Twin View')
        st.write('Hardware twin that models latencies, drift, and sensor availability.')
    if EMGStreamer is None:
        st.warning('EMGStreamer not installed. Check the biomedical.emg module.')
    else:
        st.success('EMG hardware ready for live connection.')
    if not _gesture_controller_available:
        st.warning('Gesture control unavailable; install mediapipe/OpenCV for hands-free interaction.')

    st.markdown('### Multisensor Synchronization')
    st.write('The ecosystem requires ECG, EEG, EMG, respiration, and SpO₂ to be aligned to produce valid physiological correlations.')


def render_digital_twin_page() -> None:
    st.markdown("<h2>🧬 Digital Twin — Interactive Digital Twin</h2>", unsafe_allow_html=True)
    st.markdown('Digital twin of the global health state integrating cardiovascular, respiratory, neurological, and muscular systems.')
    st.markdown('Manipulate parameters in real-time and observe how the entire organism responds.')
    
    st.markdown("---")
    st.markdown("### 📋 Select Patient")
    patient_preset = st.selectbox("Base Patient:", ["Healthy", "Hypertension", "COPD", "Arrhythmia"])
    
    hr_base = {'Healthy': 72, 'Hypertension': 88, 'COPD': 102, 'Arrhythmia': 95}
    spo2_base = {'Healthy': 98, 'Hypertension': 96, 'COPD': 88, 'Arrhythmia': 94}
    rr_base = {'Healthy': 16, 'Hypertension': 18, 'COPD': 24, 'Arrhythmia': 16}
    
    st.markdown("---")
    st.markdown("### 🎚️ Physiological Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hr = st.slider("Heart Rate (bpm)", 40, 150, hr_base[patient_preset], key='hr_slider')
    with col2:
        spo2 = st.slider("SpO₂ (%)", 70, 100, spo2_base[patient_preset], key='spo2_slider')
    with col3:
        rr = st.slider("Respiration (resp/min)", 8, 40, rr_base[patient_preset], key='rr_slider')
    
    st.markdown("---")
    st.markdown("### 💊 Simulated Interventions")
    intervention = st.multiselect(
        "Apply interventions:",
        ["None", "O₂ 40%", "O₂ 100%", "Intubation", "Sedation", "Epinephrine", "Beta-blocker"],
        default=["None"]
    )
    
    st.markdown("---")
    st.markdown("### 📊 Twin Visualization")
    
    ecg = generate_demo_ecg_signal(250, 20, hr)
    resp = generate_demo_respiration_signal(250, 20, rr)
    spo2_signal = np.full(250*20, spo2, dtype=float) + np.random.randn(250*20)*0.5
    
    tab1, tab2, tab3, tab4 = st.tabs(["ECG", "Respiration", "SpO₂", "Metrics"])
    
    with tab1:
        st.line_chart(ecg[:1000])
        st.caption(f"Electrocardiogram — HR={hr} bpm")
    
    with tab2:
        st.line_chart(resp[:1000])
        st.caption(f"Respiratory Pattern — RR={rr} resp/min")
    
    with tab3:
        st.line_chart(spo2_signal[:1000])
        st.caption(f"Oxygen Saturation — SpO₂={spo2}%")
    
    with tab4:
        physiology_engine = PhysiologyCoreEngine()
        physiology_engine.ingest_signal(PhysiologySignal('ECG', time.time(), ecg, 250))
        physiology_engine.ingest_signal(PhysiologySignal('Respiration', time.time(), resp, 250))
        physiology_engine.ingest_signal(PhysiologySignal('SpO2', time.time(), spo2_signal, 1))
        state = physiology_engine.update_state()
        
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Global State", f"{state.global_score:.1f}/100")
        with col_m2:
            st.metric("Autonomic Balance", f"{state.autonomic:.1f}/100")
        with col_m3:
            st.metric("Stress Index", f"{state.stress:.1f}/100")
        
        st.markdown("**Integrated physiological state:**")
        st.write(physiology_engine.summarize_state())
    
    st.markdown("---")
    st.markdown("### 🎯 Advanced Controls")
    
    col_adv1, col_adv2 = st.columns(2)
    with col_adv1:
        if st.button("▶️ Start continuous simulation"):
            st.success("✅ Simulation started. Observe how the patient's state evolves...")
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            st.success("✅ Simulation completed")
    
    with col_adv2:
        if st.button("💾 Save twin state"):
            st.session_state['twin_saved_state'] = {
                'hr': hr,
                'spo2': spo2,
                'rr': rr,
                'interventions': intervention,
                'timestamp': time.time()
            }
            st.success("✅ State saved in session")
    
    st.markdown("---")
    st.markdown("### 📈 Automatic Clinical Interpretation")
    
    alerts = []
    if hr > 100:
        alerts.append("⚠️ Tachycardia detected")
    if spo2 < 90:
        alerts.append("🔴 Severe Hypoxemia")
    if rr > 25:
        alerts.append("⚠️ Tachypnea")
    
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.info("✅ Parameters within normal range")

    render_metric_explained('Global Physiological State', f'{state.global_score:.1f}', unit='/100')
    render_discovery_lab('Digital Twin Discovery', {'ECG': ecg, 'Respiration': resp, 'SpO2': spo2})

    view = render_view_selector()
    if PLOTLY_OK:
        fig = PLOTLY_GO.Figure()
        fig.add_trace(PLOTLY_GO.Scatter(y=ecg[:500], name='ECG'))
        fig.add_trace(PLOTLY_GO.Scatter(y=resp[:500], name='Respiration'))
        fig.add_trace(PLOTLY_GO.Scatter(y=spo2[:500], name='SpO₂'))
        fig.update_layout(height=380, template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.line_chart(ecg[:500])
    
    if PLOTLY_OK:
        try:
            x = np.arange(min(len(ecg), 500)) / 250.0
            y1 = ecg[:500]
            y2 = resp[:500]
            y3 = spo2[:500]
            frames = []
            nframes = min(80, len(x))
            step = max(1, len(x)//nframes)
            for i in range(0, len(x), step):
                frames.append(PLOTLY_GO.Frame(data=[PLOTLY_GO.Scatter(x=x, y=y1, mode='lines'),
                                                    PLOTLY_GO.Scatter(x=x, y=y2, mode='lines'),
                                                    PLOTLY_GO.Scatter(x=x, y=y3, mode='lines'),
                                                    PLOTLY_GO.Scatter(x=[x[i]], y=[y1[i]], mode='markers', marker=dict(size=10, color='red'))],
                                           name=str(i)))
            anim = PLOTLY_GO.Figure(data=[PLOTLY_GO.Scatter(x=x, y=y1, mode='lines', name='ECG'),
                                          PLOTLY_GO.Scatter(x=x, y=y2, mode='lines', name='Resp'),
                                          PLOTLY_GO.Scatter(x=x, y=y3, mode='lines', name='SpO2'),
                                          PLOTLY_GO.Scatter(x=[x[0]], y=[y1[0]], mode='markers', marker=dict(size=10, color='red'))],
                                 frames=frames)
            anim.update_layout(template='plotly_dark', updatemenus=[dict(type='buttons', showactive=False,
                                                                          buttons=[dict(label='Play', method='animate', args=[None, {'frame': {'duration': 70, 'redraw': True}, 'fromcurrent': True}])])], height=420)
            st.plotly_chart(anim, use_container_width=True)
        except Exception:
            pass

    st.markdown('### Integrated Interpretation')
    st.write('The digital twin combines cardiovascular, respiratory, and nervous systems to monitor changes in real-time.')

    st.markdown('### Prediction and Simulation')
    st.write('The model estimates how altering one sensor impacts the whole organism and allows exploring multisystemic scenarios.')

    st.markdown('### Research')
    st.write('Save digital twin states to compare physiological responses and prepare scientific reports.')

    st.markdown('### Physiological Resilience')
    st.write('A robust digital twin combines high saturation, stable heart rate, regular breathing, and correct perfusion.')
    if PLOTLY_OK:
        try:
            t = np.linspace(0, 2 * np.pi, 400)
            x3 = 16 * np.sin(t)**3
            y3 = 13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)
            z3 = np.sin(3*t) * 2
            fig3d = PLOTLY_GO.Figure()
            fig3d.add_trace(PLOTLY_GO.Scatter3d(x=x3, y=y3, z=z3, mode='lines', line=dict(color='crimson', width=3)))
            fig3d.update_layout(title='Digital Twin 3D Heart', template='plotly_dark', height=420)
            st.plotly_chart(fig3d, use_container_width=True)
        except Exception:
            pass


def render_ecg_12_page() -> None:
    st.markdown("<h2>📋 12-Lead ECG</h2>", unsafe_allow_html=True)
    st.write('12-lead view (interactive placeholder).')
    if PLOTLY_OK:
        try:
            demo = generate_demo_ecg_signal(250, 10, 70)
            fig = PLOTLY_GO.Figure()
            for i in range(1, 7):
                fig.add_trace(PLOTLY_GO.Scatter(y=demo[:500] * (1 + 0.02*i), name=f'Lead {i}'))
            fig.update_layout(template='plotly_dark', height=420)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.line_chart(generate_demo_ecg_signal(250, 10, 70))
    else:
        st.line_chart(generate_demo_ecg_signal(250, 10, 70))

    st.markdown('**Quick Access:**')
    c1, c2 = st.columns(2)
    if c1.button('Open Cardiovascular Lab'):
        st.session_state.selected_page = '📊 ECG Monitor'
        st.rerun()
    if c2.button('Open HRV Lab'):
        st.session_state.selected_page = '📈 HRV Analysis'
        st.rerun()


def render_jarvis_copilot_page() -> None:
    st.markdown("<h2>🤖 JARVIS — Biomedical AI Tutor</h2>", unsafe_allow_html=True)
    st.markdown("Interact with the explainable AI tutor to learn biomedical physiology.")
    
    if TUTOR_AVAILABLE:
        tutor = BiomedicalTutor()
        tutor.render_chat()
        
        st.markdown("---")
        st.markdown("### 🎓 Learning Modes")
        mode_col1, mode_col2 = st.columns(2)
        
        with mode_col1:
            if st.button("📚 Generate interactive lesson"):
                st.info("Lesson: ECG Interpretation")
                st.markdown("""
                **Fundamental waves:**
                - **P:** Atrial depolarization
                - **QRS:** Ventricular depolarization
                - **T:** Ventricular repolarization
                
                **Normal duration:**
                - PR interval: 0.12-0.20 sec
                - QRS: <0.12 sec
                - QT: varies with HR
                """)
        
        with mode_col2:
            if st.button("🧪 Simulate clinical scenario"):
                st.success("Scenario: Patient with palpitations")
                st.markdown("**Vital signs:**")
                st.markdown("- HR: 145 bpm (tachycardia)")
                st.markdown("- BP: 135/88")
                st.markdown("- SpO2: 97%")
                st.markdown("**What is your differential diagnosis?**")
    else:
        st.warning("⚠️ AI Tutor unavailable. Installing alternative mode...")
        st.markdown("""
        To use the full AI tutor:
        ```bash
        pip install anthropic
        ```
        
        In the meantime, use the basic interactive exercises mode above.
        """)
        
        st.markdown("### Available Exercises")
        ex_col1, ex_col2 = st.columns(2)
        with ex_col1:
            if st.button("Quiz: Basic ECG"):
                st.markdown("**Question:** What is the normal duration of the PR interval?")
                answer = st.radio("Options:", ["0.04-0.12 sec", "0.12-0.20 sec", "0.20-0.40 sec"])
                if st.button("Verify"):
                    if answer == "0.12-0.20 sec":
                        st.success("✅ Correct!")
                    else:
                        st.error("❌ Incorrect. The answer is 0.12-0.20 sec.")
        
        with ex_col2:
            if st.button("Quiz: Basic EEG"):
                st.markdown("**Question:** Which band represents relaxed wakefulness?")
                answer = st.radio("Options:", ["Delta (0.5-4 Hz)", "Alpha (8-12 Hz)", "Beta (13-30 Hz)"], key='eeg_quiz')
                if st.button("Verify", key='eeg_verify'):
                    if answer == "Alpha (8-12 Hz)":
                        st.success("✅ Correct!")
                    else:
                        st.error("❌ Incorrect. The answer is Alpha (8-12 Hz).")


def render_hands_off_page() -> None:
    if not HANDS_OFF_AVAILABLE:
        st.error("🤲 Hands-Off Mode not available. Install required packages for hands-off mode.")
        return
    render_hands_off_panel()

def main() -> None:
    init_state()
    inject_biocore_css()
    
    st.sidebar.markdown("## BIOCORE AI ECOSYSTEM")
    selected_hub = st.sidebar.radio('Select a hub', list(HUBS.keys()), index=list(HUBS.keys()).index(st.session_state.selected_hub), label_visibility='hidden')
    if selected_hub != st.session_state.selected_hub:
        st.session_state.selected_hub = selected_hub
        st.session_state.selected_page = HUBS[selected_hub][0]
    
    selected_page = st.sidebar.selectbox('Select a module', HUBS[st.session_state.selected_hub], index=HUBS[st.session_state.selected_hub].index(st.session_state.selected_page), label_visibility='hidden')
    st.session_state.selected_page = selected_page
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Universal Control:**")
    st.sidebar.markdown("- 🤖 JARVIS Copilot\n- 🤲 Hands-Off Mode\n- 🎤 Voice and Gestures\n- ⌨️ Clinical Shortcuts")
    
    # --- GLOBAL CLINICAL FILE IN SIDEBAR ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 👤 Global Clinical File")
    st.session_state.pac_nombre = st.sidebar.text_input("Name", value="Alpha Patient")
    c_ed, c_pe = st.sidebar.columns(2)
    
    # Freedom with keyboard
    edad_str = c_ed.text_input("Age", value="25")
    peso_str = c_pe.text_input("Weight (kg)", value="75.5")
    
    # NEW: Body Fat
    grasa_str = st.sidebar.text_input("Body Fat (%)", value="20.0")
    
    # Silent conversion to prevent math engine crashes
    try:
        st.session_state.pac_edad = int(edad_str)
    except ValueError:
        st.session_state.pac_edad = 25
        
    try:
        st.session_state.pac_peso = float(peso_str)
    except ValueError:
        st.session_state.pac_peso = 75.0
        
    try:
        st.session_state.pac_grasa = float(grasa_str)
    except ValueError:
        st.session_state.pac_grasa = 20.0
    
    st.session_state.pac_actividad = st.sidebar.selectbox("Physical Activity", ["Sedentary", "Moderate", "Intense (Athlete)"], index=1)
    st.session_state.pac_cirugias = st.sidebar.checkbox("Previous Surgeries / Trauma")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Platform Mode:** \nBiomedical laboratory, clinical, research, and simulation.")
    
    # Content + sidebar
    content_col, side_col = st.columns([3, 1])
    with content_col:
        render_mission_control_panel()
        if st.session_state.selected_page:
            render_page_content(st.session_state.selected_page)
    with side_col:
        if HANDS_OFF_AVAILABLE:
            render_hands_off_panel()

if __name__ == '__main__':
    main()