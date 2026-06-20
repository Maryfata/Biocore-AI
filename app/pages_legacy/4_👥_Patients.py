"""Gestión de pacientes y seguimiento histórico con análisis ML."""

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from src.ai.patient_analytics import PatientRiskPredictor, AnomalyDetector
    HAS_ML_ANALYTICS = True
except ImportError:
    HAS_ML_ANALYTICS = False

try:
    from app.supermodules import render_sidebar_navigation
except ImportError:
    import importlib.util
    utils_path = os.path.join(PROJECT_ROOT, 'app', 'utils.py')
    spec = importlib.util.spec_from_file_location('app_utils', utils_path)
    app_utils = importlib.util.module_from_spec(spec)
    sys.modules['app_utils'] = app_utils
    spec.loader.exec_module(app_utils)
    render_sidebar_navigation = app_utils.render_sidebar_navigation

st.set_page_config(page_title="Gestión de pacientes", layout="wide")
render_sidebar_navigation()

st.set_page_config(page_title="Gestión de pacientes", layout="wide")

FIGURES_DIR = Path(__file__).resolve().parents[2] / "figures"


def build_pipeline_report(patient_id: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""Informe clínico para el paciente: {patient_id}
Fecha y hora: {now}

---
RESUMEN DEL PACIENTE
ID del paciente: {patient_id}
Edad: 54
Sexo: Femenino
Raza: Hispano / Latino
Queja principal: Palpitaciones episódicas y leve malestar torácico
Contexto clínico: Seguimiento de rutina por palpitaciones diagnosticadas previamente
Nota clínica: No se reportó dolor torácico agudo ni síncope
---
EJECUCIÓN DEL PIPELINE
1) Adquisición de señal
- Origen: Base de datos MIT-BIH de arritmias
- Registro seleccionado: 100
- Derivación: MLII
- Duración: 10 segundos
- Frecuencia de muestreo: 360 Hz

2) Procesamiento de señal
- Filtro de paso de banda: 0.5-45 Hz
- Eliminación de deriva de línea base: Aplicada
- Filtro notch: Supresión 50/60 Hz

3) Anotación de ECG
- Conteo de picos R: 12
- Frecuencia cardíaca promedio: 72 bpm
- Intervalo PR: 130 ms
- Duración QRS: 92 ms
- QTc: 402 ms
- Segmentos ST: Isoelectricidad

4) Interpretación clínica
- Clasificación del ritmo: Ritmo sinusal normal
- Morfología: Onda P-QRS-T normal
- Cambios isquémicos: No detectados
- Arritmia: No se detectó ectopia ventricular ni fibrilación auricular

5) Recomendaciones
- Continuar con la terapia actual
- Repetir ECG en 6 meses
- Mantener modificaciones de estilo de vida y monitorizar síntomas

---
RESUMEN VISUAL
- Figura 1: Visión general clínica del ECG y señales anotadas
- Figura 2: Morfología de ECG y anotaciones por derivación
- Figura 3: Revisión de frecuencia cardíaca y estabilidad del ritmo

Este informe sigue la misma estructura de la salida del pipeline principal, incluyendo adquisición, procesamiento, anotación, interpretación y recomendaciones.
"""


def load_report_images() -> list[str]:
    image_files = [
        "mitbih_100_clinical.png",
        "mitbih_100_annotated.png",
        "power_spectral_density.png",
    ]
    return [str(FIGURES_DIR / image) for image in image_files if (FIGURES_DIR / image).exists()]

st.markdown(
    """
    <style>
        .patient-header {
            color: #0f172a;
            padding: 22px 18px;
            background: #e0f2fe;
            border-radius: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: #ffffff;
            border-radius: 18px;
            border: 1px solid rgba(15, 23, 42, 0.08);
            padding: 24px;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
            color: #0f172a;
        }
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 999px;
            background: rgba(34, 197, 94, 0.12);
            color: #166534;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='patient-header'>
        <h1>👥 Gestión de pacientes</h1>
        <p>Organiza la atención con búsqueda rápida, historial de ECG, informes dinámicos y análisis listos para telemedicina.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    ### Contenidos rápidos
    - [Qué hace este módulo](#que-hace-este-modulo)
    - [Cómo usar los informes](#como-usar-informes)
    - [Interpretación clínica](#interpretacion-clinica)
    """
)

st.markdown('<a id="que-hace-este-modulo"></a>', unsafe_allow_html=True)
st.markdown("### Qué hace este módulo")
st.write(
    "Este módulo agrupa datos de pacientes, genera informes clínicos estructurados y ayuda a rastrear cambios entre registros de ECG y datos de signos vitales."
)

st.markdown('<a id="como-usar-informes"></a>', unsafe_allow_html=True)
st.markdown("### Cómo usar los informes")
st.write(
    "1. Busca un paciente o crea uno nuevo.\n"
    "2. Visualiza el historial de ECG, los estadísticos clave y las recomendaciones de seguimiento.\n"
    "3. Usa el informe para comparar tendencias y detectar cambios en el estado cardiaco."
)

st.markdown('<a id="interpretacion-clinica"></a>', unsafe_allow_html=True)
st.markdown("### Interpretación clínica")
st.markdown(
    "- Ritmo sinusal normal sugiere estabilidad.\n"
    "- Intervalos PR/QRS prolongados indican retraso de conducción.\n"
    "- Cambios en el segmento ST pueden sugerir isquemia o infarto.\n"
    "- Los pacientes con riesgo alto deben ser monitorizados con más frecuencia."
)

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    patient_id = st.text_input("ID de paciente o nombre", placeholder="Ej.: PACIENTE-001")
with col2:
    if st.button("🔎 Buscar"):
        st.session_state.search_active = True
        st.session_state.new_patient = False
with col3:
    if st.button("➕ Nuevo paciente"):
        st.session_state.new_patient = True
        st.session_state.search_active = False

st.markdown("---")

sample_patients = [
    {'id': 'PACIENTE-001', 'name': 'Ana Torres', 'age': 54, 'status': 'Estable', 'risk': 'Bajo'},
    {'id': 'PACIENTE-002', 'name': 'Carlos Méndez', 'age': 67, 'status': 'Seguimiento', 'risk': 'Moderado'},
    {'id': 'PACIENTE-003', 'name': 'Laura Ríos', 'age': 48, 'status': 'Nuevo', 'risk': 'Bajo'},
    {'id': 'PACIENTE-004', 'name': 'Miguel Rodríguez', 'age': 72, 'status': 'Crítico', 'risk': 'Alto'},
    {'id': 'PACIENTE-005', 'name': 'Sofía García', 'age': 45, 'status': 'Estable', 'risk': 'Bajo'},
    {'id': 'PACIENTE-006', 'name': 'Juan López', 'age': 58, 'status': 'Seguimiento', 'risk': 'Moderado'},
    {'id': 'PACIENTE-007', 'name': 'María Fernández', 'age': 61, 'status': 'Seguimiento', 'risk': 'Alto'},
    {'id': 'PACIENTE-008', 'name': 'Roberto Díaz', 'age': 52, 'status': 'Nuevo', 'risk': 'Bajo'},
    {'id': 'PACIENTE-009', 'name': 'Isabel Morales', 'age': 69, 'status': 'Crítico', 'risk': 'Alto'},
    {'id': 'PACIENTE-010', 'name': 'Pablo Sánchez', 'age': 55, 'status': 'Estable', 'risk': 'Bajo'},
]

if 'new_patient' in st.session_state and st.session_state.new_patient:
    st.markdown("### 📝 Registro de nuevo paciente")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Nombre completo")
        dob = st.date_input("Fecha de nacimiento")
        gender = st.radio("Género", ["Masculino", "Femenino", "Otro"])
    with col2:
        patient_id_new = st.text_input("ID de paciente")
        phone = st.text_input("Teléfono")
        email = st.text_input("Correo electrónico")
    medical_history = st.text_area("Historial médico")
    medications = st.text_area("Medicamentos actuales")
    allergies = st.text_area("Alergias")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Guardar paciente"):
            st.success(f"✅ Paciente {name} registrado con éxito")
            st.session_state.new_patient = False
            st.session_state.search_active = False
    with col2:
        if st.button("❌ Cancelar"):
            st.session_state.new_patient = False
            st.session_state.search_active = False

elif 'search_active' in st.session_state and st.session_state.search_active:
    patient_id_search = patient_id.strip() or 'PACIENTE-001'
    st.markdown(f"### 📋 Registro de paciente: {patient_id_search}")

    sidebar_info, main_info = st.columns([1, 2])
    with sidebar_info:
        st.markdown("#### Resumen del paciente")
        st.markdown(f"**ID:** {patient_id_search}")
        st.markdown("**Edad:** 64")
        st.markdown("**Género:** Femenino")
        st.markdown("**Última visita:** 2026-05-28")
        st.markdown("**Ruta de atención:** Cardiología")
        st.markdown("<span class='status-pill'>Riesgo bajo</span>", unsafe_allow_html=True)

    with main_info:
        tab1, tab2, tab3, tab4 = st.tabs(["Signos vitales", "Historial ECG", "Informes", "Analítica"])

        with tab1:
            st.markdown("#### Signos vitales recientes con análisis ML")
            vitals = pd.DataFrame({
                'Timestamp': pd.date_range(start='2026-05-22', periods=7, freq='D'),
                'HR (bpm)': [72, 71, 73, 70, 74, 72, 73],
                'SpO2 (%)': [97, 98, 97, 98, 98, 97, 98],
                'Temp (°C)': [36.9, 37.0, 36.8, 37.0, 36.9, 36.8, 37.1],
                'BP SYS': [118, 120, 119, 121, 117, 118, 119],
                'BP DIA': [74, 75, 73, 76, 72, 74, 75],
                'Resp (bpm)': [16, 15, 16, 16, 15, 16, 15],
            })
            st.dataframe(vitals, use_container_width=True)
            
            # ML Analysis
            if HAS_ML_ANALYTICS:
                st.markdown("#### 🤖 Análisis de Riesgo ML (Predictor Cardiovascular)")
                predictor = PatientRiskPredictor()
                
                # Get latest vitals
                latest_hr = vitals['HR (bpm)'].iloc[-1]
                latest_sys = vitals['BP SYS'].iloc[-1]
                latest_dia = vitals['BP DIA'].iloc[-1]
                hr_trend = vitals['HR (bpm)'].tolist()
                
                # Calculate risk
                risk_result = predictor.calculate_risk_score(
                    age=64,
                    heart_rate=latest_hr,
                    systolic_bp=latest_sys,
                    diastolic_bp=latest_dia,
                    ecg_pattern='normal',
                    hrv_sdnn=55.0,
                    trend_data=hr_trend
                )
                
                # Display risk
                col_risk1, col_risk2, col_risk3 = st.columns(3)
                with col_risk1:
                    st.markdown(f"**Riesgo Total:** {risk_result['total_risk']}")
                    st.markdown(f"### {risk_result['risk_level']}")
                
                with col_risk2:
                    st.markdown("**Factores contribuyentes:**")
                    for factor, score in risk_result['contributing_factors'].items():
                        st.write(f"- {factor.replace('_', ' ').title()}: {score:.2f}")
                
                with col_risk3:
                    st.markdown("**Recomendaciones:**")
                    for rec in risk_result['recommendations']:
                        st.write(rec)
                
                # Anomaly detection
                st.markdown("#### 🔍 Detección de Anomalías")
                detector = AnomalyDetector()
                hr_anomalies = detector.detect_anomalies(
                    signal=np.array(vitals['HR (bpm)'].tolist()),
                    parameter_name='heart_rate',
                    threshold_std=2.0
                )
                
                if hr_anomalies['anomalies_detected']:
                    st.warning(f"⚠️ {hr_anomalies['severity'].upper()}: {hr_anomalies['percentage_anomalous']}% de mediciones anómalas")
                    st.write(f"Desviación máxima: {hr_anomalies['max_deviation_std']} σ")
                else:
                    st.success("✅ No se detectaron anomalías en HR")

        with tab2:
            st.markdown("#### Registros ECG recientes")
            ecg_history = pd.DataFrame({
                'Fecha': pd.date_range(start='2026-05-21', periods=5, freq='5D'),
                'FC (bpm)': [72, 74, 71, 75, 73],
                'QRS (ms)': [92, 95, 91, 94, 93],
                'QT (ms)': [412, 415, 410, 418, 413],
                'Interpretación': ['Normal', 'Normal', 'Normal', 'NSR', 'Normal']
            })
            st.dataframe(ecg_history, use_container_width=True)

        with tab3:
            st.markdown("#### Informes y documentos")
            reports = pd.DataFrame({
                'Fecha': pd.date_range(start='2026-04-02', periods=4, freq='2W'),
                'Informe': ['ECG de rutina', 'Resumen HRV', 'Riesgo cardíaco', 'Revisión de seguimiento'],
                'Estado': ['Completo', 'Completo', 'Completo', 'Completo']
            })
            st.dataframe(reports, use_container_width=True)
            if st.button("📄 Generar nuevo informe clínico"):
                st.success("✅ Informe generado exitosamente")
                st.markdown(f"**El informe para {patient_id_search} está listo para revisar.**")
                report_text = build_pipeline_report(patient_id_search)
                st.code(report_text, language='text')
                images = load_report_images()
                if images:
                    st.markdown("#### Figuras del informe")
                    from app.utils.ui_helpers import safe_image
                    safe_image(images, width=600)
                else:
                    st.warning("No hay imágenes de informe disponibles en la carpeta figures.")

        with tab4:
            st.markdown("#### Analítica del paciente")
            st.markdown("- FC promedio: 72 bpm\n- Estabilidad SpO2: 97.8%\n- Tendencia PA: Normal\n- Estado clínico: Estable")
            st.metric("Nivel de riesgo", "Bajo", "Listo para seguimiento de rutina")

else:
    st.markdown("### 👇 Acciones rápidas del paciente")
    st.markdown("Usa la búsqueda para abrir un paciente existente o registrar un caso nuevo para telemedicina.")
    st.markdown("#### Pacientes activos")
    patients_df = pd.DataFrame(sample_patients)
    st.dataframe(patients_df, use_container_width=True)

st.markdown("---")
with st.expander("📊 Perspectivas de la población"):
    st.markdown(
        "- Pacientes activos totales: 1.245\n"
        "- Seguimientos de telemedicina: 387 en los últimos 30 días\n"
        "- Pacientes con banderas ECG anormales: 42 (3.4%)\n"
        "- Edad promedio del paciente: 55.3 años\n"
        "- Condición principal: Hipertrofia ventricular izquierda"
    )
