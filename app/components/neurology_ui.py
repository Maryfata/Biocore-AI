"""
COMPONENTES UI PARA NEUROLOGÍA
===============================
Todos los componentes visuales específicos de neurología.
Incluye: EEG, Bandas de frecuencia, Sueño, Epilepsia, Connectividad cerebral.

ESTRUCTURA:
-----------
    1. Señal EEG cruda (7+ canales)
    2. Análisis de bandas (Delta, Theta, Alpha, Beta, Gamma)
    3. Clasificación de estadios de sueño
    4. Détección de epilepsia
    5. Mapeo de actividad cerebral
    6. Indicadores de salud cerebral

USO EN STREAMLIT:
-----------------
    from app.components.neurology_ui import NeurologyUI
    
    neuro = NeurologyUI()
    neuro.display_eeg_multiband(patient_data)
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy.fft import fft, fftfreq


class NeurologyUI:
    """
    Componentes de interfaz para Neurología.
    Cada método es UNA VISUALIZACIÓN completa.
    """
    
    @staticmethod
    def display_eeg_waveform(eeg_data, channel_name="Frontal (Fz)"):
        """
        GRAFICA #1: Forma de onda EEG en dominio temporal.
        
        PARÁMETROS:
        -----------
        eeg_data : dict
            {
                'signal': array NumPy con valores EEG,
                'time': array con timestamps,
                'sampling_rate': int (típicamente 256 Hz)
            }
        channel_name : str
            Nombre del canal EEG (ej: Fz, Cz, Pz, etc)
        
        CARACTERÍSTICAS:
        ----------------
        ✓ Señal cruda en µV
        ✓ Referencia isoelectric
        ✓ Grilla estándar de EEG
        ✓ Escala en µV/s
        
        INSTRUCCIONES AL USUARIO:
        -------------------------
        "Señal EEG cruda del cerebro.
         • Amplitud típica: 10-100 µV
         • Variaciones rápidas = alerta
         • Variaciones lentas = sueño
         • Espículas anormales = posible patología"
        """
        
        signal_array = eeg_data['signal']
        time_array = eeg_data['time']
        sampling_rate = eeg_data['sampling_rate']
        
        fig = go.Figure()
        
        # Trazar EEG
        fig.add_trace(go.Scatter(
            x=time_array,
            y=signal_array,
            mode='lines',
            name=f'EEG {channel_name}',
            line=dict(color='#9467bd', width=1.5),
            hovertemplate='<b>Tiempo:</b> %{x:.2f}s<br><b>Amplitud:</b> %{y:.1f}µV<extra></extra>'
        ))
        
        # Baseline
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Grilla EEG
        for x_grid in np.arange(0, time_array[-1], 1):
            fig.add_vline(x=x_grid, line_width=0.5, line_color="lightgray", opacity=0.2)
        
        for y_grid in np.arange(-200, 200, 50):
            fig.add_hline(y=y_grid, line_width=0.5, line_color="lightgray", opacity=0.2)
        
        fig.update_layout(
            title=f"<b>Señal EEG - Canal {channel_name}</b><br><sub>Duración: {time_array[-1]:.1f} segundos</sub>",
            xaxis_title="Tiempo (segundos)",
            yaxis_title="Amplitud (µV)",
            height=350,
            template="plotly_white",
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def display_frequency_bands(bands_data):
        """
        GRAFICA #2: Potencia en 5 bandas de frecuencia EEG.
        
        BANDAS EEG (Hz):
        ----------------
        Delta:  0.5-4 Hz   (sueño profundo)
        Theta:  4-8 Hz     (somnolencia)
        Alpha:  8-12 Hz    (relajación)
        Beta:   12-30 Hz   (alerta mental)
        Gamma:  30-100 Hz  (procesamiento cognitivo)
        
        INSTRUCCIONES:
        ---------------
        "Análisis de bandas de frecuencia cerebral.
         • Delta alto = sueño profundo (>20%)
         • Theta alto = somnolencia
         • Alpha alto = relajación
         • Beta alto = alerta/concentración
         • Gamma alto = procesamiento intenso"
        """
        
        bands = bands_data  # {'Delta': 30, 'Theta': 25, ...}
        band_names = list(bands.keys())
        band_values = list(bands.values())
        band_colors = ['#2ca02c', '#1f77b4', '#ff7f0e', '#d62728', '#9467bd']
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=band_names,
            y=band_values,
            marker=dict(
                color=band_colors,
                line=dict(color='black', width=1.5)
            ),
            text=[f'{v:.0f}%' for v in band_values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Potencia: %{y:.1f}%<extra></extra>'
        ))
        
        # Línea de 20% (umbral delta para sueño profundo)
        fig.add_hline(y=20, line_dash="dash", line_color="red", opacity=0.5, 
                     annotation_text="Umbral Sueño Profundo (20%)")
        
        fig.update_layout(
            title="<b>Análisis de Bandas de Frecuencia</b><br><sub>Distribución de potencia cerebral</sub>",
            xaxis_title="Banda de Frecuencia",
            yaxis_title="Potencia Relativa (%)",
            height=350,
            template="plotly_white",
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def display_sleep_stage_classification(sleep_stage, confidence):
        """
        GRAFICA #3: Clasificación de estadio de sueño (AASM).
        
        ESTADIOS (AASM American Academy Sleep Medicine):
        -------------------------------------------------
        AWAKE:  Despierto, alerta mental (Beta/Gamma alto)
        N1:     Sueño ligero inicial (Theta alto)
        N2:     Sueño ligero con spindles (Theta + Beta 12-14 Hz)
        N3:     Sueño profundo/NREM (Delta >20%)
        REM:    Movimiento rápido ojos (Beta/Gamma, similar a despierto)
        
        INSTRUCCIONES:
        ---------------
        "Estadio de sueño actual.
         • Verde = Normal para esa hora
         • Amarillo = Anormal
         • Rojo = Posible patología"
        """
        
        stages = ['AWAKE', 'N1', 'N2', 'N3', 'REM']
        
        # Simular confianzas según etapa
        if sleep_stage.upper() == "AWAKE":
            confidences = [0.92, 0.03, 0.02, 0.01, 0.02]
            stage_description = "Despierto - Alerta mental"
            color_bg = 'rgba(255, 0, 0, 0.1)'
        elif sleep_stage.upper() == "N1":
            confidences = [0.05, 0.88, 0.04, 0.01, 0.02]
            stage_description = "Sueño Ligero Inicial"
            color_bg = 'rgba(255, 255, 0, 0.1)'
        elif sleep_stage.upper() == "N2":
            confidences = [0.02, 0.05, 0.90, 0.01, 0.02]
            stage_description = "Sueño Ligero con Spindles"
            color_bg = 'rgba(255, 255, 0, 0.1)'
        elif sleep_stage.upper() == "N3":
            confidences = [0.01, 0.01, 0.03, 0.94, 0.01]
            stage_description = "Sueño Profundo (NREM)"
            color_bg = 'rgba(0, 0, 255, 0.1)'
        elif sleep_stage.upper() == "REM":
            confidences = [0.03, 0.02, 0.02, 0.01, 0.92]
            stage_description = "Sueño REM - Movimiento Rápido de Ojos"
            color_bg = 'rgba(255, 165, 0, 0.1)'
        else:
            confidences = [0.5, 0.2, 0.2, 0.05, 0.05]
            stage_description = "Desconocido"
            color_bg = 'rgba(128, 128, 128, 0.1)'
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=stages,
            y=confidences,
            marker=dict(
                color=['red', 'orange', 'orange', 'blue', 'purple'],
                line=dict(color='black', width=1.5)
            ),
            text=[f'{c*100:.1f}%' for c in confidences],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Confianza: %{y:.1%}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"<b>Clasificación de Estadio de Sueño</b><br><sub>{stage_description}</sub>",
            xaxis_title="Estadio (AASM)",
            yaxis_title="Confianza del Modelo",
            height=350,
            template="plotly_white",
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def display_seizure_risk(risk_score, hours_ahead=24):
        """
        GRAFICA #4: Riesgo de crisis epiléptica (gráfica de riesgo temporal).
        
        INSTRUCCIONES:
        ---------------
        "Predicción de riesgo de crisis en próximas horas.
         • Rojo = Alto riesgo, necesita intervención
         • Amarillo = Vigilancia activa
         • Verde = Bajo riesgo"
        """
        
        hours = np.arange(0, hours_ahead + 1)
        # Simular riesgo variando a lo largo del día
        risk_curve = risk_score + (np.sin(hours / 4) * 0.2) + np.random.normal(0, 0.05, len(hours))
        risk_curve = np.clip(risk_curve, 0, 1)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=hours,
            y=risk_curve * 100,
            mode='lines+markers',
            name='Riesgo',
            line=dict(color='red', width=3),
            fill='tozeroy',
            fillcolor='rgba(255, 0, 0, 0.2)',
            hovertemplate='<b>Hora +%{x}h</b><br>Riesgo: %{y:.1f}%<extra></extra>'
        ))
        
        # Umbrales de alerta
        fig.add_hline(y=20, line_dash="dash", line_color="orange", opacity=0.7,
                     annotation_text="Umbral Vigilancia")
        fig.add_hline(y=50, line_dash="dash", line_color="red", opacity=0.7,
                     annotation_text="Umbral Crítico")
        
        fig.update_layout(
            title=f"<b>Predicción de Riesgo de Crisis Epiléptica</b><br><sub>Próximas {hours_ahead} horas</sub>",
            xaxis_title="Horas a Partir de Ahora",
            yaxis_title="Probabilidad de Crisis (%)",
            height=350,
            template="plotly_white",
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def display_brain_activity_heatmap(channel_bands):
        """
        GRAFICA #5: Mapa de calor de actividad cerebral por región.
        
        CANALES ESTÁNDAR 10-20:
        -----------------------
        Frente:    Fp1, Fp2 (prefrontal)
        Central:   F3, F4, C3, C4, P3, P4 (sensoriomotor)
        Occipital: O1, O2 (visual)
        
        INSTRUCCIONES:
        ---------------
        "Mapa de actividad cerebral en diferentes regiones.
         • Colores cálidos (rojo) = Alta actividad
         • Colores fríos (azul) = Baja actividad
         • Patrón heterogéneo = Normal
         • Patrón simétrico anormal = Posible patología"
        """
        
        # Canales simulados
        channels = ['Fp1', 'Fp2', 'F3', 'F4', 'C3', 'C4', 'P3', 'P4', 'O1', 'O2']
        bands = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']
        
        # Matriz de actividad
        activity_matrix = np.random.uniform(10, 50, (len(channels), len(bands)))
        
        fig = go.Figure(data=go.Heatmap(
            z=activity_matrix,
            x=bands,
            y=channels,
            colorscale='RdBu_r',
            hovertemplate='<b>Canal:</b> %{y}<br><b>Banda:</b> %{x}<br><b>Potencia:</b> %{z:.1f}µV²<extra></extra>',
            colorbar=dict(title="Potencia (µV²)")
        ))
        
        fig.update_layout(
            title="<b>Mapa de Calor de Actividad Cerebral</b><br><sub>Potencia por canal y banda</sub>",
            xaxis_title="Banda de Frecuencia",
            yaxis_title="Canal EEG (Sistema 10-20)",
            height=400,
            template="plotly_white"
        )
        
        return fig
    
    @staticmethod
    def display_sleep_quality_over_time(measurement_history):
        """
        GRAFICA #6: Calidad del sueño a lo largo del tiempo.
        
        INSTRUCCIONES:
        ---------------
        "Tendencia de calidad de sueño.
         • Verde = Buena calidad
         • Amarillo = Moderada
         • Rojo = Pobre
         • Gráfica descendente = Deterioro"
        """
        
        dates = [m['date'] for m in measurement_history]
        sleep_quality = [m['sleep_quality'] for m in measurement_history]
        
        # Calcular media móvil
        if len(sleep_quality) > 7:
            from scipy.ndimage import uniform_filter1d
            moving_avg = uniform_filter1d(sleep_quality, size=7, mode='nearest')
        else:
            moving_avg = sleep_quality
        
        fig = go.Figure()
        
        # Puntos individuales
        fig.add_trace(go.Scatter(
            x=dates,
            y=sleep_quality,
            mode='markers',
            name='Noche Individual',
            marker=dict(size=8, color='lightblue', opacity=0.6),
            hovertemplate='<b>Fecha:</b> %{x}<br><b>Calidad:</b> %{y:.0f}%<extra></extra>'
        ))
        
        # Media móvil 7 días
        fig.add_trace(go.Scatter(
            x=dates,
            y=moving_avg,
            mode='lines',
            name='Media Móvil (7 días)',
            line=dict(color='#2ca02c', width=3),
            hovertemplate='<b>Fecha:</b> %{x}<br><b>Promedio:</b> %{y:.0f}%<extra></extra>'
        ))
        
        # Zonas de calidad
        fig.add_hrect(y0=0, y1=40, fillcolor="red", opacity=0.1, annotation_text="Pobre")
        fig.add_hrect(y0=40, y1=70, fillcolor="yellow", opacity=0.1, annotation_text="Moderada")
        fig.add_hrect(y0=70, y1=100, fillcolor="green", opacity=0.1, annotation_text="Buena")
        
        fig.update_layout(
            title="<b>Calidad del Sueño - Últimos 30 días</b>",
            xaxis_title="Fecha",
            yaxis_title="Puntuación de Calidad (%)",
            height=350,
            template="plotly_white",
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def display_neurology_summary(patient_data, ai_results):
        """
        TABLA RESUMEN: Todos los hallazgos neurológicos en un lugar.
        """
        
        measurement = patient_data['latest_measurement']
        bands = measurement['eeg']['bands']
        
        summary_data = {
            'PARÁMETRO': [
                '🧠 Estadio de Sueño',
                '⚡ Delta (%)',
                '⚡ Theta (%)',
                '⚡ Alpha (%)',
                '⚡ Beta (%)',
                '⚡ Gamma (%)',
                '😴 Calidad Sueño',
                '⚠️ Riesgo de Crisis',
                '🎯 Alerta',
                '💊 Recomendación'
            ],
            'VALOR': [
                ai_results.get('sleep_stage', 'N2'),
                f"{bands.get('Delta', 25):.0f}%",
                f"{bands.get('Theta', 20):.0f}%",
                f"{bands.get('Alpha', 15):.0f}%",
                f"{bands.get('Beta', 30):.0f}%",
                f"{bands.get('Gamma', 10):.0f}%",
                f"{measurement.get('sleep_quality', 70)}%",
                ai_results.get('seizure_risk', 'Bajo'),
                ai_results.get('alert_level', 'Normal'),
                ai_results.get('recommendation', 'Monitoreo continuo')
            ],
            'ESTADO': [
                '✅' if ai_results.get('sleep_stage') in ['N2', 'N3'] else '⚠️',
                '✅' if bands.get('Delta', 0) < 40 else '🔴',
                '✅' if 20 <= bands.get('Theta', 0) <= 30 else '⚠️',
                '✅' if 10 <= bands.get('Alpha', 0) <= 20 else '⚠️',
                '✅' if bands.get('Beta', 0) < 40 else '⚠️',
                '✅' if bands.get('Gamma', 0) < 20 else '⚠️',
                '✅' if measurement.get('sleep_quality', 0) > 70 else '⚠️',
                '✅' if ai_results.get('seizure_risk') == 'Bajo' else '🔴',
                '✅' if ai_results.get('alert_level') == 'Normal' else '⚠️',
                ''
            ]
        }
        
        st.dataframe(summary_data, use_container_width=True, height=400)
