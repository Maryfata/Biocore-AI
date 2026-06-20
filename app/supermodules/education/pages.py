"""Education — envoltorio que integra la página educativa existente
en la pestaña Clínica y añade las vistas Educativa (extendida), Investigación, IA,
Simulación y Gemelo Digital.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__).rsplit('supermodules', 1)[0], 'pages_legacy', '3_🎓_Education.py')

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
        if st.button("Iniciar módulo: Interpretación de ECG (15 min)", key="btn_start_ecg_module"):
            st.success("Módulo lanzado (prototipo)")

    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Material reproducible y datasets para enseñanza avanzada.")

    with tabs[3]:
        st.header("Vista IA")
        st.write("Demostraciones de modelos y explicadores para docentes.")
        if st.button("Mostrar explicador de modelo educativo", key="btn_show_edu_explainer"):
            st.info("Explicación: características clave mostradas (prototipo)")

    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Laboratorios virtuales y simuladores paramétricos para enseñanza.")

    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Casos clínicos reproducibles como gemelos para prácticas.")


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
        st.exception(f"Fallo al cargar la página 3_Education.py: {e}")