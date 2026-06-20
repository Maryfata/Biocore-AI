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
from app.supermodules.specialties.pages import run


run()
                strength_right = st.slider("Fuerza Derecha (%)", 0, 100, 80)
            
            if st.button("✅ Guardar Medición Musculoesquelética"):
                st.session_state.patient_data['latest_measurement']['rom_left'] = rom_left
                st.session_state.patient_data['latest_measurement']['rom_right'] = rom_right
                st.session_state.patient_data['latest_measurement']['strength_left'] = strength_left
                st.session_state.patient_data['latest_measurement']['strength_right'] = strength_right
                st.session_state.patient_data['latest_measurement']['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success("✅ Medición guardada correctamente")

    elif specialty == "Respiratory":
        st.subheader("💨 Medición Respiratoria")
        
        resp_pattern = st.radio("Patrón Respiratorio Simulado",
                                 ["normal", "tachypnea", "bradypnea", "obstructed"],
                                 format_func=lambda x: {
                                     'normal': 'Normal',
                                     'tachypnea': 'Taquipnea',
                                     'bradypnea': 'Bradipnea',
                                     'obstructed': 'Obstruido'
                                 }[x])
        
        if st.button("▶️ Registrar Respiración", key="record_respiratory"):
            with st.spinner("Registrando respiración..."):
                resp_data = generate_respiratory_signal(pattern=resp_pattern)
                st.session_state.patient_data['latest_measurement']['respiratory'] = resp_data
                st.session_state.patient_data['latest_measurement']['respiratory_rate'] = resp_data['respiratory_rate']
                st.session_state.patient_data['latest_measurement']['tidal_volume'] = resp_data['tidal_volume']
                st.session_state.patient_data['latest_measurement']['oxygen_saturation'] = resp_data['oxygen_saturation']
                st.session_state.patient_data['latest_measurement']['ventilation_quality'] = resp_data['ventilation_quality']
                st.session_state.patient_data['latest_measurement']['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success("✅ Respiración registrada correctamente")
        
        if 'respiratory' in st.session_state.patient_data['latest_measurement']:
            fig = RespiratoryUI.display_respiratory_waveform(st.session_state.patient_data['latest_measurement']['respiratory'])
            st.plotly_chart(fig, use_container_width=True)
            RespiratoryUI.display_respiratory_metrics(st.session_state.patient_data['latest_measurement'])

    elif specialty == "Metabolism":
        st.subheader("⚡ Medición Metabólica")
        
        metabolic_condition = st.radio("Condición Metabólica", ["normal", "prediabetes", "diabetes"],
                                        format_func=lambda x: {
                                            'normal': 'Normal',
                                            'prediabetes': 'Prediabetes',
                                            'diabetes': 'Diabetes'
                                        }[x])
        
        if st.button("▶️ Registrar Perfil Metabólico", key="record_metabolic"):
            with st.spinner("Generando perfil metabólico..."):
                metabolic = generate_metabolic_profile(condition=metabolic_condition)
                st.session_state.patient_data['latest_measurement']['metabolic_profile'] = metabolic
                st.session_state.patient_data['latest_measurement']['blood_glucose'] = metabolic['blood_glucose']
                st.session_state.patient_data['latest_measurement']['hba1c'] = metabolic['hba1c']
                st.session_state.patient_data['latest_measurement']['insulin_sensitivity'] = metabolic['insulin_sensitivity']
                st.session_state.patient_data['latest_measurement']['energy_expenditure'] = metabolic['energy_expenditure']
                st.session_state.patient_data['latest_measurement']['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.success("✅ Perfil metabólico guardado correctamente")
        
        if 'metabolic_profile' in st.session_state.patient_data['latest_measurement']:
            MetabolismUI.display_metabolic_profile(st.session_state.patient_data['latest_measurement']['metabolic_profile'])
            fig = MetabolismUI.display_metabolic_risk_chart(st.session_state.patient_data['latest_measurement']['metabolic_profile'])
            st.plotly_chart(fig, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# TAB 2: ANÁLISIS IA (Resultados del análisis automático)
# ═════════════════════════════════════════════════════════════════════════════

with tabs[1]:
    st.header("🔬 Análisis Automático IA")
    
    st.info("""
    El sistema de IA analizó automáticamente los datos y generó:
    • Detección de anomalías
    • Clasificación de patología
    • Predicciones futuras
    • Explicabilidad (SHAP)
    """)
    
    specialty = st.session_state.current_specialty
    measurement = st.session_state.patient_data['latest_measurement']
    
    # Simular resultados IA
    ai_results = {
        'confidence': 0.87,
        'alert_level': 'Normal' if st.session_state.patient_data['condition'] == 'normal' else 'High',
        'recommendation': 'Monitoreo rutinario',
        'risk_30_days': '2.1%',
        'alerts': []
    }
    
    if specialty == "Cardiology":
        ai_results.update({
            'arrhythmia_type': 'Normal' if st.session_state.patient_data['condition'] == 'normal' else 'Fibrilación Auricular',
            'risk_classification': 'Bajo',
            'shap_explanation': 'La FC normal (72 bpm) y presión adecuada reducen riesgo',
            'intervention_needed': 'No',
            'action_items': '• Continuar monitoreo\n• Próximo chequeo en 30 días\n• Mantener actividad física'
        })
        
        # Mostrar gráficas
        col1, col2 = st.columns(2)
        
        with col1:
            if 'ecg' in measurement:
                fig = CardiacUI.display_ecg_waveform(measurement['ecg'])
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = CardiacUI.display_arrhythmia_detection(
                st.session_state.patient_data['condition'],
                ai_results['confidence']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Métricas y presión
        CardiacUI.display_heart_rate_and_bp(st.session_state.patient_data)
        
        st.divider()
        
        # Tendencias
        col1, col2 = st.columns(2)
        with col1:
            fig = CardiacUI.display_hrv_analysis(st.session_state.measurement_history)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = CardiacUI.display_cardiac_risk_assessment()
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Tabla resumen
        st.subheader("📋 Resumen de Hallazgos")
        CardiacUI.display_cardiac_summary(st.session_state.patient_data, ai_results)

    elif specialty == "Neurology":
        eeg_bands = measurement.get('eeg', {}).get('bands', {
            'Delta': 25, 'Theta': 20, 'Alpha': 15, 'Beta': 30, 'Gamma': 10
        })
        
        ai_results.update({
            'sleep_stage': 'N2',
            'seizure_risk': 'Bajo',
            'shap_explanation': 'Patrones Delta/Theta indican sueño N2 normal',
            'patient_instructions': '• Mantener rutina de sueño\n• Evitar cafeína después de 3 PM\n• Ejercicio diario de 30 min'
        })
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'eeg' in measurement:
                fig = NeurologyUI.display_eeg_waveform(measurement['eeg'])
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = NeurologyUI.display_frequency_bands(eeg_bands)
            st.plotly_chart(fig, use_container_width=True)

# truncated for brevity
