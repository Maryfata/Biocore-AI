"""Respiratory-Lab — integra la página respiratoria existente en la vista Clínica
y añade las demás vistas del Biomedical Cognitive Exploration Lab.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__), '7_💨_Respiratory-Lab.py')

def render_views():
    tabs = st.tabs(["Clínica", "Educativa", "Investigación", "IA", "Simulación", "Gemelo Digital"]) 

    with tabs[0]:
        st.header("Vista Clínica — Respiratory Lab")
        if os.path.exists(MODULE_EMOJI):
            try:
                runpy.run_path(MODULE_EMOJI, run_name='__main__')
            except Exception as e:
                st.error(f"Error ejecutando página Respiratory original: {e}")
        else:
            st.info("Respiratory Lab no encontrado. Implementación de plantilla.")

    with tabs[1]:
        st.header("Vista Educativa")
        st.write("Lecciones sobre mecánica ventilatoria y correlación con SpO2.")

    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Analiza series respiratorias, detección de apnea y cohortes.")

    with tabs[3]:
        st.header("Vista IA")
        st.write("Modelos de detección de apnea y explicabilidad.")

    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Simulador respiratorio paramétrico.")

    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Gemelo respiratorio para pruebas de ventilación e intervención.")
