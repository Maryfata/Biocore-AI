import streamlit as st
import numpy as np
from dashboard.components import generate_ecg_case, make_ecg_figure

st.set_page_config(page_title='ICU Monitor - BioSignal', layout='wide')

st.title('Simulador de Monitor ICU')
st.write('Monitor cardíaco intensivo con señales ECG, SpO2, PA, FR y alertas en tiempo real.')

duration = st.slider('Duración del ECG (s)', 8, 20, 12, step=2)
noise = st.slider('Ruido', 0.0, 0.2, 0.08, step=0.01)
zoom = st.slider('Ventana', 3, 8, 5)

_, lead1 = generate_ecg_case('ritmo_sinusal_normal', duration, fs=250, noise=noise * 0.08, heart_rate=76)
_, lead2 = generate_ecg_case('taquicardia', duration, fs=250, noise=noise * 0.12, heart_rate=135)
_, lead3 = generate_ecg_case('fibrilacion_auricular', duration, fs=250, noise=noise * 0.14, heart_rate=115)

if st.button('Generar alerta'): 
    st.warning('ALERTA: Ritmo irregular detectado. Evaluar soporte hemodinámico.')

col1, col2 = st.columns(2)
with col1:
    st.metric('SpO2', '94%')
    st.metric('Presión arterial', '128/82 mmHg')
    st.metric('Frecuencia respiratoria', '18 rpm')
    st.metric('Temperatura', '37.1 °C')
    st.metric('Estado', 'Estable / Monitoreo')

with col2:
    st.subheader('Alarmas de soporte')
    st.error('Taquicardia detectada')
    st.info('Temperatura normal')
    st.success('SpO2 dentro del rango aceptable')

st.markdown('### Derivaciones ECG')
lead_cols = st.columns(1)
for label, signal in [('Derivación I', lead1), ('Derivación II', lead2), ('Derivación III', lead3)]:
    st.markdown(f'#### {label}')
    st.plotly_chart(make_ecg_figure(np.linspace(0, duration, len(signal)), signal, fs=250, window_start=0, window_width=zoom, amplitude_scale=1.0, title=label), use_container_width=True)

st.markdown('#### Comentarios ICU')
st.write('- Monitor realista con múltiples derivaciones.')
st.write('- Las alarmas reflejan parámetros clínicos centrales.')
