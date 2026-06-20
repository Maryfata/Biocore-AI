"""
INTERFAZ UNIFICADA STREAMLIT - BIOCORE AI OS v3.0
==================================================

ARCHIVO PRINCIPAL: app/pages/specialties.py

Esta es la INTERFAZ UNIFICADA que integra TODAS las especialidades.
Es el punto de entrada principal para médicos y pacientes.

ESTRUCTURA GENERAL:
═══════════════════

┌─ BARRA LATERAL (Sidebar)
│  ├─ Selección de especialidad
│  ├─ Selección de paciente
│  ├─ Modo de usuario (Doctor/Paciente)
│  └─ Configuración
│
├─ SECCIÓN PRINCIPAL
│  ├─ Encabezado con info del paciente
│  ├─ Tabs por módulo:
│  │  ├─ Tab 1: MEDICIÓN (tomar datos nuevos)
│  │  ├─ Tab 2: ANÁLISIS (resultados IA)
│  │  ├─ Tab 3: DIGITAL TWIN (simulación)
│  │  ├─ Tab 4: ALERTAS (advertencias)
│  │  ├─ Tab 5: REPORTE (PDF/Email)
│  │  └─ Tab 6: EDUCACIÓN (explicaciones)
│  │
│  └─ Sección inferior: Historial de mediciones
│
└─ FOOTER
   └─ Info de versión y soporte

USO:
────
    streamlit run app/pages/specialties.py

REQUISITOS:
───────────
    streamlit
    plotly
    numpy
    scipy
    pandas
"""

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Agregar path para importar módulos personalizados
PROJECT_ROOT = str(Path(__file__).parent.parent.parent.parent)
sys.path.insert(0, PROJECT_ROOT)

# IMPORTACIONES
from app.supermodules import (
    CardiacUI, NeurologyUI, MusculoskeletalUI,
    DigitalTwinsUI, AlertsUI, ReportGenerator,
    RespiratoryUI, MetabolismUI,
    generate_sample_patient, generate_measurement_history,
    generate_ecg_signal, generate_eeg_signal, generate_emg_signal,
    generate_respiratory_signal, generate_metabolic_profile
)

SYSTEMS = [
    'Cardiology',
    'Neurology',
    'Respiratory',
    'Metabolism',
    'Musculoskeletal'
]

SYSTEM_LABELS = {
    'Cardiology': '🫀 Cardiología',
    'Neurology': '🧠 Neurología',
    'Respiratory': '💨 Respiratorio',
    'Metabolism': '⚡ Metabolismo',
    'Musculoskeletal': '💪 Musculoesquelético'
}


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="BIOCORE AI - Plataforma Médica Integrada",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
        /* Encabezado principal */
        .main-header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
        }
        
        /* Tarjetas de métrica */
        .metric-card {
            background: #f0f2f6;
            padding: 15px;
            border-radius: 8px;
            border-left: 5px solid #667eea;
            margin: 10px 0;
        }
        
        /* Alertas */
        .alert-critical {
            background-color: #ffcccc;
            border-left: 5px solid #ff0000;
        }
        
        .alert-high {
            background-color: #ffe0cc;
            border-left: 5px solid #ff6600;
        }
        
        .alert-medium {
            background-color: #ffffcc;
            border-left: 5px solid #ffcc00;
        }
        
        .alert-low {
            background-color: #ccffcc;
            border-left: 5px solid #00cc00;
        }
    </style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# INICIALIZACIÓN DE SESSION STATE
# ═══════════════════════════════════════════════════════════════════════════

if 'patient_data' not in st.session_state:
    st.session_state.patient_data = generate_sample_patient("Cardiology", "normal")

if 'measurement_history' not in st.session_state:
    st.session_state.measurement_history = generate_measurement_history(
        st.session_state.patient_data,
        days=30
    )

if 'current_specialty' not in st.session_state:
    st.session_state.current_specialty = "Cardiology"

if 'user_mode' not in st.session_state:
    st.session_state.user_mode = "Doctor"

# ═══════════════════════════════════════════════════════════════════════════
# BARRA LATERAL (SIDEBAR)
# ═══════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("### BIOCORE AI OS")
    st.write("Sistema de fisiología centrado en el organismo, no en la señal.")
    st.title("⚙️ CONFIGURACIÓN")
    
    st.divider()
    
    # Selección de modo de usuario
    st.session_state.user_mode = st.radio(
        "👤 Modo de Usuario",
        ["Doctor", "Paciente"],
        help="Selecciona cómo deseas ver la información"
    )
    
    st.divider()
    
    # Selección de especialidad
    st.session_state.current_specialty = st.selectbox(
        "🏥 Sistema Fisiológico",
        SYSTEMS,
        help="""
        Selecciona el dominio de fisiología central para el paciente.
        • Cardiología: estado cardíaco y hemodinámica
        • Neurología: actividad cerebral y sueño
        • Respiratorio: ventilación, intercambio gaseoso, SpO2
        • Metabolismo: energía, glucosa y estado bioquímico
        • Musculoesquelético: músculos, fuerza y fatiga
        """,
        format_func=lambda x: SYSTEM_LABELS.get(x, x)
    )
    
    st.divider()
    
    # Selección de paciente (simulado)
    st.write("👥 Pacientes en el Sistema")
    patients = [
        "Juan García (70 años)",
        "María López (55 años)",
        "Carlos Rodríguez (45 años)"
    ]
    selected_patient = st.selectbox("Selecciona paciente", patients)
    
    # Si cambió la especialidad, generar nuevo paciente
    if st.session_state.current_specialty != st.session_state.patient_data.get('specialty'):
        st.session_state.patient_data = generate_sample_patient(
            st.session_state.current_specialty,
            "normal"
        )
        st.session_state.measurement_history = generate_measurement_history(
            st.session_state.patient_data,
            days=30
        )
        st.rerun()
    
    st.divider()
    
    # Panel de información del paciente
    with st.expander("ℹ️ Info del Paciente", expanded=True):
        patient = st.session_state.patient_data
        st.write(f"**Nombre:** {patient['name']}")
        st.write(f"**ID:** {patient['id']}")
        st.write(f"**Edad:** {patient['age']} años")
        st.write(f"**Género:** {'Masculino' if patient['gender'] == 'M' else 'Femenino'}")
        st.write(f"**Especialidad:** {patient['specialty']}")
        
        if patient['medical_history']['hypertension']:
            st.warning("⚠️ Hipertensión")
        if patient['medical_history']['diabetes']:
            st.warning("⚠️ Diabetes")
        if patient['medical_history']['prior_events'] > 0:
            st.warning(f"⚠️ {patient['medical_history']['prior_events']} evento(s) previo(s)")
    
    st.divider()
    
    # Opciones de interfaz
    st.write("⚙️ Opciones")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Nuevo Examen", use_container_width=True):
            st.session_state.patient_data = generate_sample_patient(
                st.session_state.current_specialty,
                "normal"
            )
            st.rerun()
    
    with col2:
        if st.button("📥 Cargar Datos", use_container_width=True):
            st.info("Cargando...")
    
    st.divider()
    
    # Información del sistema
    st.write("📊 Sistema")
    st.caption(f"**BIOCORE AI OS v3.0**")
    st.caption(f"Versión: 3.0.0")
    st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d')}")
    st.caption("ℹ️ Contacto: biocore@hospital.com")

# ═══════════════════════════════════════════════════════════════════════════
# ENCABEZADO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
    <div class="main-header">
        <h1>🏥 BIOCORE AI OS v3.0</h1>
        <h2>Plataforma Médica Integrada de Fisiología Humana</h2>
        <p>Foco en el organismo: cardiología, neurología, respiratorio, metabolismo y musculosquelético.</p>
    </div>
""", unsafe_allow_html=True)

# Información del paciente activo (header)
patient = st.session_state.patient_data
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👤 Paciente", patient['name'].split()[0])

with col2:
    st.metric("📅 Edad", f"{patient['age']} años")

with col3:
    st.metric("🏥 Sistema", SYSTEM_LABELS.get(st.session_state.current_specialty, ''))

with col4:
    st.metric("⏰ Última Medición", 
              datetime.now().strftime("%H:%M"))

st.divider()

# ═══════════════════════════════════════════════════════════════════════════
# TABS PRINCIPALES - INTERFAZ MODULAR
# ═══════════════════════════════════════════════════════════════════════════

tabs = st.tabs([
    "📊 MEDICIÓN",
    "🔬 ANÁLISIS IA",
    "🧬 DIGITAL TWIN",
    "🚨 ALERTAS",
    "📄 REPORTE",
    "📚 EDUCACIÓN"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1: MEDICIÓN (Capturar datos nuevos)
# ═════════════════════════════════════════════════════════════════════════════

with tabs[0]:
    st.header("📊 Captura de Nuevas Mediciones")
    
    st.info("""
    **Instrucciones de Medición:**
    
    Para obtener resultados precisos:
    1. El paciente debe estar en reposo de 5 minutos
    2. Usar equipamiento calibrado
    3. Seguir los pasos indicados abajo
    4. El sistema analizará automáticamente los datos
    """)
    
    specialty = st.session_state.current_specialty
    
    if specialty == "Cardiology":
        st.subheader("🫀 Medición Cardíaca")
        st.info("Página de medición cardíaca — implementar captura")
    elif specialty == "Neurology":
        st.subheader("🧠 Medición Neurológica")
        st.info("Página de medición neurológica — implementar captura")
    elif specialty == "Musculoskeletal":
        st.subheader("💪 Medición Musculoesquelética")
        st.info("Página de medición musculoesquelética — implementar captura")
    elif specialty == "Respiratory":
        st.subheader("💨 Medición Respiratoria")
        st.info("Página de medición respiratoria — implementar captura")
    elif specialty == "Metabolism":
        st.subheader("⚡ Medición Metabólica")
        st.info("Página de medición metabólica — implementar captura")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2: ANÁLISIS IA (Resultados del análisis automático)
# ═════════════════════════════════════════════════════════════════════════════

with tabs[1]:
    st.header("🔬 Análisis Automático IA")
    st.info("Resultados del análisis IA — implementar visualizaciones")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3: DIGITAL TWIN (Simulación y escenarios)
# ═════════════════════════════════════════════════════════════════════════════

with tabs[2]:
    st.header("🧬 Digital Twin - Simulación Interactiva")
    st.info("Digital Twin visualizations — implementar simulaciones")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 4: ALERTAS (Sistema de alertas)
# ═════════════════════════════════════════════════════════════════════════════

with tabs[3]:
    st.header("🚨 Sistema de Alertas")
    st.info("Sistema de alertas — implementar visualización")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 5: REPORTE (Generación de reportes)
# ═════════════════════════════════════════════════════════════════════════════

with tabs[4]:
    st.header("📄 Generación de Reportes")
    st.info("Generación de reportes — implementar export")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 6: EDUCACIÓN (Explicaciones para el paciente)
# ═════════════════════════════════════════════════════════════════════════════

with tabs[5]:
    st.header("📚 Centro Educativo")
    st.info("Centro educativo — implementar contenido educativo")

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN INFERIOR: HISTORIAL DE MEDICIONES
# ═════════════════════════════════════════════════════════════════════════════

st.divider()

st.header("📊 Historial de Mediciones (Últimos 30 días)")

# Crear tabla del historial
history_df = pd.DataFrame(st.session_state.measurement_history) if st.session_state.measurement_history else pd.DataFrame()

# Mostrar tabla interactiva
if not history_df.empty:
    st.dataframe(
        history_df.tail(10),
        use_container_width=True,
        height=300
    )
else:
    st.info("Sin datos de historial disponibles")

# ═════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═════════════════════════════════════════════════════════════════════════════

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📞 Soporte Técnico**")
    st.caption("biocore-support@hospital.com")
    st.caption("+1-555-BIOCORE-1")

with col2:
    st.markdown("**📋 Documentación**")
    st.caption("[Guía de Usuario](https://docs.biocore.com/user-guide)")
    st.caption("[FAQ](https://docs.biocore.com/faq)")

with col3:
    st.markdown("**ℹ️ Sistema**")
    st.caption("v3.0.0 • 2026")
    st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    <p>BIOCORE AI OS v3.0 • Plataforma Médica Integrada<br>
    © 2026 • Este sistema es para propósitos educativos y de demostración.<br>
    Para uso clínico real, requiere certificación y validación médica.</p>
</div>
""", unsafe_allow_html=True)


def run():
    """No-op wrapper for API symmetry; this module renders on import."""
    return None
