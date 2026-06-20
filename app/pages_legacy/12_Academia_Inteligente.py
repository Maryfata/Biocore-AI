"""Biomedical Learning Intelligence System — Academia Clínica Mejorada.

Envoltorio interactivo para misiones, pacientes virtuales, gemelos digitales y tutor IA.
"""

import os
import sys
import streamlit as st
import numpy as np
import time
from typing import Dict, List, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from app.supermodules import (
        generate_demo_ecg_signal,
        generate_demo_eeg_signal,
        generate_demo_respiration_signal,
        generate_demo_spo2_signal,
        estimate_ecg_heart_rate,
        estimate_respiration_rate,
    )
except ImportError:
    def generate_demo_ecg_signal(fs=250, duration=30, hr=72): return np.random.randn(int(fs*duration))*0.1
    def generate_demo_eeg_signal(fs=250, duration=30): return np.random.randn(int(fs*duration))*0.05
    def generate_demo_respiration_signal(fs=250, duration=30, rr=16): return np.sin(2*np.pi*np.arange(int(fs*duration))/fs/60*rr)*2
    def generate_demo_spo2_signal(fs=250, duration=30): return np.full(int(duration), 98.0) + np.random.randn(int(duration))*0.5
    def estimate_ecg_heart_rate(sig, fs): return 72.0
    def estimate_respiration_rate(sig, fs): return 16.0

try:
    from app.biomedical_tutor import BiomedicalTutor
    TUTOR_AVAILABLE = True
except ImportError:
    TUTOR_AVAILABLE = False

VIRTUAL_PATIENTS = {
    'Paciente_1_Sano': {
        'name': 'Carlos',
        'age': 35,
        'condition': 'Sano',
        'HR': 72,
        'SpO2': 98,
        'RR': 16,
        'BP': '120/80',
        'description': 'Adulto joven sin antecedentes médicos.'
    },
    'Paciente_2_Hipertenso': {
        'name': 'María',
        'age': 58,
        'condition': 'Hipertensión',
        'HR': 88,
        'SpO2': 96,
        'RR': 18,
        'BP': '150/95',
        'description': 'Mujer con hipertensión no controlada.'
    },
    'Paciente_3_EPOC': {
        'name': 'Juan',
        'age': 72,
        'condition': 'EPOC',
        'HR': 102,
        'SpO2': 88,
        'RR': 24,
        'BP': '130/85',
        'description': 'Anciano con EPOC severa y desaturación.'
    },
    'Paciente_4_Arritmia': {
        'name': 'Pedro',
        'age': 62,
        'condition': 'Fibrilación Auricular',
        'HR': 'Irregular (80-130)',
        'SpO2': 94,
        'RR': 16,
        'BP': '135/82',
        'description': 'Paciente con fibrilación auricular paroxística.'
    }
}

CLINICAL_MISSIONS = [
    {
        'id': 1,
        'title': '🏥 Misión: Diagnóstico de Dolor Torácico',
        'description': 'Paciente llega a urgencias con dolor torácico. Debes interpretar su ECG, evaluar riesgos y tomar decisiones clínicas.',
        'patient': 'Paciente_4_Arritmia',
        'objectives': [
            'Revisar el ECG del paciente',
            'Identificar hallazgos anormales',
            'Evaluar riesgo de infarto',
            'Recomendar pruebas y tratamiento'
        ],
        'difficulty': 'Intermedio',
        'xp': 150
    },
    {
        'id': 2,
        'title': '🧠 Misión: Monitoreo Neurológico',
        'description': 'Paciente post-quirúrgico requiere monitoreo EEG. Identifica patrones anormales y reacciona ante cambios.',
        'patient': 'Paciente_1_Sano',
        'objectives': [
            'Capturar registro EEG limpio',
            'Identificar bandas de frecuencia',
            'Detectar artefactos',
            'Reportar findings'
        ],
        'difficulty': 'Principiante',
        'xp': 100
    },
    {
        'id': 3,
        'title': '💨 Misión: Manejo de Insuficiencia Respiratoria',
        'description': 'Paciente con EPOC en descompensación. Monitorea SpO2, respiration rate y toma decisiones de ventilación.',
        'patient': 'Paciente_3_EPOC',
        'objectives': [
            'Evaluar parámetros respiratorios',
            'Determinar severidad de hipoxemia',
            'Decidir si requiere O2 o ventilación',
            'Monitorear respuesta al tratamiento'
        ],
        'difficulty': 'Avanzado',
        'xp': 200
    }
]

def render_virtual_patient_card(patient_id: str, patient_data: Dict):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 👤 {patient_data['name']}, {patient_data['age']} años")
        st.markdown(f"**Condición:** {patient_data['condition']}")
        st.markdown(f"**Descripción:** {patient_data['description']}")
    
    with col2:
        st.markdown("**Signos Vitales:**")
        st.markdown(f"- **HR:** {patient_data['HR']} bpm")
        st.markdown(f"- **SpO₂:** {patient_data['SpO2']}%")
        st.markdown(f"- **RR:** {patient_data['RR']} resp/min")
        st.markdown(f"- **BP:** {patient_data['BP']}")

def render_mission_card(mission: Dict):
    st.markdown(f"### {mission['title']}")
    st.markdown(f"{mission['description']}")
    st.markdown(f"**Dificultad:** {mission['difficulty']} | **Puntos:** {mission['xp']} XP")
    st.markdown("**Objetivos:**")
    for obj in mission['objectives']:
        st.markdown(f"- {obj}")

def create_digital_twin_for_patient(patient_data: Dict):
    """Crea un gemelo digital interactivo para un paciente."""
    st.markdown("### 🧬 Gemelo Digital del Paciente")
    
    ecg = generate_demo_ecg_signal(250, 10, patient_data.get('HR', 72) if isinstance(patient_data.get('HR'), (int, float)) else 72)
    resp = generate_demo_respiration_signal(250, 10, patient_data.get('RR', 16) if isinstance(patient_data.get('RR'), (int, float)) else 16)
    spo2 = generate_demo_spo2_signal(250, 10)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Frecuencia Cardíaca", f"{patient_data.get('HR', 72)} bpm")
    with col2:
        st.metric("SpO₂", f"{patient_data.get('SpO2', 98)}%")
    with col3:
        st.metric("Respiración", f"{patient_data.get('RR', 16)} resp/min")
    with col4:
        st.metric("Presión", patient_data.get('BP', '120/80'))
    
    st.markdown("**Señales en Tiempo Real:**")
    tab1, tab2, tab3 = st.tabs(["ECG", "Respiración", "SpO₂"])
    
    with tab1:
        st.line_chart(ecg[:1000])
        st.caption("Electrocardiograma — 4 segundos")
    
    with tab2:
        st.line_chart(resp[:1000])
        st.caption("Patrón Respiratorio — 4 segundos")
    
    with tab3:
        st.line_chart(spo2)
        st.caption("Saturación de Oxígeno — 30 segundos")
    
    st.markdown("**Simulación interactiva:**")
    sim_col1, sim_col2 = st.columns(2)
    
    with sim_col1:
        new_hr = st.slider("Ajustar HR (bpm)", 40, 150, int(patient_data.get('HR', 72)) if isinstance(patient_data.get('HR'), (int, float)) else 72)
        new_spo2 = st.slider("Ajustar SpO₂ (%)", 70, 100, patient_data.get('SpO2', 98) if isinstance(patient_data.get('SpO2'), (int, float)) else 98)
    
    with sim_col2:
        new_rr = st.slider("Ajustar RR (resp/min)", 8, 40, patient_data.get('RR', 16) if isinstance(patient_data.get('RR'), (int, float)) else 16)
        intervention = st.selectbox("Intervención simulada", ["Ninguna", "O₂ 40%", "Intubación", "Sedación"])
    
    if st.button("🎯 Aplicar cambios al gemelo"):
        st.success(f"✅ Gemelo actualizado: HR={new_hr}, SpO₂={new_spo2}%, RR={new_rr}, Intervención: {intervention}")
        new_ecg = generate_demo_ecg_signal(250, 10, new_hr)
        new_resp = generate_demo_respiration_signal(250, 10, new_rr)
        st.line_chart(new_ecg[:1000])
        st.caption("ECG actualizado")
