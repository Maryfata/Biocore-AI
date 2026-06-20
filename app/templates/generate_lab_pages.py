"""Generador de páginas de 'Biomedical Cognitive Exploration Lab' a partir de la plantilla.
Ejecuta para crear archivos en `app/pages/` para cada módulo de la lista.
"""
import os
from pathlib import Path

MODULES = [
    ("📊 ECG Monitor", "1_ECG_Monitor"),
    ("🔗 Multisensor", "2_Multisensor"),
    ("🎓 Education", "3_Education"),
    ("👥 Patients", "4_Patients"),
    ("🤖 AI Analysis", "5_AI_Analysis"),
    ("📋 ECG-12-Derivaciones", "6_ECG_12"),
    ("💨 Respiratory-Lab", "7_Respiratory_Lab"),
    ("🧠 EEG-Neuro-Lab", "8_EEG_Neuro_Lab"),
    ("🦾 EMG Muscle Lab", "9_EMG_Muscle_Lab"),
    ("📚 Guides", "10_Guides"),
    ("🏫 Academia Clinica", "11_Academia_Clinica"),
]

TEMPLATE_IMPORT = "from app.templates.biomedical_lab_template import render_module_template"

PAGES_DIR = Path(__file__).resolve().parents[1] / 'pages'

PAGE_STUB = '''"""Página generada: {title}
"""

import streamlit as st
{template_import}


def load_module_metrics(module_key: str):
    # Implementa carga de métricas desde JSON/DB si existe
    return None


def main():
    st.set_page_config(page_title="{title}", layout="wide")
    metrics = load_module_metrics('{key}')
    render_module_template('{title}', subtitle='', metrics=metrics)


if __name__ == '__main__':
    main()
'''


def generate_pages(dry_run=True):
    created = []
    for title, key in MODULES:
        filename = f"{key}.py"
        target = PAGES_DIR / filename
        content = PAGE_STUB.format(title=title, key=key, template_import=TEMPLATE_IMPORT)
        if dry_run:
            created.append(str(target))
        else:
            with open(target, 'w', encoding='utf-8') as f:
                f.write(content)
            created.append(str(target))
    return created


if __name__ == '__main__':
    print('Dry run, pages that would be created:')
    for p in generate_pages(dry_run=True):
        print(' -', p)
