import streamlit as st
from dashboard.components import (
    compute_hrv_metrics,
    generate_ecg_case,
    get_arrhythmia_types,
    make_ecg_figure,
    render_clinical_panel,
    render_education_panel,
)

st.set_page_config(page_title='Overview - BioSignal', layout='wide')

st.title('Dashboard Médico Interactivo')
st.write('Explora simulaciones ECG profesionales, métricas clínicas y contenido educativo.')

arrhythmia = st.selectbox('Tipo de arritmia', get_arrhythmia_types(), index=0)
heart_rate = st.slider('Frecuencia cardiaca', 40, 180, 80, step=5)
duration = st.slider('Duración del ECG', 6, 20, 10, step=2)
noise = st.slider('Ruido del ECG', 0.0, 0.3, 0.08, step=0.01)
zoom = st.slider('Ventana de zoom (s)', 3, 10, 6)
amplitude = st.slider('Escala de amplitud', 0.6, 2.2, 1.0, step=0.1)

st.divider()

if st.button('Generar ECG'): 
    time, signal = generate_ecg_case(arrhythmia, duration, fs=250, noise=noise, heart_rate=heart_rate)
    metrics = compute_hrv_metrics(signal, fs=250)
    col1, col2 = st.columns([3, 1])
    with col1:
        fig = make_ecg_figure(
            time,
            signal,
            fs=250,
            window_start=0.0,
            window_width=zoom,
            amplitude_scale=amplitude,
            title='ECG Simulado'
        )
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        render_clinical_panel(metrics)
        st.markdown('**Modo:** Dashboard clínico de consulta rápida.')

    st.markdown('## Modo Educativo')
    render_education_panel(arrhythmia, metrics)
else:
    st.warning('Pulsa el botón para generar un caso y explorar el dashboard clínico.')
