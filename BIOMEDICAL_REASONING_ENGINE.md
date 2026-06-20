# Biomedical Reasoning Engine

This module implements `BiomedicalReasoningEngine` to convert HRV and spectral
metrics into explainable clinical reasoning: findings, hypotheses,
diagnostic differentials, risk estimation and an explanation. It is
decoupled and compatible with Streamlit via `app/bio_reasoning_streamlit.py`.

Location: `ml/reasoning_engine.py`

Usage example:

```python
from ml.reasoning_engine import BiomedicalReasoningEngine
engine = BiomedicalReasoningEngine()
out = engine.analyze({"BPM":112, "RMSSD":18, "LF/HF":3.5, "Entropy":2.0})
```
