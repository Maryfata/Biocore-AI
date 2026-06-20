"""Modo educativo interactivo de ECG con aprendizaje adaptativo ML."""

import os
import sys
import streamlit as st
import numpy as np

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from src.ai.patient_analytics import AdaptiveQuizEngine
    HAS_ADAPTIVE_QUIZ = True
except ImportError:
    HAS_ADAPTIVE_QUIZ = False

try:
    from app.supermodules import render_sidebar_navigation
except ImportError:
    import importlib.util
    utils_path = os.path.join(PROJECT_ROOT, 'app', 'utils.py')
    spec = importlib.util.spec_from_file_location('app_utils', utils_path)
    app_utils = importlib.util.module_from_spec(spec)
    sys.modules['app_utils'] = app_utils
    spec.loader.exec_module(app_utils)
    render_sidebar_navigation = app_utils.render_sidebar_navigation

st.set_page_config(page_title="Educación ECG", layout="wide")
render_sidebar_navigation()

st.markdown("""
    <h1 style="color: #1f77b4;">🎓 Educación y entrenamiento ECG</h1>
    <p>Domina la interpretación de ECG con casos interactivos, análisis de latidos y cuestionarios prácticos.</p>
""", unsafe_allow_html=True)

st.markdown(
    """
    ### Contenidos rápidos
    - [Qué aprenderás](#que-aprenderas)
    - [Cómo usar el tutor](#como-usar-el-tutor)
    - [Qué significa cada métrica](#metricas)
    """
)

st.markdown('<a id="que-aprenderas"></a>', unsafe_allow_html=True)
st.markdown("### Qué aprenderás")
st.write(
    "Aprenderás a reconocer ritmos normales, taquicardia, bradicardia y arritmias. El tutor explica cómo interpretar intervalos PR, QRS y QT, y cómo evaluar la calidad de la señal para la práctica clínica."
)

st.markdown('<a id="como-usar-el-tutor"></a>', unsafe_allow_html=True)
st.markdown("### Cómo usar el tutor")
st.write(
    "1. Selecciona un caso y la dificultad.\n"
    "2. Genera el caso y observa la señal ECG con anotaciones.\n"
    "3. Revisa la explicación clínica y comprende cada componente del latido.\n"
    "4. Responde el cuestionario para consolidar lo aprendido."
)

st.markdown('<a id="metricas"></a>', unsafe_allow_html=True)
st.markdown("### Qué significa cada métrica")
st.markdown(
    "- Frecuencia cardíaca: ritmo del corazón en bpm.\n"
    "- Intervalo PR: tiempo entre la activación auricular y ventricular.\n"
    "- Duración QRS: velocidad de despolarización ventricular.\n"
    "- QTc: riesgo de torsadas de punta y arritmias.\n"
)

try:
    from educational.ecg_tutor import ECGTutor
except ImportError:
    st.error("Módulo ECG Tutor no encontrado")
    st.stop()

tutor = ECGTutor()

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 🎯 Seleccionar caso")
    
    case_types = tutor.available_cases()
    selected_case = st.selectbox("Tipo de caso", case_types)
    
    difficulty = st.radio(
        "Nivel de dificultad",
        ["Básico", "Intermedio", "Avanzado"]
    )
    
    if st.button("📋 Generar caso"):
        st.session_state.case = tutor.create_case(
            case_type=selected_case,
            complexity=difficulty
        )

with col2:
    if 'case' in st.session_state:
        case = st.session_state.case
        r_peaks = tutor.detect_r_peaks(case.signal, case.fs)
        
        duration_seconds = float(case.time[-1]) if hasattr(case.time, '__len__') else float(case.time)
        st.markdown(f"### {tutor.case_title(case.case_type)}")
        st.markdown(f"**Complejidad:** {case.complexity}")
        st.markdown(f"**Duración:** {duration_seconds:.1f} segundos")
        
        st.markdown("---")
        
        try:
            fig = tutor.create_clinical_ecg_figure(case.signal, case.fs, r_peaks)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Visualización no disponible: {e}")
        
        st.markdown("---")
        
        with st.expander("📖 Explicación clínica"):
            explanations = tutor.explain_components(case.signal, case.fs, r_peaks)
            
            for component, details in explanations.items():
                st.markdown(f"**{component}:**")
                st.write(details)
        
        st.markdown("---")
        
        with st.expander("🔬 Análisis de plantilla de latido"):
            try:
                beat_time, beat_signal = tutor.average_beat_template(case.signal, case.fs, r_peaks)
                if beat_time.size and beat_signal.size:
                    template_fig = tutor.create_beat_template_figure(beat_time, beat_signal)
                    st.plotly_chart(template_fig, use_container_width=True)
                else:
                    st.info("No hay plantilla de latido disponible para la señal actual.")
            except Exception as e:
                st.warning(f"Visualización de plantilla no disponible: {e}")
            
            noise_analysis = tutor.noise_vs_signal(case.signal, case.fs, r_peaks)
            col1, col2, col3 = st.columns(3)
            col1.metric("Ruido (std)", f"{noise_analysis['noise_std']:.4f}", "mV")
            col2.metric("Señal (std)", f"{noise_analysis['signal_std']:.4f}", "mV")
            col3.metric("SNR", f"{noise_analysis['ratio']:.2f}", "dB")
        
        st.markdown("---")
        
        st.markdown("### 📝 Cuestionario")
        
        difficulty_map = {'Básico': 'basico', 'Intermedio': 'intermedio', 'Avanzado': 'avanzado'}
        quiz = tutor.generate_quiz(level=difficulty_map.get(difficulty, 'basico'))
        
        st.markdown(f"**Pregunta:** {quiz['pregunta']}")
        
        if 'quiz_options' not in st.session_state or st.session_state.get('quiz_question') != quiz['pregunta']:
            st.session_state.quiz_options = quiz['opciones']
            st.session_state.quiz_question = quiz['pregunta']
        
        selected_answer = st.radio(
            "Selecciona tu respuesta:",
            st.session_state.quiz_options,
            key='quiz_answer'
        )
        
        if st.button("✓ Enviar respuesta"):
            try:
                is_correct = tutor.grade_quiz(
                    quiz,
                    selected_answer
                )
                
                if is_correct:
                    st.success(f"✅ Correcto! {quiz.get('explicacion', '')}")
                else:
                    correct_index = int(quiz['respuesta'])
                    correct_answer = quiz['opciones'][correct_index] if correct_index < len(quiz['opciones']) else 'N/A'
                    st.error(f"❌ Incorrecto. La respuesta correcta es: {correct_answer}")
                    st.info(quiz.get('explicacion', ''))
            except Exception as e:
                st.error(f"Error al evaluar la respuesta: {str(e)}")
    
    else:
        st.info("👈 Genera un caso para comenzar a aprender")

st.markdown("---")

st.markdown("### 📚 Ruta de aprendizaje")

progress = st.slider("Tu progreso", 0, 100, 35, disabled=True)

col1, col2, col3 = st.columns(3)
col1.metric("Casos completados", "12/50", "24%")
col2.metric("Cuestionarios aprobados", "28/40", "70%")
col3.metric("Nivel de habilidad", "Intermedio", "")

st.markdown("---")

with st.expander("💡 Consejos de interpretación ECG"):
    st.markdown("""
    1. **Revisa siempre la frecuencia primero**
       - Normal: 60-100 bpm
       - Usa la regla de 6 segundos o la detección de picos R
    
    2. **Evalúa el ritmo**
       - ¿Es regular?
       - Busca ondas P antes de cada QRS
    
    3. **Analiza las ondas y los intervalos**
       - Onda P: < 120 ms, < 0.3 mV
       - Intervalo PR: 120-200 ms
       - QRS: < 120 ms
       - QT/QTc: < 440-460 ms
    
    4. **Observa el eje y la rotación**
       - Eje normal: -30° a +90°
       - Revisa derivaciones II y aVF
    
    5. **Verifica patología**
       - Elevación/depresión ST
       - Inversión de onda T
       - QT prolongado
       - Bloqueos de rama
    """)
