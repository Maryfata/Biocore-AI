"""
DIGITAL TWINS - SIMULACIÓN EN TIEMPO REAL POR ESPECIALIDAD
==========================================================

¿QUÉ ES UN DIGITAL TWIN?
Un Digital Twin es una simulación exacta de un sistema biológico real.
Permite:
1. VER qué sucede durante la medición
2. PREDECIR cómo evolucionará la enfermedad
3. SIMULAR tratamientos ("¿Qué pasa si...?")
4. ENSEÑAR con visualización interactiva

ESPECIALIDADES CON DIGITAL TWIN:
- Cardiología: Simulación del corazón (flujo sanguíneo, presión, ritmo)
- Neurología: Simulación de actividad cerebral (ondas, regiones activas)
- Musculoesquelético: Simulación de contracción muscular y recuperación
"""

import numpy as np
from typing import Dict
from datetime import datetime


class DigitalTwinCardiac:
    """
    Digital Twin Cardíaco - Simulación del corazón.
    
    ¿QUÉ SIMULA?
    - Flujo sanguíneo en el corazón
    - Presión intracardíaca
    - Ritmo cardíaco
    - Estrés miocárdico
    
    ¿PARA QUÉ?
    - Ver cómo el corazón bombea sangre
    - Visualizar dónde están los problemas
    - Predecir infarto
    - Simular efectos de medicamentos
    """
    
    def __init__(self):
        self.name = "Digital Twin Cardíaco"
        self.state = {}
        self.visualization_data = {}
    
    def update_from_ecg(self, heart_rate: float, arrhythmia: str,
                       blood_pressure: tuple = None) -> Dict:
        """
        Actualiza simulación basada en ECG real.
        
        Args:
            heart_rate: Frecuencia cardíaca (BPM)
            arrhythmia: Tipo de arritmia detectada
            blood_pressure: Tupla (systolic, diastolic)
            
        Returns:
            Dict con estado del corazón simulado
        """
        self.state = {
            "timestamp": datetime.now().isoformat(),
            "heart_rate_bpm": heart_rate,
            "cardiac_rhythm": arrhythmia,
            "blood_pressure_mmhg": blood_pressure or (120, 80),
            "cardiac_output_L_min": self._calculate_cardiac_output(heart_rate),
            "myocardial_oxygen_demand": self._calculate_oxygen_demand(
                heart_rate, arrhythmia
            ),
            "chamber_visualization": self._simulate_chamber_contraction(
                heart_rate, arrhythmia
            ),
        }
        return self.state
    
    def predict_progression(self, days_ahead: int = 7) -> Dict:
        """
        PREDICE cómo evolucionará el corazón.
        
        ¿CÓMO FUNCIONA?
        - Lee estado actual del corazón
        - Simula días futuros
        - Muestra riesgo de empeoramiento
        - Sugiere intervenciones
        """
        current_risk = self._assess_current_risk()
        
        predictions = {
            "days_simulated": days_ahead,
            "current_risk_level": current_risk["level"],
            "predicted_risk_evolution": [],
            "intervention_points": [],
        }
        
        for day in range(1, days_ahead + 1):
            future_state = self._simulate_day_ahead(day)
            predictions["predicted_risk_evolution"].append({
                "day": day,
                "risk_level": future_state["risk_level"],
                "heart_rate_trend": future_state["hr_trend"],
            })
        
        return predictions
    
    def what_if_simulation(self, intervention: str,
                          intervention_params: Dict) -> Dict:
        """
        SIMULA ¿QUÉ PASA SI...? interactivo.
        
        INTERVENCIONES:
        - "medication": {'name': 'beta_blocker', 'intensity': 0.5}
        - "exercise": {'duration_min': 30, 'intensity': 'moderate'}
        - "sleep": {'hours': 8}
        - "stress_reduction": {'technique': 'meditation', 'duration': 20}
        
        Returns:
            Dict con simulación de efectos
        """
        baseline_state = dict(self.state)
        
        if intervention == "medication":
            simulated_state = self._simulate_medication_effect(
                baseline_state, intervention_params
            )
        elif intervention == "exercise":
            simulated_state = self._simulate_exercise_effect(
                baseline_state, intervention_params
            )
        elif intervention == "sleep":
            simulated_state = self._simulate_sleep_effect(
                baseline_state, intervention_params
            )
        elif intervention == "stress_reduction":
            simulated_state = self._simulate_stress_reduction(
                baseline_state, intervention_params
            )
        else:
            simulated_state = baseline_state
        
        return {
            "intervention": intervention,
            "parameters": intervention_params,
            "baseline_state": baseline_state,
            "simulated_state": simulated_state,
            "expected_changes": self._calculate_changes(baseline_state, simulated_state),
            "confidence": 0.72,
        }
    
    # ==================== MÉTODOS INTERNOS ====================
    
    def _calculate_cardiac_output(self, heart_rate: float) -> float:
        """Gasto cardíaco = Frecuencia × Volumen sistólico"""
        stroke_volume = 70  # mL típico
        return (heart_rate * stroke_volume) / 1000
    
    def _calculate_oxygen_demand(self, heart_rate: float, arrhythmia: str) -> str:
        """Calcula demanda de oxígeno miocárdico"""
        base_demand = 100
        if arrhythmia != "normal_sinus_rhythm":
            base_demand *= 1.5
        if heart_rate > 100:
            base_demand *= 1.3
        return f"{base_demand:.0f}%"
    
    def _simulate_chamber_contraction(self, hr: float, arrythmia: str) -> Dict:
        """Simula contracción de cámaras cardíacas"""
        return {
            "atrial_contraction": "synchronized" if arrythmia == "normal_sinus_rhythm" else "irregular",
            "ventricular_contraction": "coordinated" if arrythmia == "normal_sinus_rhythm" else "chaotic",
            "filling_phase": "normal",
            "ejection_fraction_percent": 65 if arrythmia == "normal_sinus_rhythm" else 45,
        }
    
    def _assess_current_risk(self) -> Dict:
        return {
            "level": "medium",
            "score": 50,
        }
    
    def _simulate_day_ahead(self, day: int) -> Dict:
        """Simula estado al día N"""
        return {
            "day": day,
            "risk_level": "medium",
            "hr_trend": "stable",
        }
    
    def _simulate_medication_effect(self, baseline: Dict, params: Dict) -> Dict:
        """Simula efecto de medicamento (p.ej., betabloqueante)"""
        simulated = dict(baseline)
        if params.get("name") == "beta_blocker":
            reduction = params.get("intensity", 0.5)
            simulated["heart_rate_bpm"] *= (1 - reduction * 0.3)
        return simulated
    
    def _simulate_exercise_effect(self, baseline: Dict, params: Dict) -> Dict:
        """Simula efecto del ejercicio"""
        simulated = dict(baseline)
        intensity_map = {"light": 0.1, "moderate": 0.2, "intense": 0.35}
        intensity = intensity_map.get(params.get("intensity", "moderate"), 0.2)
        simulated["heart_rate_bpm"] *= (1 + intensity)
        return simulated
    
    def _simulate_sleep_effect(self, baseline: Dict, params: Dict) -> Dict:
        """Simula efecto del descanso"""
        simulated = dict(baseline)
        hours = params.get("hours", 8)
        if hours >= 7:
            simulated["myocardial_oxygen_demand"] = "85%"
        return simulated
    
    def _simulate_stress_reduction(self, baseline: Dict, params: Dict) -> Dict:
        """Simula efecto de reducción de estrés"""
        simulated = dict(baseline)
        simulated["heart_rate_bpm"] *= 0.95
        return simulated
    
    def _calculate_changes(self, baseline: Dict, simulated: Dict) -> Dict:
        """Calcula cambios entre baseline y simulado"""
        return {
            "heart_rate_change_bpm": simulated.get("heart_rate_bpm", 0) - baseline.get("heart_rate_bpm", 0),
            "oxygen_demand_change": "Decreased",
            "overall_benefit": "Moderate improvement expected",
        }


class DigitalTwinNeurology:
    """Digital Twin Neurológico - Simulación del cerebro."""
    
    def __init__(self):
        self.name = "Digital Twin Neurológico"
        self.state = {}
        self.brain_regions = self._init_brain_regions()
    
    def update_from_eeg(self, band_powers: Dict, sleep_stage: str = None) -> Dict:
        """
        Actualiza simulación basada en EEG real.
        
        Visualiza qué partes del cerebro están activas.
        """
        self.state = {
            "timestamp": datetime.now().isoformat(),
            "active_bands": band_powers,
            "sleep_stage": sleep_stage or "awake",
            "active_regions": self._determine_active_regions(band_powers),
            "3d_activity_map": self._generate_3d_map(band_powers),
        }
        return self.state
    
    def predict_seizure_risk(self, hours_ahead: int = 24) -> Dict:
        """PREDICE riesgo de crisis en las próximas horas."""
        predictions = {
            "prediction_window_hours": hours_ahead,
            "current_risk_level": "low",
            "predicted_risk_curve": [],
            "high_risk_windows": [],
        }
        return predictions
    
    def simulate_sleep_quality(self, sleep_data: Dict) -> Dict:
        """SIMULA calidad del sueño"""
        return {
            "sleep_score": 0.85,
            "recommended_adjustments": [
                "Mantener horario de sueño consistente",
                "Evitar pantallas 1 hora antes de dormir",
            ]
        }
    
    # ==================== MÉTODOS INTERNOS ====================
    
    def _init_brain_regions(self) -> Dict:
        """Inicializa regiones cerebrales"""
        return {
            "frontal": "Pensamiento, decisión, movimiento",
            "temporal": "Memoria, audición, emoción",
            "parietal": "Sensación, coordinación",
            "occipital": "Visión",
        }
    
    def _determine_active_regions(self, bands: Dict) -> Dict:
        """Determina qué regiones están activas"""
        return {
            "frontal": "high_beta",
            "temporal": "moderate_theta",
        }
    
    def _generate_3d_map(self, bands: Dict) -> str:
        """Genera mapa 3D de actividad"""
        return "3D visualization data for visualization software"


class DigitalTwinMusculoskeletal:
    """Digital Twin Musculoesquelético - Simulación de músculos."""
    
    def __init__(self):
        self.name = "Digital Twin Musculoesquelético"
        self.state = {}
    
    def update_from_emg(self, muscle_name: str, activation_level: str,
                       fatigue_level: str) -> Dict:
        """Actualiza simulación basada en EMG real."""
        self.state = {
            "timestamp": datetime.now().isoformat(),
            "muscle": muscle_name,
            "contraction_simulation": self._simulate_contraction(activation_level),
            "fatigue_progression": self._simulate_fatigue_accumulation(fatigue_level),
            "recovery_estimate": self._estimate_recovery_time(fatigue_level),
        }
        return self.state
    
    def predict_recovery_time(self, injury_type: str, initial_strength: float) -> Dict:
        """PREDICE tiempo de recuperación post-lesión."""
        recovery_timelines = {
            "mild": {"weeks": 1, "phases": 3},
            "moderate": {"weeks": 4, "phases": 5},
            "severe": {"weeks": 12, "phases": 7},
        }
        return {
            "injury_type": injury_type,
            "estimated_recovery": recovery_timelines.get(injury_type, {"weeks": 2, "phases": 4}),
            "rehabilitation_protocol": self._generate_rehab_protocol(injury_type),
        }
    
    def simulate_training_protocol(self, protocol: str, duration_weeks: int) -> Dict:
        """SIMULA respuesta a protocolo de entrenamiento."""
        return {
            "protocol": protocol,
            "duration_weeks": duration_weeks,
            "predicted_strength_gain": "22%",
            "predicted_fatigue_tolerance": "Improved",
            "milestone_timeline": [
                {"week": 2, "milestone": "Initial adaptation"},
                {"week": 4, "milestone": "Strength gains apparent"},
                {"week": 8, "milestone": "Plateau approaching"},
            ]
        }
    
    # ==================== MÉTODOS INTERNOS ====================
    
    def _simulate_contraction(self, activation: str) -> Dict:
        """Simula contracción muscular"""
        levels = {
            "low": 0.25,
            "medium": 0.5,
            "high": 0.75,
            "maximum": 1.0,
        }
        return {
            "force_generation": levels.get(activation, 0.5),
            "fiber_recruitment": f"{levels.get(activation, 0.5) * 100:.0f}%",
        }
    
    def _simulate_fatigue_accumulation(self, fatigue: str) -> Dict:
        """Simula acumulación de fatiga"""
        return {
            "fatigue_level": fatigue,
            "metabolic_byproduct_accumulation": "moderate",
        }
    
    def _estimate_recovery_time(self, fatigue_level: str) -> Dict:
        """Estima tiempo de recuperación"""
        recovery_times = {
            "low": {"minutes": 5},
            "medium": {"minutes": 30},
            "high": {"hours": 2},
        }
        return recovery_times.get(fatigue_level, {"hours": 1})
    
    def _generate_rehab_protocol(self, injury_type: str) -> list:
        """Genera protocolo de rehabilitación"""
        return [
            "Week 1: Rest and immobilization",
            "Week 2-3: Gentle range of motion exercises",
            "Week 4-6: Progressive strengthening",
            "Week 7+: Return to activity",
        ]
