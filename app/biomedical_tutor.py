"""Interactive AI Tutor Chatbot for BIOCORE AI."""

import streamlit as st
from typing import List, Dict, Any
import json
import os

BIOCORE_KNOWLEDGE_BASE = {
    'ECG': {
        'basics': 'El ECG mide la actividad eléctrica del corazón. Tiene ondas P (aurículas), QRS (ventrículos) y T (repolarización).',
        'interpretation': 'Busca anomalías en duración, amplitud y forma de las ondas. La frecuencia normal es 60-100 bpm.',
        'clinical': 'Arritmias, isquemia, infarto y cambios electrolíticos son hallazgos clínicos comunes.',
    },
    'EEG': {
        'basics': 'El EEG mide la actividad eléctrica del cerebro en bandas: delta, theta, alfa, beta y gamma.',
        'interpretation': 'Busca patrones normales y anormalidades como picos-ondas o desorganización.',
        'clinical': 'Epilepsia, encefalopatía, coma y trastornos del sueño son aplicaciones clínicas.',
    },
    'SpO2': {
        'basics': 'La saturación de oxígeno mide qué porcentaje de hemoglobina está cargada de O2. Normal es >95%.',
        'interpretation': 'SpO2 <90% sugiere hipoxemia. <80% es crítico.',
        'clinical': 'EPOC, neumonía, tromboembolismo pulmonar y apnea del sueño afectan SpO2.',
    },
    'HRV': {
        'basics': 'La variabilidad de la frecuencia cardíaca refleja el balance autonómico. Mayor HRV = mejor recuperación.',
        'interpretation': 'HRV baja sugiere estrés crónico. HRV alta indica buena adaptabilidad.',
        'clinical': 'Diabetes, depresión y enfermedades cardiovasculares se asocian con baja HRV.',
    },
    'Digital Twin': {
        'basics': 'Un gemelo digital es una representación viva del estado fisiológico que actualiza en tiempo real.',
        'simulation': 'Permite manipular variables (HR, respiración, SpO2) y ver cómo responde todo el organismo.',
        'education': 'Los estudiantes aprenden viendo causas y efectos multisistémicos al instante.',
    }
}

class BiomedicalTutor:
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.learning_topics: List[str] = []
        self.current_topic: str = ''

    def answer_question(self, question: str) -> str:
        question_lower = question.lower()
        
        if 'ecg' in question_lower:
            self.current_topic = 'ECG'
            if 'basico' in question_lower or 'basic' in question_lower or 'qué es' in question_lower:
                return BIOCORE_KNOWLEDGE_BASE['ECG']['basics']
            elif 'interpretación' in question_lower or 'interpret' in question_lower:
                return BIOCORE_KNOWLEDGE_BASE['ECG']['interpretation']
            elif 'clínica' in question_lower or 'clinical' in question_lower:
                return BIOCORE_KNOWLEDGE_BASE['ECG']['clinical']
            else:
                return BIOCORE_KNOWLEDGE_BASE['ECG']['basics']
        
        elif 'eeg' in question_lower:
            self.current_topic = 'EEG'
            if 'basico' in question_lower or 'basic' in question_lower or 'qué es' in question_lower:
                return BIOCORE_KNOWLEDGE_BASE['EEG']['basics']
            elif 'interpretación' in question_lower or 'interpret' in question_lower:
                return BIOCORE_KNOWLEDGE_BASE['EEG']['interpretation']
            elif 'clínica' in question_lower or 'clinical' in question_lower:
                return BIOCORE_KNOWLEDGE_BASE['EEG']['clinical']
            else:
                return BIOCORE_KNOWLEDGE_BASE['EEG']['basics']
        
        elif 'spo2' in question_lower or 'oxigenación' in question_lower or 'saturación' in question_lower:
            self.current_topic = 'SpO2'
            return BIOCORE_KNOWLEDGE_BASE['SpO2']['basics'] + ' ' + BIOCORE_KNOWLEDGE_BASE['SpO2']['interpretation']
        
        elif 'hrv' in question_lower or 'variabilidad' in question_lower:
            self.current_topic = 'HRV'
            return BIOCORE_KNOWLEDGE_BASE['HRV']['basics'] + ' ' + BIOCORE_KNOWLEDGE_BASE['HRV']['interpretation']
        
        elif 'gemelo' in question_lower or 'digital twin' in question_lower:
            self.current_topic = 'Digital Twin'
            return BIOCORE_KNOWLEDGE_BASE['Digital Twin']['basics'] + ' ' + BIOCORE_KNOWLEDGE_BASE['Digital Twin']['simulation']
        
        else:
            return ('No tengo información específica sobre ese tema. Puedo ayudarte con: ECG, EEG, SpO2, HRV, Digital Twin, '
                    'o cualquier aspecto de fisiología cardíaca, neurológica o respiratoria. ¿Qué te gustaría aprender?')

    def generate_exercise(self, topic: str = '') -> Dict[str, Any]:
        if not topic:
            topic = self.current_topic or 'ECG'
        
        exercises = {
            'ECG': {
                'question': '¿Cuál es la duración normal del intervalo PR en un ECG?',
                'options': ['0.12-0.20 segundos', '0.04-0.12 segundos', '0.20-0.40 segundos'],
                'correct': 0,
                'explanation': 'El intervalo PR normal es 0.12-0.20 segundos (3-5 cuadrículas pequeñas).'
            },
            'EEG': {
                'question': '¿A qué rango de frecuencia corresponden las ondas alfa?',
                'options': ['0.5-4 Hz', '8-12 Hz', '13-30 Hz'],
                'correct': 1,
                'explanation': 'Las ondas alfa están en el rango 8-12 Hz, típicas de vigilia relajada.'
            },
            'SpO2': {
                'question': '¿Cuál es la saturación de oxígeno crítica?',
                'options': ['<95%', '<90%', '<80%'],
                'correct': 2,
                'explanation': 'Una SpO2 < 80% es crítica y requiere intervención inmediata.'
            }
        }
        
        return exercises.get(topic, exercises['ECG'])

    def render_chat(self):
        st.markdown("### 🤖 Tutor IA Biomédico — Chatbot Interactivo")
        st.markdown("Hazme preguntas sobre ECG, EEG, SpO2, HRV, gemelos digitales o fisiología clínica.")
        
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.chat_message("user").write(message['content'])
            else:
                st.chat_message("assistant").write(message['content'])
        
        user_input = st.chat_input("Escribe tu pregunta...")
        if user_input:
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            response = self.answer_question(user_input)
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Generar ejercicio"):
                exercise = self.generate_exercise()
                st.markdown(f"**Pregunta:** {exercise['question']}")
                selected = st.radio("Opciones:", exercise['options'], key='exercise_radio')
                if st.button("Verificar respuesta"):
                    if exercise['options'].index(selected) == exercise['correct']:
                        st.success(f"✅ ¡Correcto! {exercise['explanation']}")
                    else:
                        st.error(f"❌ Incorrecto. {exercise['explanation']}")
        
        with col2:
            if st.button("🎯 Mostrar temas"):
                st.markdown("**Temas disponibles:**")
                topics = ['ECG', 'EEG', 'SpO2', 'HRV', 'Digital Twin']
                for topic in topics:
                    st.write(f"- {topic}")
