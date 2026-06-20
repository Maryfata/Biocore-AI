"""
BIOCORE AI — MULTISENSOR FUSION ENGINE

Integra resultados de los 5 motores de señal (ECG, EEG, EMG, Respiration, PPG)
en un estado fisiológico coherente con correlaciones e interacciones.

- Fusion de múltiples modalidades
- Cálculo de correlaciones cruzadas
- Generación de estado multisistema integrado
- Detección de anomalías sistémicas
"""

from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np
from datetime import datetime

from .signal_intelligence import (
    ECGAnalysis, EEGAnalysis, EMGAnalysis, 
    RespiratoryAnalysis, PPGAnalysis
)


class SystemInteraction(Enum):
    """Tipos de interacciones fisiológicas entre sistemas"""
    NEUROCARDIAC = "neurocardiac"  # Cerebro → Corazón
    CARDIORESPIRATORY = "cardiorespiratory"  # Corazón ↔ Pulmones
    CARDIOPULMONARY_OXYGEN = "cardiopulmonary_oxygen"  # Respiración → O2
    HYPOXIA_COGNITION = "hypoxia_cognition"  # Bajo O2 → Cognición baja
    STRESS_AUTONOMIC = "stress_autonomic"  # Estrés → Simpático
    MUSCLE_RECOVERY = "muscle_recovery"  # Actividad muscular → Recuperación
    AUTONOMIC_SLEEP = "autonomic_sleep"  # Parasimpático → Sueño
    RECOVERY_PERFORMANCE = "recovery_performance"  # Recuperación → Rendimiento


@dataclass
class CouplingIndex:
    """Índice de acoplamiento entre dos sistemas"""
    name: str
    value: float  # 0-1
    interpretation: str
    risk_level: str  # low, medium, high
    

@dataclass
class MultisensorFusionState:
    """Estado integrado de múltiples sensores"""
    timestamp: datetime
    
    # Estados individuales
    ecg_analysis: Optional[ECGAnalysis] = None
    eeg_analysis: Optional[EEGAnalysis] = None
    emg_analysis: Optional[EMGAnalysis] = None
    respiratory_analysis: Optional[RespiratoryAnalysis] = None
    ppg_analysis: Optional[PPGAnalysis] = None
    
    # Correlaciones
    neurocardiac_coupling: Optional[CouplingIndex] = None
    cardiorespiratory_coupling: Optional[CouplingIndex] = None
    neuromuscular_coupling: Optional[CouplingIndex] = None
    
    # Índices integrados
    physiological_stress_index: float = 0.0  # 0-100
    recovery_capacity_index: float = 100.0  # 0-100
    resilience_index: float = 50.0  # 0-100
    overall_health_index: float = 50.0  # 0-100
    
    # Detecciones
    anomalies_detected: List[str] = None
    recommendations: List[str] = None
    alerts: List[str] = None
    
    def __post_init__(self):
        if self.anomalies_detected is None:
            self.anomalies_detected = []
        if self.recommendations is None:
            self.recommendations = []
        if self.alerts is None:
            self.alerts = []


class FusionEngine:
    """Motor de fusión multisensor"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.fusion_state: Optional[MultisensorFusionState] = None
        self.history: List[MultisensorFusionState] = []
        
    def add_result(self, signal_type: str, analysis: Any) -> None:
        """Añade resultado de análisis individual"""
        self.results[signal_type] = analysis
    
    def clear_results(self) -> None:
        """Limpia resultados para nueva fusión"""
        self.results = {}
    
    def compute_neurocardiac_coupling(self) -> Optional[CouplingIndex]:
        """
        Calcula acoplamiento neurocardiaco
        (cómo cambios en EEG afectan ECG)
        """
        if 'ECG' not in self.results or 'EEG' not in self.results:
            return None
        
        ecg = self.results['ECG']
        eeg = self.results['EEG']
        
        # Cuanto mayor el estrés EEG, menos HRV
        stress_level = 1.0 - (eeg.relaxation_level / 100.0)
        expected_hrv = 50.0 * (1.0 - stress_level * 0.5)
        
        coupling_value = 1.0 - abs(ecg.hrv - expected_hrv) / (expected_hrv + 1e-6)
        coupling_value = max(0, min(1, coupling_value))
        
        if coupling_value > 0.7:
            interpretation = "Acoplamiento neurocardiaco normal"
            risk = "low"
        elif coupling_value > 0.4:
            interpretation = "Acoplamiento neurocardiaco alterado"
            risk = "medium"
        else:
            interpretation = "Acoplamiento neurocardiaco severamente alterado"
            risk = "high"
        
        return CouplingIndex(
            name="Acoplamiento Neurocardiaco",
            value=coupling_value,
            interpretation=interpretation,
            risk_level=risk
        )
    
    def compute_cardiorespiratory_coupling(self) -> Optional[CouplingIndex]:
        """
        Calcula acoplamiento cardiorrespiratorio
        (sincronización entre FC y FR)
        """
        if 'ECG' not in self.results or 'Respiratory' not in self.results:
            return None
        
        ecg = self.results['ECG']
        resp = self.results['Respiratory']
        
        # Relación óptima FC/FR es ~4:1 (72 bpm / 18 brpm = 4)
        hr = ecg.heart_rate
        rr = resp.respiratory_rate
        
        if rr > 0:
            ratio = hr / rr
            optimal_ratio = 4.0
            ratio_error = abs(ratio - optimal_ratio) / optimal_ratio
            coupling_value = max(0, 1.0 - ratio_error)
        else:
            coupling_value = 0.0
        
        if coupling_value > 0.7:
            interpretation = "Acoplamiento cardiorrespiratorio armónico"
            risk = "low"
        elif coupling_value > 0.4:
            interpretation = "Acoplamiento cardiorrespiratorio moderado"
            risk = "medium"
        else:
            interpretation = "Acoplamiento cardiorrespiratorio descoordinado"
            risk = "high"
        
        return CouplingIndex(
            name="Acoplamiento Cardiorrespiratorio",
            value=coupling_value,
            interpretation=interpretation,
            risk_level=risk
        )
    
    def compute_neuromuscular_coupling(self) -> Optional[CouplingIndex]:
        """
        Calcula acoplamiento neuromuscular
        (cómo fatiga cognitiva afecta fatiga muscular)
        """
        if 'EEG' not in self.results or 'EMG' not in self.results:
            return None
        
        eeg = self.results['EEG']
        emg = self.results['EMG']
        
        # La fatiga cognitiva debería correlacionar con fatiga muscular
        eeg_fatigue = eeg.cognitive_fatigue
        emg_fatigue = emg.fatigue_index
        
        fatigue_correlation = 1.0 - abs(eeg_fatigue - emg_fatigue) / 100.0
        coupling_value = max(0, min(1, fatigue_correlation))
        
        if coupling_value > 0.7:
            interpretation = "Fatiga correlacionada normalmente"
            risk = "low"
        elif coupling_value > 0.4:
            interpretation = "Fatiga con correlación parcial"
            risk = "medium"
        else:
            interpretation = "Fatiga descorrelacionada (posible patología)"
            risk = "high"
        
        return CouplingIndex(
            name="Acoplamiento Neuromuscular",
            value=coupling_value,
            interpretation=interpretation,
            risk_level=risk
        )
    
    def compute_physiological_stress_index(self) -> float:
        """
        Calcula índice de estrés fisiológico general
        Combina múltiples factores
        """
        stress = 0.0
        weight_sum = 0.0
        
        # ECG: taquicardia aumenta estrés
        if 'ECG' in self.results:
            ecg = self.results['ECG']
            hr_stress = max(0, (ecg.heart_rate - 60) / 100)  # Normalizar a 60-160 bpm
            stress += hr_stress * 25
            weight_sum += 25
        
        # EEG: falta de relajación aumenta estrés
        if 'EEG' in self.results:
            eeg = self.results['EEG']
            eeg_stress = 100 - eeg.relaxation_level
            stress += eeg_stress * 30
            weight_sum += 30
        
        # Respiratory: irregularidad aumenta estrés
        if 'Respiratory' in self.results:
            resp = self.results['Respiratory']
            resp_stress = 0.0 if resp.breathing_pattern == "regular" else 50.0
            stress += resp_stress * 20
            weight_sum += 20
        
        # EMG: alta activación
        if 'EMG' in self.results:
            emg = self.results['EMG']
            emg_stress = emg.activation_level
            stress += emg_stress * 15
            weight_sum += 15
        
        # PPG: bajo índice de perfusión
        if 'PPG' in self.results:
            ppg = self.results['PPG']
            perfusion_stress = 100 - ppg.perfusion_index
            stress += perfusion_stress * 10
            weight_sum += 10
        
        return min(100, stress / (weight_sum / 100) if weight_sum > 0 else 0)
    
    def compute_recovery_capacity_index(self) -> float:
        """
        Calcula capacidad de recuperación
        Basado en HRV, parasimpático, eficiencia muscular
        """
        recovery = 0.0
        weight_sum = 0.0
        
        # HRV alto indica buena capacidad de recuperación
        if 'ECG' in self.results:
            ecg = self.results['ECG']
            hrv_recovery = min(100, (ecg.hrv / 100) * 100)
            recovery += hrv_recovery * 40
            weight_sum += 40
        
        # Alta relajación EEG
        if 'EEG' in self.results:
            eeg = self.results['EEG']
            eeg_recovery = eeg.relaxation_level
            recovery += eeg_recovery * 30
            weight_sum += 30
        
        # Eficiencia muscular
        if 'EMG' in self.results:
            emg = self.results['EMG']
            emg_recovery = emg.efficiency
            recovery += emg_recovery * 20
            weight_sum += 20
        
        # Ventilación regular
        if 'Respiratory' in self.results:
            resp = self.results['Respiratory']
            resp_recovery = 100 if resp.breathing_pattern == "regular" else 50
            recovery += resp_recovery * 10
            weight_sum += 10
        
        return min(100, recovery / (weight_sum / 100) if weight_sum > 0 else 50)
    
    def compute_resilience_index(self) -> float:
        """
        Índice de resiliencia fisiológica
        Capacidad para mantener homeostasis bajo estrés
        """
        stress = self.compute_physiological_stress_index()
        recovery = self.compute_recovery_capacity_index()
        
        # La resiliencia es capacidad de recuperación bajo estrés
        resilience = recovery - (stress * 0.5)
        return max(0, min(100, resilience))
    
    def compute_overall_health_index(self) -> float:
        """
        Índice de salud general integrado
        """
        stress = self.compute_physiological_stress_index()
        recovery = self.compute_recovery_capacity_index()
        resilience = self.compute_resilience_index()
        
        # Salud es baja estrés + alta recuperación + alta resiliencia
        health = ((100 - stress) * 0.3 + recovery * 0.4 + resilience * 0.3)
        return max(0, min(100, health))
    
    def detect_anomalies(self) -> List[str]:
        """Detecta anomalías en estado multisistema"""
        anomalies = []
        
        if 'ECG' in self.results:
            ecg = self.results['ECG']
            if ecg.risk_score > 0.5:
                anomalies.append(f"⚠️ Alto riesgo cardíaco: {ecg.interpretation}")
        
        if 'EEG' in self.results:
            eeg = self.results['EEG']
            if eeg.sleepiness > 80:
                anomalies.append("⚠️ Somnolencia severa detectada")
            if eeg.stress_level > 80:
                anomalies.append("⚠️ Estrés severo detectado")
        
        if 'Respiratory' in self.results:
            resp = self.results['Respiratory']
            if resp.apnea_risk > 20:
                anomalies.append(f"⚠️ Riesgo de apnea elevado ({resp.apnea_risk:.0f}%)")
            if resp.hypoxia_risk > 20:
                anomalies.append(f"⚠️ Riesgo de hipoxia elevado ({resp.hypoxia_risk:.0f}%)")
        
        if 'PPG' in self.results:
            ppg = self.results['PPG']
            if ppg.spo2 < 92:
                anomalies.append(f"⚠️ SpO₂ bajo ({ppg.spo2:.1f}%)")
        
        if 'EMG' in self.results:
            emg = self.results['EMG']
            if emg.fatigue_index > 80:
                anomalies.append("⚠️ Fatiga muscular severa detectada")
        
        return anomalies
    
    def generate_recommendations(self) -> List[str]:
        """Genera recomendaciones basadas en estado fisiológico"""
        recommendations = []
        
        stress_index = self.compute_physiological_stress_index()
        recovery_index = self.compute_recovery_capacity_index()
        
        if stress_index > 70:
            recommendations.append("🧘 Realizar técnicas de relajación (meditación, respiración profunda)")
            recommendations.append("⏸️ Reducir actividades exigentes")
        
        if recovery_index < 40:
            recommendations.append("😴 Aumentar horas de sueño")
            recommendations.append("🚴 Actividad moderada para mejorar recuperación")
        
        if 'EEG' in self.results and self.results['EEG'].sleepiness > 70:
            recommendations.append("☕ Considerar descanso o pausas activas")
        
        if 'Respiratory' in self.results:
            resp = self.results['Respiratory']
            if resp.breathing_pattern == "irregular":
                recommendations.append("💨 Practicar respiración diafragmática")
        
        if 'ECG' in self.results:
            ecg = self.results['ECG']
            if ecg.heart_rate > 100:
                recommendations.append("❤️ Realizar ejercicios de relajación para reducir FC")
        
        return recommendations
    
    def generate_multisystem_state(self) -> MultisensorFusionState:
        """
        Genera estado integrado multisistema
        Combina análisis individuales con correlaciones
        """
        state = MultisensorFusionState(
            timestamp=datetime.now(),
            ecg_analysis=self.results.get('ECG'),
            eeg_analysis=self.results.get('EEG'),
            emg_analysis=self.results.get('EMG'),
            respiratory_analysis=self.results.get('Respiratory'),
            ppg_analysis=self.results.get('PPG'),
        )
        
        # Calcular acoplamientos
        state.neurocardiac_coupling = self.compute_neurocardiac_coupling()
        state.cardiorespiratory_coupling = self.compute_cardiorespiratory_coupling()
        state.neuromuscular_coupling = self.compute_neuromuscular_coupling()
        
        # Calcular índices integrados
        state.physiological_stress_index = self.compute_physiological_stress_index()
        state.recovery_capacity_index = self.compute_recovery_capacity_index()
        state.resilience_index = self.compute_resilience_index()
        state.overall_health_index = self.compute_overall_health_index()
        
        # Detectar anomalías y generar recomendaciones
        state.anomalies_detected = self.detect_anomalies()
        state.recommendations = self.generate_recommendations()
        
        # Generar alertas si es necesario
        if state.physiological_stress_index > 80:
            state.alerts.append("🚨 ALERTA: Estrés fisiológico severo")
        
        if state.overall_health_index < 30:
            state.alerts.append("🚨 ALERTA: Índice de salud bajo - considere evaluación médica")
        
        self.fusion_state = state
        self.history.append(state)
        
        return state


    def get_health_summary(self) -> str:
        """Resumen de salud en lenguaje natural"""
        if not self.fusion_state:
            return "No hay datos de fusión disponibles"
        
        state = self.fusion_state
        summary = f"""
        ═══════════════════════════════════════════════════════════
                    RESUMEN DE SALUD MULTISISTEMA
        ═══════════════════════════════════════════════════════════
        
        📊 ÍNDICES INTEGRALES:
           • Salud General: {state.overall_health_index:.1f}%
           • Estrés Fisiológico: {state.physiological_stress_index:.1f}%
           • Capacidad de Recuperación: {state.recovery_capacity_index:.1f}%
           • Resiliencia: {state.resilience_index:.1f}%
        
        🔗 ACOPLAMIENTOS SISTÉMICOS:
        """
        
        if state.neurocardiac_coupling:
            summary += f"\n   • {state.neurocardiac_coupling.name}: {state.neurocardiac_coupling.value:.2f}"
        if state.cardiorespiratory_coupling:
            summary += f"\n   • {state.cardiorespiratory_coupling.name}: {state.cardiorespiratory_coupling.value:.2f}"
        if state.neuromuscular_coupling:
            summary += f"\n   • {state.neuromuscular_coupling.name}: {state.neuromuscular_coupling.value:.2f}"
        
        if state.anomalies_detected:
            summary += "\n\n        ⚠️  ANOMALÍAS DETECTADAS:\n"
            for anomaly in state.anomalies_detected:
                summary += f"           {anomaly}\n"
        
        if state.recommendations:
            summary += "\n        💡 RECOMENDACIONES:\n"
            for rec in state.recommendations:
                summary += f"           {rec}\n"
        
        if state.alerts:
            summary += "\n        🚨 ALERTAS CRÍTICAS:\n"
            for alert in state.alerts:
                summary += f"           {alert}\n"
        
        summary += "\n        ═══════════════════════════════════════════════════════════\n"
        
        return summary


# Backwards-compatible alias for external importers
MultisensorFusionEngine = FusionEngine
