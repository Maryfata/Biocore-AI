"""Arrhythmia Classification Module.

Multi-class ECG arrhythmia classification using MIT-BIH Arrhythmia Database.
Supports: Normal, PVC, PAC, AFib, LBBB, RBBB, VT, Atrial Flutter.
"""

from .arrhythmia_classifier import ArrhythmiaClassifier
from .beat_segmentation import BeatSegmentation
from .feature_extraction import FeatureExtraction
from .model_training import ArrhythmiaModelTrainer
from .model_evaluation import ModelEvaluator
from .inference import ArrhythmiaInference

__all__ = [
    'ArrhythmiaClassifier',
    'BeatSegmentation',
    'FeatureExtraction',
    'ArrhythmiaModelTrainer',
    'ModelEvaluator',
    'ArrhythmiaInference',
]

__version__ = '1.0.0'
