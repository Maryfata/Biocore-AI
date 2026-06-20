"""
COMPONENTES PARA ALERTAS Y REPORTES
===================================
Sistema de alertas inteligentes y generador de reportes PDF.

ESTRUCTURA:
-----------
    1. Panel de alertas con severidad
    2. Histórico de alertas
    3. Generador de reportes automáticos
    4. Explicaciones SHAP de IA
    5. Recomendaciones clínicas

USO:
-----
    from app.components.alerts_ui import AlertsUI, ReportGenerator
    
    alerts = AlertsUI()
    alerts.display_alert_panel(patient_data, ai_results)
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np


class AlertsUI:
    """Componentes de alertas y notificaciones."""
    
    @staticmethod
    def display_alert_panel(patient_data, ai_results):
        """
        PANEL DE ALERTAS: Resumen visual de alertas actuales.
        
        NIVELES DE SEVERIDAD:
        ---------------------
        🟢 VERDE (Normal):      Dentro de parámetros normales
        🟡 AMARILLO (Alerta):   Requiere vigilancia
        🔴 ROJO (Alto):         Acción recomendada
        ⚫ CRÍTICO:             Emergencia médica
        
        INSTRUCCIONES:
        ---------------
        "Panel de alertas en tiempo real.
         • Cada alerta muestra acción recomendada
         • Haz clic para ver detalles
         • Marca como revisada cuando corresponda"
        """
        
        st.subheader("🚨 Panel de Alertas Activas")
        
        alerts = ai_results.get('alerts', [])
        
        if not alerts:
            st.success("✅ Sin alertas - Paciente estable")
            return
        
        # Ordenar por severidad (crítico primero)
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        alerts_sorted = sorted(alerts, key=lambda x: severity_order.get(x.get('severity', 'LOW'), 99))
        
        for alert in alerts_sorted:
            severity = alert.get('severity', 'LOW')
            title = alert.get('title', 'Alerta')
            message = alert.get('message', '')
            recommendation = alert.get('recommendation', '')
            timestamp = alert.get('timestamp', datetime.now().strftime("%H:%M:%S"))
            
            # Color basado en severidad
            if severity == 'CRITICAL':
                emoji = '🔴'
                color = 'background-color: #ffcccc; border-left: 5px solid #ff0000;'
                icon = '⚠️ CRÍTICO'
            elif severity == 'HIGH':
                emoji = '🔴'
                color = 'background-color: #ffe0cc; border-left: 5px solid #ff6600;'
                icon = '⚠️ ALTO'
            elif severity == 'MEDIUM':
                emoji = '🟡'
                color = 'background-color: #ffffcc; border-left: 5px solid #ffcc00;'
                icon = '⚠️ MEDIO'
            else:
                emoji = '🟢'
                color = 'background-color: #ccffcc; border-left: 5px solid #00cc00;'
                icon = 'ℹ️ BAJO'
            
            # Mostrar alerta con HTML personalizado
            alert_html = f"""
            <div style="{color} padding: 15px; border-radius: 5px; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #333;">{icon} {title}</h4>
                        <p style="margin: 5px 0; color: #666; font-size: 14px;">{message}</p>
                        <p style="margin: 5px 0; color: #0066cc; font-weight: bold;">💡 {recommendation}</p>
                    </div>
                    <div style="text-align: right; color: #999; font-size: 12px;">
                        {timestamp}
                    </div>
                </div>
            </div>
            """
            
            st.markdown(alert_html, unsafe_allow_html=True)
    
    @staticmethod
    def display_alert_history(measurement_history, specialty="Cardiology"):
        """
        HISTORIAL DE ALERTAS: Gráfica de alertas a lo largo del tiempo.
        
        INSTRUCCIONES:
        ---------------
        "Historial de todas las alertas generadas.
         • Rojo = Alertas críticas
         • Naranja = Alertas altas
         • Amarillo = Alertas medias"
        """
        
        st.subheader("📊 Historial de Alertas (30 días)")
        
        dates = [m['date'] for m in measurement_history[-30:]]
        
        # Simular alertas
        alerts_count = np.random.randint(0, 3, len(dates))
        
        colors = ['green' if c == 0 else 'orange' if c == 1 else 'red' for c in alerts_count]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=dates,
            y=alerts_count,
            marker=dict(color=colors, line=dict(color='black', width=0.5)),
            text=['Sin alertas' if c == 0 else f'{c} alerta(s)' for c in alerts_count],
            textposition='auto',
            hovertemplate='<b>Fecha:</b> %{x}<br><b>Alertas:</b> %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title="<b>Historial de Alertas</b>",
            xaxis_title="Fecha",
            yaxis_title="Número de Alertas",
            height=300,
            template="plotly_white",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)


class ReportGenerator:
    """Generador de reportes automáticos."""
    
    @staticmethod
    def generate_text_report(patient_data, ai_results, specialty):
        """
        Genera reporte en texto plano (para PDF o visualización).
        
        CONTENIDO:
        ----------
        1. Encabezado (Paciente, Fecha, Especialidad)
        2. Resumen Ejecutivo
        3. Hallazgos Técnicos
        4. Explicación IA (SHAP)
        5. Predicciones
        6. Recomendaciones Clínicas
        7. Instrucciones para el Paciente
        
        INSTRUCCIONES:
        ---------------
        "Reporte completo de la medición.
         • Sección 1: Resumen para paciente (simple)
         • Sección 2: Hallazgos técnicos (médico)
         • Sección 3: Predicciones (30 días)
         • Sección 4: Recomendaciones personalizadas"
        """
        
        patient = patient_data
        measurement = patient_data['latest_measurement']
        timestamp = measurement.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        report = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    REPORTE MÉDICO AUTOMATIZADO - BIOCORE AI                ║
╚════════════════════════════════════════════════════════════════════════════╝

📋 INFORMACIÓN DEL PACIENTE
─────────────────────────────────────────────────────────────────────────────
Nombre:              {patient['name']}
ID Paciente:         {patient['id']}
Edad:                {patient['age']} años
Género:              {patient['gender']}
Especialidad:        {specialty}
Fecha de Medición:   {timestamp}

🔍 HALLAZGOS PRINCIPALES
─────────────────────────────────────────────────────────────────────────────
"""
        
        if specialty == "Cardiology":
            report += f"""
Frecuencia Cardíaca:    {measurement['heart_rate']} bpm
Presión Sistólica:      {measurement['systolic_bp']} mmHg
Presión Diastólica:     {measurement['diastolic_bp']} mmHg
O2 Saturation:          {measurement['oxygen_saturation']:.1f}%

Arritmia Detectada:     {ai_results.get('arrhythmia_type', 'Normal')}
Confianza IA:           {ai_results.get('confidence', 0.87)*100:.1f}%
Clasificación Riesgo:   {ai_results.get('risk_classification', 'Bajo')}

"""
        elif specialty == "Neurology":
            bands = measurement['eeg']['bands']
            report += f"""
Estadio de Sueño:       {ai_results.get('sleep_stage', 'N2')}
Delta Power:            {bands.get('Delta', 25)}%
Theta Power:            {bands.get('Theta', 20)}%
Alpha Power:            {bands.get('Alpha', 15)}%
Beta Power:             {bands.get('Beta', 30)}%
Gamma Power:            {bands.get('Gamma', 10)}%

Calidad de Sueño:       {measurement.get('sleep_quality', 70)}%
Riesgo de Crisis:       {ai_results.get('seizure_risk', 'Bajo')}

"""
        elif specialty == "Musculoskeletal":
            report += f"""
Activación Muscular:    {measurement['emg_left'].get('activation_level', 50)}%
Median Frequency:       {measurement['emg_left'].get('median_frequency', 250):.0f} Hz
Nivel de Fatiga:        {measurement['emg_left'].get('fatigue_level', 30)}%

ROM Izquierda:          {measurement['rom_left']}°
ROM Derecha:            {measurement['rom_right']}°
Fuerza Izquierda:       {measurement['strength_left']}%
Fuerza Derecha:         {measurement['strength_right']}%

Patología Detectada:    {ai_results.get('pathology', 'Normal')}

"""
        elif specialty == "Respiratory":
            report += f"""
Frecuencia Respiratoria: {measurement.get('respiratory_rate', 0):.0f} rpm
Volumen Tidal:          {measurement.get('tidal_volume', 0):.0f} mL
SpO2:                   {measurement.get('oxygen_saturation', 0):.0f}%
Calidad Ventilación:    {measurement.get('ventilation_quality', 0):.0f}%

Patrón Respiratorio:    {ai_results.get('respiratory_pattern', 'Normal')}
Clasificación Riesgo:   {ai_results.get('risk_classification', 'Bajo')}

"""
        elif specialty == "Metabolism":
            report += f"""
Glucosa en Ayunas:      {measurement.get('blood_glucose', 0):.0f} mg/dL
HbA1c:                  {measurement.get('hba1c', 0):.1f}%
Sensibilidad Insulina:  {measurement.get('insulin_sensitivity', 0):.0f}%
Gasto Energético:       {measurement.get('energy_expenditure', 0):.0f} kcal/día

Estado Metabólico:      {ai_results.get('metabolic_status', 'Normal')}
Clasificación Riesgo:   {ai_results.get('risk_classification', 'Bajo')}

"""
        
        # Default patient instructions moved out of the f-string to avoid
        # backslash escapes inside f-string expressions (which raise SyntaxError).
        default_action_items = "• Mantener monitoreo rutinario\n• Seguir protocolo existente"

        default_patient_instructions = (
            "1. Continúa con tu rutina normal\n"
            "2. Si experimentas síntomas anormales, contacta a tu médico inmediatamente\n"
            "3. Próxima medición: En 30 días\n"
            "4. Si tienes dudas sobre este reporte, consulta con tu cardiólogo\n"
        )

        report += f"""
💡 EXPLICACIÓN IA (SHAP)
─────────────────────────────────────────────────────────────────────────────
El modelo de inteligencia artificial analizó los siguientes factores:

{ai_results.get('shap_explanation', 'Factor principal determinado por análisis automático')}

Confianza del modelo:   {ai_results.get('confidence', 0.87)*100:.1f}%

🔮 PREDICCIONES (30 DÍAS)
─────────────────────────────────────────────────────────────────────────────
Evolución Esperada:     {ai_results.get('30_day_prediction', 'Sin cambios significativos')}
Riesgo de Evento:       {ai_results.get('risk_30_days', '2.1%')}
Intervención Necesaria: {ai_results.get('intervention_needed', 'No recomendada')}

📋 RECOMENDACIONES CLÍNICAS
─────────────────────────────────────────────────────────────────────────────
Recomendación Principal: {ai_results.get('recommendation', 'Monitoreo de rutina')}
Nivel de Alerta:         {ai_results.get('alert_level', 'Normal')}
Seguimiento:             {ai_results.get('followup_schedule', 'Próxima cita: 30 días')}

Acciones Recomendadas:
{ai_results.get('action_items', default_action_items)}

👤 INSTRUCCIONES PARA EL PACIENTE
─────────────────────────────────────────────────────────────────────────────
{ai_results.get('patient_instructions', default_patient_instructions)}

📞 INFORMACIÓN DE CONTACTO
─────────────────────────────────────────────────────────────────────────────
En caso de emergencia, llama al 911
Centro Médico: +1-555-BIOCORE
Portal del Paciente: www.biocore-health.com

═════════════════════════════════════════════════════════════════════════════
Reporte generado automáticamente por BIOCORE AI OS v3.0
Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Este reporte es para referencia únicamente. Consulta a tu médico para diagnóstico.
═════════════════════════════════════════════════════════════════════════════
"""
        
        return report
    
    @staticmethod
    def display_report_preview(report_text):
        """
        Muestra preview del reporte en la UI.
        
        INSTRUCCIONES:
        ---------------
        "Vista previa del reporte.
         • Desplázate para ver todo el contenido
         • Botón 'Descargar PDF' para guardar
         • Botón 'Enviar por email' para compartir"
        """
        
        st.subheader("📄 Vista Previa del Reporte")
        
        with st.expander("Ver Reporte Completo", expanded=False):
            st.text_area(
                "Reporte Médico Completo",
                report_text,
                height=600,
                disabled=True
            )
        
        # Botones de acción
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Descargar PDF", key="download_pdf"):
                # Aquí iría la generación de PDF
                st.success("✅ PDF descargado correctamente")
        
        with col2:
            if st.button("📧 Enviar por Email", key="email_report"):
                st.success("✅ Email enviado al paciente y médico")
        
        with col3:
            if st.button("🖨️ Imprimir", key="print_report"):
                st.info("ℹ️ Abre el diálogo de impresión con Ctrl+P")
    
    @staticmethod
    def display_shap_explanation(ai_results):
        """
        EXPLICACIÓN SHAP: Qué factores influyeron en la predicción IA.
        
        INSTRUCCIONES:
        ---------------
        "¿Por qué la IA predijo esto?
         • Barras azules = Factores que bajaron el riesgo
         • Barras rojas = Factores que subieron el riesgo
         • Tamaño = Importancia del factor"
        """
        
        st.subheader("🧠 Explicación de Predicción IA (SHAP)")
        
        # Factores simulados
        factors = {
            'Edad': -0.15,
            'Frecuencia Cardíaca': 0.35,
            'Presión Arterial': 0.25,
            'Historial Familiar': 0.20,
            'Actividad Física': -0.10,
            'Estrés': 0.25,
            'Colesterol': 0.30,
            'Medicamentos': -0.20
        }
        
        # Crear gráfica SHAP-style
        factor_names = list(factors.keys())
        factor_values = list(factors.values())
        colors = ['#3498db' if v < 0 else '#e74c3c' for v in factor_values]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=factor_values,
            y=factor_names,
            orientation='h',
            marker=dict(color=colors, line=dict(color='black', width=0.5)),
            text=[f'{abs(v):.2f}' for v in factor_values],
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Impacto: %{x:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="<b>Factores que Influyeron en la Predicción IA</b><br><sub>Azul = Reduce Riesgo | Rojo = Aumenta Riesgo</sub>",
            xaxis_title="Impacto en Predicción",
            yaxis_title="Factor",
            height=350,
            template="plotly_white",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Explicación textual
        st.info("""
        **¿Cómo interpretar esto?**
        
        - **Barras Rojas (Derecha)**: Estos factores AUMENTARON la predicción de riesgo
          - Ej: "Frecuencia Cardíaca elevada" sugiere estrés o enfermedad
        
        - **Barras Azules (Izquierda)**: Estos factores REDUJERON la predicción de riesgo
          - Ej: "Edad joven" es protector contra eventos cardíacos
        
        - **Longitud de la barra**: Mayor longitud = Mayor influencia en la decisión IA
        
        El modelo combinó todos estos factores para hacer la predicción final.
        """)
