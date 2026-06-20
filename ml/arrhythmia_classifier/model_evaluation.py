"""
Model Evaluation Module

Evaluates model performance with comprehensive metrics:
- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix
- Classification Report
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    roc_curve, auc
)
import logging

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate arrhythmia classification models."""
    
    def __init__(self, class_names: Optional[List[str]] = None):
        """
        Initialize evaluator.
        
        Args:
            class_names: Names of classes for reporting
        """
        self.class_names = class_names or [
            'Normal', 'PVC', 'PAC', 'AFib',
            'LBBB', 'RBBB', 'VT', 'Atrial Flutter'
        ]
    
    def evaluate_model(self, model, X_test: pd.DataFrame, y_test: np.ndarray,
                      model_name: str = "Model") -> Dict:
        """
        Comprehensive model evaluation.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            model_name: Name of model for logging
            
        Returns:
            Dictionary with complete evaluation metrics
        """
        logger.info(f"\n{'='*50}")
        logger.info(f"EVALUATING {model_name.upper()}")
        logger.info(f"{'='*50}")
        
        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test) if hasattr(model, 'predict_proba') else None
        
        # Basic metrics
        accuracy = accuracy_score(y_test, y_pred)
        
        precision_per_class = precision_score(y_test, y_pred, average=None, zero_division=0)
        recall_per_class = recall_score(y_test, y_pred, average=None, zero_division=0)
        f1_per_class = f1_score(y_test, y_pred, average=None, zero_division=0)
        
        precision_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
        recall_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
        f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
        
        precision_weighted = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall_weighted = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Classification report
        class_report = classification_report(
            y_test, y_pred,
            target_names=self.class_names[:len(np.unique(y_test))],
            zero_division=0,
            output_dict=True
        )
        
        # ROC-AUC (one-vs-rest)
        try:
            if y_pred_proba is not None:
                roc_auc = roc_auc_score(y_test, y_pred_proba, multi_class='ovr', zero_division=0)
            else:
                roc_auc = None
        except:
            roc_auc = None
        
        # Build results dictionary
        results = {
            'model_name': model_name,
            'accuracy': float(accuracy),
            'precision': {
                'per_class': {self.class_names[i]: float(p) for i, p in enumerate(precision_per_class)},
                'macro': float(precision_macro),
                'weighted': float(precision_weighted),
            },
            'recall': {
                'per_class': {self.class_names[i]: float(r) for i, r in enumerate(recall_per_class)},
                'macro': float(recall_macro),
                'weighted': float(recall_weighted),
            },
            'f1': {
                'per_class': {self.class_names[i]: float(f) for i, f in enumerate(f1_per_class)},
                'macro': float(f1_macro),
                'weighted': float(f1_weighted),
            },
            'confusion_matrix': cm.tolist(),
            'classification_report': class_report,
            'roc_auc': float(roc_auc) if roc_auc is not None else None,
        }
        
        # Log results
        logger.info(f"Accuracy:  {accuracy:.4f}")
        logger.info(f"Precision (macro): {precision_macro:.4f}")
        logger.info(f"Recall (macro):    {recall_macro:.4f}")
        logger.info(f"F1 (macro):        {f1_macro:.4f}")
        if roc_auc:
            logger.info(f"ROC-AUC:   {roc_auc:.4f}")
        logger.info(f"{'='*50}\n")
        
        return results
    
    def compare_models(self, evaluations: Dict[str, Dict]) -> pd.DataFrame:
        """
        Create comparison DataFrame of multiple model evaluations.
        
        Args:
            evaluations: Dictionary of model evaluations
            
        Returns:
            DataFrame with comparison
        """
        data = []
        for model_name, metrics in evaluations.items():
            row = {
                'Model': model_name.upper(),
                'Accuracy': f"{metrics['accuracy']:.4f}",
                'Precision (macro)': f"{metrics['precision']['macro']:.4f}",
                'Recall (macro)': f"{metrics['recall']['macro']:.4f}",
                'F1 (macro)': f"{metrics['f1']['macro']:.4f}",
                'Precision (weighted)': f"{metrics['precision']['weighted']:.4f}",
                'Recall (weighted)': f"{metrics['recall']['weighted']:.4f}",
                'F1 (weighted)': f"{metrics['f1']['weighted']:.4f}",
            }
            if metrics.get('roc_auc'):
                row['ROC-AUC'] = f"{metrics['roc_auc']:.4f}"
            data.append(row)
        
        df = pd.DataFrame(data)
        logger.info("\n" + "="*80)
        logger.info("MODEL COMPARISON")
        logger.info("="*80)
        logger.info(df.to_string(index=False))
        logger.info("="*80 + "\n")
        
        return df
    
    def get_confusion_matrix_df(self, confusion_matrix: np.ndarray) -> pd.DataFrame:
        """
        Convert confusion matrix to DataFrame for better visualization.
        
        Args:
            confusion_matrix: Confusion matrix array
            
        Returns:
            DataFrame with confusion matrix
        """
        df = pd.DataFrame(
            confusion_matrix,
            index=[f"Actual {name}" for name in self.class_names[:len(confusion_matrix)]],
            columns=[f"Predicted {name}" for name in self.class_names[:len(confusion_matrix)]]
        )
        return df
    
    def get_per_class_metrics(self, evaluation: Dict) -> pd.DataFrame:
        """
        Extract per-class metrics into DataFrame.
        
        Args:
            evaluation: Model evaluation dictionary
            
        Returns:
            DataFrame with per-class metrics
        """
        data = []
        for class_name in self.class_names:
            if class_name in evaluation['precision']['per_class']:
                row = {
                    'Class': class_name,
                    'Precision': evaluation['precision']['per_class'][class_name],
                    'Recall': evaluation['recall']['per_class'][class_name],
                    'F1': evaluation['f1']['per_class'][class_name],
                }
                data.append(row)
        
        return pd.DataFrame(data)
    
    def print_classification_report(self, evaluation: Dict, model_name: str = ""):
        """
        Print detailed classification report.
        
        Args:
            evaluation: Model evaluation dictionary
            model_name: Name of model
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"CLASSIFICATION REPORT - {model_name.upper()}")
        logger.info(f"{'='*80}\n")
        
        report = evaluation.get('classification_report', {})
        
        # Print per-class metrics
        print(f"\n{'Class':<20} {'Precision':>12} {'Recall':>12} {'F1-Score':>12} {'Support':>12}")
        print("-" * 68)
        
        for class_name in self.class_names:
            if class_name in report:
                metrics = report[class_name]
                support = int(metrics.get('support', 0))
                print(f"{class_name:<20} {metrics['precision']:>12.4f} {metrics['recall']:>12.4f} "
                      f"{metrics['f1-score']:>12.4f} {support:>12d}")
        
        # Print averages
        print("-" * 68)
        if 'macro avg' in report:
            macro = report['macro avg']
            print(f"{'Macro Avg':<20} {macro['precision']:>12.4f} {macro['recall']:>12.4f} "
                  f"{macro['f1-score']:>12.4f}")
        
        if 'weighted avg' in report:
            weighted = report['weighted avg']
            print(f"{'Weighted Avg':<20} {weighted['precision']:>12.4f} {weighted['recall']:>12.4f} "
                  f"{weighted['f1-score']:>12.4f}")
        
        logger.info(f"\n{'='*80}\n")
    
    def save_metrics_to_json(self, evaluation: Dict, filepath: str):
        """
        Save evaluation metrics to JSON file.
        
        Args:
            evaluation: Model evaluation dictionary
            filepath: Path to save JSON
        """
        import json
        with open(filepath, 'w') as f:
            # Handle numpy arrays
            json_data = self._convert_to_serializable(evaluation)
            json.dump(json_data, f, indent=2)
        logger.info(f"Metrics saved to {filepath}")
    
    @staticmethod
    def _convert_to_serializable(obj):
        """Convert numpy arrays to lists for JSON serialization."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: ModelEvaluator._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [ModelEvaluator._convert_to_serializable(item) for item in obj]
        return obj
