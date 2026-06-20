"""Interpretación AI de ECG."""

import os
import sys
import numpy as np
import streamlit as st
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from app.utils import (
        create_metric_row,
        display_error_message,
        display_info_message,
        display_success_message,
        display_warning_message,
        generate_demo_ecg_signal,
        plot_signal_matplotlib,
        render_sidebar_navigation,
        safe_import_plotly,
        safe_import_src_modules,
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

    create_metric_row = app_utils.create_metric_row
    display_error_message = app_utils.display_error_message
    display_info_message = app_utils.display_info_message
    display_success_message = app_utils.display_success_message
    display_warning_message = app_utils.display_warning_message
    generate_demo_ecg_signal = app_utils.generate_demo_ecg_signal
    plot_signal_matplotlib = app_utils.plot_signal_matplotlib
    render_sidebar_navigation = app_utils.render_sidebar_navigation
    safe_import_plotly = app_utils.safe_import_plotly
    safe_import_src_modules = app_utils.safe_import_src_modules
    validate_signal = app_utils.validate_signal

try:
    from clinical.ecg_analyzer import ECGAnalyzer
except ImportError:
    ECGAnalyzer = None

try:
    from src.ai.ecg_cnn import ECGCNNModel
except ImportError:
    ECGCNNModel = None

try:
    from src.interpretability import generate_shap_lime_report, feature_importance_summary
except ImportError:
    generate_shap_lime_report = None
    feature_importance_summary = None

try:
    from src.signals.signal_sources import ESP32SignalSource, SyntheticECGSource
except ImportError:
    ESP32SignalSource = None
    SyntheticECGSource = None

try:
    from deep_learning.explainability import grad_cam_placeholder
except ImportError:
    grad_cam_placeholder = None

st.set_page_config(page_title="Interpretación AI", layout="wide")
render_sidebar_navigation()

st.markdown(
    """
    <div style='padding: 24px; background: linear-gradient(135deg, #0f172a, #1d4ed8); border-radius: 24px; color: white; margin-bottom: 24px;'>
        <h1 style='margin-bottom: 8px;'>🤖 Interpretación AI de ECG</h1>
        <p style='font-size: 1.05rem; opacity: 0.9;'>Panel clínico-educativo que aplica análisis de ECG, métricas HRV y reporte inteligente para entorno médico.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    import main as main_pipeline
    HAS_MAIN_PIPELINE = True
except Exception:
    HAS_MAIN_PIPELINE = False

uploaded_file = None
load_record = False
st.markdown("### 🔧 Entradas del pipeline AI")
col1, col2 = st.columns([1, 2])
with col1:
    model_type = st.selectbox(
        "Modelo",
        ["Clasificador de arritmia", "Predictor de riesgo", "Detector de elevación ST"],
    )

    input_method = st.radio(
        "Origen de señal",
        [
            "Registro MIT-BIH de demostración",
            "Subir ECG CSV",
            "ECG sintético",
            "ECG ESP32 en vivo",
            "PPG/SpO2 ESP32 en vivo",
        ],
    )

    if input_method == "Subir ECG CSV":
        uploaded_file = st.file_uploader("Sube un CSV ECG de una columna", type=['csv'])
    elif input_method == "Registro MIT-BIH de demostración":
        selected_record = st.selectbox("Registro MIT-BIH", ["100", "101", "115", "117", "219"])
        load_record = st.button("Cargar registro")
    elif input_method == "ECG ESP32 en vivo" or input_method == "PPG/SpO2 ESP32 en vivo":
        esp32_port = st.text_input(
            "Puerto ESP32",
            value=st.session_state.get('esp32_port', ''),
            help="Ej. COM3 o /dev/ttyUSB0. Dejar vacío para detección automática.",
        )
        esp32_baud = st.number_input("Baudios ESP32", min_value=9600, value=st.session_state.get('esp32_baud', 115200), step=1)
        connect_clicked = st.button("Conectar ESP32", key="connect_esp32")
        disconnect_clicked = st.button("Desconectar ESP32", key="disconnect_esp32")

        if connect_clicked:
            st.session_state['esp32_port'] = esp32_port
            st.session_state['esp32_baud'] = esp32_baud
            if ESP32SignalSource is None:
                display_error_message(ValueError("ESP32SignalSource no está disponible."), "Hardware ESP32")
            else:
                try:
                    stream_source = ESP32SignalSource(port=esp32_port or None, baud=esp32_baud, fs=250)
                    connected = stream_source.connect(force_port=esp32_port or None)
                    if connected:
                        stream_source.start()
                        st.session_state['esp32_source'] = stream_source
                        st.success("ESP32 conectado y listo para transmisión en vivo.")
                    else:
                        st.warning("No se pudo conectar al ESP32. Verifica el puerto o usa modo demo.")
                except Exception as exc:
                    display_error_message(exc, "Conexión ESP32")

        if disconnect_clicked and 'esp32_source' in st.session_state:
            try:
                st.session_state['esp32_source'].stop()
                st.session_state['esp32_source'].disconnect()
            except Exception:
                pass
            del st.session_state['esp32_source']
            st.success("ESP32 desconectado.")

        if 'esp32_source' in st.session_state:
            source = st.session_state['esp32_source']
            source_status = source.get_status()
            st.info(f"Estado ESP32: {source_status}")
            if hasattr(source, 'last_error') and source.last_error:
                st.warning(f"Último error ESP32: {source.last_error}")
            if hasattr(source, 'is_connected') and source.is_connected():
                st.markdown("### 🔁 Modo en vivo activo")
                st.success("✅ ESP32 conectado. Los datos se actualizan en tiempo real.")
    else:
        if st.button("Generar ECG sintético"):
            st.session_state.demo_signal = True

with col2:
    st.markdown("### 📌 Qué hace esta página")
    st.markdown(
        """
- Carga registros MIT-BIH de demostración con la lógica central de la aplicación.  
- Ejecuta filtrado banda ancha, detección de picos R y extracción HRV.  
- Presenta un resumen clínico interactivo y un informe tipo terminal.  
- Explica el resultado del modelo y ofrece métricas de confianza para facilitar la interpretación.
        """
    )

st.markdown("<a id=\"como-interpretar-resultados\"></a>", unsafe_allow_html=True)
st.markdown("### Cómo interpretar los resultados")
st.markdown(
    "- Una alta probabilidad de arritmia requiere revisión del patrón de picos R y de los intervalos.\n"
    "- HRV bajo puede indicar estrés o disfunción autonómica.\n"
    "- Un modelo AI puede sugerir elevación ST, pero siempre valida visualmente con la forma de onda.\n"
)

st.markdown("---")


def load_signal_source():
    if input_method == "Subir ECG CSV" and uploaded_file is not None:
        import pandas as pd
        df = pd.read_csv(uploaded_file)
        if df.shape[1] >= 1:
            return df.iloc[:, 0].astype(float).to_numpy(), 250.0, "ECG cargado"
        raise ValueError("El CSV debe contener al menos una columna numérica.")

    if input_method == "Registro MIT-BIH de demostración" and load_record:
        if HAS_MAIN_PIPELINE:
            try:
                result = main_pipeline.load_mitbih_record(selected_record)
                if isinstance(result, tuple) and len(result) == 3:
                    signal, fs, metadata = result
                elif isinstance(result, tuple) and len(result) == 2:
                    signal, fs = result
                    metadata = {}
                else:
                    raise RuntimeError("La función de carga MIT-BIH devolvió un formato inesperado.")

                if signal is None:
                    raise RuntimeError("No se pudo cargar el registro MIT-BIH.")

                record_name = metadata.get('record_name', f"MIT-BIH {selected_record}")
                return signal, fs, record_name
            except Exception as exc:
                display_warning_message(f"El asistente MIT-BIH falló: {exc}")
                st.warning("Se usará ECG sintético de respaldo. Instala wfdb y activa internet para MIT-BIH real.")
                return generate_demo_ecg_signal(fs=250, duration=20), 250.0, "Demo sintético (fallback MIT-BIH)"
        else:
            display_warning_message("El asistente de pipeline main.py no está disponible.")
            st.warning("No se puede cargar MIT-BIH sin el pipeline principal. Usa ECG CSV o sintético.")
            return generate_demo_ecg_signal(fs=250, duration=20), 250.0, "Demo sintético"

    if input_method in ("ECG ESP32 en vivo", "PPG/SpO2 ESP32 en vivo"):
        if ESP32SignalSource is None:
            raise ImportError("ESP32SignalSource no está disponible. Instala pyserial y revisa hardware/esp32_stream.py")

        port_value = st.session_state.get('esp32_port', '') or None
        baud_value = st.session_state.get('esp32_baud', 115200)
        source = st.session_state.get('esp32_source')

        if source is None:
            source = ESP32SignalSource(port=port_value, baud=baud_value, fs=250)
            connected = source.connect(force_port=port_value)
            if connected:
                source.start()
                st.session_state['esp32_source'] = source
            else:
                display_warning_message(
                    f"No se pudo conectar al ESP32 en {port_value or 'auto'}. Usando demo sintética de respaldo cuando sea necesario."
                )

        if source is not None and hasattr(source, 'is_connected') and source.is_connected():
            if source._thread is None or not source._thread.is_alive():
                source.start()

        if input_method == "ECG ESP32 en vivo":
            t, signal = source.get_filtered_buffer() if source is not None else (np.array([]), np.array([]))
            if len(signal) < 5 or np.all(np.isnan(signal)):
                display_warning_message(
                    "Aún no hay suficientes datos ECG en el buffer del ESP32. Se usará ECG sintético de respaldo."
                )
                if SyntheticECGSource is not None:
                    synth = SyntheticECGSource(fs=250, duration=20)
                    return synth.get_buffer()[1], synth.fs, "Demo sintético ECG (fallback ESP32)"
                return generate_demo_ecg_signal(fs=250, duration=20), 250.0, "Demo sintético ECG"
            return signal, source.fs, f"ESP32 ECG en vivo ({source.port or 'auto'})"

        if input_method == "PPG/SpO2 ESP32 en vivo":
            t, ppg_buffer = source.get_ppg_buffer() if source is not None else (np.array([]), np.array([]))
            _, spo2_buffer = source.get_spo2_buffer() if source is not None else (np.array([]), np.array([]))
            ppg = np.nan_to_num(ppg_buffer, nan=0.0)
            if len(ppg) < 5 or np.all(ppg == 0.0):
                display_warning_message(
                    "Aún no hay suficientes datos PPG en el buffer del ESP32. Se usará ECG sintético de respaldo."
                )
                if SyntheticECGSource is not None:
                    synth = SyntheticECGSource(fs=250, duration=20)
                    return synth.get_buffer()[1], synth.fs, "Demo sintético PPG (fallback ESP32)"
                return generate_demo_ecg_signal(fs=250, duration=20), 250.0, "Demo sintético PPG"
            return ppg, source.fs, f"ESP32 PPG/SpO2 en vivo ({source.port or 'auto'})"

    if 'demo_signal' in st.session_state and st.session_state.demo_signal:
        return generate_demo_ecg_signal(fs=250, duration=20), 250.0, "Demo sintético"

    raise RuntimeError("No se seleccionó señal. Carga un registro de demostración o sube un CSV.")


def analyze_signal(signal, fs):
    modules, src_ok = safe_import_src_modules()
    if not src_ok:
        raise ImportError("Los módulos del pipeline no están disponibles.")

    filtered = modules['bandpass_filter'](signal, fs)
    peaks, _ = modules['detect_r_peaks'](filtered, fs)
    rr_intervals = modules['compute_rr_intervals'](peaks, fs) if len(peaks) > 1 else np.array([])
    hrv = {}
    psd_meta = None
    if rr_intervals.size >= 4:
        freqs, psd = modules['compute_psd'](rr_intervals)
        hrv = modules['extract_features'](rr_intervals, psd, freqs)
        psd_meta = (freqs, psd)
    return filtered, peaks, rr_intervals, hrv, psd_meta


def create_terminal_report(record_name, fs, peaks, hrv, pattern_info=None, explainability=None):
    bpm = hrv.get('BPM', np.nan)
    sdnn_ms = hrv.get('SDNN', np.nan) * 1000 if 'SDNN' in hrv else np.nan
    rmssd_ms = hrv.get('RMSSD', np.nan) * 1000 if 'RMSSD' in hrv else np.nan
    lf_hf = hrv.get('LF_HF', np.nan)
    diagnosis = pattern_info.get('pattern', 'No disponible') if pattern_info else 'No disponible'
    confidence = pattern_info.get('confidence', 0.0) if pattern_info else 0.0
    reasoning = ', '.join(pattern_info.get('reasoning', [])) if pattern_info else 'Sin razonamiento disponible'
    explain_text = '\n'.join(explainability) if explainability else 'No hay información de explicabilidad disponible.'
    return f"""
=== Informe del Pipeline AI ===
Fuente: {record_name}
Frecuencia de muestreo: {fs:.0f} Hz
Picos R detectados: {len(peaks)}

Características HRV:
- BPM: {bpm:.1f} bpm
- SDNN: {sdnn_ms:.1f} ms
- RMSSD: {rmssd_ms:.1f} ms
- Relación LF/HF: {lf_hf:.2f}

Clasificación AI:
- Predicción: {diagnosis}
- Confianza: {confidence*100:.0f}%
- Insights: {reasoning}

Explicabilidad SHAP/LIME:
{explain_text}

Resumen clínico:
- Ritmo: {'Ritmo sinusal normal' if 60 <= bpm <= 100 else 'Anormal'}
- Recomendación: revisar la morfología del ECG y seguir protocolo clínico.
"""


def render_plots(signal, fs, peaks, psd_meta):
    go, sp, plotly_ok = safe_import_plotly()
    if plotly_ok:
        try:
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=np.arange(len(signal)) / fs, y=signal, name='Señal ECG', line=dict(color='#1d4ed8')))
            fig.update_layout(title='Señal ECG', xaxis_title='Tiempo (s)', yaxis_title='Amplitud', height=380)
            st.plotly_chart(fig, use_container_width=True)
            if psd_meta is not None:
                freqs, psd = psd_meta
                psd_fig = go.Figure()
                psd_fig.add_trace(go.Scatter(x=freqs, y=psd, mode='lines', name='PSD', line=dict(color='#0f766e')))
                psd_fig.update_layout(title='Espectro de potencia de intervalos RR', xaxis_title='Frecuencia (Hz)', yaxis_title='Potencia', height=360)
                st.plotly_chart(psd_fig, use_container_width=True)
            return
        except Exception as exc:
            display_warning_message(f"La visualización Plotly falló: {exc}")
    plot_signal_matplotlib(signal, fs, title="Señal ECG")


def render_feature_importance_chart(importances):
    if not importances:
        return
    go, sp, plotly_ok = safe_import_plotly()
    if not plotly_ok:
        return
    try:
        import plotly.graph_objects as go
        labels = [item['label'] for item in importances]
        values = [item['value'] for item in importances]
        fig = go.Figure(go.Bar(x=values, y=labels, orientation='h', marker_color='#2563eb'))
        fig.update_layout(title='Importancia de características', xaxis_title='Valor', yaxis_title='Característica', height=360)
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        pass

try:
    if (input_method == "Subir ECG CSV" and uploaded_file is not None) or (input_method == "Registro MIT-BIH de demostración" and load_record) or (input_method in ("ECG ESP32 en vivo", "PPG/SpO2 ESP32 en vivo")) or ('demo_signal' in st.session_state and st.session_state.demo_signal):
        signal, fs, record_name = load_signal_source()
        valid, message = validate_signal(signal)
        if not valid:
            st.error(f"Validación de señal fallida: {message}")
        else:
            filtered, peaks, rr_intervals, hrv, psd_meta = analyze_signal(signal, fs)
            if ECGAnalyzer is not None:
                analyzer = ECGAnalyzer(fs=fs)
                pattern_info = analyzer.detect_clinical_pattern(filtered)
            else:
                analyzer = None
                pattern_info = {'pattern': 'AI no disponible', 'confidence': 0.0, 'reasoning': ['Analizador clínico no cargado']}

            if model_type == 'Clasificador de arritmia':
                diagnosis = pattern_info['pattern']
            elif model_type == 'Predictor de riesgo':
                confidence = pattern_info['confidence']
                risk_level = 'Alto riesgo' if confidence > 0.85 else 'Moderado riesgo' if confidence > 0.6 else 'Bajo riesgo'
                diagnosis = f"{risk_level} ({confidence*100:.0f}% de confianza)"
            else:
                diagnosis = 'STEMI probable' if pattern_info['pattern'] == 'STEMI' else 'Sin elevación ST clara'

            explainability = {
                'shap': ['Explicabilidad no disponible.'],
                'lime': ['Explicabilidad no disponible.'],
                'importance': []
            }
            if generate_shap_lime_report is not None:
                explainability = generate_shap_lime_report(hrv, pattern_info['pattern'], pattern_info.get('confidence', 0.0))
            elif feature_importance_summary is not None:
                explainability['importance'] = feature_importance_summary(hrv, pattern_info['pattern'], pattern_info.get('confidence', 0.0))

            st.markdown("### 🔬 Resumen del pipeline")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Origen", record_name)
            col2.metric("Frecuencia", f"{fs:.0f} Hz")
            col3.metric("Picos R", len(peaks))
            col4.metric("Predicción", diagnosis)

            if hrv:
                create_metric_row({
                    'BPM': (f"{hrv.get('BPM', np.nan):.1f}", 'bpm'),
                    'SDNN': (f"{hrv.get('SDNN', np.nan)*1000:.1f}", 'ms'),
                    'RMSSD': (f"{hrv.get('RMSSD', np.nan)*1000:.1f}", 'ms'),
                    'LF/HF': (f"{hrv.get('LF_HF', np.nan):.2f}", ''),
                }, columns=4)

            st.markdown("---")
            st.markdown("### 📈 Revisión de señal")
            render_plots(filtered, fs, peaks, psd_meta)

            if analyzer is not None:
                st.markdown("---")
                st.markdown("### 🧠 Explicabilidad y hallazgos AI")
                st.write(f"**Clasificación detectada:** {pattern_info['pattern']}")
                st.write(f"**Confianza:** {pattern_info['confidence']*100:.0f}%")
                st.write(f"**Insights:** {', '.join(pattern_info.get('reasoning', []))}")

                if explainability and explainability.get('shap'):
                    st.markdown("#### SHAP-like Explanation")
                    for row in explainability['shap']:
                        st.write(row)

                if explainability and explainability.get('lime'):
                    st.markdown("#### LIME-like Explanation")
                    for row in explainability['lime']:
                        st.write(row)

                if explainability and explainability.get('importance'):
                    st.markdown("#### Feature Importance")
                    for importance_item in explainability['importance'][:4]:
                        st.write(
                            f"- {importance_item['label']}: {importance_item['value']:.2f} "
                            f"({importance_item['percent']:.0f}%) - {importance_item['human']}"
                        )
                    render_feature_importance_chart(explainability['importance'])

            st.markdown("---")
            st.markdown("### 🧾 Informe estilo terminal")
            report_text = create_terminal_report(record_name, fs, peaks, hrv, pattern_info, explainability=explainability.get('shap') if explainability else None)
            st.code(report_text, language='text')
            st.success("Análisis del pipeline completado usando módulos clínicos centrales.")
    else:
        display_info_message("Selecciona una fuente y carga una señal para ejecutar el pipeline AI.")
except Exception as exc:
    display_error_message(exc, "Pipeline AI")

st.markdown("---")
with st.expander("ℹ️ Acerca de esta página"):
    st.markdown(
        "Esta página integra el mismo flujo central de carga de ECG y análisis de señal usado en el pipeline de main.py, presentando un informe clínico pulido para datos demo o cargados."
    )
