# ECG Arrhythmia Classifier - Comprehensive Guide

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Training](#training)
7. [Evaluation](#evaluation)
8. [Inference](#inference)
9. [Integration](#integration)
10. [API Reference](#api-reference)
11. [Examples](#examples)
12. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The **ECG Arrhythmia Classifier** is a multi-class machine learning system for automated classification of cardiac arrhythmias from ECG signals. It implements a complete pipeline from raw ECG signal to clinical classification.

### Supported Arrhythmia Classes

| Class | Full Name | Description |
|-------|-----------|-------------|
| **NORMAL** | Normal Sinus Rhythm | Regular cardiac rhythm |
| **PVC** | Premature Ventricular Contraction | Early heartbeat from ventricles |
| **PAC** | Premature Atrial Contraction | Early heartbeat from atria |
| **AFib** | Atrial Fibrillation | Irregular, rapid atrial rhythm |
| **LBBB** | Left Bundle Branch Block | Conduction delay in left bundle |
| **RBBB** | Right Bundle Branch Block | Conduction delay in right bundle |
| **VT** | Ventricular Tachycardia | Rapid ventricular rhythm (>100 bpm) |
| **Atrial Flutter** | Atrial Flutter | Regular rapid atrial rhythm |

### Supported Models

- **Random Forest**: Ensemble of decision trees
- **XGBoost**: Gradient boosting with optimal regularization
- **LightGBM**: Lightweight gradient boosting (fastest)

---

## ✨ Features

### Core Capabilities

- ✅ **Multi-class Classification**: 8 arrhythmia types
- ✅ **Beat Segmentation**: Automatic R-peak detection
- ✅ **Feature Extraction**: 25 morphological, statistical, and frequency-domain features
- ✅ **Model Comparison**: Train and compare 3 different algorithms
- ✅ **Real-time Inference**: Single beat or full signal analysis
- ✅ **Comprehensive Metrics**: Accuracy, Precision, Recall, F1, ROC-AUC, Confusion Matrix
- ✅ **Streamlit Integration**: Interactive web UI
- ✅ **Batch Processing**: Process multiple signals efficiently
- ✅ **Model Persistence**: Save/load trained models (`.pkl`)
- ✅ **JSON Export**: Export results for integration

### Data Processing

```
Raw ECG Signal
    ↓
Preprocessing (Bandpass Filter)
    ↓
Beat Segmentation (R-peak Detection)
    ↓
Feature Extraction (25 features)
    ↓
Feature Normalization (Z-score)
    ↓
Model Prediction
    ↓
Classification Result
```

---

## 🏗️ Architecture

### Module Structure

```
ml/arrhythmia_classifier/
├── __init__.py                    # Package exports
├── arrhythmia_classifier.py       # Main orchestrator class
├── beat_segmentation.py           # R-peak detection & beat extraction
├── feature_extraction.py          # 25 features from beats
├── model_training.py              # Training 3 models
├── model_evaluation.py            # Comprehensive evaluation metrics
├── inference.py                   # Real-time classification
├── models/                        # Trained model storage
├── data/                          # Training/test data
└── utils/                         # Helper functions
```

### Core Classes

#### `ArrhythmiaClassifier` (Orchestrator)
Main facade class managing the entire system.

```python
from ml.arrhythmia_classifier import ArrhythmiaClassifier

classifier = ArrhythmiaClassifier(
    model_dir=Path("./models"),
    sampling_rate=360
)

# Get available trained models
available = classifier.available_models

# Export system summary
summary = classifier.export_summary()
```

#### `BeatSegmentation`
Detects R-peaks and segments ECG into individual beats.

```python
from ml.arrhythmia_classifier import BeatSegmentation

segmenter = BeatSegmentation(sampling_rate=360)

# Detect R peaks
r_peaks = segmenter.detect_r_peaks(ecg_signal)

# Segment into beats
beats, r_peaks = segmenter.segment_ecg(ecg_signal)
```

#### `FeatureExtraction`
Extracts 25 features from each beat.

```python
from ml.arrhythmia_classifier import FeatureExtraction

extractor = FeatureExtraction(sampling_rate=360)

# Extract from single beat
features = extractor.extract_all_features(beat_signal)

# Batch extraction
features_df = extractor.extract_features_batch(beat_list)

# Normalize
X_train_norm, X_test_norm = extractor.normalize_features(X_train, X_test)
```

#### `ArrhythmiaModelTrainer`
Trains and compares 3 models.

```python
from ml.arrhythmia_classifier import ArrhythmiaModelTrainer

trainer = ArrhythmiaModelTrainer(random_state=42)

# Train all 3 models
results = trainer.train_all_models(X, y, validation_split=0.2)

# Access individual models
rf_model = results['random_forest']['model']
xgb_model = results['xgboost']['model']
lgb_model = results['lightgbm']['model']
```

#### `ModelEvaluator`
Comprehensive evaluation and metrics.

```python
from ml.arrhythmia_classifier import ModelEvaluator

evaluator = ModelEvaluator()

# Evaluate single model
evaluation = evaluator.evaluate_model(model, X_test, y_test)

# Compare multiple models
comparison_df = evaluator.compare_models(evaluations)

# Get confusion matrix
cm_df = evaluator.get_confusion_matrix_df(evaluation['confusion_matrix'])

# Print classification report
evaluator.print_classification_report(evaluation, "Random Forest")
```

#### `ArrhythmiaInference`
Real-time prediction on new signals.

```python
from ml.arrhythmia_classifier import ArrhythmiaInference

inference = ArrhythmiaInference(
    model_path="./models/random_forest_model.pkl",
    model_type=ModelType.RANDOM_FOREST
)

# Single beat classification
result = inference.predict_single_beat(beat_signal)
print(f"Class: {result.predicted_class.name}")
print(f"Confidence: {result.confidence:.2%}")

# Full signal analysis
result = inference.predict_ecg_signal(ecg_signal)

# Batch processing
results = inference.predict_batch(beat_list)

# Get human-readable summary
summary = inference.get_prediction_summary(result)
```

---

## 📦 Installation

### Prerequisites
- Python 3.8+
- NumPy, Pandas, SciPy
- Scikit-learn
- XGBoost
- LightGBM
- Streamlit (for UI)
- Matplotlib, Seaborn (for visualization)
- Plotly (for interactive charts)

### Install Dependencies

```bash
# From requirements.txt
pip install numpy pandas scipy scikit-learn xgboost lightgbm
pip install streamlit plotly matplotlib seaborn

# Or install all at once
pip install -r requirements_arrhythmia.txt
```

---

## 🚀 Usage

### 1. Training Models

```bash
# Generate synthetic data, extract features, and train all 3 models
python train_arrhythmia_classifier.py
```

**Output:**
- Random Forest model: `ml/arrhythmia_classifier/models/random_forest_model.pkl`
- XGBoost model: `ml/arrhythmia_classifier/models/xgboost_model.pkl`
- LightGBM model: `ml/arrhythmia_classifier/models/lightgbm_model.pkl`

### 2. Evaluating Models

```bash
# Test models on validation set and generate metrics
python evaluate_arrhythmia_classifier.py
```

**Output:**
- Model comparison: `models/model_comparison.csv`
- Confusion matrices: `models/{model_name}_confusion_matrix.csv`
- Confusion matrix plots: `models/{model_name}_confusion_matrix.png`
- Evaluation summary: `models/evaluation_summary_YYYYMMDD_HHMMSS.json`

### 3. Running Inference

```bash
# Demonstrate real-time classification on synthetic data
python infer_arrhythmia.py
```

**Demonstrates:**
- Single beat classification
- Full ECG signal analysis
- Batch processing
- Input validation
- Result export

### 4. Interactive Streamlit App

```bash
# Launch interactive web application
streamlit run app_arrhythmia_classifier.py
```

**Features:**
- Single beat classification
- Full ECG signal analysis with beat detection
- Batch processing
- Real-time visualization
- Result export (CSV)

---

## 📊 Training Pipeline

### Step 1: Data Generation
```python
from train_arrhythmia_classifier import generate_synthetic_beats

# Generate synthetic MIT-BIH-like beats
beats, labels = generate_synthetic_beats(
    num_samples_per_class=50,
    sampling_rate=360,
    beat_length=216
)
```

### Step 2: Feature Extraction
```python
from ml.arrhythmia_classifier import FeatureExtraction

feature_extractor = FeatureExtraction(sampling_rate=360)
X = feature_extractor.extract_features_batch(beats)
```

### Step 3: Feature Normalization
```python
X_norm, _ = feature_extractor.normalize_features(X)
```

### Step 4: Model Training
```python
from ml.arrhythmia_classifier import ArrhythmiaModelTrainer

trainer = ArrhythmiaModelTrainer()
results = trainer.train_all_models(X_norm, labels)

# Save models
for model_type, result in results.items():
    classifier.save_model(result['model'], model_type)
```

---

## 📈 Evaluation Metrics

### Classification Metrics

| Metric | Description |
|--------|-------------|
| **Accuracy** | Overall correct predictions |
| **Precision** | True positives / (True positives + False positives) |
| **Recall** | True positives / (True positives + False negatives) |
| **F1 Score** | Harmonic mean of precision and recall |
| **ROC-AUC** | Area under ROC curve (one-vs-rest) |

### Output Metrics
```
Model Comparison:
├── Accuracy (overall accuracy)
├── Precision (macro, weighted, per-class)
├── Recall (macro, weighted, per-class)
├── F1 Score (macro, weighted, per-class)
├── ROC-AUC (one-vs-rest)
└── Confusion Matrix (8x8)
```

---

## 🔮 Inference Examples

### Example 1: Single Beat Classification
```python
from ml.arrhythmia_classifier import ArrhythmiaInference, ModelType
import numpy as np

# Initialize
inference = ArrhythmiaInference(
    model_path="./models/random_forest_model.pkl",
    model_type=ModelType.RANDOM_FOREST
)

# Generate or load beat
beat = np.random.randn(216)

# Classify
result = inference.predict_single_beat(beat)

# Display results
print(f"Predicted: {result.predicted_class.name}")
print(f"Confidence: {result.confidence:.1%}")
print(f"Probabilities: {result.probabilities}")
```

### Example 2: Full ECG Signal Analysis
```python
# Analyze entire ECG signal
result = inference.predict_ecg_signal(ecg_signal, return_beat_predictions=True)

overall = result['overall_result']
beats = result['beat_predictions']

print(f"Overall class: {overall.predicted_class.name}")
print(f"Total beats: {result['total_beats']}")

for beat_pred in beats:
    print(f"Beat {beat_pred['beat_index']}: {beat_pred['predicted_class']}")
```

### Example 3: Batch Processing
```python
# Process multiple beats
beat_list = [np.random.randn(216) for _ in range(100)]

results = inference.predict_batch(beat_list)

for i, result in enumerate(results):
    print(f"{i}: {result.predicted_class.name} ({result.confidence:.1%})")
```

---

## 🔧 Integration with Biomedical Signal Visualizer

### Integration Point 1: HRV Analysis
```python
# Add to existing HRV analysis module
from ml.arrhythmia_classifier import ArrhythmiaInference, ModelType

def analyze_with_arrhythmia(ecg_signal, sampling_rate=360):
    # Existing HRV analysis...
    hrv_metrics = compute_hrv(ecg_signal)
    
    # New: Arrhythmia classification
    inference = ArrhythmiaInference(
        model_path="./models/random_forest_model.pkl",
        model_type=ModelType.RANDOM_FOREST
    )
    arrhythmia_result = inference.predict_ecg_signal(ecg_signal)
    
    return {
        'hrv': hrv_metrics,
        'arrhythmia': arrhythmia_result.to_dict()
    }
```

### Integration Point 2: Dashboard Display
```python
# Add arrhythmia component to dashboard
from app.reasoning_engine_streamlit import create_reasoning_component
from ml.arrhythmia_classifier import ArrhythmiaInference

def add_arrhythmia_panel(ecg_signal):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### HRV Analysis")
        # Existing reasoning engine output
        reasoning_output = create_reasoning_component("HRV Metrics")
    
    with col2:
        st.markdown("### Arrhythmia Classification")
        inference = ArrhythmiaInference()
        result = inference.predict_ecg_signal(ecg_signal)
        
        st.metric("Predicted", result.predicted_class.name)
        st.metric("Confidence", f"{result.confidence:.1%}")
```

### Integration Point 3: Reports
```python
# Generate combined clinical report
from ml.arrhythmia_classifier import ArrhythmiaInference

def generate_combined_report(ecg_signal):
    # Reasoning engine analysis
    reasoning = engine.reason(metrics)
    
    # Arrhythmia classification
    inference = ArrhythmiaInference()
    arrhythmia = inference.predict_ecg_signal(ecg_signal)
    
    report = f"""
    ## Clinical Analysis Report
    
    ### Cardiac Autonomic Status (Reasoning Engine)
    - Risk Level: {reasoning.risk_level.value}
    - Autonomic State: {reasoning.autonomic_state.value}
    
    ### Arrhythmia Analysis (Deep Learning)
    - Detected Arrhythmia: {arrhythmia.predicted_class.name}
    - Confidence: {arrhythmia.confidence:.1%}
    - Differential Diagnosis: {arrhythmia.probabilities}
    """
    
    return report
```

---

## 📚 API Reference

### ArrhythmiaClassifier

```python
class ArrhythmiaClassifier:
    def __init__(self, model_dir=None, sampling_rate=360)
    def get_class_name(arrhythmia_class) -> str
    def get_class_description(arrhythmia_class) -> str
    def save_model(model, model_type) -> Path
    def load_model(model_type) -> object
    def save_metrics(metrics, model_type) -> Path
    def load_metrics(model_type) -> ModelMetrics
    def validate_beat(beat) -> (bool, str)
    @property available_models -> List[ModelType]
    @property model_comparison_df -> DataFrame
    def export_summary(output_path=None) -> Dict
```

### BeatSegmentation

```python
class BeatSegmentation:
    def __init__(self, sampling_rate=360, beat_length_ms=600)
    def preprocess_signal(signal) -> ndarray
    def detect_r_peaks(signal, min_distance=None) -> ndarray
    def segment_beats(signal, r_peaks, pre_samples=None, post_samples=None) -> List
    def segment_ecg(signal) -> (List[ndarray], ndarray)
    def validate_segmentation(beats) -> (bool, str)
```

### FeatureExtraction

```python
class FeatureExtraction:
    def __init__(self, sampling_rate=360)
    def extract_morphological_features(beat) -> Dict
    def extract_statistical_features(beat) -> Dict
    def extract_frequency_features(beat) -> Dict
    def extract_all_features(beat) -> Dict
    def extract_features_batch(beats) -> DataFrame
    def normalize_features(X_train, X_test=None) -> (DataFrame, DataFrame)
    def validate_features(features_df) -> (bool, str)
    def get_feature_names() -> List[str]
```

### ArrhythmiaModelTrainer

```python
class ArrhythmiaModelTrainer:
    def __init__(self, random_state=42, n_jobs=-1)
    def train_random_forest(X, y, ...) -> (model, accuracy)
    def train_xgboost(X, y, ...) -> (model, accuracy)
    def train_lightgbm(X, y, ...) -> (model, accuracy)
    def train_all_models(X, y, validation_split=0.2) -> Dict
    def cross_validate_model(model, X, y, cv=5) -> Dict
```

### ArrhythmiaInference

```python
class ArrhythmiaInference:
    def __init__(self, model_path=None, model_type=None, sampling_rate=360)
    def load_model(model_path)
    def predict_single_beat(beat) -> ClassificationResult
    def predict_ecg_signal(signal, return_beat_predictions=False)
    def predict_batch(beat_list) -> List[ClassificationResult]
    def get_prediction_summary(result) -> Dict
    def validate_and_predict(signal) -> (bool, result_or_error)
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/test_arrhythmia_classifier.py -v
```

### Test Coverage
```
- BeatSegmentation: R-peak detection, beat segmentation
- FeatureExtraction: All 25 features, normalization
- ArrhythmiaClassifier: Class validation, serialization
- Model Training: All 3 models, validation
- Integration: Full pipeline
```

---

## 🐛 Troubleshooting

### Issue: "No trained models found"
**Solution:** Run training first
```bash
python train_arrhythmia_classifier.py
```

### Issue: Low accuracy
**Possible causes:**
- Insufficient training data
- Poor feature extraction
- Hyperparameter tuning needed

**Solutions:**
- Increase `num_samples_per_class` in training
- Adjust model hyperparameters
- Try different model types

### Issue: Slow inference
**Solutions:**
- Use LightGBM (fastest)
- Reduce batch size
- Use GPU acceleration

### Issue: Memory error on large signals
**Solution:**
- Process signal in chunks
- Use batch processing with smaller batches

---

## ⚠️ Important Notes

1. **Educational Purpose**: This classifier is for research and educational use
2. **Not Medical Device**: Should not be used for clinical diagnosis
3. **Validation Required**: Always validate with medical professionals
4. **Synthetic Data**: Training uses synthetic MIT-BIH-like data (not real patient data)
5. **Accuracy**: Real-world performance depends on data quality and domain shift

---

## 📖 References

- MIT-BIH Arrhythmia Database
- ECG Signal Processing and Analysis
- Machine Learning for Healthcare
- Scikit-learn, XGBoost, LightGBM Documentation

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Maintainer**: Biomedical Signal Visualizer Team
