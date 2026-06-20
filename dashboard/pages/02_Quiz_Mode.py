import streamlit as st
from dashboard.components import (
    compute_hrv_metrics,
    generate_ecg_case,
    get_arrhythmia_types,
    render_quiz_metrics,
)

st.set_page_config(page_title='Quiz Mode - BioSignal', layout='wide')

st.title('Quiz Médico de ECG')
st.write('Practica la interpretación clínica con casos aleatorios y feedback educativo.')

arrhythmia = st.selectbox('Tipo de caso', get_arrhythmia_types(), index=0)
heart_rate = st.slider('Frecuencia cardíaca objetivo', 40, 180, 90, step=5)
duration = st.slider('Duración del ECG', 6, 20, 12, step=2)
noise = st.slider('Nivel de ruido', 0.0, 0.3, 0.1, step=0.01)

if st.button('Generar Caso de Quiz'):
    time, signal = generate_ecg_case(arrhythmia, duration, fs=250, noise=noise, heart_rate=heart_rate)
    metrics = compute_hrv_metrics(signal, fs=250)
    st.session_state['quiz_signal'] = (arrhythmia, metrics)
    st.success('Caso generado. Responde el quiz a continuación.')

if 'quiz_signal' in st.session_state:
    case_type, metrics = st.session_state['quiz_signal']
    st.markdown('## Datos del caso')
    st.write(f'- Tipo de arritmia: {case_type.replace("_", " ")}')
    st.write(f'- BPM estimado: {metrics["BPM"]:.0f}')
    st.write(f'- QTc estimado: {metrics["QTc"]:.3f} s')

    render_quiz_metrics(case_type, metrics)
else:
    st.info('Genera un caso para comenzar el quiz médico.')
