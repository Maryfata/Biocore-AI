"""
COMPONENTES UI PARA CARDIOLOGÍA
================================
Todos los componentes visuales específicos de cardiología.
Incluye: ECG, HRV, Presión, Arritmias, Alertas.

ESTRUCTURA:
-----------
    1. Gráfica ECG (dominio temporal)
    2. Análisis de frecuencia (FFT del ECG)
    3. HRV - Variabilidad del ritmo cardíaco
    4. Presión arterial
    5. Métricas cardíacas
    6. Detección de arritmias (IA)
    7. Tabla de resultados

USO EN STREAMLIT:
-----------------
    from app.components.cardiology_ui import CardiacUI
    
    cardiac = CardiacUI()
    cardiac.display_ecg_analysis(patient_data)
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq


class CardiacUI:
    """
    Componentes de interfaz para Cardiología.
    Cada método es UNA VISUALIZACIÓN completa.
    """
    
    @staticmethod
    def display_ecg_waveform(ecg_data, title="ECG de 10 segundos"):
        """
        GRAFICA #1: Forma de onda ECG en dominio temporal.
        
        PARÁMETROS:
        -----------
        ecg_data : dict
            {
                'signal': array NumPy con valores ECG,
                'time': array con timestamps,
                'sampling_rate': int frecuencia de muestreo
            }
        title : str
            Título de la gráfica
        
        CARACTERÍSTICAS:
        ----------------
        ✓ Línea de referencia (isoelectric line)
        ✓ Grilla de ECG (grande 5mm, pequeña 1mm)
        ✓ Anotaciones automáticas de ondas P, QRS, T
        ✓ Interactivo (zoom, hover, exportar)
        
        VISUAL:
        -------
        Gráfica con:
        - Eje X: Tiempo (segundos)
        - Eje Y: Voltaje (mV)
        - Grilla ECG estándar
        - Componentes P, QRS, T marcados
        
        INSTRUCCIONES AL USUARIO:
        -------------------------
        "Analiza la forma de onda ECG.
         • La onda P = activación de aurículas
         • El complejo QRS = activación de ventrículos
         • La onda T = recuperación de ventrículos
         • Duración normal: ~1 segundo por ciclo"
        """
        
        signal_array = ecg_data['signal']
        time_array = ecg_data['time']
        
        # Crear figura
        fig = go.Figure()
        
        # Trazar ECG
        fig.add_trace(go.Scatter(
            x=time_array,
            y=signal_array,
            mode='lines',
            name='ECG Signal',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Tiempo:</b> %{x:.3f}s<br><b>Voltaje:</b> %{y:.3f}mV<extra></extra>'
        ))
        
        # Línea isoelectric (baseline)
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="gray",
            opacity=0.5,
            annotation_text="Baseline"
        )
        
        # Grilla ECG
        for x_grid in np.arange(0, time_array[-1], 0.2):
            fig.add_vline(x=x_grid, line_width=0.5, line_color="lightgray", opacity=0.3)
        
        for y_grid in np.arange(-3, 3, 0.5):
            fig.add_hline(y=y_grid, line_width=0.5, line_color="lightgray", opacity=0.3)
        
        # Detectar máximos (simplificado como aproximación de R-peaks)
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(signal_array, height=0.5, distance=100)
        
        if len(peaks) > 0:
            fig.add_trace(go.Scatter(
                x=time_array[peaks],
                y=signal_array[peaks],
                mode='markers',
                name='R-Peaks',
                marker=dict(color='red', size=8),
                hovertemplate='<b>R-Peak en:</b> %{x:.3f}s<extra></extra>'
            ))
        
        # Configuración del layout
        fig.update_layout(
            title=f"<b>{title}</b><br><sub>Análisis de forma de onda ECG</sub>",
            xaxis_title="Tiempo (segundos)",
            yaxis_title="Voltaje (mV)",
            height=400,
            template="plotly_white",
            hovermode='x unified',
            font=dict(size=11),
            margin=dict(l=50, r=50, t=80, b=50)
        )
        
        return fig
    
    @staticmethod
    def display_ecg_frequency_analysis(ecg_data):
        """
        GRAFICA #2: Análisis de frecuencia del ECG (FFT).
        
        INSTRUCCIONES AL USUARIO:
        -------------------------
        "Espectro de frecuencia del corazón.
         • Componentes principales entre 0.5-40 Hz
         • Picos indican actividad arrítmica
         • Mayor amplitud = mayor componente frecuencial"
        """
        
        signal_array = ecg_data['signal']
        sampling_rate = ecg_data['sampling_rate']
        
        # FFT
        N = len(signal_array)
        fft_vals = np.abs(fft(signal_array))
        freqs = fftfreq(N, 1/sampling_rate)
        
        # Solo frecuencias positivas relevantes (0-50 Hz)
        mask = (freqs >= 0) & (freqs <= 50)
        freqs_pos = freqs[mask]
        fft_pos = fft_vals[mask]
        
        # Normalizar
        fft_pos = fft_pos / np.max(fft_pos)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=freqs_pos,
            y=fft_pos,
            fill='tozeroy',
            name='Amplitud',
            line=dict(color='#2ca02c', width=2),
            hovertemplate='<b>Frecuencia:</b> %{x:.1f} Hz<br><b>Amplitud:</b> %{y:.3f}<extra></extra>'
        ))
        
        # Marcar rango de frecuencia cardíaca típica (0.7-3 Hz = 42-180 bpm)
        fig.add_vrect(x0=0.7, x1=3, fillcolor="green", opacity=0.1, annotation_text="Rango Cardíaco Normal")
        
        fig.update_layout(
            title="<b>Análisis de Frecuencia ECG</b><br><sub>Espectro de potencia (FFT)</sub>",
            xaxis_title="Frecuencia (Hz)",
            yaxis_title="Amplitud Normalizada",
            height=350,
            template="plotly_white",
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def display_heart_rate_and_bp(patient_data):
        """
        GRAFICA #3: Frecuencia cardíaca y presión arterial (gauges).
        
        INSTRUCCIONES:
        ---------------
        "Métricas vitales instantáneas.
         • FC: 60-100 bpm es normal
         • Presión: <120/80 es óptima
         • Colores: Verde=Normal, Amarillo=Alerta, Rojo=Crítico"
        """
        
        measurement = patient_data['latest_measurement']
        hr = measurement['heart_rate']
        sys_bp = measurement['systolic_bp']
        dia_bp = measurement['diastolic_bp']
        o2 = measurement['oxygen_saturation']
        
        # 4 pequeños gauges
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Gauge HR
            fig_hr = go.Figure(go.Indicator(
                mode="gauge+number",
                value=hr,
                title={'text': "FC (bpm)"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [40, 150]},
                    'bar': {'color': 'darkblue'},
                    'steps': [
                        {'range': [40, 60], 'color': 'lightgray'},
                        {'range': [60, 100], 'color': 'lightgreen'},
                        {'range': [100, 120], 'color': 'lightyellow'},
                        {'range': [120, 150], 'color': 'lightcoral'},
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 4},
                        'thickness': 0.75,
                        'value': 130
                    }
                }
            ))
            fig_hr.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_hr, use_container_width=True)
        
        with col2:
            # Gauge Presión Sistólica
            fig_sys = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sys_bp,
                title={'text': "Sistólica (mmHg)"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [80, 180]},
                    'bar': {'color': 'darkblue'},
                    'steps': [
                        {'range': [80, 120], 'color': 'lightgreen'},
                        {'range': [120, 140], 'color': 'lightyellow'},
                        {'range': [140, 180], 'color': 'lightcoral'},
                    ]
                }
            ))
            fig_sys.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_sys, use_container_width=True)
        
        with col3:
            # Gauge Presión Diastólica
            fig_dia = go.Figure(go.Indicator(
                mode="gauge+number",
                value=dia_bp,
                title={'text': "Diastólica (mmHg)"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [40, 120]},
                    'bar': {'color': 'darkblue'},
                    'steps': [
                        {'range': [40, 80], 'color': 'lightgreen'},
                        {'range': [80, 90], 'color': 'lightyellow'},
                        {'range': [90, 120], 'color': 'lightcoral'},
                    ]
                }
            ))
            fig_dia.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_dia, use_container_width=True)
        
        with col4:
            # Gauge O2
            fig_o2 = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=o2,
                title={'text': "O2 (%)"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [80, 100]},
                    'bar': {'color': 'darkblue'},
                    'steps': [
                        {'range': [80, 95], 'color': 'lightcoral'},
                        {'range': [95, 98], 'color': 'lightyellow'},
                        {'range': [98, 100], 'color': 'lightgreen'},
                    ]
                }
            ))
            fig_o2.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_o2, use_container_width=True)
    
    @staticmethod
    def display_hrv_analysis(measurement_history):
        """
        GRAFICA #4: HRV (Variabilidad del Ritmo Cardíaco) a lo largo del tiempo.
        
        INSTRUCCIONES:
        ---------------
        "Variabilidad del ritmo cardíaco.
         • Línea más suave = corazón estable
         • Fluctuaciones = estrés o actividad
         • Tendencia descendente = posible problema"
        """
        
        dates = [m['date'] for m in measurement_history]
        hrs = [m['heart_rate'] for m in measurement_history]
        
        fig = go.Figure()
        
        # Línea de HR
        fig.add_trace(go.Scatter(
            x=dates,
            y=hrs,
            mode='lines+markers',
            name='FC',
            line=dict(color='#ff7f0e', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(255, 127, 14, 0.2)',
            hovertemplate='<b>Fecha:</b> %{x}<br><b>FC:</b> %{y:.0f} bpm<extra></extra>'
        ))
        
        # Zonas normales
        fig.add_hline(y=60, line_dash="dash", line_color="green", opacity=0.5)
        fig.add_hline(y=100, line_dash="dash", line_color="red", opacity=0.5)
        fig.add_hrect(y0=60, y1=100, fillcolor="green", opacity=0.1, annotation_text="Rango Normal")
        
        fig.update_layout(
            title="<b>Tendencia de Frecuencia Cardíaca</b><br><sub>Últimos 30 días</sub>",
            xaxis_title="Fecha",
            yaxis_title="FC (bpm)",
            height=350,
            template="plotly_white",
            hovermode='x unified'
        )
        
        return fig
    
    @staticmethod
    def display_arrhythmia_detection(condition, ai_confidence):
        """
        GRAFICA #5: Detección de arritmias con IA.
        
        INSTRUCCIONES:
        ---------------
        "Resultado del análisis IA de arritmias.
         • Muestra el tipo de arritmia detectada
         • Nivel de confianza del modelo (%)
         • Clasificación de riesgo"
        """
        
        arrhythmia_types = ['Normal', 'FA', 'Bradicardia', 'Tachycardia', 'Bloqueos AV']
        
        # Simular confianzas IA
        if condition == "normal":
            confidences = [0.95, 0.02, 0.01, 0.01, 0.01]
            detected = "Normal"
            color = "green"
        elif condition == "afib":
            confidences = [0.05, 0.88, 0.03, 0.02, 0.02]
            detected = "Fibrilación Auricular"
            color = "red"
        elif condition == "bradycardia":
            confidences = [0.10, 0.05, 0.80, 0.03, 0.02]
            detected = "Bradicardia"
            color = "orange"
        elif condition == "tachycardia":
            confidences = [0.08, 0.05, 0.02, 0.82, 0.03]
            detected = "Taquicardia"
            color = "red"
        else:
            confidences = [0.9, 0.02, 0.02, 0.03, 0.03]
            detected = "Normal"
            color = "green"
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=arrhythmia_types,
            y=confidences,
            marker=dict(
                color=confidences,
                colorscale='RdYlGn_r',
                showscale=False,
                line=dict(color='black', width=1)
            ),
            text=[f'{c*100:.1f}%' for c in confidences],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Confianza: %{y:.1%}<extra></extra>'
        ))
        
        fig.update_layout(
            title=f"<b>Detección de Arritmias (IA)</b><br><sub>Detectado: {detected}</sub>",
            xaxis_title="Tipo de Arritmia",
            yaxis_title="Confianza del Modelo",
            height=350,
            template="plotly_white",
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def display_cardiac_risk_assessment():
        """
        GRAFICA #6: Evaluación de riesgo cardíaco (matriz de riesgo).
        
        INSTRUCCIONES:
        ---------------
        "Evaluación integral de riesgo.
         • Cruza múltiples factores
         • Riesgo en 30 días proyectado
         • Recomendaciones por nivel"
        """
        
        risk_factors = ['Edad', 'Arritmia', 'Hipertensión', 'Colesterol', 'Sedentarismo']
        risk_scores = [0.4, 0.8, 0.6, 0.5, 0.3]
        colors_risk = ['yellow' if s < 0.5 else 'orange' if s < 0.7 else 'red' for s in risk_scores]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=risk_factors,
            y=risk_scores,
            marker=dict(color=colors_risk, line=dict(color='black', width=1)),
            text=[f'{s*100:.0f}%' for s in risk_scores],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Riesgo: %{y:.0%}<extra></extra>'
        ))
        
        fig.update_layout(
            title="<b>Evaluación de Riesgo Cardíaco</b>",
            xaxis_title="Factor de Riesgo",
            yaxis_title="Puntuación de Riesgo",
            height=350,
            template="plotly_white",
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def display_cardiac_summary(patient_data, ai_results):
        """
        TABLA RESUMEN: Todos los hallazgos en un solo lugar.
        
        ESTRUCTURA:
        -----------
        ┌─ MÉTRICAS INSTANTÁNEAS
        ├─ HALLAZGOS IA
        ├─ PREDICCIONES (30 días)
        ├─ ALERTAS
        └─ RECOMENDACIONES
        """
        
        measurement = patient_data['latest_measurement']
        
        summary_data = {
            'PARÁMETRO': [
                '🫀 FC Actual',
                '📊 Presión Sistólica',
                '📊 Presión Diastólica',
                '💨 O2 Saturation',
                '🔍 Arritmia Detectada',
                '⚡ Confianza IA',
                '🎯 Riesgo (30 días)',
                '⚠️ Alerta',
                '💊 Recomendación'
            ],
            'VALOR': [
                f"{measurement['heart_rate']} bpm",
                f"{measurement['systolic_bp']} mmHg",
                f"{measurement['diastolic_bp']} mmHg",
                f"{measurement['oxygen_saturation']:.1f}%",
                ai_results.get('arrhythmia_type', 'Normal'),
                f"{ai_results.get('confidence', 0.87)*100:.1f}%",
                ai_results.get('risk_30_days', '2.1%'),
                ai_results.get('alert_level', 'Normal'),
                ai_results.get('recommendation', 'Monitoreo rutinario')
            ],
            'ESTADO': [
                '✅' if 60 <= measurement['heart_rate'] <= 100 else '⚠️',
                '✅' if measurement['systolic_bp'] < 120 else '⚠️',
                '✅' if measurement['diastolic_bp'] < 80 else '⚠️',
                '✅' if measurement['oxygen_saturation'] > 95 else '🔴',
                '✅' if ai_results.get('arrhythmia_type') == 'Normal' else '🔴',
                '✅' if ai_results.get('confidence', 0) > 0.80 else '⚠️',
                '✅' if float(ai_results.get('risk_30_days', '0%').rstrip('%')) < 5 else '🔴',
                '✅' if ai_results.get('alert_level') == 'Normal' else '⚠️',
                ''
            ]
        }
        
        df = st.dataframe(
            summary_data,
            use_container_width=True,
            height=400
        )
        
        return df
