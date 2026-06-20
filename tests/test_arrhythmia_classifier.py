"""
Test Suite - Arrhythmia Classifier

Comprehensive unit tests for all components.

Usage:
    pytest test_arrhythmia_classifier.py -v
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import unittest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from biomedical.arrhythmia_classifier import (
    ArrhythmiaClassifier,
    BeatSegmentation,
    FeatureExtraction,
    ArrhythmiaClass,
    ECGBeat,
    ClassificationResult,
    ModelType,
)


class TestBeatSegmentation(unittest.TestCase):
    """Test beat segmentation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.segmentation = BeatSegmentation(sampling_rate=360)
        self.sampling_rate = 360
    
    def test_detect_r_peaks(self):
        """Test R peak detection."""
        # Create synthetic signal with clear R peaks
        t = np.linspace(0, 5, 5 * self.sampling_rate)
        signal = np.sin(2 * np.pi * 1.2 * t)  # 1.2 Hz = ~70 BPM
        
        r_peaks = self.segmentation.detect_r_peaks(signal)
        
        self.assertGreater(len(r_peaks), 0, "Should detect at least one R peak")
    
    def test_segment_beats(self):
        """Test beat segmentation."""
        t = np.linspace(0, 5, 5 * self.sampling_rate)
        signal = np.sin(2 * np.pi * 1.2 * t)
        
        r_peaks = np.array([360, 660, 960, 1260])
        beats = self.segmentation.segment_beats(signal, r_peaks)
        
        self.assertEqual(len(beats), len(r_peaks))
        for beat, _ in beats:
            self.assertGreater(len(beat), 0)
    
    def test_validate_segmentation(self):
        """Test segmentation validation."""
        beat_signal = np.random.randn(216)
        beats = [beat_signal] * 10
        
        is_valid, msg = self.segmentation.validate_segmentation(beats)
        self.assertTrue(is_valid)


class TestFeatureExtraction(unittest.TestCase):
    """Test feature extraction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.feature_extractor = FeatureExtraction(sampling_rate=360)
    
    def test_extract_morphological_features(self):
        """Test morphological feature extraction."""
        beat = np.random.randn(216)
        
        features = self.feature_extractor.extract_morphological_features(beat)
        
        self.assertIn('qrs_duration', features)
        self.assertIn('r_peak_amplitude', features)
        self.assertGreater(len(features), 0)
    
    def test_extract_statistical_features(self):
        """Test statistical feature extraction."""
        beat = np.random.randn(216)
        
        features = self.feature_extractor.extract_statistical_features(beat)
        
        self.assertIn('mean', features)
        self.assertIn('std', features)
        self.assertIn('energy', features)
        self.assertEqual(len(features), 9)
    
    def test_extract_frequency_features(self):
        """Test frequency feature extraction."""
        t = np.linspace(0, 0.6, 216)
        beat = np.sin(2 * np.pi * 5 * t)  # 5 Hz component
        
        features = self.feature_extractor.extract_frequency_features(beat)
        
        self.assertIn('dominant_frequency', features)
        self.assertIn('spectral_energy', features)
        self.assertGreater(features['spectral_energy'], 0)
    
    def test_extract_all_features(self):
        """Test complete feature extraction."""
        beat = np.random.randn(216)
        
        features = self.feature_extractor.extract_all_features(beat)
        
        expected_features = len(self.feature_extractor.all_features)
        self.assertEqual(len(features), expected_features)
    
    def test_extract_features_batch(self):
        """Test batch feature extraction."""
        beats = [np.random.randn(216) for _ in range(10)]
        
        df = self.feature_extractor.extract_features_batch(beats)
        
        self.assertEqual(df.shape[0], 10)
        self.assertEqual(df.shape[1], len(self.feature_extractor.all_features))
    
    def test_normalize_features(self):
        """Test feature normalization."""
        X_train = pd.DataFrame(np.random.randn(50, 10) * 100)
        X_test = pd.DataFrame(np.random.randn(10, 10) * 100)
        
        X_train_norm, X_test_norm = self.feature_extractor.normalize_features(X_train, X_test)
        
        # Check normalization
        self.assertAlmostEqual(X_train_norm.mean().mean(), 0, places=5)
        self.assertAlmostEqual(X_train_norm.std().mean(), 1, places=5)


class TestArrhythmiaClassifier(unittest.TestCase):
    """Test main classifier."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.classifier = ArrhythmiaClassifier()
    
    def test_get_class_name(self):
        """Test getting class name."""
        name = self.classifier.get_class_name(ArrhythmiaClass.NORMAL)
        self.assertEqual(name, "Normal")
        
        name = self.classifier.get_class_name(ArrhythmiaClass.PVC)
        self.assertEqual(name, "Premature Ventricular Contraction")
    
    def test_get_class_description(self):
        """Test getting class description."""
        desc = self.classifier.get_class_description(ArrhythmiaClass.NORMAL)
        self.assertIsNotNone(desc)
        self.assertGreater(len(desc), 0)
    
    def test_validate_beat(self):
        """Test beat validation."""
        beat = ECGBeat(signal=np.random.randn(216), label=ArrhythmiaClass.NORMAL)
        is_valid, msg = self.classifier.validate_beat(beat)
        self.assertTrue(is_valid)
        
        # Invalid beat
        beat_invalid = ECGBeat(signal=np.array([]), label=ArrhythmiaClass.NORMAL)
        is_valid, msg = self.classifier.validate_beat(beat_invalid)
        self.assertFalse(is_valid)
    
    def test_classification_result_to_dict(self):
        """Test result serialization."""
        from datetime import datetime
        
        result = ClassificationResult(
            predicted_class=ArrhythmiaClass.NORMAL,
            confidence=0.95,
            probabilities={'NORMAL': 0.95, 'PVC': 0.05},
            features_used=25,
            model_type=ModelType.RANDOM_FOREST,
            timestamp=datetime.now()
        )
        
        result_dict = result.to_dict()
        
        self.assertIn('predicted_class', result_dict)
        self.assertIn('confidence', result_dict)
        self.assertEqual(result_dict['predicted_class'], 'NORMAL')


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_full_pipeline(self):
        """Test complete pipeline."""
        from train_arrhythmia_classifier import generate_synthetic_beats
        
        # Generate beats
        beats, labels = generate_synthetic_beats(num_samples_per_class=5)
        self.assertGreater(len(beats), 0)
        
        # Segment
        segmentation = BeatSegmentation()
        is_valid, msg = segmentation.validate_segmentation(beats)
        self.assertTrue(is_valid)
        
        # Extract features
        feature_extractor = FeatureExtraction()
        features_df = feature_extractor.extract_features_batch(beats)
        is_valid, msg = feature_extractor.validate_features(features_df)
        self.assertTrue(is_valid)


if __name__ == '__main__':
    unittest.main()
