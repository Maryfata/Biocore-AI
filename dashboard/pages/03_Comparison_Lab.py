import streamlit as st
from dashboard.components import (
    compute_hrv_metrics,
    generate_ecg_case,
    get_arrhythmia_types,
    make_ecg_figure,
)

st.set_page_config(page_title='Comparison Lab - BioSignal', layout='wide')

st.title('Comparison Lab')
st.write('Comparación entre ECG normal y patrones patológicos con métricas clínicas.')

baseline_type = st.selectbox('ECG Normal', ['ritmo_sinusal_normal'], index=0)
pathology = st.selectbox('ECG Patológico', [t for t in get_arrhythmia_types() if t != 'ritmo_sinusal_normal'], index=0)

duration = st.slider('Duración (s)', 6, 20, 10, step=2)
noise = st.slider('Ruido', 0.0, 0.25, 0.08, step=0.01)
zoom = st.slider('Zoom (s) comparación', 3, 8, 5)

normal_time, normal_signal = generate_ecg_case(baseline_type, duration, fs=250, noise=noise * 0.2, heart_rate=75)
path_time, path_signal = generate_ecg_case(pathology, duration, fs=250, noise=noise, heart_rate=100)
normal_metrics = compute_hrv_metrics(normal_signal, fs=250)
path_metrics = compute_hrv_metrics(path_signal, fs=250)

col1, col2 = st.columns(2)
with col1:
    st.subheader('ECG Normal')
    st.plotly_chart(make_ecg_figure(normal_time, normal_signal, fs=250, window_start=0, window_width=zoom, amplitude_scale=1.0, title='Normal'), use_container_width=True)
    st.write(normal_metrics)
with col2:
    st.subheader('ECG Patológico')
    st.plotly_chart(make_ecg_figure(path_time, path_signal, fs=250, window_start=0, window_width=zoom, amplitude_scale=1.0, title='Patológico'), use_container_width=True)
    st.write(path_metrics)

st.markdown('## Diferencias clínicas')
st.write('- Compare la frecuencia cardíaca y el balance LF/HF entre los dos casos.')
st.write('- Observa cómo cambian las métricas de variabilidad y los patrones de ECG.')
