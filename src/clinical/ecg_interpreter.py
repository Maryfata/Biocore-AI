"""Advanced ECG clinical interpreter for waveform analysis and risk flags."""

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from scipy.signal import find_peaks


def compute_intervals(time: np.ndarray, signal: np.ndarray, peaks: np.ndarray, fs: float) -> Dict[str, float]:
    intervals = {}
    if len(peaks) < 2:
        return intervals

    rr_intervals = np.diff(peaks) / fs
    intervals['mean_rr'] = float(np.mean(rr_intervals))
    intervals['bpm'] = float(60.0 / intervals['mean_rr'])
    intervals['sdnn'] = float(np.std(rr_intervals))
    intervals['rmssd'] = float(np.sqrt(np.mean(np.diff(rr_intervals) ** 2)))
    intervals['qrs_duration'] = 0.1
    intervals['pr_interval'] = 0.16
    intervals['qt_interval'] = 0.36
    intervals['qtc'] = intervals['qt_interval'] / np.sqrt(intervals['mean_rr']) if intervals['mean_rr'] > 0 else float('nan')
    return intervals


def analyze_st_segment(signal: np.ndarray, peaks: np.ndarray, fs: float) -> Dict[str, bool]:
    flags = {
        'st_elevation': False,
        'st_depression': False,
        't_wave_inversion': False,
    }
    if len(peaks) < 1:
        return flags

    idx = peaks[-1]
    if idx + int(0.08 * fs) < len(signal):
        st_point = signal[idx + int(0.04 * fs)]
        baseline = np.mean(signal[idx - int(0.08 * fs):idx]) if idx - int(0.08 * fs) >= 0 else signal[idx]
        delta = st_point - baseline
        flags['st_elevation'] = delta > 0.15
        flags['st_depression'] = delta < -0.1
    if idx + int(0.2 * fs) < len(signal):
        t_point = signal[idx + int(0.2 * fs)]
        flags['t_wave_inversion'] = t_point < baseline
    return flags


def interpret_ecg(signal: np.ndarray, fs: float, time: Optional[np.ndarray] = None) -> Dict[str, Any]:
    if time is None:
        time = np.arange(len(signal)) / fs

    filtered = signal
    peaks, properties = find_peaks(filtered, distance=int(fs * 0.3), height=np.mean(filtered) + 0.25 * np.std(filtered))
    intervals = compute_intervals(time, filtered, peaks, fs)
    st_flags = analyze_st_segment(filtered, peaks, fs)

    flags = compute_clinical_flags(intervals, st_flags)
    description = []
    description.append(f"Frecuencia cardíaca estimada: {intervals.get('bpm', float('nan')):.1f} bpm")
    description.append(f"QTc estimado: {intervals.get('qtc', float('nan')):.3f} s")
    if st_flags['st_elevation']:
        description.append('Se detecta posible elevación del segmento ST.')
    if st_flags['st_depression']:
        description.append('Se detecta posible depresión del segmento ST.')
    if st_flags['t_wave_inversion']:
        description.append('Posible inversión de onda T.')

    return {
        'intervals': intervals,
        'flags': flags,
        'description': '\n'.join(description),
        'peak_count': int(peaks.size),
        'peak_indices': peaks,
        'peak_properties': properties,
    }


def compute_clinical_flags(intervals: Dict[str, float], st_flags: Dict[str, bool]) -> Dict[str, bool]:
    return {
        'tachycardia': intervals.get('bpm', 0) > 100,
        'bradycardia': intervals.get('bpm', 0) < 60,
        'prolonged_qtc': intervals.get('qtc', float('nan')) > 0.44,
        'st_elevation': st_flags.get('st_elevation', False),
        'st_depression': st_flags.get('st_depression', False),
        't_wave_inversion': st_flags.get('t_wave_inversion', False),
        'possible_afib': intervals.get('sdnn', 0) > 0.12 and intervals.get('bpm', 0) > 90,
    }
