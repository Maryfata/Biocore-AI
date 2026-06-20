import os
import sys
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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

st.set_page_config(page_title="Guides", page_icon="📚", layout="wide")
render_sidebar_navigation()

st.markdown(
    """
    <h1 id="guides" style="color: #1f77b4;">📚 Guías de uso</h1>
    <p>Esta página muestra instrucciones paso a paso para principiantes, incluyendo hardware, formatos de datos y cómo interpretar señales biomédicas en la plataforma.</p>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    ### Secciones rápidas
    - [¿Qué hace esta guía?](#que-hace-esta-guia)
    - [Hardware para principiantes](#hardware-para-principiantes)
    - [Conectar sensores a la plataforma](#conectar-sensores-a-la-plataforma)
    - [Interpretación básica de señales](#interpretacion-basica-de-senales)
    - [Panel Multisensor y EMG](#panel-multisensor-y-emg)
    """
)

st.markdown('<a id="que-hace-esta-guia"></a>', unsafe_allow_html=True)
st.markdown("### ¿Qué hace esta guía?")
st.write(
    "Esta guía está diseñada para usuarios que empiezan en señales biomédicas. Explica qué son los datos, cómo conectar hardware común y qué observar en ECG, EEG, respiración, SpO2 y EMG."
)

st.markdown('<a id="hardware-para-principiantes"></a>', unsafe_allow_html=True)
st.markdown("### Hardware para principiantes")
st.markdown(
    "1. Usa un conjunto de sensores básicos: ECG, PPG/SpO2, respiración y EMG.\n"
    "2. Para ECG, un cable con electrodos adhesivos es suficiente para una señal de referencia.\n"
    "3. Para EMG, coloca los electrodos sobre el músculo y un electrodo de referencia en un punto óseo.\n"
    "4. Un microcontrolador común como ESP32 puede transmitir datos a la aplicación por USB o Wi-Fi.\n"
)

with st.expander("Ver detalles de hardware"):
    st.write("- ECG: electrodos de superficie y amplificador de señal.\n- PPG: sensor óptico en dedo.\n- SpO2: sensor combinado con luz roja e infrarroja.\n- EMG: dos electrodos de detección y uno de referencia.\n- Respiración: banda torácica o flujo de aire.\n")

st.markdown('<a id="conectar-sensores-a-la-plataforma"></a>', unsafe_allow_html=True)
st.markdown("### Conectar sensores a la plataforma")
st.write(
    "Primero asegúrate de que el dispositivo esté encendido y que el software detecte el puerto de comunicación. "
    "Luego elige el tipo de señal en la aplicación y carga los datos en vivo o desde el archivo."
)

st.markdown("- Conecta el sensor al equipo.\n- Selecciona la entrada correcta en la app.\n- Verifica la calidad de la señal antes de comenzar la interpretación.\n")

st.markdown('<a id="interpretacion-basica-de-senales"></a>', unsafe_allow_html=True)
st.markdown("### Interpretación básica de señales")
st.markdown(
    "- ECG: busca ritmo regular, picos R y posibles arritmias.\n"
    "- PPG: observa la forma de pulso y la frecuencia cardiaca.\n"
    "- SpO2: valores por encima de 95% son normales en reposo.\n"
    "- Respiración: revisa frecuencia y profundidad, y detecta pausas o respiración superficial.\n"
    "- EMG: identifica picos de contracción muscular y ruido de movimiento.\n"
)

st.markdown('<a id="panel-multisensor-y-emg"></a>', unsafe_allow_html=True)
st.markdown("### Panel Multisensor y EMG")
st.write(
    "Visita la pestaña Multisensor para explorar cómo se correlacionan múltiples señales juntas. "
    "Usa la página EMG Muscle Lab para aprender a conectar y analizar una señal muscular desde cero."
)

st.markdown("- [Abrir Multisensor](http://localhost:8501/Multisensor)\n- [Abrir EMG Muscle Lab](http://localhost:8501/EMG_Muscle_Lab)")

st.markdown("### Consejos rápidos para principiantes")
st.write(
    "Empieza con datos de demo o archivos CSV antes de usar sensores reales. "
    "Comprueba siempre la calidad de la señal y limpia los electrodos si es necesario."
)

st.markdown("### Ejemplo de flujo para nuevos usuarios")
st.markdown(
    "1. Abre el panel Multisensor y activa las señales de ECG, SpO2 y respiración.\n"
    "2. Genera datos sintéticos si no tienes hardware.\n"
    "3. Revisa cada señal y compara su comportamiento en conjunto.\n"
    "4. Usa la página EMG para practicar la adquisición y la interpretación de señales musculares.\n"
)
