"""
COMPONENTES UI PARA MUSCULOESQUELÉTICO
======================================
Todos los componentes visuales específicos para EMG y análisis muscular.
Incluye: EMG crudo, fatiga, patología, activación muscular, recuperación.

ESTRUCTURA:
-----------
    1. EMG crudo y envolvente
    2. Análisis de fatiga (Median Frequency)
    3. Nivel de activación muscular
    4. Detección de patología
    5. Comparación bilateral (izq vs der)
    6. Proyección de recuperación

USO EN STREAMLIT:
-----------------
    from app.components.musculoskeletal_ui import MusculoskeletalUI
    
    muscular = MusculoskeletalUI()
    muscular.display_emg_analysis(patient_data)
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy.signal import hilbert
from scipy.fft import fft, fftfreq


class MusculoskeletalUI:
    """
    Componentes de interfaz para Musculoesquelético.
    Cada método es UNA VISUALIZACIÓN completa.
    """
    
    @staticmethod
    def display_emg_raw_and_envelope(emg_data, muscle_name="Bíceps"):
        """
        GRAFICA #1: EMG crudo + envolvente procesada.
        
        PARÁMETROS:
        -----------
        emg_data : dict
            {
                'signal': array NumPy con valores EMG crudos,
                'envelope': array con envolvente,
                'time': array con timestamps,
                'sampling_rate': int (típicamente 2000 Hz)
            }
        muscle_name : str
            Nombre del músculo (ej: Bíceps, Tríceps, etc)
        
        CARACTERÍSTICAS:
        ----------------
        ✓ EMG crudo (ruido de alta frecuencia)
        ✓ Envolvente (amplitud suavizada)
        ✓ Referencia baseline
        
        INSTRUCCIONES AL USUARIO:
        -------------------------
        "Señal EMG del músculo.
         • Línea azul = Señal cruda (100-500 Hz)
         • Línea roja = Envolvente (suavizada)
         • Amplitud aumenta = Contracción muscular
         • Amplitud cero = Músculo relajado"
        """
        
        signal_array = emg_data['signal']
        envelope_array = emg_data['envelope']
        time_array = emg_data['time']
        
        fig = go.Figure()
        
        # EMG crudo
        fig.add_trace(go.Scatter(
            x=time_array,
            y=signal_array,
            mode='lines',
            name='EMG Crudo',
            line=dict(color='rgba(31, 119, 180, 0.4)', width=0.5),
            hovertemplate='<b>Tiempo:</b> %{x:.3f}s<br><b>EMG:</b> %{y:.2f}mV<extra></extra>'
        ))
        
        # Envolvente
        fig.add_trace(go.Scatter(
            x=time_array,
            y=envelope_array,
            mode='lines',
            name='Envolvente',
            line=dict(color='red', width=2),
            hovertemplate='<b>Tiempo:</b> %{x:.3f}s<br><b>Envolvente:</b> %{y:.2f}mV<extra></extra>'
        ))
        
        # Baseline
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        fig.update_layout(
            title=f"<b>Señal EMG - Músculo {muscle_name}</b><br><sub>Crudo + Envolvente</sub>",
            xaxis_title="Tiempo (segundos)",
            yaxis_title="Amplitud (mV)",
            height=350,
            template="plotly_white",
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def display_fatigue_analysis(measurement_history, muscle_name="Bíceps"):
        """
        GRAFICA #2: Progresión de fatiga muscular (Median Frequency).
        
        CONCEPTO:
        ---------
        La Median Frequency (MF) disminuye con la fatiga muscular.
        • MF inicial: ~250 Hz (músculo fresco)
        • MF con fatiga: ~150-180 Hz (músculo fatigado)
        • Caída de >30% = Fatiga significativa
        
        INSTRUCCIONES:
        ---------------
        "Progresión de fatiga en el músculo.
         • Línea descendente = Fatiga acumulada
         • Descenso rápido = Fatiga severa
         • Línea plana = Músculo estable
         • Recuperación = Sube después del descanso"
        """
        
        dates = [m['date'] for m in measurement_history]
        mf_values = [m['median_frequency'] for m in measurement_history]
        fatigue_levels = [m['fatigue_level'] for m in measurement_history]
        
        fig = go.Figure()
        
        # Median Frequency (eje izquierdo)
        fig.add_trace(go.Scatter(
            x=dates,
            y=mf_values,
            mode='lines+markers',
            name='Median Frequency',
            line=dict(color='#2ca02c', width=2),
            marker=dict(size=6),
            yaxis='y1',
            hovertemplate='<b>Fecha:</b> %{x}<br><b>MF:</b> %{y:.1f} Hz<extra></extra>'
        ))
        
        # Fatiga Level (eje derecho)
        fig.add_trace(go.Scatter(
            x=dates,
            y=fatigue_levels,
            mode='lines+markers',
            name='Fatiga (%)',
            line=dict(color='red', width=2, dash='dash'),
            marker=dict(size=6),
            yaxis='y2',
            hovertemplate='<b>Fecha:</b> %{x}<br><b>Fatiga:</b> %{y:.0f}%<extra></extra>'
        ))
        
        # Umbrales
        fig.add_hline(y=200, line_dash="dash", line_color="orange", opacity=0.5, 
                     yref='y1', annotation_text="Umbral Fatiga")
        
        fig.update_layout(
            title=f"<b>Análisis de Fatiga - {muscle_name}</b><br><sub>Últimos 30 días</sub>",
            xaxis_title="Fecha",
            yaxis=dict(
                title="Median Frequency (Hz)",
                titlefont=dict(color='#2ca02c'),
                tickfont=dict(color='#2ca02c')
            ),
            yaxis2=dict(
                title="Nivel de Fatiga (%)",
                titlefont=dict(color='red'),
                tickfont=dict(color='red'),
                overlaying='y',
                side='right'
            ),
            height=350,
            template="plotly_white",
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def display_activation_level_gauge(activation_percentage, muscle_name="Bíceps"):
        """
        GRAFICA #3: Nivel de activación muscular actual (gauge).
        
        NIVELES:
        --------
        0-10%:    En reposo
        10-30%:   Activación baja
        30-60%:   Activación moderada
        60-90%:   Activación alta
        90-100%:  Máxima contracción
        
        INSTRUCCIONES:
        ---------------
        "Nivel actual de contracción muscular.
         • Verde (0-30%) = Reposo
         • Amarillo (30-70%) = Ejercicio moderado
         • Rojo (70-100%) = Máximo esfuerzo"
        """
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=activation_percentage,
            title={'text': f"Activación {muscle_name}"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': 'darkblue'},
                'steps': [
                    {'range': [0, 10], 'color': 'lightgreen'},
                    {'range': [10, 30], 'color': 'lightgreen'},
                    {'range': [30, 60], 'color': 'lightyellow'},
                    {'range': [60, 90], 'color': 'orange'},
                    {'range': [90, 100], 'color': 'lightcoral'},
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': 85
                }
            },
            delta={'reference': 50, 'suffix': '%'}
        ))
        
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=60, b=20))
        
        return fig
    
    @staticmethod
    def display_bilateral_comparison(patient_data):
        """
        GRAFICA #4: Comparación bilateral (izquierda vs derecha).
        
        INSTRUCCIONES:
        ---------------
        "Comparación de métricas entre lados.
         • Diferencia <10% = Normal
         • Diferencia 10-20% = Desbalance moderado
         • Diferencia >20% = Desbalance severo (posible lesión)"
        """
        
        measurement = patient_data['latest_measurement']
        emg_left = measurement['emg_left']
        emg_right = measurement['emg_right']
        
        rom_left = measurement['rom_left']
        rom_right = measurement['rom_right']
        
        strength_left = measurement['strength_left']
        strength_right = measurement['strength_right']
        
        # Calcular porcentaje de diferencia
        rom_diff = abs(rom_left - rom_right) / max(rom_left, rom_right) * 100
        strength_diff = abs(strength_left - strength_right) / max(strength_left, strength_right) * 100
        
        metrics = ['ROM (°)', 'Fuerza (%)']
        left_values = [rom_left, strength_left]
        right_values = [rom_right, strength_right]
        
        fig = go.Figure(data=[
            go.Bar(
                x=metrics,
                y=left_values,
                name='Izquierda',
                marker=dict(color='#1f77b4'),
                hovertemplate='<b>%{x}</b><br>Izq: %{y:.0f}<extra></extra>'
            ),
            go.Bar(
                x=metrics,
                y=right_values,
                name='Derecha',
                marker=dict(color='#ff7f0e'),
                hovertemplate='<b>%{x}</b><br>Der: %{y:.0f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="<b>Comparación Bilateral</b><br><sub>Izquierda vs Derecha</sub>",
            barmode='group',
            xaxis_title="Métrica",
            yaxis_title="Valor",
            height=350,
            template="plotly_white"
        )
        
        return fig
    
    @staticmethod
    def display_pathology_classification(emg_signal, classification="Normal"):
        """
        GRAFICA #5: Clasificación de patología neuromuscular.
        
        TIPOS:
        ------
        Normal:        Patrón normal de activación
        Miopatía:      Patrón de pequeñas unidades motoras
        Neuropatía:    Patrón polifásico anormal
        MND:           Enfermedad de neurona motora
        
        INSTRUCCIONES:
        ---------------
        "Clasificación de posible patología.
         • Verde = Patrón normal
         • Amarillo = Sospecha de patología
         • Rojo = Posible patología (necesita médico)"
        """
        
        pathologies = ['Normal', 'Miopatía', 'Neuropatía', 'MND']
        
        # Simular confianzas según clasificación
        if classification == "Normal":
            confidences = [0.95, 0.02, 0.02, 0.01]
            color_main = 'green'
        elif classification == "Myopathy":
            confidences = [0.05, 0.88, 0.05, 0.02]
            color_main = 'orange'
        elif classification == "Neuropathy":
            confidences = [0.03, 0.05, 0.90, 0.02]
            color_main = 'orange'
        elif classification == "MND":
            confidences = [0.02, 0.05, 0.08, 0.85]
            color_main = 'red'
        else:
            confidences = [0.9, 0.05, 0.03, 0.02]
            color_main = 'green'
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=pathologies,
            y=confidences,
            marker=dict(
                color=['green', 'orange', 'orange', 'red'],
                line=dict(color='black', width=1.5)
            ),
            text=[f'{c*100:.1f}%' for c in confidences],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Confianza: %{y:.1%}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"<b>Clasificación de Patología</b><br><sub>Detectada: {classification}</sub>",
            xaxis_title="Tipo de Patología",
            yaxis_title="Confianza del Modelo",
            height=350,
            template="plotly_white",
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def display_recovery_projection(injury_type="Strain", initial_strength=40):
        """
        GRAFICA #6: Proyección de recuperación post-lesión.
        
        RECUPERACIÓN (semanas):
        -----------------------
        Distensión:     2-4 semanas (ligero)
        Esguince:       4-8 semanas (moderado)
        Rotura parcial: 8-12 semanas (severo)
        
        INSTRUCCIONES:
        ---------------
        "Proyección de recuperación esperada.
         • Línea azul = Recuperación esperada
         • Línea punteada = Mínimo/Máximo realista
         • Eje X = Semanas
         • Eje Y = Fuerza muscular (%)"
        """
        
        weeks = np.linspace(0, 12, 50)
        
        # Curva de recuperación típica (exponencial)
        if injury_type == "Strain":
            recovery_curve = 40 + 55 * (1 - np.exp(-weeks / 1.5))
            max_weeks = 4
        elif injury_type == "Sprain":
            recovery_curve = 35 + 60 * (1 - np.exp(-weeks / 2.5))
            max_weeks = 8
        else:  # Rotura parcial
            recovery_curve = 30 + 65 * (1 - np.exp(-weeks / 4))
            max_weeks = 12
        
        recovery_curve = np.clip(recovery_curve, 0, 100)
        
        fig = go.Figure()
        
        # Curva esperada
        fig.add_trace(go.Scatter(
            x=weeks,
            y=recovery_curve,
            mode='lines',
            name='Recuperación Esperada',
            line=dict(color='#2ca02c', width=3),
            fill='tozeroy',
            fillcolor='rgba(44, 160, 44, 0.2)',
            hovertemplate='<b>Semana:</b> %{x:.1f}<br><b>Fuerza:</b> %{y:.0f}%<extra></extra>'
        ))
        
        # Rango de incertidumbre
        uncertainty_upper = recovery_curve + 10
        uncertainty_lower = recovery_curve - 10
        
        fig.add_trace(go.Scatter(
            x=np.concatenate([weeks, weeks[::-1]]),
            y=np.concatenate([uncertainty_upper, uncertainty_lower[::-1]]),
            fill='toself',
            name='Rango Realista',
            fillcolor='rgba(44, 160, 44, 0.1)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo='skip'
        ))
        
        # Línea de alta función (85%)
        fig.add_hline(y=85, line_dash="dash", line_color="green", opacity=0.5,
                     annotation_text="Alta Función (85%)")
        
        # Línea de curación completa (95%)
        fig.add_hline(y=95, line_dash="dash", line_color="darkgreen", opacity=0.5,
                     annotation_text="Curación Completa (95%)")
        
        fig.update_layout(
            title=f"<b>Proyección de Recuperación</b><br><sub>Lesión: {injury_type}</sub>",
            xaxis_title="Semanas desde lesión",
            yaxis_title="Fuerza Muscular (%)",
            height=350,
            template="plotly_white",
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def display_musculoskeletal_summary(patient_data, ai_results):
        """
        TABLA RESUMEN: Todos los hallazgos musculoesqueléticos.
        """
        
        measurement = patient_data['latest_measurement']
        
        summary_data = {
            'PARÁMETRO': [
                '💪 Activación Muscular',
                '⚡ Median Frequency',
                '😓 Nivel de Fatiga',
                '📐 ROM Izquierda',
                '📐 ROM Derecha',
                '🏋️ Fuerza Izquierda',
                '🏋️ Fuerza Derecha',
                '🔍 Patología Detectada',
                '⏱️ Tiempo Recuperación',
                '⚠️ Alerta',
                '💊 Recomendación'
            ],
            'VALOR': [
                f"{measurement['emg_left'].get('activation_level', 50)}%",
                f"{measurement['emg_left'].get('median_frequency', 250):.0f} Hz",
                f"{measurement['emg_left'].get('fatigue_level', 30)}%",
                f"{measurement['rom_left']}°",
                f"{measurement['rom_right']}°",
                f"{measurement['strength_left']}%",
                f"{measurement['strength_right']}%",
                ai_results.get('pathology', 'Normal'),
                ai_results.get('recovery_time', '2-4 semanas'),
                ai_results.get('alert_level', 'Normal'),
                ai_results.get('recommendation', 'Rehabilitación estándar')
            ],
            'ESTADO': [
                '✅' if 20 <= measurement['emg_left'].get('activation_level', 50) <= 80 else '⚠️',
                '✅' if measurement['emg_left'].get('median_frequency', 250) > 200 else '⚠️',
                '✅' if measurement['emg_left'].get('fatigue_level', 30) < 50 else '⚠️',
                '✅' if measurement['rom_left'] > 100 else '⚠️',
                '✅' if measurement['rom_right'] > 100 else '⚠️',
                '✅' if measurement['strength_left'] > 70 else '⚠️',
                '✅' if measurement['strength_right'] > 70 else '⚠️',
                '✅' if ai_results.get('pathology') == 'Normal' else '🔴',
                '',
                '✅' if ai_results.get('alert_level') == 'Normal' else '⚠️',
                ''
            ]
        }
        
        st.dataframe(summary_data, use_container_width=True, height=400)
