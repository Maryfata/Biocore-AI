"""EMG Muscle Lab — integra la página EMG existente y añade las 6 vistas.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__), '9_🦾_EMG_Muscle_Lab.py')

def render_views():
    tabs = st.tabs(["Clínica", "Educativa", "Investigación", "IA", "Simulación", "Gemelo Digital"]) 

    with tabs[0]:
        st.header("Vista Clínica — EMG Muscle Lab")
        if os.path.exists(MODULE_EMOJI):
            try:
                runpy.run_path(MODULE_EMOJI, run_name='__main__')
            except Exception as e:
                st.error(f"Error ejecutando página EMG original: {e}")
        else:
            st.info("EMG Muscle Lab no encontrado. Implementación de plantilla.")

    with tabs[1]:
        st.header("Vista Educativa")
        st.write("Ejercicios para identificar potenciales de acción y artefactos.")

    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Análisis de fatiga muscular, patrón de activación y cohortes.")

    with tabs[3]:
        st.header("Vista IA")
        st.write("Modelos de clasificación de actividad muscular y explicadores.")

    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Simulador de contracción y respuesta muscular.")

    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Gemelo muscular para pruebas de rehabilitación.")
