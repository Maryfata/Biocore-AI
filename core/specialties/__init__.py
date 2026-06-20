"""
SISTEMA DE ESPECIALIDADES MÉDICAS - BIOCORE AI OS v3.0
======================================================

Este módulo orquesta la integración total de TODAS las especialidades médicas.
Cada especialidad está completamente integrada con:
- Captura de señales específicas
- IA automática de análisis
- Digital Twin correspondiente
- Documentación explícita para principiantes

ESPECIALIDADES DISPONIBLES:
1. Cardiología (ECG, HRV, Presión arterial, Digital Twin Cardíaco)
2. Neurología (EEG, Análisis de sueño, Detección de epilepsia, Digital Twin Neuro)
3. Musculoesquelético (EMG, Análisis de fatiga, Digital Twin Muscular)
4. Respiratorio (SpO2, Frecuencia respiratoria, Digital Twin Respiratorio)
"""

from .cardiology import CardiacSpecialty
from .neurology import NeurologySpecialty
from .musculoskeletal import MusculoskeletalSpecialty

__all__ = [
    "CardiacSpecialty",
    "NeurologySpecialty", 
    "MusculoskeletalSpecialty",
]

# Registro de especialidades
SPECIALTIES = {
    "cardiology": CardiacSpecialty,
    "neurology": NeurologySpecialty,
    "musculoskeletal": MusculoskeletalSpecialty,
}
