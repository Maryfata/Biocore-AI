"""Página: 📊 ECG Monitor — prototipo 'Biomedical Cognitive Exploration Lab'.

Fusiona la funcionalidad clínica existente con las seis vistas obligatorias:
Clínica, Educativa, Investigación, IA, Simulación y Gemelo Digital.
"""

import os
import sys
import streamlit as st
import numpy as np

try:
    from streamlit import st_autorefresh
except Exception:
    st_autorefresh = None  # type: ignore

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from app.supermodules import (
        display_error_message,
        display_info_message,
        display_success_message,
        display_warning_message,
        generate_demo_ecg_signal,
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
    ECGAnalyzer = None
    # ensure create_clinical_ecg_figure defaults
    try:
        create_clinical_ecg_figure = app_utils.create_clinical_ecg_figure
    except Exception:
        create_clinical_ecg_figure = None



def load_clinical_case(case_name: str, fs: int = 250):
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


def _save_signal_csv(signal: np.ndarray, fs: float, prefix: str = 'ecg_export') -> str:
    import time
    import pandas as pd

    ts = int(time.time())
    os.makedirs('datasets/exports', exist_ok=True)
    filename = f'datasets/exports/{prefix}_{ts}.csv'
    times = np.arange(len(signal)) / float(fs)
    df = pd.DataFrame({'time': times, 'signal': signal})
    df.to_csv(filename, index=False)
    return filename


def _create_reproducible_notebook(csv_path: str, metadata: dict) -> str:
    import json
    import time

    nb = {
        'cells': [
            {
                'cell_type': 'markdown',
                'metadata': {'language': 'markdown'},
                'source': [
                    f"# ECG Analysis Notebook\n",
                    f"**Provenance:** {json.dumps(metadata)}\n",
                    "This notebook loads the exported ECG CSV and runs a simple plot and HR estimate."
                ],
            },
            {
                'cell_type': 'code',
                'metadata': {'language': 'python'},
                'source': [
                    "import pandas as pd\n",
                    "import matplotlib.pyplot as plt\n",
                    f"df = pd.read_csv(r'{csv_path}')\n",
                    "plt.plot(df['time'], df['signal'])\n",
                    "plt.xlabel('Time (s)')\n",
                    "plt.ylabel('ECG')\n",
                    "plt.show()\n",
                ],
            },
        ],
        'metadata': {'kernelspec': {'name': 'python3', 'language': 'python'}, 'language_info': {'name': 'python'}},
        'nbformat': 4,
        'nbformat_minor': 5,
    }

    ts = int(time.time())
    os.makedirs('notebooks/exports', exist_ok=True)
    nb_path = f'notebooks/exports/ecg_notebook_{ts}.ipynb'
    with open(nb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2)

    # save provenance alongside
    prov_path = nb_path + '.prov.json'
    with open(prov_path, 'w', encoding='utf-8') as pf:
        json.dump(metadata, pf, indent=2)

    return nb_path


def render_ecg_analysis(signal: np.ndarray, fs: float, title: str = 'ECG Signal'):
    signal = np.asarray(signal, dtype=float)
    valid, message = validate_signal(signal)
    if not valid:
        st.error(f"Señal inválida: {message}")
        return

    analyzer = None
    try:
        analyzer = ECGAnalyzer(fs=fs) if ECGAnalyzer else None
    except Exception:
        analyzer = None
    r_peaks = analyzer.detect_r_peaks(signal) if analyzer else None
    # Preferir Plotly clínico si está disponible (intentamos importarlo dinámicamente)
    try:
        _, create_fig, _, _, _ = safe_import_ecg_modules()
    except Exception:
        create_fig = None

    if create_fig:
        try:
            fig = create_fig(
                signal,
                fs,
                r_peaks=r_peaks,
                time_window=(0, min(10, len(signal) / fs)),
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
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


def main():
    st.set_page_config(page_title="Monitor ECG en Tiempo Real", layout="wide")
    render_sidebar_navigation()

    st.markdown(
        """
        <h1 id="ecg-monitor" style="color: #1f77b4;">📊 Monitor ECG en Tiempo Real</h1>
        <p>Interpreta ECG paso a paso con opciones de carga de archivo, MIT-BIH y hardware simulado.</p>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["Clínica", "Educativa", "Investigación", "IA", "Simulación", "Gemelo Digital"])

    # Clínica
    with tabs[0]:
        st.header("Vista Clínica")
        st.markdown("### Cargar y visualizar ECG")
        col1, col2 = st.columns([1, 3])

        with col1:
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
                record_options = ['10038', '11106', '14544', '17242', '52651']
                selected_ptb = st.selectbox("Seleccionar registro PTB-XL", record_options)
                if st.button("Cargar PTB-XL"):
                    try:
                        signal, loaded_fs, metadata = load_ptbxl_record(selected_ptb)
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

            elif data_source == "Hardware en vivo":
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
                        except Exception as e:
                            display_error_message(e, 'Conexión ESP32')

    # Educativa
    with tabs[1]:
        st.header("Vista Educativa")
        st.write("Lecciones interactivas: descomposición de la señal, identificación de ondas P/QRS/T y quizzes.")
        if st.button("Mostrar lección interactiva: ondas ECG"):
            demo = generate_demo_ecg_signal(fs=250, duration=10)
            plot_signal_matplotlib(demo, 250, title="ECG: Ejemplo de ondas P-QRS-T")
        with st.expander("Quiz rápido: Identifica arritmias"):
            st.write("Pregunta: ¿Cuál de las siguientes trazas muestra fibrilación auricular?")
            st.radio("Opciones", ["A", "B", "C"]) 

    # Investigación
    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Exporta segmentos, notebooks reproducibles y define cohortes para análisis estadístico.")
        if st.button("Exportar segmento actual (CSV)"):
            # prefer loaded signal, then twin
            sig = st.session_state.get('_bsp_loaded_signal') or st.session_state.get('twin_signal')
            sig_fs = st.session_state.get('_bsp_loaded_fs') or 250
            if sig is None:
                st.warning("No hay señal cargada para exportar. Carga un caso clínico o archivo primero.")
            else:
                try:
                    csv_path = _save_signal_csv(sig, sig_fs, prefix='ecg_segment')
                    metadata = {
                        'timestamp': int(__import__('time').time()),
                        'module': 'ECG Monitor',
                        'source': st.session_state.get('_bsp_source', 'unknown'),
                        'fs': sig_fs,
                    }
                    nb_path = _create_reproducible_notebook(csv_path, metadata)
                    st.success(f"CSV exportado: {csv_path}")
                    st.success(f"Notebook reproducible creado: {nb_path}")
                except Exception as e:
                    display_error_message(e, "Exportar segmento")

        if st.button("Crear notebook reproducible desde señal cargada"):
            sig = st.session_state.get('_bsp_loaded_signal') or st.session_state.get('twin_signal')
            sig_fs = st.session_state.get('_bsp_loaded_fs') or 250
            if sig is None:
                st.warning("No hay señal cargada para construir el notebook.")
            else:
                try:
                    csv_path = _save_signal_csv(sig, sig_fs, prefix='ecg_for_notebook')
                    metadata = {
                        'timestamp': int(__import__('time').time()),
                        'module': 'ECG Monitor',
                        'source': st.session_state.get('_bsp_source', 'unknown'),
                        'fs': sig_fs,
                    }
                    nb_path = _create_reproducible_notebook(csv_path, metadata)
                    st.success(f"Notebook reproducible creado: {nb_path}")
                except Exception as e:
                    display_error_message(e, "Crear notebook")
        st.markdown("- Notebooks reproducibles: Guardan provenance y CSV asociado.")

    # IA
    with tabs[3]:
        st.header("Vista IA")
        st.write("Interpretabilidad del modelo, contribuciones de features y contra-factuales.")
        if st.button("Explicar última predicción AI"):
            st.info("Mostrando explicación (prototipo)")

    # Simulación
    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Ajusta parámetros fisiológicos y observa el efecto en la señal ECG.")
        hr_multiplier = st.slider("Multiplicador de frecuencia cardíaca", 0.5, 2.0, 1.0)
        base_hr = st.slider("FC base (bpm)", 40, 150, 72)
        ectopy = st.slider("Tasa de ectopias (por minuto)", 0, 30, 0)
        if st.button("Generar ECG simulado con parámetros"):
            adjusted_hr = base_hr * hr_multiplier
            sim = generate_demo_ecg_signal(fs=250, duration=15, hr=adjusted_hr)
            render_ecg_analysis(sim, 250, title=f"ECG simulado (FC={adjusted_hr:.0f} bpm)")

    # Gemelo Digital
    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Crea un gemelo a partir de datos cargados y prueba intervenciones en un entorno reproducible.")
        if st.button("Crear gemelo desde señal cargada"):
            if st.session_state.get('_bsp_loaded_signal') is not None:
                st.session_state['twin_signal'] = st.session_state['_bsp_loaded_signal']
                st.success("Gemelo creado (señal histórica clonada).")
            else:
                st.warning("Carga primero un caso clínico o archivo para crear el gemelo.")
        if st.session_state.get('twin_signal') is not None:
            if st.button("Aplicar intervención: aumentar frecuencia 20%"):
                twin = st.session_state['twin_signal']
                modified = twin * 1.0  # placeholder — en prototipo no alteramos forma, solo re-render
                render_ecg_analysis(modified, 250, title="Gemelo: intervención aumento freq 20%")


def run():
    """Wrapper entrypoint compatible with importing as `run` from supermodules."""
    try:
        main()
    except Exception as e:
        st.exception(f"Fallo al cargar la página ECG Monitor: {e}")


if __name__ == "__main__":
    run()
