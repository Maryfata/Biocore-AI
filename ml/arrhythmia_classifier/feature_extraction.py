"""
Feature Extraction Module

Extracts relevant features from ECG beats for arrhythmia classification.
Features include morphological, statistical, and frequency domain characteristics.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from scipy.signal import welch, find_peaks
from scipy.stats import skew, kurtosis
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class FeatureExtraction:
    """Extract features from ECG beats."""
    
    # Feature categories
    MORPHOLOGICAL_FEATURES = [
        'qrs_duration', 'st_elevation', 'r_peak_amplitude',
        'q_amplitude', 's_amplitude', 'qt_interval'
    ]
    
    STATISTICAL_FEATURES = [
        'mean', 'std', 'min', 'max', 'median', 'range',
        'skewness', 'kurtosis', 'energy'
    ]
    
    FREQUENCY_FEATURES = [
        'dominant_frequency', 'spectral_energy', 'spectral_entropy'
    ]
    
    def __init__(self, sampling_rate: int = 360):
        """
        Initialize feature extraction.
        
        Args:
            sampling_rate: ECG sampling rate in Hz
        """
        self.sampling_rate = sampling_rate
        self.all_features = self.MORPHOLOGICAL_FEATURES + self.STATISTICAL_FEATURES + self.FREQUENCY_FEATURES
        logger.info(f"FeatureExtraction initialized with {len(self.all_features)} features")
    
    def extract_morphological_features(self, beat: np.ndarray) -> Dict[str, float]:
        """
        Extract morphological features from beat.
        
        Args:
            beat: ECG beat signal
            
        Returns:
            Dictionary of morphological features
        """
        features = {}
        
        # Find peaks (positive peaks like R wave)
        peaks, peak_props = find_peaks(beat, distance=self.sampling_rate // 10)
        
        # Find troughs (negative peaks like Q, S waves)
        troughs, trough_props = find_peaks(-beat, distance=self.sampling_rate // 10)
        
        # QRS duration (simplification: width of main peak)
        if len(peaks) > 0:
            main_peak_idx = peaks[np.argmax(peak_props['peak_heights'])]
            # Find slopes around main peak
            left_slope = np.where(beat[:main_peak_idx] > np.max(beat) * 0.3)[0]
            right_slope = np.where(beat[main_peak_idx:] > np.max(beat) * 0.3)[0]
            qrs_samples = len(left_slope) + len(right_slope)
            features['qrs_duration'] = qrs_samples / self.sampling_rate * 1000  # ms
        else:
            features['qrs_duration'] = 0.0
        
        # ST elevation (mean value from 0.04-0.12s after R peak)
        r_peak_idx = np.argmax(np.abs(beat))
        st_start = int(r_peak_idx + 0.04 * self.sampling_rate)
        st_end = int(r_peak_idx + 0.12 * self.sampling_rate)
        if st_end <= len(beat):
            features['st_elevation'] = np.mean(beat[st_start:st_end])
        else:
            features['st_elevation'] = 0.0
        
        # R peak amplitude
        features['r_peak_amplitude'] = np.max(beat)
        
        # Q amplitude (first trough if exists)
        if len(troughs) > 0:
            features['q_amplitude'] = np.min(beat[troughs])
        else:
            features['q_amplitude'] = np.min(beat)
        
        # S amplitude (trough after R peak)
        s_candidates = troughs[troughs > r_peak_idx]
        if len(s_candidates) > 0:
            features['s_amplitude'] = beat[s_candidates[0]]
        else:
            features['s_amplitude'] = np.min(beat[r_peak_idx:])
        
        # QT interval (from Q to T, approximation)
        features['qt_interval'] = len(beat) / self.sampling_rate * 1000  # ms
        
        return features
    
    def extract_statistical_features(self, beat: np.ndarray) -> Dict[str, float]:
        """
        Extract statistical features from beat.
        
        Args:
            beat: ECG beat signal
            
        Returns:
            Dictionary of statistical features
        """
        features = {
            'mean': float(np.mean(beat)),
            'std': float(np.std(beat)),
            'min': float(np.min(beat)),
            'max': float(np.max(beat)),
            'median': float(np.median(beat)),
            'range': float(np.max(beat) - np.min(beat)),
            'skewness': float(skew(beat)),
            'kurtosis': float(kurtosis(beat)),
            'energy': float(np.sum(beat ** 2)),
        }
        return features
    
    def extract_frequency_features(self, beat: np.ndarray) -> Dict[str, float]:
        """
        Extract frequency domain features from beat.
        
        Args:
            beat: ECG beat signal
            
        Returns:
            Dictionary of frequency features
        """
        features = {}
        
        # Welch power spectral density
        f, Pxx = welch(beat, fs=self.sampling_rate, nperseg=min(256, len(beat)))
        
        # Dominant frequency
        dominant_freq_idx = np.argmax(Pxx)
        features['dominant_frequency'] = float(f[dominant_freq_idx])
        
        # Spectral energy (total power)
        features['spectral_energy'] = float(np.sum(Pxx))
        
        # Spectral entropy
        # Normalize power spectrum
        Pxx_normalized = Pxx / np.sum(Pxx)
        # Remove zeros for log calculation
        Pxx_normalized = Pxx_normalized[Pxx_normalized > 0]
        spectral_entropy = -np.sum(Pxx_normalized * np.log2(Pxx_normalized))
        features['spectral_entropy'] = float(spectral_entropy)
        
        return features
    
    def extract_all_features(self, beat: np.ndarray) -> Dict[str, float]:
        """
        Extract all features from beat.
        
        Args:
            beat: ECG beat signal
            
        Returns:
            Dictionary of all features
        """
        all_features = {}
        
        all_features.update(self.extract_morphological_features(beat))
        all_features.update(self.extract_statistical_features(beat))
        all_features.update(self.extract_frequency_features(beat))
        
        return all_features
    
    def extract_features_batch(self, beats: List[np.ndarray]) -> pd.DataFrame:
        """
        Extract features from multiple beats.
        
        Args:
            beats: List of ECG beats
            
        Returns:
            DataFrame with features (rows=beats, columns=features)
        """
        features_list = []
        
        for beat in beats:
            if len(beat) > 0:
                features = self.extract_all_features(beat)
                features_list.append(features)
        
        df = pd.DataFrame(features_list)
        logger.info(f"Extracted features from {len(beats)} beats: {df.shape}")
        
        return df
    
    def normalize_features(self, X_train: pd.DataFrame,
                          X_test: Optional[pd.DataFrame] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
        """
        Normalize features using Z-score normalization.
        
        Args:
            X_train: Training features
            X_test: Optional test features
            
        Returns:
            (normalized_X_train, normalized_X_test or None)
        """
        means = X_train.mean()
        stds = X_train.std()
        stds = stds.replace(0, 1)  # Avoid division by zero
        
        X_train_normalized = (X_train - means) / stds
        
        if X_test is not None:
            X_test_normalized = (X_test - means) / stds
        else:
            X_test_normalized = None
        
        return X_train_normalized, X_test_normalized
    
    def validate_features(self, features_df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate extracted features.
        
        Args:
            features_df: DataFrame of extracted features
            
        Returns:
            (is_valid, message)
        """
        if features_df is None or features_df.empty:
            return False, "Features DataFrame is empty"
        
        if features_df.isnull().any().any():
            null_cols = features_df.columns[features_df.isnull().any()].tolist()
            return False, f"Null values in columns: {null_cols}"
        
        if (features_df == np.inf).any().any() or (features_df == -np.inf).any().any():
            return False, "Infinite values in features"
        
        expected_cols = len(self.all_features)
        if len(features_df.columns) != expected_cols:
            return False, f"Expected {expected_cols} features, got {len(features_df.columns)}"
        
        return True, f"Valid: {features_df.shape[0]} samples, {features_df.shape[1]} features"
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names."""
        return self.all_features
