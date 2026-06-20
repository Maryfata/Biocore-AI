"""
COMPONENTES UI PARA METABOLISMO
================================
Visualizaciones de estado metabólico, glucosa y energía.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np


class MetabolismUI:
    """Componentes de interfaz para el dominio metabólico."""

    @staticmethod
    def display_metabolic_profile(metabolic):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Glucosa en Ayunas', f"{metabolic.get('blood_glucose', 0):.0f} mg/dL")
        col2.metric('HbA1c', f"{metabolic.get('hba1c', 0):.1f}%")
        col3.metric('Sensibilidad a Insulina', f"{metabolic.get('insulin_sensitivity', 0):.0f}%")
        col4.metric('Gasto Energético', f"{metabolic.get('energy_expenditure', 0):.0f} kcal/día")

    @staticmethod
    def display_metabolic_risk_chart(metabolic):
        risks = {
            'Hiperglucemia': max(0, metabolic.get('blood_glucose', 0) - 100),
            'Resistencia Insulina': max(0, 70 - metabolic.get('insulin_sensitivity', 0)),
            'HbA1c Alta': max(0, metabolic.get('hba1c', 0) - 5.7)
        }
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(risks.keys()),
            y=list(risks.values()),
            marker=dict(color=['#e74c3c', '#f39c12', '#c0392b']),
            text=[f"{v:.1f}" for v in risks.values()],
            textposition='auto'
        ))
        fig.update_layout(
            title='<b>Riesgo Metabólico</b>',
            yaxis=dict(title='Índice de Riesgo', range=[0, max(20, max(risks.values()) + 5)]),
            height=360,
            template='plotly_white'
        )
        return fig

    @staticmethod
    def display_metabolic_summary(patient_data, ai_results):
        metabolic = patient_data['latest_measurement'].get('metabolic_profile', {})
        summary_data = {
            'PARÁMETRO': [
                '🩸 Glucosa en Ayunas',
                '📈 HbA1c',
                '⚡ Sensibilidad a Insulina',
                '🔥 Gasto Energético',
                '🔍 Estado Metabólico',
                '🎯 Recomendación'
            ],
            'VALOR': [
                f"{metabolic.get('blood_glucose', 0):.0f} mg/dL",
                f"{metabolic.get('hba1c', 0):.1f}%",
                f"{metabolic.get('insulin_sensitivity', 0):.0f}%",
                f"{metabolic.get('energy_expenditure', 0):.0f} kcal/día",
                ai_results.get('metabolic_status', 'Normal'),
                ai_results.get('recommendation', 'Mantener hábitos saludables')
            ],
            'ESTADO': [
                '✅' if 70 <= metabolic.get('blood_glucose', 0) <= 99 else '⚠️',
                '✅' if metabolic.get('hba1c', 0) < 5.7 else '⚠️',
                '✅' if metabolic.get('insulin_sensitivity', 0) >= 65 else '⚠️',
                '✅' if metabolic.get('energy_expenditure', 0) >= 1700 else '⚠️',
                '✅' if ai_results.get('metabolic_status') == 'Normal' else '⚠️',
                ''
            ]
        }
        st.dataframe(summary_data, use_container_width=True, height=320)
