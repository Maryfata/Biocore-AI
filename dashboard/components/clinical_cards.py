import streamlit as st


def render_clinical_panel(metrics: dict):
    st.markdown('### Panel Clínico')
    col1, col2, col3 = st.columns(3)

    col1.metric('BPM', f"{metrics['BPM']:.0f}")
    col1.metric('SDNN', f"{metrics['SDNN']:.4f} s")
    col1.metric('RMSSD', f"{metrics['RMSSD']:.4f} s")

    col2.metric('LF/HF', f"{metrics['LF_HF']:.2f}")
    col2.metric('QT', f"{metrics['QT']:.3f} s")
    col2.metric('QTc', f"{metrics['QTc']:.3f} s")

    rr = metrics.get('RR', [])
    rr_text = f"{len(rr)} intervalos" if len(rr) > 0 else 'Sin datos'
    col3.metric('RR', rr_text)
    col3.metric('Duración', f"{metrics.get('duration', 0):.1f} s")
    col3.metric('Ruido', f"{metrics.get('noise_pct', 0):.0f}%")

    st.markdown('---')
    severity = 'Estable'
    if metrics['BPM'] > 110 or metrics['LF_HF'] > 3.5:
        severity = 'Alerta clínica'
    elif metrics['BPM'] < 50 or metrics['LF_HF'] < 0.5:
        severity = 'Revisión recomendada'

    st.info(f'**Estado clínico:** {severity}')
