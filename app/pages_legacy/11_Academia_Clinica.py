"""Academia Clinica — integra la página existente en la pestaña Clínica
y añade las otras vistas para formación, investigación, IA y simulación.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__), '11_🏫_Academia_Clinica.py')

def render_views():
    tabs = st.tabs(["Clínica", "Educativa", "Investigación", "IA", "Simulación", "Gemelo Digital"]) 

    with tabs[0]:
        st.header("Vista Clínica — Academia Clinica")
        if os.path.exists(MODULE_EMOJI):
            try:
                runpy.run_path(MODULE_EMOJI, run_name='__main__')
            except Exception as e:
                st.error(f"Error ejecutando página Academia original: {e}")
        else:
            st.info("Academia Clinica no encontrada; añade cursos y programas aquí.")

    with tabs[1]:
        st.header("Vista Educativa")
        st.write("Cursos, módulos y laboratorios clínicos para profesionales.")

    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Programas de investigación aplicada y datasets.")

    with tabs[3]:
        st.header("Vista IA")
        st.write("Materiales para enseñar desarrollo y auditoría de IA clínica.")

    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Laboratorios de simulación y escenarios de práctica.")

    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Programas que usan gemelos digitales para enseñanza.")
