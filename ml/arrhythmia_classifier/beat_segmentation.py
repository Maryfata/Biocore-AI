"""
Beat Segmentation Module

Detects R peaks and segments ECG signal into individual beats.
Uses standard ECG analysis techniques.
"""

from typing import List, Tuple, Optional
import numpy as np
from scipy.signal import find_peaks, butter, filtfilt
import logging

logger = logging.getLogger(__name__)


class BeatSegmentation:
    """ECG beat segmentation using R-peak detection."""
    
    def __init__(self, sampling_rate: int = 360, beat_length_ms: int = 600):
        """
        Initialize beat segmentation.
        
        Args:
            sampling_rate: ECG sampling rate in Hz
            beat_length_ms: Beat window length in milliseconds
        """
        self.sampling_rate = sampling_rate
        self.beat_length_ms = beat_length_ms
        self.beat_length = int(beat_length_ms / 1000 * sampling_rate)  # Convert to samples
        
        logger.info(f"BeatSegmentation initialized: {sampling_rate}Hz, {beat_length_ms}ms window")
    
    def preprocess_signal(self, signal: np.ndarray) -> np.ndarray:
        """
        Preprocess ECG signal for R-peak detection.
        
        Steps:
        1. Bandpass filter (5-15 Hz)
        2. Square the signal
        3. Apply moving average
        
        Args:
            signal: Raw ECG signal
            
        Returns:
            Preprocessed signal
        """
        # Bandpass filter 5-15 Hz
        sos = butter(4, [5, 15], 'bandpass', fs=self.sampling_rate, output='sos')
        filtered = filtfilt(sos, signal)
        
        # Square
        squared = filtered ** 2
        
        # Moving average (120ms window)
        window_size = int(0.12 * self.sampling_rate)
        averaged = np.convolve(squared, np.ones(window_size) / window_size, mode='same')
        
        return averaged
    
    def detect_r_peaks(self, signal: np.ndarray, min_distance: Optional[int] = None) -> np.ndarray:
        """
        Detect R peaks in ECG signal.
        
        Args:
            signal: ECG signal
            min_distance: Minimum distance between peaks (samples).
                         If None, uses 0.4s at sampling rate (240 samples @ 360Hz)
            
        Returns:
            Array of R peak indices
        """
        if min_distance is None:
            min_distance = int(0.4 * self.sampling_rate)  # 400ms minimum between beats
        
        # Preprocess signal
        processed = self.preprocess_signal(signal)
        
        # Find peaks
        peaks, _ = find_peaks(processed, distance=min_distance, height=np.max(processed) * 0.3)
        
        logger.info(f"Detected {len(peaks)} R peaks")
        return peaks
    
    def segment_beats(self, signal: np.ndarray, r_peaks: np.ndarray,
                      pre_samples: Optional[int] = None,
                      post_samples: Optional[int] = None) -> List[Tuple[np.ndarray, int]]:
        """
        Segment ECG signal into individual beats centered on R peaks.
        
        Args:
            signal: ECG signal
            r_peaks: R peak indices
            pre_samples: Samples before R peak (default: 0.2 * sampling_rate)
            post_samples: Samples after R peak (default: 0.4 * sampling_rate)
            
        Returns:
            List of (beat_signal, r_peak_index) tuples
        """
        if pre_samples is None:
            pre_samples = int(0.2 * self.sampling_rate)  # 200ms
        if post_samples is None:
            post_samples = int(0.4 * self.sampling_rate)  # 400ms
        
        beats = []
        
        for r_peak in r_peaks:
            start = max(0, r_peak - pre_samples)
            end = min(len(signal), r_peak + post_samples)
            
            beat_signal = signal[start:end].copy()
            
            # Pad if necessary
            if len(beat_signal) < self.beat_length:
                pad_width = self.beat_length - len(beat_signal)
                beat_signal = np.pad(beat_signal, (0, pad_width), mode='constant')
            elif len(beat_signal) > self.beat_length:
                beat_signal = beat_signal[:self.beat_length]
            
            beats.append((beat_signal, r_peak))
        
        logger.info(f"Segmented {len(beats)} beats from signal")
        return beats
    
    def segment_ecg(self, signal: np.ndarray) -> Tuple[List[np.ndarray], np.ndarray]:
        """
        Complete beat segmentation pipeline.
        
        Args:
            signal: ECG signal
            
        Returns:
            (beat_signals, r_peaks)
        """
        r_peaks = self.detect_r_peaks(signal)
        beat_segments = self.segment_beats(signal, r_peaks)
        
        beat_signals = [beat[0] for beat in beat_segments]
        r_peaks_final = np.array([beat[1] for beat in beat_segments])
        
        return beat_signals, r_peaks_final
    
    def validate_segmentation(self, beats: List[np.ndarray]) -> Tuple[bool, str]:
        """
        Validate beat segmentation results.
        
        Args:
            beats: List of beat signals
            
        Returns:
            (is_valid, message)
        """
        if not beats:
            return False, "No beats segmented"
        
        if len(beats) < 5:
            return False, f"Too few beats: {len(beats)} (min 5)"
        
        for beat in beats:
            if not isinstance(beat, np.ndarray):
                return False, "Beat is not numpy array"
            if len(beat) == 0:
                return False, "Empty beat signal"
            if not np.isfinite(beat).all():
                return False, "Beat contains NaN or infinite values"
        
        return True, f"Valid: {len(beats)} beats segmented"
