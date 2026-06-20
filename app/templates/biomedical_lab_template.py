"""Plantilla reutilizable para un "Biomedical Cognitive Exploration Lab".
Incluye esqueleto de vistas obligatorias y helper para mostrar métricas que responden las 5 preguntas.
Diseñado para integrarse con Streamlit.
"""

from typing import Dict, Any
import streamlit as st


REQUIRED_VIEWS = [
    "Clínica",
    "Educativa",
    "Investigación",
    "IA",
    "Simulación",
    "Gemelo Digital",
]


def render_header(module_name: str, subtitle: str = ""):
    st.markdown(f"<h1 style='color:#1f77b4;'>{module_name}</h1>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<p>{subtitle}</p>", unsafe_allow_html=True)


def render_view_tabs(module_key: str):
    tabs = st.tabs(REQUIRED_VIEWS)
    return {name: tab for name, tab in zip(REQUIRED_VIEWS, tabs)}


def metric_card(metric: Dict[str, Any]):
    """Renderiza una métrica con los campos obligatorios.

    Espera un dict con claves:
    - id, name, value, unit, normal_range, meaning, why_it_matters, what_affects_it,
      relation_to_other_systems, what_if_changes, confidence, evidence_link
    """
    cols = st.columns([2, 5])
    left, right = cols
    with left:
        st.markdown(f"### {metric.get('name', 'Métrica')}")
        val = metric.get('value', '—')
        unit = metric.get('unit', '')
        st.metric(label="Valor", value=f"{val} {unit}")
        nr = metric.get('normal_range')
        if nr:
            st.caption(f"Rango esperado: {nr}")
    with right:
        st.markdown("**¿Qué significa?**")
        st.write(metric.get('meaning', 'No definido.'))
        st.markdown("**¿Por qué importa?**")
        st.write(metric.get('why_it_matters', 'No definido.'))
        st.markdown("**¿Qué la afecta?**")
        st.write(metric.get('what_affects_it', 'No definido.'))
        st.markdown("**Relación con otros sistemas**")
        st.write(metric.get('relation_to_other_systems', 'No definido.'))
        st.markdown("**¿Qué pasaría si cambia?**")
        st.write(metric.get('what_if_changes', 'No definido.'))
        conf = metric.get('confidence')
        if conf is not None:
            st.caption(f"Confianza: {conf}")
        ev = metric.get('evidence_link')
        if ev:
            st.markdown(f"Más info: [{ev}]({ev})")


def empty_view_note(view_name: str):
    st.info(f"Esta vista ({view_name}) está en modo plantilla. Implementa visualizaciones y flujos específicos del módulo aquí.")


def render_module_template(module_name: str, subtitle: str = "", metrics: list[Dict[str, Any]] | None = None):
    render_header(module_name, subtitle)
    tabs = render_view_tabs(module_name)

    # Clínica
    with tabs['Clínica']:
        st.header("Vista Clínica")
        st.write("Acciones clínicas, timeline, alertas explicadas y recomendaciones accionables.")
        st.divider()
        if metrics:
            for m in metrics:
                metric_card(m)
        else:
            empty_view_note('Clínica')

    # Educativa
    with tabs['Educativa']:
        st.header("Vista Educativa")
        st.write("Lecciones interactivas, descomposición y quizzes aplicados al caso real.")
        empty_view_note('Educativa')

    # Investigación
    with tabs['Investigación']:
        st.header("Vista Investigación")
        st.write("Descarga de datos, notebooks reproducibles, cohortes y tests estadísticos.")
        empty_view_note('Investigación')

    # IA
    with tabs['IA']:
        st.header("Vista IA")
        st.write("Modelos explicables, confianza, contra-factuales y auditoría.")
        empty_view_note('IA')

    # Simulación
    with tabs['Simulación']:
        st.header("Vista Simulación")
        st.write("Motor paramétrico para manipular variables fisiológicas y ver efectos en tiempo real.")
        empty_view_note('Simulación')

    # Gemelo Digital
    with tabs['Gemelo Digital']:
        st.header("Vista Gemelo Digital")
        st.write("Instancia paciente-específica sincronizada con datos reales y simulados.")
        empty_view_note('Gemelo Digital')


if __name__ == '__main__':
    # Ejemplo rápido para probar la plantilla localmente con Streamlit
    sample_metric = {
        'id': 'hr_mean',
        'name': 'Frecuencia cardíaca (media)',
        'value': 72,
        'unit': 'bpm',
        'normal_range': '60-100',
        'meaning': 'Promedio de latidos por minuto durante la ventana seleccionada.',
        'why_it_matters': 'Indicador básico de estado cardiovascular; cambios bruscos pueden indicar arritmia o fallo hemodinámico.',
        'what_affects_it': 'Actividad física, estrés, medicamentos, artefactos de medición.',
        'relation_to_other_systems': 'Respiración, sistema autonómico, presión arterial.',
        'what_if_changes': 'Si sube significativamente, aumenta la demanda miocárdica y riesgo de isquemia; si baja mucho, riesgo de hipoperfusión.',
        'confidence': '0.85',
        'evidence_link': 'https://doi.org/example',
    }
    render_module_template('Plantilla Lab', 'Demo de plantilla', metrics=[sample_metric])
