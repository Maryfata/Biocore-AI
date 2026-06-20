import streamlit as st

st.set_page_config(page_title='Research Lab - BioSignal', layout='wide')

st.title('Laboratorio de Investigación Biomédica')
st.write('Panel de benchmarking, exportación de datos y métricas clínicas para estudios.')

st.markdown('### Funcionalidades de investigación')
st.write('- Exportación de datasets sintéticos y reales.')
st.write('- Comparación de algoritmos y métricas clínicas.')
st.write('- Generación de figuras y tablas listas para publicaciones.')

st.markdown('### Avance hacia inteligencia artificial cardiovascular')
st.write('- Implementaciones de CNN, Grad-CAM y detección automatizada.')
st.write('- Módulos de entrenamiento y validación clínica en `deep_learning/`.')

if st.button('Exportar dataset educativo'): 
    st.success('Dataset exportado a `data/exported/ecg_research_dataset.csv` (simulado).')

st.markdown('### Módulos disponibles')
st.write('- `deep_learning/cnn_model.py`')
st.write('- `deep_learning/trainer.py`')
st.write('- `deep_learning/inference.py`')
st.write('- `deep_learning/explainability.py`')
