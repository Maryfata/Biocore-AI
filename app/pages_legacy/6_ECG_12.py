"""ECG-12 Derivaciones — integra la página 12-leads existente en la pestaña Clínica
y añade vistas para educación, investigación, IA, simulación y gemelo.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__), '6_📋_ECG-12-Derivaciones.py')

def render_views():
    tabs = st.tabs(["Clínica", "Educativa", "Investigación", "IA", "Simulación", "Gemelo Digital"]) 

    with tabs[0]:
        st.header("Vista Clínica — ECG 12 Derivaciones")
        if os.path.exists(MODULE_EMOJI):
            try:
                runpy.run_path(MODULE_EMOJI, run_name='__main__')
            except Exception as e:
                st.error(f"Error ejecutando página ECG-12 original: {e}")
        else:
            st.info("ECG-12: se requiere implementación original para contenido clínico completo.")

    with tabs[1]:
        st.header("Vista Educativa")
        st.write("Lecciones sobre derivaciones, localización de infartos y ejemplos.")

    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Comparación de derivaciones y análisis de segmentos para investigación.")

    with tabs[3]:
        st.header("Vista IA")
        st.write("Modelos de clasificación de 12 derivaciones y explicaciones.")

    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Simula cambio de ubicación de derivaciones y observa efectos.")

    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Gemelo cardiaco con mapeo de derivaciones para pruebas.")
