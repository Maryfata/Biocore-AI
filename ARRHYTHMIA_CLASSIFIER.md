# Arrhythmia Classifier

Module: `ml/arrhythmia_classifier.py`

Features:
- Beat segmentation -> simple time-domain feature extraction
- Trains Random Forest, XGBoost (optional), LightGBM (optional)
- Evaluates accuracy, precision, recall, F1, confusion matrix
- Saves models as `.pkl` in `models/trained_models/` by default

Quick usage:

```python
from ml.arrhythmia_classifier import ArrhythmiaClassifier
ac = ArrhythmiaClassifier()
# segments: list of 1D numpy arrays, labels: list of strings
results = ac.train(segments, labels)
```
