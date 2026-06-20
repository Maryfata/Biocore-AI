"""
COMPONENTES PARA DIGITAL TWINS Y VISUALIZACIÓN
===============================================
Simulación en tiempo real de órganos y predicciones.

ESTRUCTURA:
-----------
    1. Digital Twin Cardíaco - Simulación de corazón
    2. Digital Twin Neurológico - Actividad cerebral
    3. Digital Twin Musculoesquelético - Contracción muscular
    4. Escenarios "¿Qué pasa si?" interactivos

USO:
-----
    from app.components.digital_twins_ui import DigitalTwinsUI
    
    dt = DigitalTwinsUI()
    dt.display_cardiac_simulation(patient_data)
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np


class DigitalTwinsUI:
    """Visualización de simulaciones digitales de órganos."""
    
    @staticmethod
    def display_cardiac_simulation(heart_rate, arrhythmia=False):
        """
        SIMULACIÓN #1: Corazón latiendo en tiempo real.
        
        INSTRUCCIONES:
        ---------------
        "Animación del corazón simulado.
         • Rojo = Sístole (contracción)
         • Azul = Diástole (relajación)
         • Números = Frecuencia cardíaca actual"
        """
        
        # Crear figura con subplots (4 cámaras)
        fig = go.Figure()
        
        # Simulación de contracción ventricular
        t = np.linspace(0, 1, 100)
        contraction = 0.5 + 0.5 * np.sin(np.pi * t)
        
        if not arrhythmia:
            # Normal
            fig.add_trace(go.Scatter(
                x=[0, 1, 1, 0, 0],
                y=[0.5, 0.8, 0.2, 0, 0.5],
                fill='toself',
                name='Ventrículo Izquierdo',
                marker=dict(color='rgba(255, 0, 0, 0.7)'),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=[1, 2, 2, 1, 1],
                y=[0.5, 0.8, 0.2, 0, 0.5],
                fill='toself',
                name='Ventrículo Derecho',
                marker=dict(color='rgba(0, 0, 255, 0.7)'),
                showlegend=False
            ))
        else:
            # Arrítmico - forma irregular
            fig.add_trace(go.Scatter(
                x=[0, 0.8, 1.2, 0.5, 0],
                y=[0.5, 0.9, 0.3, 0.1, 0.5],
                fill='toself',
                name='Ventrículo (Arrítmico)',
                marker=dict(color='rgba(255, 100, 0, 0.7)'),
                showlegend=False
            ))
        
        # Aurículas
        fig.add_trace(go.Scatter(
            x=[0.3, 0.7, 0.7, 0.3, 0.3],
            y=[0.8, 0.8, 1, 1, 0.8],
            fill='toself',
            name='Aurículas',
            marker=dict(color='rgba(255, 150, 0, 0.5)'),
            showlegend=False
        ))
        
        # Aorta (salida)
        fig.add_annotation(
            x=2.3, y=0.5,
            text="🫀",
            font=dict(size=40),
            showarrow=False
        )
        
        # Agregar texto de FC
        fig.add_annotation(
            x=1, y=-0.2,
            text=f"<b>Frecuencia Cardíaca: {heart_rate} bpm</b>",
            showarrow=False,
            font=dict(size=14)
        )
        
        fig.update_layout(
            title=f"<b>Simulación Digital Twin - Corazón</b><br><sub>{'Ritmo Normal' if not arrhythmia else 'Arritmia Detectada'}</sub>",
            height=400,
            template="plotly_white",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            hovermode=False,
            margin=dict(l=0, r=0, t=80, b=60)
        )
        
        return fig
    
    @staticmethod
    def display_brain_activity_3d(band_powers):
        """
        SIMULACIÓN #2: Mapa 3D de actividad cerebral.
        
        INSTRUCCIONES:
        ---------------
        "Visualización 3D del cerebro.
         • Rojo = Alta actividad
         • Azul = Baja actividad
         • Interactivo (rotar, zoom)"
        """
        
        # Crear matriz 3D de actividad simulada
        x = np.arange(0, 5, 0.5)
        y = np.arange(0, 5, 0.5)
        z = np.arange(0, 5, 0.5)
        
        # Datos simulados de actividad
        activity = np.random.uniform(20, 50, (len(x), len(y), len(z)))
        
        # Simplificar para visualización en corte frontal
        frontal_slice = activity[:, :, 2]
        
        fig = go.Figure(data=go.Heatmap(
            z=frontal_slice,
            x=x,
            y=y,
            colorscale='RdBu_r',
            colorbar=dict(title="Actividad (µV²)")
        ))
        
        fig.update_layout(
            title="<b>Digital Twin - Actividad Cerebral (Corte Frontal)</b>",
            xaxis_title="Eje X (Lateral)",
            yaxis_title="Eje Y (Anteroposterior)",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    @staticmethod
    def display_muscle_contraction_simulation(activation_level):
        """
        SIMULACIÓN #3: Contracción muscular simulada.
        
        INSTRUCCIONES:
        ---------------
        "Visualización de contracción muscular.
         • Rojo intenso = Máxima contracción
         • Azul claro = Relajado"
        """
        
        # Simular longitud del músculo
        relaxed_length = 10
        contracted_length = relaxed_length * (1 - activation_level / 100 * 0.3)
        
        fig = go.Figure()
        
        # Muscle fiber
        fiber_color = f'rgba({int(255 * activation_level / 100)}, 0, {int(255 * (1 - activation_level / 100))}, 0.7)'
        
        fig.add_trace(go.Bar(
            x=['Longitud del Músculo'],
            y=[contracted_length],
            marker=dict(color=fiber_color, line=dict(color='black', width=2)),
            text=[f'{contracted_length:.1f} cm'],
            textposition='auto',
            hovertemplate='<b>Longitud:</b> %{y:.1f} cm<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"<b>Digital Twin - Contracción Muscular</b><br><sub>Activación: {activation_level}%</sub>",
            yaxis=dict(range=[0, 15], title='Longitud (cm)'),
            height=350,
            template="plotly_white",
            showlegend=False
        )
        
        return fig

    @staticmethod
    def display_respiratory_simulation(respiratory_rate, oxygen_saturation):
        """
        SIMULACIÓN #4: Función respiratoria.
        """
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Frecuencia Respiratoria', 'SpO2'],
            y=[respiratory_rate, oxygen_saturation],
            marker=dict(color=['#1f77b4', '#2ca02c']),
            text=[f"{respiratory_rate} rpm", f"{oxygen_saturation}%"],
            textposition='auto'
        ))
        fig.update_layout(
            title="<b>Digital Twin - Función Respiratoria</b>",
            yaxis=dict(range=[0, max(20, oxygen_saturation + 10)], title='Valor'),
            height=380,
            template="plotly_white",
            showlegend=False
        )
        return fig

    @staticmethod
    def display_metabolism_simulation(blood_glucose, energy_expenditure):
        """
        SIMULACIÓN #5: Estado metabólico.
        """
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Glucosa en Ayunas', 'Gasto Energético'],
            y=[blood_glucose, energy_expenditure],
            marker=dict(color=['#ff7f0e', '#9467bd']),
            text=[f"{blood_glucose:.1f} mg/dL", f"{energy_expenditure:.0f} kcal/día"],
            textposition='auto'
        ))
        fig.update_layout(
            title="<b>Digital Twin - Estado Metabólico</b>",
            yaxis=dict(title='Valor', rangemode='tozero'),
            height=380,
            template="plotly_white",
            showlegend=False
        )
        return fig

    @staticmethod
    def display_what_if_scenarios(specialty, current_metrics):
        """
        SIMULACIÓN INTERACTIVA: "¿Qué pasa si...?"
        
        Permite visualizar escenarios hipotéticos.
        
        PARÁMETROS:
        -----------
        specialty : str ("Cardiology", "Neurology", "Musculoskeletal")
        current_metrics : dict (métricas actuales)
        
        INSTRUCCIONES:
        ---------------
        "Simulación de diferentes escenarios.
         • Ajusta parámetros con los sliders
         • Ve cómo cambia el sistema
         • Compara diferentes tratamientos"
        """
        
        st.subheader("🔮 Escenarios de Simulación")
        
        if specialty == "Cardiology":
            st.info("**Cardiología**: Simula efectos de intervenciones")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Intervención 1: Medicamento**")
                med_efficacy = st.slider("Eficacia del medicamento (%)", 0, 100, 40, key="med_effect")
                
                # Simular reducción de FC
                baseline_hr = current_metrics.get('heart_rate', 70)
                new_hr = baseline_hr - (baseline_hr * med_efficacy / 100 * 0.2)
                
                st.metric("Nueva FC Esperada", f"{int(new_hr)} bpm", 
                         delta=f"{int(baseline_hr - new_hr)} bpm ↓")
            
            with col2:
                st.write("**Intervención 2: Ejercicio**")
                exercise_intensity = st.slider("Intensidad de ejercicio (%)", 0, 100, 50, key="exercise")
                
                # Simular cambio de presión
                baseline_sys = current_metrics.get('systolic_bp', 120)
                change = (baseline_sys - 120) * (1 - exercise_intensity / 100)
                new_sys = baseline_sys - change * 0.15
                
                st.metric("Presión Sistólica Esperada", f"{int(new_sys)} mmHg", 
                         delta=f"{int(baseline_sys - new_sys):.0f} ↓")
        
        elif specialty == "Neurology":
            st.info("**Neurología**: Simula mejora del sueño")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Intervención 1: Higiene del Sueño**")
                sleep_improvement = st.slider("Mejora esperada (%)", 0, 100, 30, key="sleep_hygiene")
                
                baseline_quality = current_metrics.get('sleep_quality', 60)
                new_quality = min(baseline_quality + (100 - baseline_quality) * sleep_improvement / 100, 100)
                
                st.metric("Nueva Calidad Esperada", f"{int(new_quality)}%", 
                         delta=f"+{int(new_quality - baseline_quality)}%")
            
            with col2:
                st.write("**Intervención 2: Meditación Diaria**")
                meditation_minutes = st.slider("Minutos diarios", 0, 60, 15, key="meditation")
                
                baseline_stress = current_metrics.get('stress_level', 50)
                new_stress = max(baseline_stress - meditation_minutes / 2, 0)
                
                st.metric("Nivel de Estrés Esperado", f"{int(new_stress)}%", 
                         delta=f"{int(baseline_stress - new_stress)}% ↓")
        
        elif specialty == "Musculoskeletal":
            st.info("**Musculoesquelético**: Simula recuperación")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Protocolo 1: Fisioterapia**")
                therapy_frequency = st.slider("Sesiones por semana", 0, 7, 3, key="therapy")
                
                baseline_strength = current_metrics.get('strength_left', 50)
                weekly_gain = therapy_frequency * 2
                projected_strength = min(baseline_strength + weekly_gain, 100)
                
                st.metric("Fuerza Esperada (4 semanas)", f"{int(projected_strength)}%", 
                         delta=f"+{int(projected_strength - baseline_strength)}%")
            
            with col2:
                st.write("**Protocolo 2: Descanso Activo**")
                rest_hours = st.slider("Horas de reposo por día", 0, 24, 8, key="rest")
                
                baseline_fatigue = current_metrics.get('fatigue_level', 50)
                recovery_rate = rest_hours / 8  # 8 horas es óptimo
                new_fatigue = max(baseline_fatigue - baseline_fatigue * recovery_rate * 0.3, 0)
                
                st.metric("Fatiga Esperada", f"{int(new_fatigue)}%", 
                         delta=f"{int(baseline_fatigue - new_fatigue)}% ↓")

        elif specialty == "Respiratory":
            st.info("**Respiratorio**: Simula soporte ventilatorio")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Intervención 1: Soporte de Oxígeno**")
                oxygen_flow = st.slider("Flujo de oxígeno (L/min)", 0, 10, 2, key="oxygen_flow")
                baseline_spo2 = current_metrics.get('oxygen_saturation', 96)
                expected_spo2 = min(baseline_spo2 + oxygen_flow * 1.2, 100)
                st.metric("SpO2 Esperado", f"{int(expected_spo2)}%", delta=f"+{int(expected_spo2 - baseline_spo2)}%")
            with col2:
                st.write("**Intervención 2: Ejercicio Respiratorio**")
                breathing_exercises = st.slider("Sesiones diarias", 0, 5, 1, key="breathing_exercises")
                baseline_rate = current_metrics.get('respiratory_rate', 16)
                new_rate = baseline_rate - breathing_exercises * 0.8
                new_rate = max(new_rate, 10)
                st.metric("Frecuencia Respiratoria Esperada", f"{int(new_rate)} rpm", delta=f"{int(baseline_rate - new_rate)} rpm ↓")

        elif specialty == "Metabolism":
            st.info("**Metabolismo**: Simula control glucémico")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Intervención 1: Dieta Balanceada**")
                carb_reduction = st.slider("Reducción de carbohidratos (%)", 0, 100, 20, key="carb_reduction")
                baseline_glucose = current_metrics.get('blood_glucose', 100)
                expected_glucose = baseline_glucose - baseline_glucose * carb_reduction / 100 * 0.1
                st.metric("Glucosa en Ayunas Esperada", f"{expected_glucose:.1f} mg/dL", delta=f"-{baseline_glucose - expected_glucose:.1f} mg/dL")
            with col2:
                st.write("**Intervención 2: Actividad Física**")
                exercise_minutes = st.slider("Minutos de ejercicio por día", 0, 120, 30, key="exercise_met")
                baseline_sensitivity = current_metrics.get('insulin_sensitivity', 60)
                expected_sensitivity = min(baseline_sensitivity + exercise_minutes * 0.2, 100)
                st.metric("Sensibilidad a Insulina Esperada", f"{expected_sensitivity:.1f}%", delta=f"+{expected_sensitivity - baseline_sensitivity:.1f}%")
        
        return None
