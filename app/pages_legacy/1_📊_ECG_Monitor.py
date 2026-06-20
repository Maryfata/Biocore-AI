"""Real-Time ECG Analysis and Visualization."""

import os
import sys
import time
import streamlit as st
import numpy as np

try:
    from streamlit import st_autorefresh
except Exception:
    st_autorefresh = None  # type: ignore

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from app.utils import (
        display_error_message,
        display_info_message,
        display_success_message,
        display_warning_message,
        generate_demo_ecg_signal,
        generate_demo_ppg_signal,
        generate_demo_spo2_signal,
        plot_clinical_ecg_safe,
        plot_signal_matplotlib,
        render_sidebar_navigation,
        safe_import_ecg_modules,
        safe_import_plotly,
        validate_signal,
    )
    from src.signals.signal_sources import ESP32SignalSource, PhysioNetECGSource, SyntheticECGSource
    from clinical.ecg_analyzer import ECGAnalyzer
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

    display_error_message = app_utils.display_error_message
    display_info_message = app_utils.display_info_message
    display_success_message = app_utils.display_success_message
    display_warning_message = app_utils.display_warning_message
    generate_demo_ecg_signal = app_utils.generate_demo_ecg_signal
    plot_clinical_ecg_safe = app_utils.plot_clinical_ecg_safe
    plot_signal_matplotlib = app_utils.plot_signal_matplotlib
    render_sidebar_navigation = app_utils.render_sidebar_navigation
    safe_import_ecg_modules = app_utils.safe_import_ecg_modules
    safe_import_plotly = app_utils.safe_import_plotly
    validate_signal = app_utils.validate_signal
    try:
        from src.signals.signal_sources import ESP32SignalSource, PhysioNetECGSource, SyntheticECGSource
    except ImportError:
        ESP32SignalSource = None
        PhysioNetECGSource = None
        SyntheticECGSource = None


def load_clinical_case(case_name: str, fs: int = 250):
    """Load a predefined clinical demo case for ECG interpretation."""
    try:
        from src.clinical.case_database import (
            generate_afib_case,
            generate_pvc_case,
            generate_vt_case,
            generate_av_block_case,
            generate_bundle_branch_case,
            generate_stemi_case,
            ArrhythmiaType,
        )
    except Exception:
        return generate_demo_ecg_signal(fs=fs, duration=15), fs, "Demo sintético"

    case_map = {
        'AFib demo': generate_afib_case('DEMO', age=65, sex='F'),
        'PVC demo': generate_pvc_case('DEMO', age=58, sex='M', pvc_rate=8),
        'VT demo': generate_vt_case('DEMO', age=60, sex='M', sustained=True),
        'AV Block demo': generate_av_block_case('DEMO', age=72, sex='F', degree=2),
        'LBBB demo': generate_bundle_branch_case('DEMO', age=68, sex='F', block_type='LBBB'),
        'RBBB demo': generate_bundle_branch_case('DEMO', age=62, sex='M', block_type='RBBB'),
        'STEMI demo': generate_stemi_case('DEMO', age=54, sex='M', location='anterior'),
    }

    case = case_map.get(case_name)
    if case is None:
        return generate_demo_ecg_signal(fs=fs, duration=15), fs, "Demo sintético"

    return case.ecg_signal, case.fs, f"Caso clínico {case_name}"


def load_ptbxl_record(record_id: str, lead: int = 0) -> tuple[np.ndarray, float, dict]:
    try:
        import wfdb
    except ImportError as e:
        raise ImportError('wfdb no está instalado. Instala con: pip install wfdb') from e

    try:
        record = wfdb.rdrecord(record_id, pn_dir='ptbxl')
    except Exception as exc:
        error_text = str(exc).lower()
        if '404' in error_text or 'not found' in error_text or 'pn_dir' in error_text or 'no se pudo' in error_text:
            fallback_signal = generate_demo_ecg_signal(fs=250, duration=30)
            return fallback_signal, 250.0, {
                'record_name': f'Fallback demo PTB-XL {record_id}',
                'source': 'PTB-XL fallback',
            }
        raise RuntimeError(f'No se pudo cargar el registro PTB-XL: {exc}') from exc

    signal = record.p_signal[:, lead]
    fs = record.fs
    metadata = {'record_name': record.record_name, 'source': 'PTB-XL'}
    return signal, fs, metadata


def get_ptbxl_records() -> list[str]:
    return ['10038', '11106', '14544', '17242', '52651']


def init_ecg_monitor_session_state() -> None:
    defaults = {
        'esp32_source': None,
        'esp32_port': 'Auto',
        'esp32_baud': 115200,
        'esp32_simulate': True,
        'esp32_refresh_ms': 800,
        'esp32_mode': 'ECG sólo',
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_ecg_analysis(signal: np.ndarray, fs: float, title: str = 'ECG Signal'):
    signal = np.asarray(signal, dtype=float)
    valid, message = validate_signal(signal)
    if not valid:
        st.error(f"Señal inválida: {message}")
        return

    analyzer = ECGAnalyzer(fs=fs) if ECGAnalyzer else None
    r_peaks = analyzer.detect_r_peaks(signal) if analyzer else None

    if create_clinical_ecg_figure:
        try:
            fig = create_clinical_ecg_figure(
                signal,
                fs,
                r_peaks=r_peaks,
                time_window=(0, min(window_length, len(signal) / fs)),
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            display_warning_message(f"La visualización Plotly falló: {e}")
            plot_signal_matplotlib(signal, fs, title=title)
    else:
        plot_signal_matplotlib(signal, fs, title=title)

    if analyzer:
        hr = analyzer.estimate_heart_rate(r_peaks)
        intervals = analyzer.measure_intervals(signal)
        pattern_info = analyzer.detect_clinical_pattern(signal)

        st.markdown("---")
        col_hr, col_pr, col_qrs, col_qt = st.columns(4)
        col_hr.metric("Frecuencia cardíaca", f"{hr:.0f}", "bpm")
        col_pr.metric("Intervalo PR", f"{intervals.get('PR_interval_ms', 0):.0f}", "ms")
        col_qrs.metric("Duración QRS", f"{intervals.get('QRS_duration_ms', 0):.0f}", "ms")
        col_qt.metric("QTc", f"{intervals.get('QTc_ms', 0):.0f}", "ms")

        st.markdown("### 🧠 Interpretación clínica AI")
        st.write(f"**Clasificación:** {pattern_info['pattern']} ({pattern_info['confidence']*100:.0f}%)")
        st.write(f"**Insights:** {', '.join(pattern_info.get('reasoning', ['Revisión recomendada']))}")
        st.write(analyzer.clinical_summary(signal))

st.set_page_config(page_title="Monitor ECG en Tiempo Real", layout="wide")
render_sidebar_navigation()

st.markdown(
    """
    <h1 id="ecg-monitor" style="color: #1f77b4;">📊 Monitor ECG en Tiempo Real</h1>
    <p>Interpreta ECG paso a paso con opciones de carga de archivo, MIT-BIH y hardware simulado.</p>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    ### Contenidos rápidos
    - [Introducción al ECG](#introduccion-al-ecg)
    - [Cómo cargar datos](#como-cargar-datos)
    - [Interpretación básica](#interpretacion-basica)
    - [Qué hacer si no tienes hardware](#sin-hardware)
    """
)

st.markdown('<a id="introduccion-al-ecg"></a>', unsafe_allow_html=True)
st.markdown("### Introducción al ECG")
st.write(
    "El electrocardiograma mide la actividad eléctrica del corazón. En esta página puedes analizar la forma de onda, la frecuencia cardíaca, los intervalos PR/QRS/QT y detectar arritmias básicas."
)

st.markdown("<a id=\"como-cargar-datos\"></a>", unsafe_allow_html=True)
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### ⚙️ Configuración")
    data_source = st.radio(
        "Fuente de datos",
        ["Archivo subido", "Base de datos MIT-BIH", "Base de datos PTB-XL", "Caso clínico demo", "Hardware en vivo"],
    )
    fs = st.slider("Frecuencia de muestreo (Hz)", 100, 1000, 250)
    window_length = st.slider("Ventana de visualización (s)", 5, 30, 10)

    if data_source == "Caso clínico demo":
        sample_case = st.selectbox(
            "Seleccionar caso clínico",
            [
                "AFib demo",
                "PVC demo",
                "VT demo",
                "AV Block demo",
                "LBBB demo",
                "RBBB demo",
                "STEMI demo",
            ],
        )
        if st.button("Cargar caso clínico"):
            try:
                signal, loaded_fs, record_label = load_clinical_case(sample_case, fs=fs)
                st.session_state['_bsp_loaded_signal'] = signal
                st.session_state['_bsp_loaded_fs'] = loaded_fs
                st.session_state['_bsp_loaded_label'] = record_label
                st.session_state['_bsp_source'] = 'clinical_case'
                st.success(f"Caso clínico cargado: {sample_case}")
            except Exception as exc:
                display_error_message(exc, "Carga de caso clínico")

with col2:
    st.markdown("### 📈 Visualización ECG")
    
    ECGAnalyzer, create_clinical_ecg_figure, load_mitbih_record, get_mitbih_records, ecg_ok = safe_import_ecg_modules()
    
    if data_source == "Archivo subido":
        uploaded_file = st.file_uploader(
            "Selecciona archivo ECG (CSV, WFDB, EDF)",
            type=['csv', 'hea', 'edf', 'txt'],
        )

        if uploaded_file is not None:
            try:
                signal = None
                if uploaded_file.type == 'text/csv':
                    import pandas as pd
                    df = pd.read_csv(uploaded_file)
                    signal = df.iloc[:, 0].astype(float).to_numpy()
                else:
                    st.warning("Tipo de archivo no compatible directamente. Usa CSV o WFDB.")

                if signal is not None:
                    is_valid, validation_message = validate_signal(signal)
                    if is_valid:
                        render_ecg_analysis(signal, fs, title="ECG de archivo cargado")
                    else:
                        st.error(f"No se encontró una señal ECG válida en el archivo cargado: {validation_message}")
                else:
                    st.error("No se encontró una señal ECG válida en el archivo cargado.")
            except Exception as e:
                display_error_message(e, "Carga de archivo ECG")

    elif data_source == "Base de datos MIT-BIH":
        if get_mitbih_records is None or load_mitbih_record is None:
            st.warning("Soporte MIT-BIH no disponible. Instala wfdb y reinicia la app.")
            st.markdown("**Ejemplos MIT-BIH:** 100, 101, 115, 117, 219")
            if st.button("Mostrar demo ECG sintético"):
                demo_signal = generate_demo_ecg_signal(fs=fs, duration=30)
                render_ecg_analysis(demo_signal, fs, title="ECG Demo Sintético")
        else:
            try:
                records = get_mitbih_records()
            except Exception as mit_exc:
                st.warning("No se pudo obtener la lista MIT-BIH. Verifica wfdb y la conexión a internet.")
                st.warning(str(mit_exc))
                records = []

            if not records:
                st.warning("No hay registros MIT-BIH disponibles. Usa CSV o muestra demo para continuar.")
                if st.button("Mostrar demo ECG sintético"):
                    demo_signal = generate_demo_ecg_signal(fs=fs, duration=30)
                    render_ecg_analysis(demo_signal, fs, title="ECG Demo Sintético")
            else:
                selected_record = st.selectbox("Seleccionar registro", records)
                if st.button("Cargar registro MIT-BIH"):
                    try:
                        signal, loaded_fs, metadata = load_mitbih_record(selected_record)
                        st.info(f"Cargado: {metadata.get('record_name', selected_record)}")
                        render_ecg_analysis(signal, loaded_fs, title=f"MIT-BIH {selected_record}")
                    except Exception as e:
                        error_text = str(e)
                        if 'pb_dir' in error_text or 'pn_dir' in error_text or 'Not Found' in error_text or '404' in error_text:
                            display_warning_message(
                                "El loader MIT-BIH falló por incompatibilidad o registro no disponible en PhysioNet. Usando ECG demo sintético."
                            )
                            demo_signal = generate_demo_ecg_signal(fs=fs, duration=30)
                            render_ecg_analysis(demo_signal, fs, title="ECG Demo Sintético")
                        else:
                            display_error_message(e, "Registro MIT-BIH")

    elif data_source == "Base de datos PTB-XL":
        record_options = get_ptbxl_records()
        selected_ptb = st.selectbox("Seleccionar registro PTB-XL", record_options)
        if st.button("Cargar PTB-XL"):
            try:
                signal, loaded_fs, metadata = load_ptbxl_record(selected_ptb)
                if metadata.get('source') == 'PTB-XL fallback':
                    display_warning_message(
                        "No se pudo descargar PTB-XL desde PhysioNet. Se cargó un ECG sintético de respaldo."
                    )
                st.info(f"Cargado: {metadata.get('record_name', selected_ptb)}")
                render_ecg_analysis(signal, loaded_fs, title=f"PTB-XL {selected_ptb}")
            except Exception as e:
                display_error_message(e, "Registro PTB-XL")

    elif data_source == "Caso clínico demo":
        if st.session_state.get('_bsp_source') == 'clinical_case' and st.session_state.get('_bsp_loaded_signal') is not None:
            render_ecg_analysis(
                st.session_state['_bsp_loaded_signal'],
                st.session_state['_bsp_loaded_fs'],
                title=st.session_state.get('_bsp_loaded_label', 'Caso clínico demo'),
            )
        else:
            st.info("Carga un caso clínico demo para comenzar la interpretación.")

    else:
        init_ecg_monitor_session_state()
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Live Hardware Stream")
        st.session_state.esp32_mode = st.sidebar.selectbox(
            "Modo de señal",
            ["ECG sólo", "ECG + PPG + SpO2"],
            index=0 if st.session_state.esp32_mode == "ECG sólo" else 1,
        )
        port = st.sidebar.text_input('Puerto serial o Auto', value=st.session_state.esp32_port)
        baud_rate_options = [9600, 19200, 38400, 57600, 115200]
        baud = st.sidebar.selectbox(
            'Baudrate',
            baud_rate_options,
            index=baud_rate_options.index(st.session_state.esp32_baud) if st.session_state.esp32_baud in baud_rate_options else 4,
        )
        simulate = st.sidebar.checkbox('Simular si no detecta hardware', value=st.session_state.esp32_simulate)
        refresh_ms = st.sidebar.number_input(
            'Refrescar cada (ms)',
            min_value=250,
            max_value=2000,
            value=st.session_state.esp32_refresh_ms,
            step=50,
        )
        connect_button = st.sidebar.button('Conectar y empezar streaming')
        stop_button = st.sidebar.button('Detener streaming')

        st.session_state.esp32_port = port
        st.session_state.esp32_baud = baud
        st.session_state.esp32_simulate = simulate
        st.session_state.esp32_refresh_ms = refresh_ms

        source = st.session_state.get('esp32_source')
        if source is not None and hasattr(source, 'is_connected') and not source.is_connected():
            st.session_state.esp32_source = None
            source = None

        if connect_button:
            if ESP32SignalSource is None:
                st.error(
                    'El soporte de hardware ESP32 no está disponible. Revisa la instalación de pyserial y el módulo src.signals.signal_sources.'
                )
            else:
                chosen_port = None if port.strip().lower() == 'auto' else port.strip()
                try:
                    new_source = ESP32SignalSource(
                        port=chosen_port,
                        baud=baud,
                        timeout=1.0,
                        fs=fs,
                        buffer_seconds=30,
                        simulate_if_missing=simulate,
                    )
                    if new_source.connect(force_port=chosen_port):
                        new_source.start()
                        st.session_state.esp32_source = new_source
                        source = new_source
                        st.success('Streaming iniciado desde ESP32.')
                    else:
                        st.error('No se pudo conectar al ESP32. Revisa el puerto y la configuración.')
                except Exception as exc:
                    display_error_message(exc, 'Conexión ESP32')

        if stop_button:
            if source is not None:
                try:
                    source.stop()
                    source.disconnect()
                except Exception:
                    pass
            st.session_state.esp32_source = None
            source = None
            st.info('Streaming detenido.')

        if source is not None and source.is_connected():
            health = source.get_health_summary()
            status_cols = st.columns(4)
            status_cols[0].metric('Estado', health.get('state', 'Desconocido'))
            status_cols[1].metric('Buffer (s)', f"{health.get('buffer_seconds', 0):.1f}")
            status_cols[2].metric('BPM', f"{health.get('bpm', 'N/A') if health.get('bpm') else 'N/A'}")
            status_cols[3].metric('Ruido', f"{health.get('noise_std', 0):.2f}")
            st.markdown(f"- PPG presente: {health.get('ppg_present', 'No')}")
            st.markdown(f"- SpO2 presente: {health.get('spo2_present', 'No')}")
            if health.get('last_error'):
                st.warning(f"Último error: {health.get('last_error')}")

            t_ecg, ecg_signal = source.get_filtered_buffer()
            ppg_time, ppg_signal = source.get_ppg_buffer()
            spo2_time, spo2_signal = source.get_spo2_buffer()

            if ecg_signal.size > 0:
                if create_clinical_ecg_figure is not None:
                    try:
                        import plotly.graph_objects as go
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=t_ecg, y=ecg_signal, mode='lines', name='ECG'))
                        fig.update_layout(title='ECG en vivo', xaxis_title='Tiempo (s)', yaxis_title='mV')
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        st.line_chart(ecg_signal)
                else:
                    st.line_chart(ecg_signal)

                if source.is_connected() and ecg_signal.size >= fs * 5:
                    st.markdown('### Interpretación clínica temporal')
                    render_ecg_analysis(ecg_signal[-int(min(len(ecg_signal), fs * window_length)):], fs, title='ECG Vivo — Última ventana')

            if st.session_state.esp32_mode == 'ECG + PPG + SpO2':
                if ppg_signal.size > 0 and np.isfinite(ppg_signal).any():
                    st.markdown('### PPG en vivo')
                    st.line_chart(ppg_signal)
                else:
                    st.info('Aún no se reciben datos PPG desde el ESP32.')

                if spo2_signal.size > 0 and np.isfinite(spo2_signal).any():
                    st.markdown('### SpO2 en vivo')
                    st.line_chart(spo2_signal)
                else:
                    st.info('Aún no se reciben datos SpO2 desde el ESP32.')

            if st.sidebar.button('Exportar última ventana como CSV') and ecg_signal.size > 0:
                try:
                    import pandas as pd
                    df = pd.DataFrame({'time': t_ecg, 'ecg': ecg_signal})
                    csv_path = f"datasets/esp32_live_{int(time.time())}.csv"
                    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
                    df.to_csv(csv_path, index=False)
                    st.success(f'CSV guardado en {csv_path}')
                except Exception as exc:
                    display_error_message(exc, 'Exportar CSV')

            if st_autorefresh is not None:
                st_autorefresh(interval=refresh_ms, key='esp32_refresh')
        else:
            st.info('Conecta hardware ESP32 para iniciar streaming o habilita simulación para ver la señal en vivo.')
            st.markdown(
                """
                **Hardware Setup:**
                - ESP32 Development Board
                - AD8232 ECG Amplifier or PPG/Spo2 sensor module
                - Electrode pads and USB cable
                - Firmware that outputs lines like `timestamp,ecg` or `timestamp,ecg,ppg,spo2`
                """
            )
            with st.expander('Cómo usar el streaming en vivo'):
                st.markdown(
                    "1. Conecta el ESP32 por USB y selecciona el puerto `Auto` o escribe el COM correcto.\n"
                    "2. Ajusta `Baudrate` a 115200 o el valor usado por tu firmware.\n"
                    "3. El firmware debe emitir `timestamp,ecg[,ppg[,spo2]]` por serie.\n"
                    "4. Pulsa `Conectar y empezar streaming`.\n"
                    "5. Si no tienes hardware, activa simulación para ver datos sintéticos."
                )
