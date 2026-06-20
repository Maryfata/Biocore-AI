"""Education — envoltorio que integra la página educativa existente
en la pestaña Clínica y añade las vistas Educativa (extendida), Investigación, IA,
Simulación y Gemelo Digital.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__), '3_🎓_Education.py')

def render_views():
    tabs = st.tabs(["Clínica", "Educativa", "Investigación", "IA", "Simulación", "Gemelo Digital"]) 

    with tabs[0]:
        st.header("Vista Clínica (Contexto Educativo)")
        if os.path.exists(MODULE_EMOJI):
            try:
                runpy.run_path(MODULE_EMOJI, run_name='__main__')
            except Exception as e:
                st.error(f"Error ejecutando página educativa original: {e}")
        else:
            st.info("Plantilla educativa: carga ejercicios y casos clínicos aquí.")

    with tabs[1]:
        st.header("Vista Educativa — Cursos y Lecciones")
        st.write("Módulos interactivos, quizzes, y prácticas sobre análisis de señales.")
        if st.button("Iniciar módulo: Interpretación de ECG (15 min)"):
            st.success("Módulo lanzado (prototipo)")

    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Material reproducible y datasets para enseñanza avanzada.")

    with tabs[3]:
        st.header("Vista IA")
        st.write("Demostraciones de modelos y explicadores para docentes.")
        if st.button("Mostrar explicador de modelo educativo"):
            st.info("Explicación: características clave mostradas (prototipo)")

    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Laboratorios virtuales y simuladores paramétricos para enseñanza.")

    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Casos clínicos reproducibles como gemelos para prácticas.")
