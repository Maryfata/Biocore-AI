"""
Model Training Module

Trains multiple arrhythmia classification models:
- Random Forest
- XGBoost
- LightGBM
"""

from typing import Tuple, Dict, Optional, List
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class ArrhythmiaModelTrainer:
    """Train arrhythmia classification models."""
    
    def __init__(self, random_state: int = 42, n_jobs: int = -1):
        """
        Initialize model trainer.
        
        Args:
            random_state: Random seed for reproducibility
            n_jobs: Number of parallel jobs (-1 for all CPUs)
        """
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.scaler = StandardScaler()
        logger.info(f"ModelTrainer initialized (random_state={random_state})")
    
    def train_random_forest(self, X: pd.DataFrame, y: np.ndarray,
                           n_estimators: int = 100,
                           max_depth: Optional[int] = None,
                           min_samples_split: int = 5,
                           min_samples_leaf: int = 2,
                           validation_split: float = 0.2) -> Tuple[RandomForestClassifier, float]:
        """
        Train Random Forest classifier.
        
        Args:
            X: Features
            y: Labels
            n_estimators: Number of trees
            max_depth: Maximum depth of trees
            min_samples_split: Minimum samples to split
            min_samples_leaf: Minimum samples per leaf
            validation_split: Validation split ratio
            
        Returns:
            (trained_model, validation_accuracy)
        """
        logger.info("Training Random Forest...")
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=self.random_state,
            stratify=y
        )
        
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=self.random_state,
            n_jobs=self.n_jobs,
            verbose=0
        )
        
        model.fit(X_train, y_train)
        val_accuracy = model.score(X_val, y_val)
        
        logger.info(f"Random Forest - Validation Accuracy: {val_accuracy:.4f}")
        return model, val_accuracy
    
    def train_xgboost(self, X: pd.DataFrame, y: np.ndarray,
                     n_estimators: int = 100,
                     max_depth: int = 6,
                     learning_rate: float = 0.1,
                     subsample: float = 0.8,
                     colsample_bytree: float = 0.8,
                     validation_split: float = 0.2) -> Tuple[xgb.XGBClassifier, float]:
        """
        Train XGBoost classifier.
        
        Args:
            X: Features
            y: Labels
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate (eta)
            subsample: Subsample ratio
            colsample_bytree: Column subsample ratio
            validation_split: Validation split ratio
            
        Returns:
            (trained_model, validation_accuracy)
        """
        logger.info("Training XGBoost...")
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=self.random_state,
            stratify=y
        )
        
        model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            random_state=self.random_state,
            n_jobs=self.n_jobs,
            verbosity=0,
            use_label_encoder=False,
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        val_accuracy = model.score(X_val, y_val)
        logger.info(f"XGBoost - Validation Accuracy: {val_accuracy:.4f}")
        return model, val_accuracy
    
    def train_lightgbm(self, X: pd.DataFrame, y: np.ndarray,
                      n_estimators: int = 100,
                      max_depth: int = 5,
                      learning_rate: float = 0.1,
                      num_leaves: int = 31,
                      subsample: float = 0.8,
                      colsample_bytree: float = 0.8,
                      validation_split: float = 0.2) -> Tuple[lgb.LGBMClassifier, float]:
        """
        Train LightGBM classifier.
        
        Args:
            X: Features
            y: Labels
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate
            num_leaves: Number of leaves
            subsample: Subsample ratio
            colsample_bytree: Column subsample ratio
            validation_split: Validation split ratio
            
        Returns:
            (trained_model, validation_accuracy)
        """
        logger.info("Training LightGBM...")
        
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=validation_split, random_state=self.random_state,
            stratify=y
        )
        
        model = lgb.LGBMClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            num_leaves=num_leaves,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            random_state=self.random_state,
            n_jobs=self.n_jobs,
            verbose=-1,
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        val_accuracy = model.score(X_val, y_val)
        logger.info(f"LightGBM - Validation Accuracy: {val_accuracy:.4f}")
        return model, val_accuracy
    
    def train_all_models(self, X: pd.DataFrame, y: np.ndarray,
                        validation_split: float = 0.2) -> Dict:
        """
        Train all three models with optimal hyperparameters.
        
        Args:
            X: Features
            y: Labels
            validation_split: Validation split ratio
            
        Returns:
            Dictionary with trained models and validation accuracies
        """
        logger.info("="*50)
        logger.info("TRAINING ALL MODELS")
        logger.info("="*50)
        
        # Normalize features
        X_normalized = pd.DataFrame(
            self.scaler.fit_transform(X),
            columns=X.columns
        )
        
        results = {}
        
        # Random Forest
        rf_model, rf_acc = self.train_random_forest(
            X_normalized, y, validation_split=validation_split
        )
        results['random_forest'] = {
            'model': rf_model,
            'validation_accuracy': rf_acc,
        }
        
        # XGBoost
        xgb_model, xgb_acc = self.train_xgboost(
            X_normalized, y, validation_split=validation_split
        )
        results['xgboost'] = {
            'model': xgb_model,
            'validation_accuracy': xgb_acc,
        }
        
        # LightGBM
        lgb_model, lgb_acc = self.train_lightgbm(
            X_normalized, y, validation_split=validation_split
        )
        results['lightgbm'] = {
            'model': lgb_model,
            'validation_accuracy': lgb_acc,
        }
        
        logger.info("="*50)
        logger.info("MODEL COMPARISON (Validation Accuracy)")
        logger.info("="*50)
        logger.info(f"Random Forest: {rf_acc:.4f}")
        logger.info(f"XGBoost:       {xgb_acc:.4f}")
        logger.info(f"LightGBM:      {lgb_acc:.4f}")
        best_model_name = max(results, key=lambda x: results[x]['validation_accuracy'])
        logger.info(f"\nBest Model: {best_model_name.upper()}")
        logger.info("="*50)
        
        return results
    
    def cross_validate_model(self, model, X: pd.DataFrame, y: np.ndarray,
                           cv: int = 5) -> Dict[str, float]:
        """
        Perform cross-validation on model.
        
        Args:
            model: Trained model
            X: Features
            y: Labels
            cv: Number of folds
            
        Returns:
            Dictionary with cross-validation scores
        """
        scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
        
        return {
            'mean': float(np.mean(scores)),
            'std': float(np.std(scores)),
            'fold_scores': scores.tolist(),
        }
