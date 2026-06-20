"""Guides — integra la página de guías existente y añade las vistas del lab.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__), '10_📚_Guides.py')

def render_views():
    tabs = st.tabs(["Clínica", "Educativa", "Investigación", "IA", "Simulación", "Gemelo Digital"]) 

    with tabs[0]:
        st.header("Vista Clínica — Guides")
        if os.path.exists(MODULE_EMOJI):
            try:
                runpy.run_path(MODULE_EMOJI, run_name='__main__')
            except Exception as e:
                st.error(f"Error ejecutando página Guides original: {e}")
        else:
            st.info("Guías no encontradas; añade Markdown o recursos aquí.")

    with tabs[1]:
        st.header("Vista Educativa")
        st.write("Guías paso a paso y material didáctico.")

    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Documentación técnica, papers y referencias.")

    with tabs[3]:
        st.header("Vista IA")
        st.write("Guías para auditar modelos y describir límites.")

    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Guías para usar simuladores y reproducir experimentos.")

    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Guías para creación y validación de gemelos.")
