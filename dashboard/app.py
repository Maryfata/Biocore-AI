import os
import streamlit as st
import numpy as np

from dashboard.components import (
    compute_hrv_metrics,
    generate_ecg_case,
    get_arrhythmia_types,
    make_ecg_figure,
    render_clinical_panel,
    render_education_panel,
)

st.set_page_config(
    page_title='BioSignal Medical Dashboard',
    page_icon='🫀',
    layout='wide',
    initial_sidebar_state='expanded'
)

STYLE_PATH = os.path.join(os.path.dirname(__file__), 'styles', 'style.css')


def load_css():
    if os.path.exists(STYLE_PATH):
        with open(STYLE_PATH, 'r', encoding='utf-8') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def init_state():
    if 'window_start' not in st.session_state:
        st.session_state.window_start = 0.0
    if 'seed' not in st.session_state:
        st.session_state.seed = 42
    if 'mode' not in st.session_state:
        st.session_state.mode = 'Clinical Dashboard'


def main():
    init_state()
    load_css()

    st.title('BioSignal Medical Dashboard')
    st.markdown('Plataforma profesional de simulación ECG para estudiantes y equipos clínicos.')

    with st.sidebar:
        st.header('Controles Médicos')
        arrhythmia_type = st.selectbox('Tipo de arritmia', get_arrhythmia_types(), index=0)
        heart_rate = st.slider('Frecuencia cardíaca (BPM)', min_value=40, max_value=180, value=75, step=5)
        duration = st.slider('Duración ECG (s)', min_value=6, max_value=30, value=12, step=2)
        noise = st.slider('Nivel de ruido', min_value=0.0, max_value=0.3, value=0.08, step=0.01)
        zoom = st.slider('Zoom (s)', min_value=3, max_value=12, value=6, step=1)
        speed = st.slider('Velocidad ECG', min_value=0.5, max_value=2.0, value=1.0, step=0.1)
        amplitude = st.slider('Amplitud', min_value=0.6, max_value=2.5, value=1.0, step=0.1)
        st.divider()
        st.session_state.mode = st.radio(
            'Modo',
            ['Clinical Dashboard', 'Educational Mode', 'Quiz Mode', 'Comparison Lab', 'ICU Monitor', 'Research Lab']
        )
        if st.button('Reiniciar ECG'):
            st.session_state.window_start = 0.0
            st.session_state.seed += 1
            st.rerun()

    if st.button('Avanzar 1s'):
        st.session_state.window_start += 1.0 * float(speed)

    np.random.seed(st.session_state.seed)
    time, signal = generate_ecg_case(arrhythmia_type, duration, fs=250, noise=noise, heart_rate=heart_rate)
    metrics = compute_hrv_metrics(signal, fs=250)
    metrics['duration'] = duration
    metrics['noise_pct'] = noise * 100

    if st.session_state.window_start >= duration - zoom:
        st.session_state.window_start = max(0.0, duration - zoom)

    if st.session_state.mode == 'Clinical Dashboard':
        with st.expander('Monitor Hospitalario', expanded=True):
            fig = make_ecg_figure(
                time,
                signal,
                fs=250,
                window_start=st.session_state.window_start,
                window_width=zoom,
                amplitude_scale=amplitude,
                title='ECG Scrolling Real-Time'
            )
            st.plotly_chart(fig, use_container_width=True, theme='streamlit')

        col_left, col_right = st.columns([3, 1])
        with col_left:
            st.markdown('## ECG en tiempo real')
            st.write('Visualización de señal ECG con desplazamiento dinámico y anotaciones de picos.')
            st.metric('Posición de ventana', f"{st.session_state.window_start:.1f} s / {duration:.1f} s")
            st.markdown('### Análisis en vivo')
            st.write('- Monitor hospitalario estilo UCI')
            st.write('- Alarmas basadas en frecuencia y balance autonómico')

        with col_right:
            render_clinical_panel(metrics)

        st.markdown('## Interpretación Clínica')
        risk_state = 'Normal'
        if metrics['BPM'] > 110 or metrics['LF_HF'] > 3.5:
            risk_state = 'Alerta alta'
        elif metrics['BPM'] < 50 or metrics['LF_HF'] < 0.5:
            risk_state = 'Revisión necesaria'
        st.info(f'**Estado de riesgo:** {risk_state}')
        render_education_panel(arrhythmia_type, metrics)

    elif st.session_state.mode == 'Educational Mode':
        st.markdown('## Modo Educativo')
        st.write('Crea explicaciones clínicas, consejos y conceptos médicos en tiempo real.')
        render_education_panel(arrhythmia_type, metrics)

    elif st.session_state.mode == 'Quiz Mode':
        st.markdown('## Quiz Mode')
        st.write('Para entrenar con preguntas interactivas abre la página Quiz Mode en la barra lateral de páginas.')
        st.info('Puedes practicar con arritmias, frecuencia, PR, QRS, ST y diagnóstico clínico.')

    elif st.session_state.mode == 'Comparison Lab':
        st.markdown('## Comparison Lab')
        st.write('Visita la página Comparison Lab para comparar ECG normal y patológico de forma simultánea.')

    elif st.session_state.mode == 'ICU Monitor':
        st.markdown('## ICU Monitor')
        st.write('Visita la página ICU Monitor para la experiencia de monitor intensivo con alarmas y múltiples derivaciones.')

    else:
        st.markdown('## Research Lab')
        st.write('Explora los módulos de investigación, exportación de datasets y la plataforma de IA cardiovascular.')


if __name__ == '__main__':
    main()
