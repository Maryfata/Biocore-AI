"""Patients — envuelve la página de pacientes existente en la vista Clínica
y añade las otras vistas obligatorias.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__), '4_👥_Patients.py')

def render_views():
    tabs = st.tabs(["Clínica", "Educativa", "Investigación", "IA", "Simulación", "Gemelo Digital"]) 

    with tabs[0]:
        st.header("Vista Clínica — Pacientes")
        if os.path.exists(MODULE_EMOJI):
            try:
                runpy.run_path(MODULE_EMOJI, run_name='__main__')
            except Exception as e:
                st.error(f"Error ejecutando página de pacientes original: {e}")
        else:
            st.info("Gestión de pacientes disponible en la implementación original.")

    with tabs[1]:
        st.header("Vista Educativa")
        st.write("Casos clínicos guiados y tutoriales centrados en el paciente.")

    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Cohortes, anonimización y export de datos para investigación.")

    with tabs[3]:
        st.header("Vista IA")
        st.write("Auditoría de modelos aplicados a cohorts de pacientes.")

    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Simula la respuesta del paciente a intervenciones.")

    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Gemelos paciente-específicos con datos históricos.")
