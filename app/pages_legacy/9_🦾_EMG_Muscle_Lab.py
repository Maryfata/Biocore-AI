import io
import os
import sys
import streamlit as st
import numpy as np
import plotly.graph_objects as go

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from hardware.sensor_manager import SensorManager
except ImportError:
    SensorManager = None

try:
    from hardware.emg_stream import EMGStreamer
except ImportError:
    EMGStreamer = None

try:
    from app.supermodules import render_sidebar_navigation
except ImportError:
    import importlib.util
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    utils_path = os.path.join(PROJECT_ROOT, 'app', 'utils.py')
    spec = importlib.util.spec_from_file_location('app_utils', utils_path)
    app_utils = importlib.util.module_from_spec(spec)
    sys.modules['app_utils'] = app_utils
    spec.loader.exec_module(app_utils)
    render_sidebar_navigation = app_utils.render_sidebar_navigation


def load_emg_csv(uploaded_file):
    raw = uploaded_file.getvalue().decode('utf-8', errors='replace')
    text = io.StringIO(raw)
    try:
        data = np.genfromtxt(text, delimiter=',', names=True, dtype=float, invalid_raise=False)
    except ValueError:
        text.seek(0)
        data = np.genfromtxt(text, delimiter=',', dtype=float)

    if data is None:
        return np.array([]), np.array([])

    if hasattr(data, 'dtype') and data.dtype.names is not None:
        time_keys = [name for name in data.dtype.names if name.lower() in ('time', 't', 'timestamp', 'ts')]
        if time_keys:
            time = np.asarray(data[time_keys[0]], dtype=float)
        else:
            first = data.dtype.names[0]
            time = np.arange(len(data[first]), dtype=float)
        channel_keys = [name for name in data.dtype.names if name.lower() not in ('time', 't', 'timestamp', 'ts')]
        if not channel_keys:
            return time, np.array([])
        return time, np.asarray(data[channel_keys[0]], dtype=float)

    if isinstance(data, np.ndarray):
        if data.ndim == 1:
            return np.arange(data.shape[0], dtype=float), data
        return np.arange(data.shape[0], dtype=float), data[:, 0]

    return np.array([]), np.array([])


def create_emg_demo_signal(duration=5.0, fs=1000):
    time = np.linspace(0, duration, int(duration * fs), endpoint=False)
    signal = (np.sin(2 * np.pi * 12.0 * time) * np.exp(-time * 0.3) +
              0.3 * np.random.randn(len(time)))
    return time, signal


def smooth_signal(signal, window=5):
    if window <= 1 or len(signal) == 0:
        return signal
    kernel = np.ones(window) / float(window)
    return np.convolve(signal, kernel, mode='same')


def render_emg_summary(signal):
    if len(signal) == 0:
        st.warning('No hay datos EMG disponibles para análisis.')
        return
    rms = np.sqrt(np.mean(np.square(signal)))
    peak = float(np.max(np.abs(signal)))
    threshold = np.percentile(np.abs(signal), 90) if len(signal) else 0.0
    spikes = int(np.sum(np.abs(signal) >= threshold))
    col1, col2, col3 = st.columns(3)
    col1.metric('RMS', f'{rms:.3f}')
    col2.metric('Amplitud pico', f'{peak:.3f}')
    col3.metric('Picos altos', spikes)

st.set_page_config(page_title="EMG Muscle Lab", page_icon="🦾", layout="wide")
render_sidebar_navigation()

st.markdown(
    """
    <h1 id="emg-muscle-lab" style="color: #1f77b4;">🦾 EMG Muscle Lab</h1>
    <p>Laboratorio básico de electromiografía para principiantes. Aprende cómo conectar hardware EMG, entender la señal y explorar datos en vivo o en demo.</p>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    ### Contenidos rápidos
    - [Introducción al EMG](#introduccion-al-emg)
    - [Conectar hardware EMG paso a paso](#conectar-hardware-emg)
    - [Formato CSV para EMG](#formato-csv-para-emg)
    - [Interpretación básica](#interpretacion-basica)
    - [Modo demo y pruebas](#modo-demo)
    """
)

st.markdown('<a id="introduccion-al-emg"></a>', unsafe_allow_html=True)
st.markdown("### Introducción al EMG")
st.markdown(
    "La electromiografía (EMG) mide la actividad eléctrica de los músculos. Este laboratorio está diseñado para que un principiante entienda cómo capturar señales de contracción muscular y qué observar en la forma de onda."
)

st.markdown('<a id="conectar-hardware-emg"></a>', unsafe_allow_html=True)
st.markdown("### Conectar hardware EMG paso a paso")
st.markdown(
    "1. Coloca los electrodos en el músculo objetivo, típicamente dos electrodos de detección y un electrodo de referencia cerca del tendón.\n"
    "2. Conecta los electrodos al amplificador EMG o al módulo de adquisición (por ejemplo, un sensor basado en ESP32 o Arduino).\n"
    "3. Asegura una buena conexión de piel y evita artefactos de movimiento.\n"
    "4. Conecta el módulo al computador mediante USB o Wi-Fi.\n"
    "5. Selecciona la señal EMG en la aplicación y pulsa iniciar para ver la forma de onda en vivo."
)

with st.expander("🔧 Pasos exactos para principiantes"):
    st.write("- Asegúrate de que la piel esté limpia y seca.")
    st.write("- Coloca el electrodo de referencia en un punto óseo estable.")
    st.write("- Usa cableado corto y sin tensión para reducir ruido.")
    st.write("- Si no tienes hardware, usa un archivo CSV de ejemplo o el modo demo.")

st.markdown('<a id="formato-csv-para-emg"></a>', unsafe_allow_html=True)
st.markdown("### Formato CSV para EMG")
st.markdown(
    "La aplicación acepta CSV con una columna de tiempo y una o varias columnas de canales EMG.\n"
    "Ejemplo de encabezado: `time,EMG1,EMG2`.\n"
    "Cada fila debe contener un instante y el valor de la señal en ese instante."
)

signal_source = st.sidebar.radio(
    "Origen de datos EMG",
    ["Demo EMG", "Hardware EMG en vivo", "Cargar CSV EMG"],
    index=0,
)

live_mode = st.sidebar.checkbox(
    "Habilitar análisis en tiempo real",
    value=False,
    help="Actualiza la visualización EMG cuando hay datos de hardware en vivo."
)
apply_smoothing = st.sidebar.checkbox(
    "Aplicar suavizado de visualización",
    value=True,
    help="Reduce el ruido en la vista gráfica para resaltar mejor los picos musculares."
)
smoothing_window = st.sidebar.slider(
    "Ancho de ventana de suavizado",
    min_value=1,
    max_value=21,
    value=5,
    step=2,
)

uploaded_file = None
emg_streamer = st.session_state.get('emg_streamer')

if signal_source == "Cargar CSV EMG":
    uploaded_file = st.file_uploader("Cargar archivo CSV de EMG", type=["csv"])
    if uploaded_file is not None:
        st.success(f"Archivo cargado: {uploaded_file.name}")
        st.info("Archivo CSV listo para procesar. Usa el control de visualización para revisar la señal.")

if signal_source == "Hardware EMG en vivo":
    st.sidebar.markdown("### Configuración de hardware EMG")
    if SensorManager is not None:
        manager = SensorManager()
        port_options = manager.available_ports or ["Auto"]
        selected_port = st.sidebar.selectbox("Puerto EMG", port_options)
        st.sidebar.markdown("**Puertos detectados:**")
        st.sidebar.write(manager.describe_ports())
    else:
        selected_port = st.sidebar.text_input(
            "Puerto EMG manual",
            value=st.session_state.get('emg_port', ''),
            help="Escribe el puerto COM o /dev/ttyUSB0 si no hay detección automática.",
        )
        st.sidebar.warning("No se pudo enumerar puertos seriales; ingresa el puerto manualmente o usa el modo demo.")

    emg_baud = st.sidebar.number_input(
        "Baudios EMG",
        min_value=9600,
        value=st.session_state.get('emg_baud', 115200),
        step=1,
    )
    connect_emg = st.sidebar.button("Conectar EMG", key="connect_emg")
    disconnect_emg = st.sidebar.button("Desconectar EMG", key="disconnect_emg")

    if connect_emg:
        st.session_state['emg_port'] = selected_port
        st.session_state['emg_baud'] = emg_baud
        if EMGStreamer is None:
            st.sidebar.error("EMGStreamer no está disponible. Instala pyserial y revisa hardware/emg_stream.py")
        else:
            chosen_port = selected_port if selected_port not in (None, "Auto", "No hay puertos detectados") else None
            try:
                emg_streamer = EMGStreamer(port=chosen_port, baud=emg_baud, fs=1000)
                if emg_streamer.connect(force_port=chosen_port):
                    emg_streamer.start()
                    st.session_state['emg_streamer'] = emg_streamer
                    st.sidebar.success("EMG hardware conectado y transmitiendo.")
                else:
                    st.sidebar.warning("No se pudo conectar el hardware EMG. Usa modo demo o revisa el puerto.")
            except Exception as exc:
                st.sidebar.error(f"Error al conectar EMG: {exc}")
                emg_streamer = None

    if disconnect_emg and 'emg_streamer' in st.session_state:
        try:
            st.session_state['emg_streamer'].stop()
            st.session_state['emg_streamer'].disconnect()
        except Exception:
            pass
        del st.session_state['emg_streamer']
        emg_streamer = None
        st.sidebar.success("EMG hardware desconectado.")

    if emg_streamer is not None:
        st.sidebar.info(f"Estado EMG: {emg_streamer.get_status()}")
        if hasattr(emg_streamer, 'last_error') and emg_streamer.last_error:
            st.sidebar.warning(f"Último error EMG: {emg_streamer.last_error}")
        if live_mode:
            st.sidebar.success("✅ Análisis EMG en vivo habilitado.")

st.markdown("---")
st.markdown("### Visualización y análisis de EMG")

emg_time = np.array([])
emg_signal = np.array([])
source_description = "Demo EMG"

if signal_source == "Cargar CSV EMG":
    if uploaded_file is not None:
        emg_time, emg_signal = load_emg_csv(uploaded_file)
        source_description = f"CSV EMG ({uploaded_file.name})"
    else:
        st.warning("Sube un archivo CSV para visualizar datos reales de EMG.")
elif signal_source == "Hardware EMG en vivo":
    if emg_streamer is not None and emg_streamer.is_connected():
        emg_time, emg_signal = emg_streamer.get_filtered_buffer()
        source_description = f"Hardware EMG ({emg_streamer.port or 'auto'})"
        if len(emg_signal) < 16 or np.allclose(emg_signal, 0.0):
            st.warning("Aún no hay suficientes datos de hardware EMG. Se cargará una señal de demostración mientras llega el buffer.")
            emg_time, emg_signal = create_emg_demo_signal()
            source_description += " (fallback demo)"
    else:
        st.warning("No hay hardware EMG conectado. Puedes conectar un dispositivo en el panel lateral o usar el modo demo.")
        emg_time, emg_signal = create_emg_demo_signal()
        source_description += " (demo)"
else:
    emg_time, emg_signal = create_emg_demo_signal()
    source_description = "Demo EMG"

st.markdown(f"**Fuente:** {source_description}")
if len(emg_signal) > 0:
    display_signal = smooth_signal(emg_signal, smoothing_window) if apply_smoothing else emg_signal
    fig = go.Figure(go.Scatter(x=emg_time, y=display_signal, mode='lines', line=dict(color='#1f77b4')))
    fig.update_layout(
        title='Señal EMG',
        xaxis_title='Tiempo (s)',
        yaxis_title='Amplitud',
        height=420,
        template='plotly_white',
        plot_bgcolor='#f8fafc',
        paper_bgcolor='#f8fafc',
    )
    fig.update_xaxes(showgrid=True, gridcolor='#cbd5e1', zeroline=True, zerolinecolor='#94a3b8')
    fig.update_yaxes(showgrid=True, gridcolor='#cbd5e1', zeroline=True, zerolinecolor='#94a3b8')
    st.plotly_chart(fig, use_container_width=True)

    render_emg_summary(emg_signal)

    mean_activity = np.mean(np.abs(emg_signal))
    activation = 'Alta' if mean_activity > 0.35 else 'Moderada' if mean_activity > 0.18 else 'Baja'
    st.markdown(f"### 🧠 Actividad muscular estimada: {activation}")
    if activation == 'Alta':
        st.write("La señal muestra contracciones fuertes y un nivel de actividad muscular relevante.")
    elif activation == 'Moderada':
        st.write("Hay buena presencia de actividad muscular, con picos definidos y energía moderada.")
    else:
        st.write("La actividad es baja; podría indicar relajación muscular o baja captación de la señal.")
else:
    st.warning("No hay datos EMG disponibles para mostrar.")

st.markdown('<a id="interpretacion-basica"></a>', unsafe_allow_html=True)
st.markdown("### Interpretación básica")
st.markdown(
    "- Una señal EMG normal muestra picos cuando el músculo se contrae.\n"
    "- El ruido de baja frecuencia puede deberse a movimientos o mala conexión.\n"
    "- Una señal débil y plana suele indicar poca actividad muscular.\n"
    "- El patrón de picos y su frecuencia ayudan a distinguir contracciones voluntarias de contracciones espasmódicas."
)

st.markdown('<a id="modo-demo"></a>', unsafe_allow_html=True)
st.markdown("### Modo demo y pruebas")
st.info(
    "Si aún no tienes hardware EMG, utiliza el modo demo o carga un archivo CSV de ejemplo. "
    "Esto te permite practicar antes de conectar los electrodos reales."
)

if st.button("Ver señal EMG de ejemplo"):
    time = np.linspace(0, 2, 500)
    example_signal = np.sin(2 * np.pi * 10 * time) * np.exp(-time * 0.5)
    st.line_chart(example_signal)
    st.write("Ejemplo de forma de onda EMG generada para demostración.")
