"""AI Analysis — wrapper que integra la página AI original en la pestaña Clínica
y añade las demás vistas requeridas.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__).rsplit('supermodules', 1)[0], 'pages_legacy', '5_🤖_AI_Analysis.py')

def render_views():
    tabs = st.tabs(["Clínica", "Educativa", "Investigación", "IA", "Simulación", "Gemelo Digital"]) 

    with tabs[0]:
        st.header("Vista Clínica — AI Analysis")
        if os.path.exists(MODULE_EMOJI):
            try:
                runpy.run_path(MODULE_EMOJI, run_name='__main__')
            except Exception as e:
                st.error(f"Error ejecutando página AI original: {e}")
        else:
            st.info("Página AI no encontrada; implementación de plantilla disponible.")

    with tabs[1]:
        st.header("Vista Educativa")
        st.write("Material educativo sobre interpretabilidad y limitaciones de modelos.")

    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Benchmarks, datasets y experimentos reproducibles para IA clínica.")

    with tabs[3]:
        st.header("Vista IA — Explicabilidad")
        st.write("Herramientas para explicar predicciones y contra-factuales.")
        if st.button("Generar contra-factual (prototipo)", key="btn_generar_contrafactual"):
            st.info("Contra-factual generado (prototipo)")

    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Prueba de robustez: perturba entradas y observa salida del modelo.")

    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Gemelo alimentado por el modelo para ensayar intervenciones.")


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
        st.exception(f"Fallo al cargar la página 5_AI_Analysis.py: {e}")