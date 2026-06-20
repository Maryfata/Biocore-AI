import os
import sys
import numpy as np

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.signal_generator import ECGGenerator


def get_arrhythmia_types() -> list[str]:
    return [
        'ritmo_sinusal_normal',
        'taquicardia',
        'bradicardia',
        'fibrilacion_auricular',
        'taquicardia_ventricular',
        'stemi'
    ]


def generate_ecg_case(case_type: str, duration: float, fs: int, noise: float, heart_rate: float):
    if case_type == 'ritmo_sinusal_normal':
        return ECGGenerator.generate_base_ecg(duration, fs, heart_rate, noise)
    if case_type == 'taquicardia':
        return ECGGenerator.generate_base_ecg(duration, fs, max(110, heart_rate), noise)
    if case_type == 'bradicardia':
        return ECGGenerator.generate_base_ecg(duration, fs, min(55, heart_rate), noise)
    if case_type == 'fibrilacion_auricular':
        return ECGGenerator.generate_afib(duration, fs, avg_hr=max(90, heart_rate))
    if case_type == 'taquicardia_ventricular':
        return ECGGenerator.generate_vt(duration, fs, hr=max(150, heart_rate))
    if case_type == 'stemi':
        return ECGGenerator.generate_stemi(duration, fs, max(70, heart_rate))
    return ECGGenerator.generate_base_ecg(duration, fs, heart_rate, noise)


def _detect_peaks(signal: np.ndarray, fs: int) -> np.ndarray:
    if len(signal) < 5:
        return np.array([], dtype=int)

    local_max = (signal[1:-1] > signal[:-2]) & (signal[1:-1] >= signal[2:])
    threshold = np.mean(signal) + 0.35 * np.std(signal)
    peak_indices = np.where(local_max & (signal[1:-1] >= threshold))[0] + 1
    if len(peak_indices) == 0:
        peak_indices = np.array([np.argmax(signal)])
    return peak_indices


def compute_rr_intervals(peaks: np.ndarray, fs: int) -> np.ndarray:
    if len(peaks) < 2:
        return np.array([])
    rr = np.diff(peaks) / fs
    return rr


def compute_hrv_metrics(signal: np.ndarray, fs: int) -> dict:
    peaks = _detect_peaks(signal, fs)
    rr = compute_rr_intervals(peaks, fs)

    if len(rr) == 0:
        return {
            'BPM': 0.0,
            'RR': [],
            'SDNN': 0.0,
            'RMSSD': 0.0,
            'LF_HF': 0.0,
            'QT': 0.36,
            'QTc': 0.36
        }

    bpm = 60.0 / np.mean(rr)
    sdnn = float(np.std(rr, ddof=1)) if len(rr) > 1 else float(np.std(rr))
    rmssd = float(np.sqrt(np.mean(np.diff(rr) ** 2))) if len(rr) > 1 else 0.0

    freqs = np.fft.rfftfreq(len(rr), d=1.0)
    power = np.abs(np.fft.rfft(rr - np.mean(rr))) ** 2
    lf = np.trapz(power[(freqs >= 0.04) & (freqs <= 0.15)], freqs[(freqs >= 0.04) & (freqs <= 0.15)])
    hf = np.trapz(power[(freqs >= 0.15) & (freqs <= 0.4)], freqs[(freqs >= 0.15) & (freqs <= 0.4)])

    lf_hf = float(lf / hf) if hf > 0 else float(lf)
    qt = 0.36
    qtc = float(qt / np.sqrt(np.mean(rr))) if np.mean(rr) > 0 else qt

    return {
        'BPM': float(np.clip(bpm, 25.0, 220.0)),
        'RR': rr.tolist(),
        'SDNN': round(sdnn, 4),
        'RMSSD': round(rmssd, 4),
        'LF_HF': round(lf_hf, 2),
        'QT': round(qt, 3),
        'QTc': round(qtc, 3)
    }
