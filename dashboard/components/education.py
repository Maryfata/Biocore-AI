import os
import sys
import streamlit as st

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.ecg_education import ECGEducationPlatform


def render_education_panel(case_type: str, metrics: dict):
    platform = ECGEducationPlatform()
    lesson = platform.obtener_leccion(case_type)
    teaching = platform.modo_ensenanza(metrics['BPM'], metrics['SDNN'], metrics['LF_HF'])

    st.markdown('### Modo Educativo')
    st.info(f"**{lesson.titulo}** — {lesson.descripcion}")
    st.markdown(f"**Concepto clave:** {lesson.concepto_clave}")
    st.write(lesson.explicacion_fisiologica)

    st.markdown('#### Hallazgos clínicos')
    for finding in lesson.hallazgos_clinicos:
        st.write(f'- {finding}')

    with st.expander('Ver explicación automatizada'): 
        for line in teaching['explicaciones']:
            st.write(line)
        st.markdown('**Tipo de ritmo sugerido:** ' + teaching['tipo_ritmo'].replace('_', ' ').title())


def render_concepts_panel():
    st.markdown('### Conceptos Médicos')
    st.write('- **Onda P**: despolarización auricular')
    st.write('- **Intervalo PR**: retraso auriculoventricular normal')
    st.write('- **Complejo QRS**: despolarización ventricular rápida')
    st.write('- **Onda T**: repolarización ventricular')
    st.write('- **QTc**: corrección del intervalo QT por frecuencia cardíaca')
