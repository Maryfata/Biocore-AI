"""
Inference Module

Performs arrhythmia classification on new ECG signals.
Handles real-time prediction and batch processing.
"""

from typing import Union, List, Dict, Optional, Tuple
import numpy as np
import pandas as pd
from pathlib import Path
import pickle
import logging

from .beat_segmentation import BeatSegmentation
from .feature_extraction import FeatureExtraction
from .arrhythmia_classifier import ArrhythmiaClass, ClassificationResult, ModelType

logger = logging.getLogger(__name__)


class ArrhythmiaInference:
    """Perform inference for arrhythmia classification."""
    
    def __init__(self, model_path: Optional[Union[str, Path]] = None,
                 model_type: ModelType = ModelType.RANDOM_FOREST,
                 sampling_rate: int = 360):
        """
        Initialize inference engine.
        
        Args:
            model_path: Path to trained model (optional)
            model_type: Type of model to use
            sampling_rate: ECG sampling rate
        """
        self.model_type = model_type
        self.sampling_rate = sampling_rate
        
        self.model = None
        self.scaler = None
        
        self.beat_segmentation = BeatSegmentation(sampling_rate=sampling_rate)
        self.feature_extraction = FeatureExtraction(sampling_rate=sampling_rate)
        
        if model_path:
            self.load_model(model_path)
        
        logger.info(f"ArrhythmiaInference initialized (model_type={model_type.value})")
    
    def load_model(self, model_path: Union[str, Path]):
        """
        Load trained model from disk.
        
        Args:
            model_path: Path to model file
        """
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        if isinstance(model_data, dict):
            self.model = model_data.get('model')
            self.scaler = model_data.get('scaler')
        else:
            self.model = model_data
        
        logger.info(f"Model loaded from {model_path}")
    
    def predict_single_beat(self, beat: np.ndarray) -> ClassificationResult:
        """
        Classify single ECG beat.
        
        Args:
            beat: ECG beat signal
            
        Returns:
            Classification result
        """
        if self.model is None:
            raise ValueError("No model loaded. Call load_model() first.")
        
        # Extract features
        features = self.feature_extraction.extract_all_features(beat)
        X = pd.DataFrame([features])
        
        # Normalize if scaler available
        if self.scaler:
            X = pd.DataFrame(self.scaler.transform(X), columns=X.columns)
        
        # Predict
        y_pred = self.model.predict(X)[0]
        y_proba = self.model.predict_proba(X)[0] if hasattr(self.model, 'predict_proba') else None
        
        # Get confidence
        confidence = float(np.max(y_proba)) if y_proba is not None else 1.0
        
        # Create probabilities dictionary
        if y_proba is not None:
            probabilities = {
                ArrhythmiaClass(i).name: float(prob)
                for i, prob in enumerate(y_proba)
            }
        else:
            probabilities = {ArrhythmiaClass(y_pred).name: 1.0}
        
        from datetime import datetime
        result = ClassificationResult(
            predicted_class=ArrhythmiaClass(y_pred),
            confidence=confidence,
            probabilities=probabilities,
            features_used=len(features),
            model_type=self.model_type,
            timestamp=datetime.now()
        )
        
        return result
    
    def predict_ecg_signal(self, signal: np.ndarray,
                          return_beat_predictions: bool = False) -> Union[ClassificationResult, Dict]:
        """
        Classify entire ECG signal by analyzing all beats.
        
        Args:
            signal: ECG signal
            return_beat_predictions: If True, return all beat predictions
            
        Returns:
            Overall classification result or dictionary with beat-level predictions
        """
        # Segment beats
        beats, r_peaks = self.beat_segmentation.segment_ecg(signal)
        
        if not beats:
            raise ValueError("No beats detected in signal")
        
        # Classify each beat
        beat_results = []
        class_votes = {}
        
        for i, beat in enumerate(beats):
            try:
                result = self.predict_single_beat(beat)
                beat_results.append({
                    'beat_index': i,
                    'r_peak': int(r_peaks[i]),
                    'predicted_class': result.predicted_class.name,
                    'confidence': result.confidence,
                    'probabilities': result.probabilities,
                })
                
                # Vote for class
                class_name = result.predicted_class.name
                class_votes[class_name] = class_votes.get(class_name, 0) + result.confidence
            except Exception as e:
                logger.warning(f"Error classifying beat {i}: {e}")
        
        # Determine overall classification by weighted voting
        if class_votes:
            overall_class_name = max(class_votes, key=class_votes.get)
            overall_class = ArrhythmiaClass[overall_class_name]
            overall_confidence = class_votes[overall_class_name] / len(beats)
        else:
            overall_class = ArrhythmiaClass.NORMAL
            overall_confidence = 0.0
        
        from datetime import datetime
        overall_result = ClassificationResult(
            predicted_class=overall_class,
            confidence=overall_confidence,
            probabilities={k: v / len(beats) for k, v in class_votes.items()},
            features_used=len(beat_results),
            model_type=self.model_type,
            timestamp=datetime.now()
        )
        
        if return_beat_predictions:
            return {
                'overall_result': overall_result,
                'beat_predictions': beat_results,
                'total_beats': len(beats),
            }
        else:
            return overall_result
    
    def predict_batch(self, beat_list: List[np.ndarray]) -> List[ClassificationResult]:
        """
        Classify multiple beats.
        
        Args:
            beat_list: List of ECG beats
            
        Returns:
            List of classification results
        """
        results = []
        for i, beat in enumerate(beat_list):
            try:
                result = self.predict_single_beat(beat)
                results.append(result)
            except Exception as e:
                logger.warning(f"Error classifying beat {i}: {e}")
        
        logger.info(f"Classified {len(results)}/{len(beat_list)} beats")
        return results
    
    def get_prediction_summary(self, result: ClassificationResult) -> Dict:
        """
        Get human-readable prediction summary.
        
        Args:
            result: Classification result
            
        Returns:
            Dictionary with summary information
        """
        from .arrhythmia_classifier import ArrhythmiaClassifier
        
        classifier = ArrhythmiaClassifier()
        predicted_class = result.predicted_class
        
        summary = {
            'predicted_class': predicted_class.name,
            'class_name': classifier.get_class_name(predicted_class),
            'description': classifier.get_class_description(predicted_class),
            'confidence': f"{result.confidence * 100:.1f}%",
            'model_used': result.model_type.value,
            'timestamp': result.timestamp.isoformat(),
            'top_3_candidates': sorted(
                result.probabilities.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3],
        }
        
        return summary
    
    def validate_and_predict(self, signal: np.ndarray) -> Tuple[bool, Union[ClassificationResult, str]]:
        """
        Validate signal and perform prediction.
        
        Args:
            signal: ECG signal
            
        Returns:
            (success, result_or_error_message)
        """
        # Validate input
        if signal is None or len(signal) == 0:
            return False, "Signal is empty"
        
        if not np.isfinite(signal).all():
            return False, "Signal contains NaN or infinite values"
        
        if len(signal) < 360:  # Less than 1 second at 360Hz
            return False, "Signal too short (minimum 1 second)"
        
        # Perform prediction
        try:
            result = self.predict_ecg_signal(signal)
            return True, result
        except Exception as e:
            return False, f"Prediction error: {str(e)}"
