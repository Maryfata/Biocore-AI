"""
Arrhythmia Classifier - Main Module

Multi-class ECG arrhythmia classification pipeline based on MIT-BIH Arrhythmia Database.
Supports 8 arrhythmia classes with feature extraction, model training, and inference.

Classes:
    - Normal
    - PVC (Premature Ventricular Contraction)
    - PAC (Premature Atrial Contraction)
    - AFib (Atrial Fibrillation)
    - LBBB (Left Bundle Branch Block)
    - RBBB (Right Bundle Branch Block)
    - VT (Ventricular Tachycardia)
    - Atrial Flutter

Models:
    - Random Forest
    - XGBoost
    - LightGBM
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from pathlib import Path
import json
import pickle
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArrhythmiaClass(Enum):
    """Supported arrhythmia classifications."""
    NORMAL = 0
    PVC = 1
    PAC = 2
    AFIB = 3
    LBBB = 4
    RBBB = 5
    VT = 6
    ATRIAL_FLUTTER = 7


class ModelType(Enum):
    """Supported model types."""
    RANDOM_FOREST = "random_forest"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"


@dataclass
class ECGBeat:
    """ECG beat representation."""
    signal: np.ndarray  # Beat signal array
    label: Optional[ArrhythmiaClass] = None
    timestamp: Optional[float] = None
    r_peak_index: Optional[int] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'signal': self.signal.tolist() if isinstance(self.signal, np.ndarray) else self.signal,
            'label': self.label.value if self.label else None,
            'timestamp': self.timestamp,
            'r_peak_index': self.r_peak_index,
        }


@dataclass
class ClassificationResult:
    """Result of arrhythmia classification."""
    predicted_class: ArrhythmiaClass
    confidence: float  # 0-1
    probabilities: Dict[str, float]  # Class -> probability
    features_used: int
    model_type: ModelType
    timestamp: datetime
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'predicted_class': self.predicted_class.name,
            'confidence': float(self.confidence),
            'probabilities': {k: float(v) for k, v in self.probabilities.items()},
            'features_used': self.features_used,
            'model_type': self.model_type.value,
            'timestamp': self.timestamp.isoformat(),
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ModelMetrics:
    """Model performance metrics."""
    accuracy: float
    precision: Dict[str, float]  # Class -> precision
    recall: Dict[str, float]  # Class -> recall
    f1: Dict[str, float]  # Class -> F1 score
    macro_avg: Dict[str, float]  # Macro averages
    weighted_avg: Dict[str, float]  # Weighted averages
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'accuracy': float(self.accuracy),
            'precision': {k: float(v) for k, v in self.precision.items()},
            'recall': {k: float(v) for k, v in self.recall.items()},
            'f1': {k: float(v) for k, v in self.f1.items()},
            'macro_avg': {k: float(v) for k, v in self.macro_avg.items()},
            'weighted_avg': {k: float(v) for k, v in self.weighted_avg.items()},
        }


class ArrhythmiaClassifier:
    """
    Main Arrhythmia Classification System.
    
    Orchestrates the complete pipeline:
    1. Beat segmentation
    2. Feature extraction
    3. Model training
    4. Evaluation
    5. Inference
    """
    
    ARRHYTHMIA_NAMES = {
        ArrhythmiaClass.NORMAL: "Normal",
        ArrhythmiaClass.PVC: "Premature Ventricular Contraction",
        ArrhythmiaClass.PAC: "Premature Atrial Contraction",
        ArrhythmiaClass.AFIB: "Atrial Fibrillation",
        ArrhythmiaClass.LBBB: "Left Bundle Branch Block",
        ArrhythmiaClass.RBBB: "Right Bundle Branch Block",
        ArrhythmiaClass.VT: "Ventricular Tachycardia",
        ArrhythmiaClass.ATRIAL_FLUTTER: "Atrial Flutter",
    }
    
    ARRHYTHMIA_DESCRIPTIONS = {
        ArrhythmiaClass.NORMAL: "Normal cardiac rhythm",
        ArrhythmiaClass.PVC: "Premature contraction from ventricles",
        ArrhythmiaClass.PAC: "Premature contraction from atria",
        ArrhythmiaClass.AFIB: "Irregular atrial rhythm",
        ArrhythmiaClass.LBBB: "Conduction delay in left bundle branch",
        ArrhythmiaClass.RBBB: "Conduction delay in right bundle branch",
        ArrhythmiaClass.VT: "Rapid ventricular rhythm",
        ArrhythmiaClass.ATRIAL_FLUTTER: "Regular rapid atrial rhythm",
    }
    
    def __init__(self, model_dir: Optional[Path] = None, sampling_rate: int = 360):
        """
        Initialize Arrhythmia Classifier.
        
        Args:
            model_dir: Directory to store trained models
            sampling_rate: ECG sampling rate in Hz (default: 360 Hz for MIT-BIH)
        """
        self.model_dir = Path(model_dir) if model_dir else Path(__file__).parent / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.sampling_rate = sampling_rate
        self.beat_length = int(0.6 * sampling_rate)  # 600ms window (0-360 points at 360Hz)
        
        self.models: Dict[ModelType, Optional[object]] = {
            ModelType.RANDOM_FOREST: None,
            ModelType.XGBOOST: None,
            ModelType.LIGHTGBM: None,
        }
        
        self.metrics: Dict[ModelType, Optional[ModelMetrics]] = {
            ModelType.RANDOM_FOREST: None,
            ModelType.XGBOOST: None,
            ModelType.LIGHTGBM: None,
        }
        
        self.scaler = None
        self.feature_names: List[str] = []
        
        logger.info(f"Initialized ArrhythmiaClassifier (sampling_rate={sampling_rate}Hz)")
    
    def get_class_name(self, arrhythmia_class: ArrhythmiaClass) -> str:
        """Get human-readable class name."""
        return self.ARRHYTHMIA_NAMES.get(arrhythmia_class, "Unknown")
    
    def get_class_description(self, arrhythmia_class: ArrhythmiaClass) -> str:
        """Get class description."""
        return self.ARRHYTHMIA_DESCRIPTIONS.get(arrhythmia_class, "Unknown")
    
    def save_model(self, model: object, model_type: ModelType) -> Path:
        """
        Save trained model to disk.
        
        Args:
            model: Trained model object
            model_type: Type of model
            
        Returns:
            Path to saved model
        """
        model_path = self.model_dir / f"{model_type.value}_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"Model saved to {model_path}")
        return model_path
    
    def load_model(self, model_type: ModelType) -> Optional[object]:
        """
        Load trained model from disk.
        
        Args:
            model_type: Type of model to load
            
        Returns:
            Loaded model or None if not found
        """
        model_path = self.model_dir / f"{model_type.value}_model.pkl"
        if model_path.exists():
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"Model loaded from {model_path}")
            return model
        logger.warning(f"Model not found at {model_path}")
        return None
    
    def save_metrics(self, metrics: ModelMetrics, model_type: ModelType) -> Path:
        """
        Save model metrics to JSON.
        
        Args:
            metrics: Model metrics
            model_type: Type of model
            
        Returns:
            Path to saved metrics
        """
        metrics_path = self.model_dir / f"{model_type.value}_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics.to_dict(), f, indent=2)
        logger.info(f"Metrics saved to {metrics_path}")
        return metrics_path
    
    def load_metrics(self, model_type: ModelType) -> Optional[ModelMetrics]:
        """Load metrics from JSON."""
        metrics_path = self.model_dir / f"{model_type.value}_metrics.json"
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                data = json.load(f)
            logger.info(f"Metrics loaded from {metrics_path}")
            return ModelMetrics(**data)
        return None
    
    def validate_beat(self, beat: ECGBeat) -> Tuple[bool, str]:
        """
        Validate beat signal.
        
        Args:
            beat: ECG beat to validate
            
        Returns:
            (is_valid, message)
        """
        if beat.signal is None or len(beat.signal) == 0:
            return False, "Beat signal is empty"
        
        if len(beat.signal) < 100:
            return False, f"Beat too short: {len(beat.signal)} samples (min 100)"
        
        if not np.isfinite(beat.signal).all():
            return False, "Beat contains NaN or infinite values"
        
        if beat.label and not isinstance(beat.label, ArrhythmiaClass):
            return False, "Invalid label"
        
        return True, "Valid"
    
    @property
    def available_models(self) -> List[ModelType]:
        """Get list of available trained models."""
        return [model_type for model_type, model in self.models.items() if model is not None]
    
    @property
    def model_comparison_df(self) -> Optional[pd.DataFrame]:
        """Get comparison of all trained models."""
        if not self.available_models:
            return None
        
        rows = []
        for model_type in self.available_models:
            metrics = self.metrics.get(model_type)
            if metrics:
                rows.append({
                    'Model': model_type.value.upper(),
                    'Accuracy': f"{metrics.accuracy:.4f}",
                    'Precision (macro)': f"{metrics.macro_avg.get('precision', 0):.4f}",
                    'Recall (macro)': f"{metrics.macro_avg.get('recall', 0):.4f}",
                    'F1 (macro)': f"{metrics.macro_avg.get('f1', 0):.4f}",
                })
        
        return pd.DataFrame(rows) if rows else None
    
    def export_summary(self, output_path: Optional[Path] = None) -> Dict:
        """
        Export complete summary of classification system.
        
        Args:
            output_path: Optional path to save summary as JSON
            
        Returns:
            Summary dictionary
        """
        summary = {
            'timestamp': datetime.now().isoformat(),
            'sampling_rate': self.sampling_rate,
            'beat_length': self.beat_length,
            'arrhythmia_classes': [
                {
                    'id': cls.value,
                    'name': self.get_class_name(cls),
                    'description': self.get_class_description(cls),
                }
                for cls in ArrhythmiaClass
            ],
            'available_models': [m.value for m in self.available_models],
            'metrics': {
                model_type.value: self.metrics[model_type].to_dict()
                for model_type in self.available_models
                if self.metrics[model_type] is not None
            },
        }
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"Summary exported to {output_path}")
        
        return summary
