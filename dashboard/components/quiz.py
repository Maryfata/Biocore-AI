import streamlit as st
import numpy as np


def render_quiz_metrics(case_type: str, metrics: dict):
    if 'quiz' not in st.session_state:
        st.session_state.quiz = None

    if st.session_state.quiz is None:
        st.session_state.quiz = _create_quiz(case_type, metrics)

    quiz = st.session_state.quiz
    st.markdown('### Quiz Clínico')
    st.write(quiz['description'])

    answers = []
    for idx, question in enumerate(quiz['questions']):
        options = st.radio(question['label'], question['choices'], key=f'quiz_q_{idx}')
        answers.append(options)

    if st.button('Enviar respuestas'): 
        score = 0
        for answer, question in zip(answers, quiz['questions']):
            if answer == question['correct']:
                score += 1
        st.success(f'Has respondido correctamente {score} de {len(answers)} preguntas.')
        for question in quiz['questions']:
            st.write(f"**{question['label']}** — Respuesta correcta: {question['correct']}")
            st.write(question['explanation'])


def _create_quiz(case_type: str, metrics: dict) -> dict:
    questions = [
        {
            'label': '¿Cuál es la frecuencia cardíaca estimada?',
            'choices': [str(x) for x in range(40, 161, 20)],
            'correct': str(int(round(metrics['BPM'] / 10) * 10)),
            'explanation': 'La frecuencia cardíaca se calcula en base al promedio de intervalos RR.'
        },
        {
            'label': '¿Hay una arritmia presente?',
            'choices': ['Sí', 'No'],
            'correct': 'Sí' if case_type != 'ritmo_sinusal_normal' else 'No',
            'explanation': 'Los arritmias alteran los intervalos RR o la morfología del ECG.'
        },
        {
            'label': '¿El QTc parece normal?',
            'choices': ['Sí', 'No'],
            'correct': 'Sí' if metrics['QTc'] < 0.45 else 'No',
            'explanation': 'Un QTc normal suele ser menor de 450 ms en hombres y 460 ms en mujeres.'
        }
    ]
    return {
        'description': 'Responde las preguntas clínicas basadas en el ECG y los hallazgos métricos.',
        'questions': questions
    }
