"""Respiratory-Lab — integra la página respiratoria existente en la vista Clínica
y añade las demás vistas del Biomedical Cognitive Exploration Lab.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__).rsplit('supermodules', 1)[0], 'pages_legacy', '7_💨_Respiratory-Lab.py')

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


def main():
    render_views()


def run():
    """Wrapper entrypoint compatible with importing as `run` from supermodules."""
    return main()


# Seguro de ejecución para evitar doble renderizado
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import streamlit as st
        st.exception(f"Fallo al cargar la página 7_Respiratory_Lab.py: {e}")