"""Advanced clinical ECG analysis with PQRST detection and measurements."""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Any

import numpy as np
from scipy.signal import find_peaks, savgol_filter


class ECGAnalyzer:
    """Professional ECG analysis engine for clinical interpretation."""
    
    def __init__(self, fs: float = 250.0):
        """
        Initialize ECG analyzer.
        
        Parameters
        ----------
        fs : float
            Sampling frequency in Hz
        """
        self.fs = fs
    
    def detect_r_peaks(
        self,
        signal: np.ndarray,
        prominence_factor: float = 0.3
    ) -> np.ndarray:
        """
        Detect R peaks (QRS complexes) in ECG signal.
        
        Parameters
        ----------
        signal : ndarray
            ECG signal in mV
        prominence_factor : float
            Prominence threshold factor
            
        Returns
        -------
        peaks : ndarray
            Indices of detected R peaks
        """
        threshold = np.mean(signal) + prominence_factor * np.std(signal)
        peaks, _ = find_peaks(
            signal,
            distance=int(0.3 * self.fs),
            height=threshold
        )
        return peaks
    
    def segment_qrs_complex(
        self,
        signal: np.ndarray,
        r_peak: int,
        window: float = 0.12
    ) -> Tuple[int, int]:
        """
        Segment QRS complex around R peak.
        
        Parameters
        ----------
        signal : ndarray
            ECG signal
        r_peak : int
            Index of R peak
        window : float
            Window width in seconds
            
        Returns
        -------
        q_idx : int
            Index of Q point (start of QRS)
        s_idx : int
            Index of S point (end of QRS)
        """
        half_window = int(window * self.fs / 2)
        start = max(0, r_peak - half_window)
        end = min(len(signal), r_peak + half_window)
        
        segment = signal[start:end]
        q_idx = np.argmin(segment)
        s_idx = np.argmin(segment[r_peak - start:]) + (r_peak - start)
        
        return start + q_idx, start + s_idx
    
    def detect_pqrst(
        self,
        signal: np.ndarray
    ) -> Dict[str, Dict[str, Any]]:
        """
        Detect P, QRS, and T waves in ECG signal.
        
        Uses template matching and morphological analysis.
        
        Returns
        -------
        dict
            Detected waves with indices, amplitudes, and durations
        """
        r_peaks = self.detect_r_peaks(signal)
        
        if len(r_peaks) == 0:
            return {}
        
        waves = {}
        
        for idx, r_peak in enumerate(r_peaks[:5]):
            beat_label = f'beat_{idx}'
            
            q_idx, s_idx = self.segment_qrs_complex(signal, r_peak)
            
            p_start = max(0, r_peak - int(0.16 * self.fs))
            p_end = q_idx
            p_segment = signal[p_start:p_end]
            p_idx = p_start + np.argmax(np.abs(p_segment))
            
            t_start = s_idx
            t_end = min(len(signal), r_peak + int(0.36 * self.fs))
            t_segment = signal[t_start:t_end]
            t_idx = t_start + np.argmax(np.abs(t_segment))
            
            waves[beat_label] = {
                'P': {'index': p_idx, 'amplitude': float(signal[p_idx])},
                'Q': {'index': q_idx, 'amplitude': float(signal[q_idx])},
                'R': {'index': r_peak, 'amplitude': float(signal[r_peak])},
                'S': {'index': s_idx, 'amplitude': float(signal[s_idx])},
                'T': {'index': t_idx, 'amplitude': float(signal[t_idx])}
            }
        
        return waves
    
    def measure_intervals(
        self,
        signal: np.ndarray
    ) -> Dict[str, float]:
        """
        Measure diagnostic ECG intervals in milliseconds.
        
        Returns
        -------
        dict
            PR, QRS, QT, QTc intervals
        """
        r_peaks = self.detect_r_peaks(signal)
        
        if len(r_peaks) < 1:
            return {}
        
        measurements = {}
        
        r_peak = r_peaks[0]
        q_idx, s_idx = self.segment_qrs_complex(signal, r_peak)
        
        p_start = max(0, r_peak - int(0.16 * self.fs))
        p_segment = signal[p_start:q_idx]
        p_idx = p_start + np.argmax(np.abs(p_segment))
        
        t_end = min(len(signal), r_peak + int(0.40 * self.fs))
        t_segment = signal[s_idx:t_end]
        t_idx = s_idx + np.argmax(np.abs(t_segment))
        
        pr_interval = (r_peak - p_idx) / self.fs * 1000
        qrs_duration = (s_idx - q_idx) / self.fs * 1000
        qt_interval = (t_idx - q_idx) / self.fs * 1000
        
        mean_rr = np.mean(np.diff(r_peaks) / self.fs) if len(r_peaks) > 1 else 1.0
        
        qtc = qt_interval / np.sqrt(mean_rr) if mean_rr > 0 else qt_interval
        
        measurements = {
            'PR_interval_ms': float(np.clip(pr_interval, 0, 300)),
            'QRS_duration_ms': float(np.clip(qrs_duration, 0, 200)),
            'QT_interval_ms': float(np.clip(qt_interval, 0, 600)),
            'QTc_ms': float(np.clip(qtc, 0, 600)),
            'RR_interval_ms': float(mean_rr * 1000)
        }
        
        return measurements
    
    def detect_st_elevation(
        self,
        signal: np.ndarray,
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Detect ST segment elevation (STEMI indicator).
        
        Parameters
        ----------
        signal : ndarray
            ECG signal in mV
        threshold : float
            Elevation threshold in mV
            
        Returns
        -------
        dict
            ST elevation analysis results
        """
        r_peaks = self.detect_r_peaks(signal)
        
        if len(r_peaks) == 0:
            return {'st_elevation_detected': False, 'elevation_magnitude': 0.0}
        
        st_points = []
        for r_peak in r_peaks[:5]:
            st_idx = min(len(signal) - 1, r_peak + int(0.08 * self.fs))
            st_points.append(signal[st_idx])
        
        mean_st = np.mean(st_points)
        baseline = np.median(signal)
        elevation = mean_st - baseline
        
        return {
            'st_elevation_detected': elevation > threshold,
            'elevation_magnitude': float(elevation),
            'elevation_threshold': threshold
        }
    
    def estimate_heart_rate(self, r_peaks: np.ndarray) -> float:
        """Estimate heart rate from R peaks."""
        if len(r_peaks) < 2:
            return 0.0
        
        rr_intervals = np.diff(r_peaks) / self.fs
        return 60.0 / np.mean(rr_intervals) if len(rr_intervals) > 0 else 0.0
    
    def detect_arrhythmias(self, signal: np.ndarray) -> Dict[str, Any]:
        """
        Detect common arrhythmias from ECG.
        
        Detects: tachycardia, bradycardia, irregular rhythm, PVC, AFib indicators
        """
        r_peaks = self.detect_r_peaks(signal)
        
        if len(r_peaks) < 2:
            return {'status': 'insufficient_data'}
        
        rr_intervals = np.diff(r_peaks) / self.fs
        hr = 60.0 / np.mean(rr_intervals)
        
        rr_variance = np.var(rr_intervals)
        rr_cv = np.std(rr_intervals) / np.mean(rr_intervals)
        
        findings = {
            'heart_rate': float(hr),
            'arrhythmias': []
        }
        
        if hr > 100:
            findings['arrhythmias'].append('Tachycardia')
        elif hr < 60:
            findings['arrhythmias'].append('Bradycardia')
        
        if rr_cv > 0.15:
            findings['arrhythmias'].append('Irregular rhythm')
        
        if np.any(np.diff(rr_intervals) / np.mean(rr_intervals) > 0.3):
            findings['arrhythmias'].append('Ectopic beats (possible PVC)')
        
        rr_std = np.std(rr_intervals)
        if rr_std > 0.15 and hr > 90:
            findings['arrhythmias'].append('Possible atrial fibrillation')

        return findings
    
    def detect_clinical_pattern(
        self,
        signal: np.ndarray
    ) -> Dict[str, Any]:
        """
        Detect a clinical ECG pattern and assign a multiclass cardiology label.
        """
        r_peaks = self.detect_r_peaks(signal)
        intervals = self.measure_intervals(signal)
        st_info = self.detect_st_elevation(signal)
        arrhythmias = self.detect_arrhythmias(signal)

        pattern = "Normal Sinus Rhythm"
        confidence = 0.60
        details: List[str] = []

        hr = arrhythmias.get('heart_rate', 0.0)
        qrs = intervals.get('QRS_duration_ms', 0.0)
        pr = intervals.get('PR_interval_ms', 0.0)
        qtc = intervals.get('QTc_ms', 0.0)
        rr_intervals = np.diff(r_peaks) / self.fs if len(r_peaks) > 1 else np.array([])
        rr_cv = float(np.std(rr_intervals) / np.mean(rr_intervals)) if rr_intervals.size > 1 else 0.0

        if st_info.get('st_elevation_detected', False):
            pattern = "STEMI"
            confidence = 0.95
            details.append(f"ST elevation {st_info.get('elevation_magnitude', 0.0):.2f} mV")
        elif 'Possible atrial fibrillation' in arrhythmias.get('arrhythmias', []):
            pattern = "AFib"
            confidence = 0.92
            details.append("Irregularly irregular RR intervals")
        elif any('Ectopic beats' in x for x in arrhythmias.get('arrhythmias', [])):
            pattern = "PVC"
            confidence = 0.83
            details.append("Ectopic ventricular beats detected")
        elif hr > 120 and qrs > 110:
            pattern = "VT"
            confidence = 0.90
            details.append("Sustained fast rate with wide QRS")
        elif qrs > 120 and hr >= 40 and hr <= 110:
            if pr < 200:
                pattern = "LBBB" if np.mean(signal[: min(10, len(signal))]) > np.mean(signal[-min(10, len(signal)):]) else "RBBB"
                confidence = 0.78
                details.append("Wide QRS compatible with bundle branch block")
            else:
                pattern = "AV Block"
                confidence = 0.80
                details.append("PR prolongation and conduction delay")
        elif pr > 210:
            pattern = "AV Block"
            confidence = 0.85
            details.append("Prolonged PR interval")
        elif qtc > 470:
            pattern = "Long QT / Risk"
            confidence = 0.70
            details.append("Prolonged QTc detected")
        elif qrs > 120:
            pattern = "Bundle Branch Block"
            confidence = 0.72
            details.append("Wide QRS detected")

        if len(r_peaks) < 3:
            confidence = max(confidence - 0.15, 0.35)
            details.append("Datos limitados para clasificación")

        return {
            'pattern': pattern,
            'confidence': float(np.clip(confidence, 0.0, 1.0)),
            'reasoning': details,
            'features': {
                'heart_rate': float(hr),
                'qrs_duration_ms': float(qrs),
                'pr_interval_ms': float(pr),
                'qtc_ms': float(qtc),
                'rr_cv': float(rr_cv)
            }
        }

    def compute_heart_rate_variability(
        self,
        r_peaks: np.ndarray
    ) -> Dict[str, float]:
        """
        Compute HRV metrics from R peaks.
        
        Returns temporal and frequency domain indices.
        """
        if len(r_peaks) < 2:
            return {}
        
        rr_intervals = np.diff(r_peaks) / self.fs
        
        sdnn = float(np.std(rr_intervals))
        rmssd = float(np.sqrt(np.mean(np.diff(rr_intervals) ** 2)))
        nn50 = float(np.sum(np.abs(np.diff(rr_intervals)) > 0.05))
        pnn50 = float(100 * nn50 / len(rr_intervals)) if len(rr_intervals) > 0 else 0.0
        
        from scipy.fft import fft
        
        frequencies = np.fft.fftfreq(len(rr_intervals), np.mean(np.diff(r_peaks)) / self.fs)
        power = np.abs(fft(rr_intervals)) ** 2
        
        power = power[frequencies > 0]
        frequencies = frequencies[frequencies > 0]
        
        vlf = float(np.sum(power[(frequencies >= 0.003) & (frequencies < 0.04)]))
        lf = float(np.sum(power[(frequencies >= 0.04) & (frequencies < 0.15)]))
        hf = float(np.sum(power[(frequencies >= 0.15) & (frequencies <= 0.4)]))
        
        lf_hf = float(lf / hf) if hf > 0 else 0.0
        
        return {
            'SDNN_s': sdnn,
            'RMSSD_s': rmssd,
            'pNN50_%': pnn50,
            'VLF_power': vlf,
            'LF_power': lf,
            'HF_power': hf,
            'LF_HF_ratio': lf_hf,
            'total_power': vlf + lf + hf
        }
    
    def clinical_summary(self, signal: np.ndarray) -> str:
        """Generate clinical ECG summary."""
        r_peaks = self.detect_r_peaks(signal)

        if len(r_peaks) < 1:
            return "ECG: Insufficient signal quality for analysis"

        hr = self.estimate_heart_rate(r_peaks)
        intervals = self.measure_intervals(signal)
        st_elevation = self.detect_st_elevation(signal)
        arrhythmias = self.detect_arrhythmias(signal)
        pattern_info = self.detect_clinical_pattern(signal)

        recommendations = "Correlacionar hallazgos ECG con datos clínicos y considerar derivación cardiológica."
        if pattern_info['pattern'] == 'STEMI':
            recommendations = "Activar protocolo STEMI y priorizar reperfusión inmediata."
        elif pattern_info['pattern'] == 'AFib':
            recommendations = "Evaluar control de frecuencia y considerar anticoagulación según CHA2DS2-VASc."
        elif pattern_info['pattern'] == 'PVC':
            recommendations = "Valorar ecocardiograma y seguimiento de ectopias si son frecuentes o sintomáticas."
        elif pattern_info['pattern'] == 'VT':
            recommendations = "Iniciar manejo urgente de taquiarritmia ventricular y considerar soporte avanzado."
        elif pattern_info['pattern'] in ('LBBB', 'RBBB'):
            recommendations = "Investigar enfermedad estructural subyacente y correlacionar con síntomas."
        elif pattern_info['pattern'] == 'AV Block':
            recommendations = "Evaluar grado de bloqueo y considerar marcapasos si es sintomático."

        findings = arrhythmias.get('arrhythmias', ['Regular sinus rhythm'])
        if findings == ['Regular sinus rhythm']:
            findings = ['Regular sinus rhythm']

        summary = f"""
╔════════════════════════════════════════════════╗
║         ECG CLINICAL SUMMARY                   ║
╚════════════════════════════════════════════════╝

RHYTHM & RATE:
  • Heart Rate: {hr:.0f} bpm

INTERVALS (normal ranges):
  • PR: {intervals.get('PR_interval_ms', 0):.0f} ms (120-200)
  • QRS: {intervals.get('QRS_duration_ms', 0):.0f} ms (<120)
  • QT: {intervals.get('QT_interval_ms', 0):.0f} ms
  • QTc: {intervals.get('QTc_ms', 0):.0f} ms (<440 male, <460 female)

ST SEGMENT:
  • Elevation: {st_elevation.get('elevation_magnitude', 0):.2f} mV
  • Status: {'ELEVATED' if st_elevation['st_elevation_detected'] else 'Normal'}

FINDINGS:
  • {', '.join(findings)}

CLASSIFICATION:
  • Pattern detected: {pattern_info['pattern']}
  • Confidence: {pattern_info['confidence']*100:.0f}%
  • Reasoning: {', '.join(pattern_info.get('reasoning', ['Revisión completa recomendada']))}

RECOMMENDATIONS:
  • {recommendations}

╔════════════════════════════════════════════════╗
"""
        return summary


