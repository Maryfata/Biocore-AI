"""EEG-Neuro-Lab — integra la página EEG original en la pestaña Clínica
y añade las demás vistas requeridas.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__), '8_🧠_EEG-Neuro-Lab.py')

def render_views():
    tabs = st.tabs(["Clínica", "Educativa", "Investigación", "IA", "Simulación", "Gemelo Digital"]) 

    with tabs[0]:
        st.header("Vista Clínica — EEG Neuro Lab")
        if os.path.exists(MODULE_EMOJI):
            try:
                runpy.run_path(MODULE_EMOJI, run_name='__main__')
            except Exception as e:
                st.error(f"Error ejecutando página EEG original: {e}")
        else:
            st.info("EEG Neuro Lab no encontrado. Implementación de plantilla.")

    with tabs[1]:
        st.header("Vista Educativa")
        st.write("Tutoriales interactivos sobre identificación de ritmos y artefactos EEG.")

    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Análisis de bandas, conectividad y cohortes de pacientes neurológicos.")

    with tabs[3]:
        st.header("Vista IA")
        st.write("Modelos para detección de crisis y herramientas explicables.")

    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Simuladores de actividad cerebral y perturbaciones.")

    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Gemelo neuronal para ensayar intervenciones y estimulación.")
