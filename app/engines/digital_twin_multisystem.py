"""
DIGITAL TWIN MULTISYSTEM — Representación computacional viva de fisiología humana

Arquitectura de 10 gemelos digitales interconectados:
1. Cardiac Twin - Actividad eléctrica, mecánica, hemodinámica
2. Neurological Twin - Actividad cortical, estados cerebrales
3. Respiratory Twin - Ventilación, intercambio gaseoso
4. Musculoskeletal Twin - Activación muscular, fatiga
5. Autonomic Twin - Actividad simpática/parasimpática
6. Oxygenation Twin - Saturación de oxígeno, perfusión
7. Stress Response Twin - Respuesta al estrés, cortisol
8. Recovery Twin - Capacidad de recuperación
9. Sleep Twin - Estadios de sueño
10. Performance Twin - Desempeño físico y cognitivo

Todos los gemelos se comunican dinámicamente a través de una red de interacciones.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json


@dataclass
class CardiacTwinState:
    """Gemelo cardíaco: Actividad eléctrica, mecánica, hemodinámica"""
    heart_rate: float = 72.0  # bpm
    hrv: float = 50.0  # ms
    cardiac_output: float = 5.0  # L/min
    stroke_volume: float = 70.0  # ml
    qrs_duration: float = 0.08  # seg
    pr_interval: float = 0.16  # seg
    qt_interval: float = 0.40  # seg
    rhythm_stability: float = 85.0  # 0-100
    myocardial_stress: float = 30.0  # 0-100
    sa_node_rate: float = 60.0  # bpm
    av_conduction_delay: float = 0.12  # seg
    ventricular_ejection_fraction: float = 60.0  # %
    autonomic_influence: float = 50.0  # 0-100 (0=parasympathetic, 100=sympathetic)
    
    def to_dict(self) -> Dict:
        return {
            'heart_rate': self.heart_rate,
            'hrv': self.hrv,
            'cardiac_output': self.cardiac_output,
            'stroke_volume': self.stroke_volume,
            'rhythm_stability': self.rhythm_stability,
            'myocardial_stress': self.myocardial_stress,
            'ejection_fraction': self.ventricular_ejection_fraction,
        }


@dataclass
class NeurologicalTwinState:
    """Gemelo neurológico: Actividad cortical, estados cerebrales"""
    attention: float = 70.0  # 0-100
    mental_workload: float = 40.0  # 0-100
    cognitive_fatigue: float = 20.0  # 0-100
    relaxation_level: float = 60.0  # 0-100
    stress_perception: float = 30.0  # 0-100
    sleepiness: float = 10.0  # 0-100
    neural_activation: float = 50.0  # 0-100
    frontal_activity: float = 55.0  # 0-100
    temporal_activity: float = 45.0  # 0-100
    parietal_activity: float = 50.0  # 0-100
    occipital_activity: float = 40.0  # 0-100
    motor_cortex_activation: float = 35.0  # 0-100
    sensory_integration: float = 60.0  # 0-100
    
    def to_dict(self) -> Dict:
        return {
            'attention': self.attention,
            'mental_workload': self.mental_workload,
            'cognitive_fatigue': self.cognitive_fatigue,
            'relaxation_level': self.relaxation_level,
            'stress_perception': self.stress_perception,
            'sleepiness': self.sleepiness,
        }


@dataclass
class RespiratoryTwinState:
    """Gemelo respiratorio: Ventilación, intercambio gaseoso"""
    respiratory_rate: float = 16.0  # resp/min
    tidal_volume: float = 500.0  # ml
    minute_ventilation: float = 8.0  # L/min
    breathing_pattern: str = "normal"  # normal, shallow, deep, irregular
    oxygen_uptake: float = 250.0  # ml/min
    ventilation_quality: float = 85.0  # 0-100
    apnea_risk: float = 5.0  # 0-100
    hypoxia_risk: float = 10.0  # 0-100
    respiratory_effort: float = 40.0  # 0-100
    gas_exchange_efficiency: float = 90.0  # 0-100
    
    def to_dict(self) -> Dict:
        return {
            'respiratory_rate': self.respiratory_rate,
            'tidal_volume': self.tidal_volume,
            'breathing_pattern': self.breathing_pattern,
            'ventilation_quality': self.ventilation_quality,
            'apnea_risk': self.apnea_risk,
            'hypoxia_risk': self.hypoxia_risk,
        }


@dataclass
class MusculoskeletalTwinState:
    """Gemelo musculoesquelético: Activación muscular, fatiga"""
    emg_activity: float = 20.0  # 0-100
    fatigue_index: float = 10.0  # 0-100
    recruitment_pattern: float = 50.0  # 0-100
    motor_symmetry: float = 90.0  # 0-100
    neuromuscular_efficiency: float = 80.0  # 0-100
    muscle_tension: float = 30.0  # 0-100
    movement_smoothness: float = 85.0  # 0-100
    power_output: float = 100.0  # % of max
    endurance_status: float = 70.0  # 0-100
    
    def to_dict(self) -> Dict:
        return {
            'emg_activity': self.emg_activity,
            'fatigue_index': self.fatigue_index,
            'neuromuscular_efficiency': self.neuromuscular_efficiency,
            'muscle_tension': self.muscle_tension,
            'movement_smoothness': self.movement_smoothness,
        }


@dataclass
class AutonomicTwinState:
    """Gemelo autonómico: Actividad simpática/parasimpática"""
    sympathetic_activity: float = 40.0  # 0-100
    parasympathetic_activity: float = 60.0  # 0-100
    sympathetic_balance: float = 40.0  # 0-100
    parasympathetic_balance: float = 60.0  # 0-100
    stress_index: float = 30.0  # 0-100
    recovery_index: float = 70.0  # 0-100
    autonomic_flexibility: float = 75.0  # 0-100
    hrv_based_parasympathetic: float = 55.0  # 0-100
    lf_hf_ratio: float = 1.5  # Low Freq / High Freq
    
    def to_dict(self) -> Dict:
        return {
            'sympathetic_activity': self.sympathetic_activity,
            'parasympathetic_activity': self.parasympathetic_activity,
            'stress_index': self.stress_index,
            'recovery_index': self.recovery_index,
            'autonomic_flexibility': self.autonomic_flexibility,
        }


@dataclass
class OxygenationTwinState:
    """Gemelo de oxigenación: Saturación, perfusión"""
    spo2: float = 98.0  # %
    sao2: float = 98.0  # %
    arterial_oxygen: float = 95.0  # mmHg
    venous_oxygen: float = 40.0  # mmHg
    oxygen_saturation_trend: str = "stable"  # stable, improving, declining
    perfusion_index: float = 85.0  # 0-100
    capillary_refill: float = 2.0  # seconds
    tissue_oxygenation: float = 80.0  # 0-100
    
    def to_dict(self) -> Dict:
        return {
            'spo2': self.spo2,
            'perfusion_index': self.perfusion_index,
            'tissue_oxygenation': self.tissue_oxygenation,
        }


@dataclass
class StressResponseTwinState:
    """Gemelo de respuesta al estrés: Cortisol, activación"""
    cortisol_level: float = 10.0  # μg/dL
    cortisol_trend: str = "declining"  # rising, stable, declining
    acute_stress: float = 20.0  # 0-100
    chronic_stress: float = 35.0  # 0-100
    inflammatory_markers: float = 40.0  # 0-100
    immune_suppression: float = 15.0  # 0-100
    
    def to_dict(self) -> Dict:
        return {
            'cortisol_level': self.cortisol_level,
            'acute_stress': self.acute_stress,
            'chronic_stress': self.chronic_stress,
        }


@dataclass
class RecoveryTwinState:
    """Gemelo de recuperación: Capacidad regenerativa"""
    recovery_capacity: float = 75.0  # 0-100
    parasympathetic_tone: float = 65.0  # 0-100
    metabolic_recovery: float = 70.0  # 0-100
    sleep_quality_indicator: float = 65.0  # 0-100
    circadian_alignment: float = 80.0  # 0-100
    adaptation_status: float = 72.0  # 0-100
    
    def to_dict(self) -> Dict:
        return {
            'recovery_capacity': self.recovery_capacity,
            'parasympathetic_tone': self.parasympathetic_tone,
            'metabolic_recovery': self.metabolic_recovery,
        }


@dataclass
class SleepTwinState:
    """Gemelo de sueño: Estadios, calidad"""
    sleep_stage: str = "awake"  # awake, N1, N2, N3, REM
    sleep_quality: float = 65.0  # 0-100
    rem_percentage: float = 20.0  # % of total
    deep_sleep_percentage: float = 15.0  # % of total
    sleep_fragmentation: float = 10.0  # 0-100 (lower is better)
    sleep_efficiency: float = 85.0  # 0-100
    
    def to_dict(self) -> Dict:
        return {
            'sleep_stage': self.sleep_stage,
            'sleep_quality': self.sleep_quality,
            'sleep_efficiency': self.sleep_efficiency,
        }


@dataclass
class PerformanceTwinState:
    """Gemelo de desempeño: Capacidad física y cognitiva"""
    physical_capacity: float = 80.0  # 0-100
    cognitive_capacity: float = 75.0  # 0-100
    reaction_time: float = 250.0  # ms
    focus_level: float = 70.0  # 0-100
    endurance_capacity: float = 75.0  # 0-100
    peak_performance_window: str = "optimal"  # suboptimal, optimal, overreached
    
    def to_dict(self) -> Dict:
        return {
            'physical_capacity': self.physical_capacity,
            'cognitive_capacity': self.cognitive_capacity,
            'reaction_time': self.reaction_time,
            'focus_level': self.focus_level,
        }


@dataclass
class PhysiologicalInteraction:
    """Define cómo un gemelo afecta a otro"""
    source_twin: str
    target_twin: str
    interaction_type: str  # "increases", "decreases", "synchronizes"
    strength: float = 0.5  # 0-1
    delay: float = 0.0  # seconds
    description: str = ""


class DigitalTwinMultisystem:
    """
    Representación computacional viva de la fisiología humana.
    
    Integra 10 gemelos digitales con una red de interacciones dinámicas.
    Permite simulación, predicción, educación y análisis clínico.
    """
    
    def __init__(self):
        """Inicializa el gemelo digital multisistema"""
        self.cardiac = CardiacTwinState()
        self.neurological = NeurologicalTwinState()
        self.respiratory = RespiratoryTwinState()
        self.musculoskeletal = MusculoskeletalTwinState()
        self.autonomic = AutonomicTwinState()
        self.oxygenation = OxygenationTwinState()
        self.stress = StressResponseTwinState()
        self.recovery = RecoveryTwinState()
        self.sleep = SleepTwinState()
        self.performance = PerformanceTwinState()
        
        self.timestamp = datetime.now()
        self.interactions: List[PhysiologicalInteraction] = self._init_interactions()
        self.history: List[Dict] = []
        
    def _init_interactions(self) -> List[PhysiologicalInteraction]:
        """Define la red de interacciones fisiológicas"""
        return [
            # Brain ↔ Heart
            PhysiologicalInteraction(
                source_twin="neurological", target_twin="cardiac",
                interaction_type="increases", strength=0.7,
                description="Estrés mental aumenta frecuencia cardíaca"
            ),
            # Heart ↔ Lungs
            PhysiologicalInteraction(
                source_twin="cardiac", target_twin="respiratory",
                interaction_type="synchronizes", strength=0.6,
                description="Ritmo cardíaco sincronizado con respiración"
            ),
            # Respiration ↔ Oxygenation
            PhysiologicalInteraction(
                source_twin="respiratory", target_twin="oxygenation",
                interaction_type="increases", strength=0.8,
                description="Ventilación mejora saturación de oxígeno"
            ),
            # SpO2 ↔ Cognitive State
            PhysiologicalInteraction(
                source_twin="oxygenation", target_twin="neurological",
                interaction_type="increases", strength=0.7,
                description="Hipoxia reduce atención y cognición"
            ),
            # Stress ↔ Autonomic
            PhysiologicalInteraction(
                source_twin="stress", target_twin="autonomic",
                interaction_type="increases", strength=0.8,
                description="Estrés aumenta actividad simpática"
            ),
            # EMG ↔ Fatigue
            PhysiologicalInteraction(
                source_twin="musculoskeletal", target_twin="recovery",
                interaction_type="decreases", strength=0.7,
                description="Actividad muscular reduce capacidad de recuperación"
            ),
            # Autonomic ↔ Sleep
            PhysiologicalInteraction(
                source_twin="autonomic", target_twin="sleep",
                interaction_type="synchronizes", strength=0.6,
                description="Balance parasimpático facilita sueño"
            ),
            # Recovery ↔ Performance
            PhysiologicalInteraction(
                source_twin="recovery", target_twin="performance",
                interaction_type="increases", strength=0.8,
                description="Recuperación mejora desempeño"
            ),
        ]
    
    def update_from_sensors(self, sensor_data: Dict) -> None:
        """
        Actualiza el estado del gemelo desde datos de sensores.
        
        Args:
            sensor_data: Dict con claves como 'ecg', 'respiracion', 'spo2', etc.
        """
        if 'ecg' in sensor_data:
            ecg_data = sensor_data['ecg']
            self.cardiac.heart_rate = ecg_data.get('heart_rate', 72)
            self.cardiac.hrv = ecg_data.get('hrv', 50)
        
        if 'respiracion' in sensor_data:
            resp_data = sensor_data['respiracion']
            self.respiratory.respiratory_rate = resp_data.get('rate', 16)
            self.respiratory.tidal_volume = resp_data.get('tidal_volume', 500)
        
        if 'spo2' in sensor_data:
            spo2_data = sensor_data['spo2']
            self.oxygenation.spo2 = spo2_data.get('spo2', 98)
            self.oxygenation.perfusion_index = spo2_data.get('perfusion', 85)
        
        if 'eeg' in sensor_data:
            eeg_data = sensor_data['eeg']
            self.neurological.attention = eeg_data.get('attention', 70)
            self.neurological.mental_workload = eeg_data.get('workload', 40)
        
        if 'emg' in sensor_data:
            emg_data = sensor_data['emg']
            self.musculoskeletal.emg_activity = emg_data.get('activity', 20)
            self.musculoskeletal.fatigue_index = emg_data.get('fatigue', 10)
        
        # Actualizar timestamp
        self.timestamp = datetime.now()
        
        # Aplicar interacciones fisiológicas
        self._apply_interactions()
    
    def _apply_interactions(self) -> None:
        """Aplica la red de interacciones fisiológicas"""
        for interaction in self.interactions:
            if interaction.source_twin == "neurological":
                # El estrés mental afecta el corazón
                stress_factor = self.neurological.stress_perception / 100.0
                self.cardiac.heart_rate = 72 + (stress_factor * 30)
                self.cardiac.myocardial_stress = stress_factor * 80
            
            if interaction.source_twin == "stress":
                # El estrés aumenta actividad simpática
                stress_level = self.stress.acute_stress / 100.0
                self.autonomic.sympathetic_activity = 40 + (stress_level * 50)
                self.autonomic.parasympathetic_activity = 60 - (stress_level * 30)
            
            if interaction.source_twin == "respiratory":
                # La respiración afecta oxigenación
                ventilation_quality = self.respiratory.ventilation_quality / 100.0
                self.oxygenation.spo2 = 90 + (ventilation_quality * 8)
            
            if interaction.source_twin == "oxygenation":
                # Hipoxia afecta cognición
                spo2_deficit = max(0, (98 - self.oxygenation.spo2) / 8)
                self.neurological.attention = max(20, 70 - (spo2_deficit * 30))
                self.neurological.cognitive_fatigue = min(80, 20 + (spo2_deficit * 40))
    
    def simulate_intervention(self, intervention: str, intensity: float = 0.5) -> Dict:
        """
        Simula una intervención médica.
        
        Args:
            intervention: Tipo de intervención (e.g., "oxygen", "sedation", "exercise")
            intensity: Intensidad de 0-1
        
        Returns:
            Cambios en el estado
        """
        changes = {}
        
        if intervention == "oxygen":
            # O2 mejora saturación
            self.oxygenation.spo2 = min(100, self.oxygenation.spo2 + (intensity * 8))
            self.oxygenation.tissue_oxygenation += intensity * 15
            self.neurological.cognitive_fatigue -= intensity * 10
            changes['spo2'] = self.oxygenation.spo2
            
        elif intervention == "sedation":
            # Sedación reduce estrés y actividad
            self.neurological.stress_perception -= intensity * 40
            self.autonomic.sympathetic_activity -= intensity * 30
            self.cardiac.heart_rate = max(50, self.cardiac.heart_rate - (intensity * 20))
            changes['stress'] = self.neurological.stress_perception
            
        elif intervention == "exercise":
            # Ejercicio aumenta HR, fatiga, estrés inicial
            self.cardiac.heart_rate = min(180, self.cardiac.heart_rate + (intensity * 40))
            self.musculoskeletal.fatigue_index += intensity * 30
            self.respiratory.respiratory_rate += intensity * 8
            changes['heart_rate'] = self.cardiac.heart_rate
            
        elif intervention == "rest":
            # Descanso mejora recuperación
            self.recovery.recovery_capacity += intensity * 20
            self.stress.acute_stress -= intensity * 30
            self.musculoskeletal.fatigue_index -= intensity * 15
            changes['recovery'] = self.recovery.recovery_capacity
        
        self._apply_interactions()
        return changes
    
    def predict_physiological_events(self, horizon_minutes: int = 60) -> Dict:
        """
        Predice eventos fisiológicos futuros.
        
        Args:
            horizon_minutes: Minutos en el futuro para predecir
        
        Returns:
            Predicciones con confianza
        """
        predictions = {}
        
        # Predicción de fatiga
        fatigue_progression = self.musculoskeletal.fatigue_index + (horizon_minutes / 60 * 5)
        predictions['fatigue'] = {
            'predicted': min(100, fatigue_progression),
            'confidence': 0.75
        }
        
        # Predicción de recuperación
        recovery_trajectory = self.recovery.recovery_capacity - (horizon_minutes / 120 * 2)
        predictions['recovery'] = {
            'predicted': max(0, recovery_trajectory),
            'confidence': 0.70
        }
        
        # Predicción de estrés
        stress_trend = self.stress.acute_stress if self.stress.acute_stress > 50 else max(0, self.stress.acute_stress - 5)
        predictions['stress'] = {
            'predicted': stress_trend,
            'confidence': 0.65
        }
        
        # Predicción de inestabilidad cardiovascular
        if self.cardiac.heart_rate > 120 or self.oxygenation.spo2 < 90:
            predictions['cardiovascular_instability'] = {
                'risk': 'HIGH',
                'confidence': 0.80
            }
        else:
            predictions['cardiovascular_instability'] = {
                'risk': 'LOW',
                'confidence': 0.85
            }
        
        return predictions
    
    def generate_clinical_summary(self) -> str:
        """Genera un resumen clínico del estado del gemelo"""
        summary = f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    RESUMEN CLÍNICO DEL GEMELO DIGITAL                      ║
║                          {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}                              ║
╚════════════════════════════════════════════════════════════════════════════╝

🫀 SISTEMA CARDIOVASCULAR:
   • Frecuencia Cardíaca: {self.cardiac.heart_rate:.1f} bpm
   • Variabilidad (HRV): {self.cardiac.hrv:.1f} ms
   • Estabilidad de Ritmo: {self.cardiac.rhythm_stability:.1f}%
   • Estrés Miocárdico: {self.cardiac.myocardial_stress:.1f}%
   • Gasto Cardíaco: {self.cardiac.cardiac_output:.1f} L/min

🧠 SISTEMA NEUROLÓGICO:
   • Atención: {self.neurological.attention:.1f}%
   • Carga Cognitiva: {self.neurological.mental_workload:.1f}%
   • Fatiga Cognitiva: {self.neurological.cognitive_fatigue:.1f}%
   • Nivel de Estrés: {self.neurological.stress_perception:.1f}%
   • Somnolencia: {self.neurological.sleepiness:.1f}%

💨 SISTEMA RESPIRATORIO:
   • Frecuencia Respiratoria: {self.respiratory.respiratory_rate:.1f} resp/min
   • Patrón: {self.respiratory.breathing_pattern}
   • Calidad de Ventilación: {self.respiratory.ventilation_quality:.1f}%
   • Riesgo de Apnea: {self.respiratory.apnea_risk:.1f}%
   • Riesgo de Hipoxia: {self.respiratory.hypoxia_risk:.1f}%

🫁 OXIGENACIÓN:
   • SpO₂: {self.oxygenation.spo2:.1f}%
   • Índice de Perfusión: {self.oxygenation.perfusion_index:.1f}%
   • Oxigenación Tisular: {self.oxygenation.tissue_oxygenation:.1f}%

🦾 SISTEMA MUSCULOESQUELÉTICO:
   • Actividad EMG: {self.musculoskeletal.emg_activity:.1f}%
   • Índice de Fatiga: {self.musculoskeletal.fatigue_index:.1f}%
   • Eficiencia Neuromuscular: {self.musculoskeletal.neuromuscular_efficiency:.1f}%
   • Suavidad del Movimiento: {self.musculoskeletal.movement_smoothness:.1f}%

🔄 SISTEMA AUTONÓMICO:
   • Actividad Simpática: {self.autonomic.sympathetic_activity:.1f}%
   • Actividad Parasimpática: {self.autonomic.parasympathetic_activity:.1f}%
   • Índice de Estrés: {self.autonomic.stress_index:.1f}%
   • Flexibilidad Autonómica: {self.autonomic.autonomic_flexibility:.1f}%

⚡ RECUPERACIÓN Y RENDIMIENTO:
   • Capacidad de Recuperación: {self.recovery.recovery_capacity:.1f}%
   • Tono Parasimpático: {self.recovery.parasympathetic_tone:.1f}%
   • Desempeño Físico: {self.performance.physical_capacity:.1f}%
   • Desempeño Cognitivo: {self.performance.cognitive_capacity:.1f}%
   • Ventana de Desempeño Pico: {self.performance.peak_performance_window}

════════════════════════════════════════════════════════════════════════════════
"""
        return summary
    
    def to_json(self) -> str:
        """Convierte el estado completo a JSON"""
        state = {
            'timestamp': self.timestamp.isoformat(),
            'cardiac': self.cardiac.to_dict(),
            'neurological': self.neurological.to_dict(),
            'respiratory': self.respiratory.to_dict(),
            'musculoskeletal': self.musculoskeletal.to_dict(),
            'autonomic': self.autonomic.to_dict(),
            'oxygenation': self.oxygenation.to_dict(),
            'stress': self.stress.to_dict(),
            'recovery': self.recovery.to_dict(),
            'sleep': self.sleep.to_dict(),
            'performance': self.performance.to_dict(),
        }
        return json.dumps(state, indent=2)
    
    def create_patient_scenario(self, scenario: str) -> None:
        """
        Crea un escenario de paciente específico.
        
        Args:
            scenario: Tipo de paciente (healthy, hypertension, copd, arrhythmia, sepsis, etc.)
        """
        scenarios = {
            'healthy': {
                'cardiac': {'heart_rate': 72, 'hrv': 60, 'rhythm_stability': 95},
                'respiratory': {'respiratory_rate': 16, 'ventilation_quality': 95},
                'oxygenation': {'spo2': 98},
                'stress': {'acute_stress': 20},
                'performance': {'physical_capacity': 90, 'cognitive_capacity': 85},
            },
            'hypertension': {
                'cardiac': {'heart_rate': 85, 'myocardial_stress': 45},
                'autonomic': {'sympathetic_activity': 60},
                'stress': {'chronic_stress': 55},
            },
            'copd': {
                'respiratory': {'respiratory_rate': 22, 'ventilation_quality': 60},
                'oxygenation': {'spo2': 88},
                'neurological': {'cognitive_fatigue': 35},
            },
            'arrhythmia': {
                'cardiac': {'rhythm_stability': 45, 'myocardial_stress': 70},
                'autonomic': {'lf_hf_ratio': 3.5},
            },
            'sepsis': {
                'cardiac': {'heart_rate': 110, 'cardiac_output': 7.5},
                'respiratory': {'respiratory_rate': 28},
                'stress': {'acute_stress': 85},
                'oxygenation': {'spo2': 92},
            },
        }
        
        if scenario in scenarios:
            config = scenarios[scenario]
            for system, params in config.items():
                if system == 'cardiac':
                    for key, value in params.items():
                        setattr(self.cardiac, key, value)
                elif system == 'respiratory':
                    for key, value in params.items():
                        setattr(self.respiratory, key, value)
                elif system == 'oxygenation':
                    for key, value in params.items():
                        setattr(self.oxygenation, key, value)
                elif system == 'neurological':
                    for key, value in params.items():
                        setattr(self.neurological, key, value)
                elif system == 'autonomic':
                    for key, value in params.items():
                        setattr(self.autonomic, key, value)
                elif system == 'stress':
                    for key, value in params.items():
                        setattr(self.stress, key, value)
                elif system == 'performance':
                    for key, value in params.items():
                        setattr(self.performance, key, value)
            
            self._apply_interactions()
