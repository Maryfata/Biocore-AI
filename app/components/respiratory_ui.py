"""
COMPONENTES UI PARA RESPIRATORIO
================================
Visualizaciones de fisiología respiratoria, métricas de ventilación y gasometría.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np


class RespiratoryUI:
    """Componentes de interfaz para el dominio respiratorio."""

    @staticmethod
    def display_respiratory_waveform(resp_data):
        signal = resp_data.get('signal', np.zeros(1))
        time = resp_data.get('time', np.arange(len(signal)))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time,
            y=signal,
            mode='lines',
            name='Respiratory Signal',
            line=dict(color='#1f77b4', width=2),
            hovertemplate='<b>Time:</b> %{x:.1f}s<br><b>Amplitude:</b> %{y:.2f}<extra></extra>'
        ))
        fig.update_layout(
            title='<b>Señal Respiratoria</b><br><sub>Frecuencia respiratoria y volumen relativo</sub>',
            xaxis_title='Tiempo (s)',
            yaxis_title='Amplitud relativa',
            height=360,
            template='plotly_white',
            hovermode='x unified'
        )
        return fig

    @staticmethod
    def display_respiratory_metrics(resp_data):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Frecuencia Respiratoria', f"{resp_data.get('respiratory_rate', 0):.0f} resp/min")
        col2.metric('Volumen Tidal', f"{resp_data.get('tidal_volume', 0):.0f} mL")
        col3.metric('O2 Saturación', f"{resp_data.get('oxygen_saturation', 0):.0f}%")
        col4.metric('Calidad Ventilación', f"{resp_data.get('ventilation_quality', 0):.0f}%")

    @staticmethod
    def display_gas_exchange_assessment(resp_data):
        spo2 = resp_data.get('oxygen_saturation', 0)
        ventilation = resp_data.get('ventilation_quality', 0)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['SpO2', 'Ventilation Quality'],
            y=[spo2, ventilation],
            marker=dict(color=['#2ca02c' if spo2 >= 95 else '#ff7f0e', '#1f77b4']),
            text=[f'{spo2:.0f}%', f'{ventilation:.0f}%'],
            textposition='auto'
        ))
        fig.update_layout(
            title='<b>Evaluación de Intercambio Gaseoso</b>',
            yaxis=dict(range=[0, 100], title='Porcentaje'),
            height=340,
            template='plotly_white'
        )
        return fig

    @staticmethod
    def display_respiratory_summary(patient_data, ai_results):
        measurement = patient_data['latest_measurement']
        summary_data = {
            'PARÁMETRO': [
                '💨 Frecuencia Respiratoria',
                '🌬️ Volumen Tidal',
                '🩸 SpO2',
                '📈 Calidad de Ventilación',
                '⚠️ Patrón Respiratorio',
                '🎯 Recomendación'
            ],
            'VALOR': [
                f"{measurement.get('respiratory_rate', 0):.0f} resp/min",
                f"{measurement.get('tidal_volume', 0):.0f} mL",
                f"{measurement.get('oxygen_saturation', 0):.0f}%",
                f"{measurement.get('ventilation_quality', 0):.0f}%",
                ai_results.get('respiratory_pattern', 'Normal'),
                ai_results.get('recommendation', 'Monitoreo respiratorio')
            ],
            'ESTADO': [
                '✅' if 12 <= measurement.get('respiratory_rate', 0) <= 20 else '⚠️',
                '✅' if 400 <= measurement.get('tidal_volume', 0) <= 600 else '⚠️',
                '✅' if measurement.get('oxygen_saturation', 0) >= 95 else '🔴',
                '✅' if measurement.get('ventilation_quality', 0) >= 80 else '⚠️',
                '✅' if ai_results.get('respiratory_pattern', 'Normal') == 'Normal' else '⚠️',
                ''
            ]
        }
        st.dataframe(summary_data, use_container_width=True, height=320)
