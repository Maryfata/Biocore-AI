"""
Training Script - Arrhythmia Classifier

Generates synthetic MIT-BIH-like dataset and trains all three models.
Demonstrates complete training pipeline.

Usage:
    python train_arrhythmia_classifier.py
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import logging
from datetime import datetime
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from biomedical.arrhythmia_classifier import (
    ArrhythmiaClassifier,
    BeatSegmentation,
    FeatureExtraction,
    ArrhythmiaModelTrainer,
    ModelEvaluator,
    ArrhythmiaClass,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_synthetic_beats(num_samples_per_class: int = 50,
                           sampling_rate: int = 360,
                           beat_length: int = 216) -> tuple:
    """
    Generate synthetic ECG beats for each arrhythmia class.
    
    Uses MIT-BIH-like signal characteristics.
    
    Args:
        num_samples_per_class: Number of samples per class
        sampling_rate: ECG sampling rate
        beat_length: Beat length in samples
        
    Returns:
        (beat_signals, labels)
    """
    logger.info("="*60)
    logger.info("GENERATING SYNTHETIC ECG BEATS")
    logger.info("="*60)
    
    np.random.seed(42)
    beats = []
    labels = []
    
    def create_normal_beat():
        """Create normal sinus rhythm beat."""
        t = np.linspace(0, 1, beat_length)
        # P wave
        p_wave = 0.1 * np.exp(-((t - 0.2) ** 2) / 0.01)
        # QRS complex
        q_wave = -0.1 * np.exp(-((t - 0.45) ** 2) / 0.001)
        r_wave = 1.0 * np.exp(-((t - 0.5) ** 2) / 0.002)
        s_wave = -0.3 * np.exp(-((t - 0.55) ** 2) / 0.002)
        # T wave
        t_wave = 0.2 * np.exp(-((t - 0.75) ** 2) / 0.03)
        beat = p_wave + q_wave + r_wave + s_wave + t_wave
        return beat + np.random.normal(0, 0.05, beat_length)
    
    def create_pvc_beat():
        """Create PVC beat (wider QRS)."""
        t = np.linspace(0, 1, beat_length)
        # No P wave
        # Abnormal QRS (wider, different morphology)
        q_wave = -0.15 * np.exp(-((t - 0.4) ** 2) / 0.003)
        r_wave = 1.2 * np.exp(-((t - 0.5) ** 2) / 0.005)
        s_wave = -0.5 * np.exp(-((t - 0.62) ** 2) / 0.004)
        # Inverted T wave
        t_wave = -0.1 * np.exp(-((t - 0.75) ** 2) / 0.03)
        beat = q_wave + r_wave + s_wave + t_wave
        return beat + np.random.normal(0, 0.05, beat_length)
    
    def create_pac_beat():
        """Create PAC beat (early P wave)."""
        t = np.linspace(0, 1, beat_length)
        # Early P wave
        p_wave = 0.15 * np.exp(-((t - 0.1) ** 2) / 0.01)
        # Normal QRS
        r_wave = 0.9 * np.exp(-((t - 0.5) ** 2) / 0.002)
        s_wave = -0.2 * np.exp(-((t - 0.55) ** 2) / 0.001)
        t_wave = 0.15 * np.exp(-((t - 0.75) ** 2) / 0.03)
        beat = p_wave + r_wave + s_wave + t_wave
        return beat + np.random.normal(0, 0.05, beat_length)
    
    def create_afib_beat():
        """Create AFib beat (irregular baseline, variable rate)."""
        t = np.linspace(0, 1, beat_length)
        # Irregular baseline (fibrillatory waves)
        fibrillation = 0.1 * np.sin(2 * np.pi * 6 * t) * np.random.uniform(0.5, 1.5, beat_length)
        # Reduced R wave
        r_wave = 0.6 * np.exp(-((t - 0.5) ** 2) / 0.002)
        beat = fibrillation + r_wave
        return beat + np.random.normal(0, 0.08, beat_length)
    
    def create_lbbb_beat():
        """Create LBBB beat (broad QRS, M-shaped in V1-V3)."""
        t = np.linspace(0, 1, beat_length)
        # Broad QRS with notch
        q_wave = -0.05 * np.exp(-((t - 0.42) ** 2) / 0.002)
        r1_wave = 0.7 * np.exp(-((t - 0.48) ** 2) / 0.003)
        s_wave = -0.3 * np.exp(-((t - 0.54) ** 2) / 0.003)
        r2_wave = 0.8 * np.exp(-((t - 0.60) ** 2) / 0.003)
        # Delayed T wave
        t_wave = -0.15 * np.exp(-((t - 0.75) ** 2) / 0.04)
        beat = q_wave + r1_wave + s_wave + r2_wave + t_wave
        return beat + np.random.normal(0, 0.05, beat_length)
    
    def create_rbbb_beat():
        """Create RBBB beat (RSR' pattern)."""
        t = np.linspace(0, 1, beat_length)
        # RSR' pattern
        r1_wave = 0.6 * np.exp(-((t - 0.48) ** 2) / 0.002)
        s_wave = -0.4 * np.exp(-((t - 0.54) ** 2) / 0.002)
        r2_wave = 0.8 * np.exp(-((t - 0.60) ** 2) / 0.003)
        # Normal T wave
        t_wave = 0.15 * np.exp(-((t - 0.75) ** 2) / 0.03)
        beat = r1_wave + s_wave + r2_wave + t_wave
        return beat + np.random.normal(0, 0.05, beat_length)
    
    def create_vt_beat():
        """Create VT beat (very wide QRS, abnormal morphology)."""
        t = np.linspace(0, 1, beat_length)
        # Very wide QRS
        q_wave = -0.2 * np.exp(-((t - 0.35) ** 2) / 0.005)
        r_wave = 1.5 * np.exp(-((t - 0.52) ** 2) / 0.008)
        s_wave = -0.7 * np.exp(-((t - 0.70) ** 2) / 0.006)
        # Abnormal T wave
        t_wave = 0.3 * np.exp(-((t - 0.85) ** 2) / 0.05)
        beat = q_wave + r_wave + s_wave + t_wave
        return beat + np.random.normal(0, 0.06, beat_length)
    
    def create_atrial_flutter_beat():
        """Create Atrial Flutter beat (saw-tooth baseline)."""
        t = np.linspace(0, 1, beat_length)
        # Saw-tooth flutter waves
        flutter = 0.15 * (2 * np.abs(2 * ((t * 3) % 1) - 1) - 1)
        # Variable QRS
        r_wave = 0.7 * np.exp(-((t - 0.5) ** 2) / 0.003)
        beat = flutter + r_wave
        return beat + np.random.normal(0, 0.06, beat_length)
    
    generators = {
        ArrhythmiaClass.NORMAL: create_normal_beat,
        ArrhythmiaClass.PVC: create_pvc_beat,
        ArrhythmiaClass.PAC: create_pac_beat,
        ArrhythmiaClass.AFIB: create_afib_beat,
        ArrhythmiaClass.LBBB: create_lbbb_beat,
        ArrhythmiaClass.RBBB: create_rbbb_beat,
        ArrhythmiaClass.VT: create_vt_beat,
        ArrhythmiaClass.ATRIAL_FLUTTER: create_atrial_flutter_beat,
    }
    
    for arrhythmia_class, generator in generators.items():
        for _ in range(num_samples_per_class):
            beat = generator()
            beats.append(beat)
            labels.append(arrhythmia_class.value)
        logger.info(f"Generated {num_samples_per_class} samples for {arrhythmia_class.name}")
    
    beats = np.array(beats)
    labels = np.array(labels)
    
    logger.info(f"Total beats generated: {len(beats)}")
    logger.info(f"Shape: {beats.shape}")
    logger.info("="*60 + "\n")
    
    return beats, labels


def train_classifier():
    """Main training pipeline."""
    logger.info("\n")
    logger.info("╔" + "="*58 + "╗")
    logger.info("║" + " ARRHYTHMIA CLASSIFIER - TRAINING PIPELINE ".center(58) + "║")
    logger.info("╚" + "="*58 + "╝\n")
    
    # Initialize classifier
    classifier = ArrhythmiaClassifier()
    
    # Generate synthetic data
    beats, labels = generate_synthetic_beats(num_samples_per_class=50)
    
    # Segment and extract features
    logger.info("="*60)
    logger.info("EXTRACTING FEATURES")
    logger.info("="*60)
    
    feature_extractor = FeatureExtraction(sampling_rate=360)
    X = feature_extractor.extract_features_batch(beats)
    y = labels
    
    is_valid, msg = feature_extractor.validate_features(X)
    logger.info(f"Feature validation: {msg}")
    
    if not is_valid:
        logger.error("Feature extraction failed!")
        return False
    
    logger.info("="*60 + "\n")
    
    # Train models
    trainer = ArrhythmiaModelTrainer()
    results = trainer.train_all_models(X, y, validation_split=0.2)
    
    # Store models and scaler
    for model_type, result in results.items():
        model = result['model']
        classifier.models[model_type] = model
        classifier.scaler = trainer.scaler
    
    # Save models
    logger.info("="*60)
    logger.info("SAVING MODELS")
    logger.info("="*60)
    
    for model_type in [m for m in classifier.models.keys() if classifier.models[m]]:
        classifier.save_model(classifier.models[model_type], model_type)
    
    logger.info("="*60 + "\n")
    
    return classifier, X, y, trainer.scaler


if __name__ == "__main__":
    try:
        classifier, X, y, scaler = train_classifier()
        
        logger.info("\n✅ TRAINING COMPLETED SUCCESSFULLY\n")
        
        logger.info("Summary:")
        logger.info(f"  • Total beats: {len(y)}")
        logger.info(f"  • Total features: {X.shape[1]}")
        logger.info(f"  • Models trained: {len([m for m in classifier.models.values() if m])}")
        logger.info(f"  • Models saved to: {classifier.model_dir}\n")
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)
