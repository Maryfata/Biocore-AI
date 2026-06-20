import numpy as np
import pandas as pd
from typing import Dict, Any, Union

class BiocoreEngine:
    """
    Motor de Análisis Fisiológico Avanzado para BIOCORE.
    Calcula 7 biomarcadores propietarios basados en fusión de señales (ECG, EEG, EDA).
    """
    def __init__(self):
        self.baselines = {
            'resting_hr_target': 60.0,    
            'sdnn_target': 50.0,          
            'rmssd_target': 45.0,         
            'vo2_max_proxy_target': 50.0  
        }

    def _normalize(self, value: float, min_val: float, max_val: float, invert: bool = False) -> float:
        if max_val == min_val:
            return 50.0
        norm = (value - min_val) / (max_val - min_val) * 100
        norm = np.clip(norm, 0, 100)
        return round(100 - norm if invert else norm, 2)

    def calculate_stress_index(self, hrv_lf_hf_ratio: float, eda_scr_peaks: int, scl_u_siemens: float) -> float:
        hrv_score = self._normalize(hrv_lf_hf_ratio, 0.5, 5.0)
        eda_f_score = self._normalize(eda_scr_peaks, 0, 25)
        eda_t_score = self._normalize(scl_u_siemens, 1.0, 15.0)
        stress_score = (hrv_score * 0.50) + (eda_f_score * 0.35) + (eda_t_score * 0.15)
        return round(np.clip(stress_score, 0, 100), 2)

    def calculate_recovery_index(self, current_resting_hr: float, hrv_rmssd: float, sleep_hours: float) -> float:
        hr_component = self._normalize(current_resting_hr, 45.0, 90.0, invert=True)
        rmssd_component = self._normalize(hrv_rmssd, 10.0, 100.0)
        sleep_component = self._normalize(sleep_hours, 4.0, 9.0)
        recovery_score = (hr_component * 0.40) + (rmssd_component * 0.45) + (sleep_component * 0.15)
        return round(np.clip(recovery_score, 0, 100), 2)

    def calculate_neurocardiac_coupling_score(self, eeg_alpha_power: float, hrv_hf_power: float, signal_coherence: float) -> float:
        alpha_norm = self._normalize(eeg_alpha_power, 2.0, 30.0)
        hf_norm = self._normalize(hrv_hf_power, 50.0, 1000.0)
        coherence_norm = self._normalize(signal_coherence, 0.0, 1.0)
        coupling = (alpha_norm * 0.3) + (hf_norm * 0.3) + (coherence_norm * 0.4)
        return round(np.clip(coupling, 0, 100), 2)

    def calculate_cognitive_load_score(self, eeg_theta_power: float, eeg_alpha_power: float, hr_surge: float) -> float:
        theta_alpha_ratio = eeg_theta_power / max(eeg_alpha_power, 0.1)
        ratio_norm = self._normalize(theta_alpha_ratio, 0.5, 4.0)
        hr_surge_norm = self._normalize(hr_surge, 0.0, 30.0)
        cognitive_load = (ratio_norm * 0.7) + (hr_surge_norm * 0.3)
        return round(np.clip(cognitive_load, 0, 100), 2)

    def calculate_physiological_resilience_score(self, hr_recovery_rate: float, hrv_sdnn: float, metabolic_efficiency: float) -> float:
        hrr_norm = self._normalize(hr_recovery_rate, 15.0, 50.0)
        sdnn_norm = self._normalize(hrv_sdnn, 15.0, 150.0)
        metabolic_norm = self._normalize(metabolic_efficiency, 0.5, 1.5)
        resilience = (hrr_norm * 0.45) + (sdnn_norm * 0.35) + (metabolic_norm * 0.20)
        return round(np.clip(resilience, 0, 100), 2)

    def calculate_autonomic_stability_score(self, bp_variance: float, ppg_pulse_transit_time_var: float) -> float:
        bp_score = self._normalize(bp_variance, 2.0, 25.0, invert=True)
        ptt_score = self._normalize(ppg_pulse_transit_time_var, 5.0, 50.0, invert=True)
        stability = (bp_score * 0.5) + (ptt_score * 0.5)
        return round(np.clip(stability, 0, 100), 2)

    def calculate_learning_readiness_index(self, neurocardiac_coupling: float, sleep_recovery_score: float, eeg_beta_attenuation: float) -> float:
        beta_norm = self._normalize(eeg_beta_attenuation, 1.0, 10.0)
        readiness = (neurocardiac_coupling * 0.4) + (sleep_recovery_score * 0.4) + (beta_norm * 0.2)
        return round(np.clip(readiness, 0, 100), 2)

    def get_full_biomarker_suite(self, raw_metrics: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        hrv_lf_hf = raw_metrics.get('hrv_lf_hf_ratio', 1.5)
        eda_peaks = int(raw_metrics.get('eda_scr_peaks', 4))
        scl_us = raw_metrics.get('scl_u_siemens', 3.0)
        resting_hr = raw_metrics.get('current_resting_hr', 70.0)
        rmssd = raw_metrics.get('hrv_rmssd', 35.0)
        sleep = raw_metrics.get('sleep_hours', 7.0)
        eeg_alpha = raw_metrics.get('eeg_alpha_power', 12.0)
        eeg_theta = raw_metrics.get('eeg_theta_power', 8.0)
        eeg_coherence = raw_metrics.get('signal_coherence', 0.65)
        hrv_hf = raw_metrics.get('hrv_hf_power', 250.0)
        hr_surge = raw_metrics.get('hr_surge', 5.0)
        hr_recovery = raw_metrics.get('hr_recovery_rate', 25.0)
        sdnn = raw_metrics.get('hrv_sdnn', 45.0)
        metabolic = raw_metrics.get('metabolic_efficiency', 1.0)
        bp_var = raw_metrics.get('bp_variance', 5.0)
        ptt_var = raw_metrics.get('ppg_pulse_transit_time_var', 12.0)
        beta_atten = raw_metrics.get('eeg_beta_attenuation', 4.0)

        stress = self.calculate_stress_index(hrv_lf_hf, eda_peaks, scl_us)
        recovery = self.calculate_recovery_index(resting_hr, rmssd, sleep)
        coupling = self.calculate_neurocardiac_coupling_score(eeg_alpha, hrv_hf, eeg_coherence)
        cognitive = self.calculate_cognitive_load_score(eeg_theta, eeg_alpha, hr_surge)
        resilience = self.calculate_physiological_resilience_score(hr_recovery, sdnn, metabolic)
        stability = self.calculate_autonomic_stability_score(bp_var, ptt_var)
        readiness = self.calculate_learning_readiness_index(coupling, recovery, beta_atten)

        return {
            'Stress Index': {'score': stress, 'status': 'Alto' if stress > 65 else 'Moderado' if stress > 35 else 'Óptimo'},
            'Recovery Index': {'score': recovery, 'status': 'Bajo' if recovery < 45 else 'Bueno' if recovery < 75 else 'Excelente'},
            'NeuroCardiac Coupling Score': {'score': coupling, 'status': 'Sincronizado' if coupling > 60 else 'Asincrónico'},
            'Cognitive Load Score': {'score': cognitive, 'status': 'Sobrecarga' if cognitive > 70 else 'Normal'},
            'Physiological Resilience Score': {'score': resilience, 'status': 'Excelente' if resilience > 75 else 'Promedio'},
            'Autonomic Stability Score': {'score': stability, 'status': 'Estable' if stability > 55 else 'Inestable'},
            'Learning Readiness Index': {'score': readiness, 'status': 'Listo' if readiness > 65 else 'Fatigado'}
        }
    