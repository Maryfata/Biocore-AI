"""Academia Clínica Digital: UI para lecciones, quizzes y casos clínicos."""
from __future__ import annotations
import streamlit as st
from typing import Dict

from educational.learning_engine import LearningEngine, generate_quiz
from educational.clinical_cases import sample_cases
from educational.ecg_academy import generate_synthetic_ecg

PROJECT_ROOT = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__)))
try:
    from app.supermodules import render_sidebar_navigation
except Exception:
    # fallback minimal implementation
    def render_sidebar_navigation():
        st.sidebar.markdown('### Navegación')


st.set_page_config(page_title='Academia Clínica', layout='wide')
render_sidebar_navigation()

st.title('🏫 Academia Clínica Digital')
st.markdown('Plataforma educativa: lecciones interactivas, quizzes y casos clínicos.')

student_id = st.text_input('ID del estudiante', value='estudiante_demo')
# Modo Rural: persistencia local
rural_mode_enabled = st.checkbox('Modo Rural (offline, guardar progreso localmente)', value=False)

engine = st.session_state.get('learning_engine')
if engine is None or getattr(engine, 'student_id', None) != student_id:
    engine = LearningEngine(student_id=student_id)
    st.session_state['learning_engine'] = engine
    # If rural mode is enabled, attempt to load saved progress
    if rural_mode_enabled:
        try:
            engine.load_progress_local()
            st.success('Progreso cargado desde almacenamiento local (Modo Rural)')
        except Exception:
            st.warning('No se encontró progreso local o falló la carga.')

col1, col2 = st.columns([1, 2])

with col1:
    lesson = st.selectbox('Lección', ['ECG Básico', 'ECG 12-derivaciones', 'Arritmias'])
    level = st.radio('Nivel', ['basic', 'intermediate', 'advanced'])
    if st.button('Iniciar Quiz'):
        topic = 'ecg_basics'
        questions = generate_quiz(topic=topic, level=level)
        st.session_state['academy_quiz'] = {
            'lesson_id': lesson,
            'questions': questions,
            'responses': {},
            'current_q': 0,
        }

    st.markdown('---')
    st.markdown('Casos clínicos de ejemplo')
    cases = sample_cases()
    for c in cases:
        if st.button(f"Cargar caso {c.patient_id}: {c.true_diagnosis}"):
            st.session_state['current_case'] = c

with col2:
    quiz_state = st.session_state.get('academy_quiz')
    if quiz_state:
        questions: Dict[int, object] = quiz_state['questions']
        current = quiz_state['current_q']
        total = len(questions)
        st.write(f'Pregunta {current+1} de {total}')
        q = questions[current]
        st.markdown(f"**{q.prompt}**")
        choice_key = f"quiz_choice_{current}"
        if choice_key not in st.session_state:
            st.session_state[choice_key] = None

        selected = st.radio('Opciones', q.choices, key=choice_key)

        def submit_current():
            # store numeric index of selected choice
            try:
                idx = q.choices.index(st.session_state[choice_key])
            except Exception:
                idx = None
            if idx is not None:
                quiz_state['responses'][current] = idx
            # advance
            if current + 1 < total:
                quiz_state['current_q'] = current + 1
            else:
                # finalize
                score = engine.submit_quiz(quiz_state['lesson_id'], questions, quiz_state['responses'])
                st.session_state['academy_result'] = {'score': score, 'responses': dict(quiz_state['responses'])}
                # Persist progress if rural mode active
                if rural_mode_enabled:
                    try:
                        engine.save_progress_local()
                        st.success('Progreso guardado localmente (Modo Rural)')
                    except Exception:
                        st.warning('No se pudo guardar el progreso localmente.')
    else:
        st.info('Inicia un quiz para comenzar.')

    if 'academy_result' in st.session_state:
        res = st.session_state['academy_result']
        st.success(f"Quiz finalizado — Puntuación: {res['score']:.1f}%")
        st.write('Respuestas enviadas:')
        st.json(res['responses'])

    if 'current_case' in st.session_state:
        c = st.session_state['current_case']
        st.markdown(f"**Caso {c.patient_id} — {c.true_diagnosis}**")
        st.write(c.history)
        if 'ecg' in c.signals:
            sig, fs = c.signals['ecg']
            st.line_chart(sig)
