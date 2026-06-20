"""Multisensor — envoltorio que integra la página multisensorial existente
en la pestaña Clínica y añade las vistas educativas, de investigación, IA,
simulación y gemelo digital.
"""

import os
import runpy
import streamlit as st

MODULE_EMOJI = os.path.join(os.path.dirname(__file__).rsplit('supermodules', 1)[0], 'pages_legacy', '2_🔗_Multisensor.py')

def render_additional_views():
    tabs = st.tabs(["Clínica", "Educativa", "Investigación", "IA", "Simulación", "Gemelo Digital"]) 

    # Clínica: ejecutar el script original para conservar lógica y visualizaciones
    with tabs[0]:
        st.header("Vista Clínica — Multisensor")
        if os.path.exists(MODULE_EMOJI):
            try:
                runpy.run_path(MODULE_EMOJI, run_name='__main__')
            except Exception as e:
                st.error(f"Error ejecutando página multisensor original: {e}")
        else:
            st.warning("No se encontró la página multisensor original. Implementación de plantilla disponible.")

    # Educativa
    with tabs[1]:
        st.header("Vista Educativa")
        st.write("Lecciones interactivas sobre integración multisensorial: correlación ECG↔SpO2↔Respiración.")
        if st.button("Mostrar mini-lesson: correlación SpO2 vs respiración", key="btn_lesson_spo2"):
            st.info("Demostración: la desaturación suele acompañarse de cambios en la respiración (prototipo).")

    # Investigación
    with tabs[2]:
        st.header("Vista Investigación")
        st.write("Exporta series, construye cohortes y lanza análisis reproducibles (notebooks).")
        st.markdown("- [Crear notebook reproducible](#) — prototipo")

    # IA
    with tabs[3]:
        st.header("Vista IA")
        st.write("Modelos multisensor, interpretabilidad y evaluación de fairness/robustness.")
        if st.button("Mostrar explicador AI (prototipo)", key="btn_ai_explainer"):
            st.info("Importancia de features: SpO2 (0.45), Resp rate (0.25), ECG HRV (0.30)")

    # Simulación
    with tabs[4]:
        st.header("Vista Simulación")
        st.write("Ajusta parámetros de varios sensores a la vez y observa efectos cruzados.")
        hr_mult = st.slider("Multiplicador HR", 0.5, 2.0, 1.0, key="sim_hr_mult")
        spo2_drop = st.slider("Caída de SpO2 (%) simulada", 0, 20, 0, key="sim_spo2_drop")
        if st.button("Ejecutar simulación multisensor", key="btn_run_sim"):
            st.info(f"Simulación ejecutada: HRx{hr_mult}, SpO2 drop {spo2_drop}% (prototipo)")

    # Gemelo Digital
    with tabs[5]:
        st.header("Vista Gemelo Digital")
        st.write("Crea un gemelo a partir de un registro multisensor y prueba intervenciones.")
        if st.button("Crear gemelo multisensor (prototipo)", key="btn_create_twin"):
            st.success("Gemelo multisensor creado (prototipo)")


def main():
    render_additional_views()


def run():
    """Wrapper entrypoint compatible with importing as `run` from supermodules."""
    return main()


# El control de seguridad principal para que no se ejecute dos veces
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import streamlit as st
        st.exception(f"Fallo al cargar la página 2_Multisensor.py: {e}")