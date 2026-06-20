"""
SETUP_GUIDE.md - Complete Setup Instructions for Biomedical Signal Platform

This guide covers installation, configuration, and deployment.
"""

# Biomedical Signal Platform - Setup Guide

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.11+
- pip or conda
- Git
- 2GB available disk space

### Installation

```bash
# Clone repository
git clone https://github.com/user/Biomedical-Signal-Visualizer.git
cd Biomedical-Signal-Visualizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install optional dependencies for advanced features
pip install wfdb mne pyedflib  # For data loading
pip install tensorflow  # For AI models (optional)
pip install shap lime fpdf2  # For Explainable AI and Reports
pip install mypy pylint pytest-cov # For Software Quality and Testing
```

### Run Application

```bash
# Start Streamlit app
streamlit run app/main.py

# Or use alternative launcher
python main.py --mode dashboard

# For pipeline mode
python main.py --mode pipeline --record 100

# For ECG trainer
python main.py --mode trainer
```

Application opens at `http://localhost:8501`

---

## 📦 Project Structure

```
Biomedical-Signal-Visualizer/
├── app/                          # Streamlit Applications
│   ├── main.py                  # Main app launcher
│   ├── config.py                # Streamlit config
│   ├── streamlit_app.py         # Multi-mode dashboard
│   ├── ecg_trainer.py           # ECG training mode
│   └── pages/                   # Multi-page structure
│       ├── 0_🏠_Home.py
│       ├── 1_📊_ECG_Monitor.py
│       ├── 2_🔗_Multisensor.py
│       ├── 3_🎓_Education.py
│       ├── 4_👥_Patients.py
│       └── 5_🤖_AI_Analysis.py
│
├── signals/                      # Biomedical Signal Processing
│   ├── loaders/                 # Universal data loaders
│   │   ├── universal_loader.py  # Main loader dispatcher
│   │   ├── wfdb_loader.py       # MIT-BIH database
│   │   ├── edf_loader.py        # EDF format
│   │   ├── csv_loader.py        # CSV & wearables
│   │   └── wearable_loader.py   # Wearable devices
│   └── __init__.py
│
├── src/                         # Core modules (existing)
│   ├── signal_generator.py      # Synthetic ECG generation
│   ├── signal_processing.py     # DSP utilities
│   ├── visualization.py         # Matplotlib plotting
│   ├── ecg_education.py         # Educational content
│   ├── feature_extraction.py    # HRV, intervals
│   ├── machine_learning.py      # ML models
│   ├── risk_analysis.py         # Clinical risk assessment
│   └── interpretability.py      # Model explainability
│
├── clinical/                     # Clinical Analysis
│   ├── ecg_analyzer.py          # Advanced ECG analysis
│   ├── ecg_interpreter.py       # Clinical interpretation
│   └── __init__.py
│
├── visualization/               # Visualization Modules
│   ├── medical/                 # Medical visualization
│   │   ├── plotly_clinical.py   # Plotly figures
│   │   ├── ecg_medical_plot.py  # Advanced ECG plots
│   │   └── __init__.py
│   ├── ecg_clinical_plot.py     # (existing)
│   └── ecg_annotations.py       # (existing)
│
├── dashboards/                  # Dashboard Layouts
│   ├── multisensor.py           # Multisensorial platform
│   ├── vital_signs_panel.py     # Vital signs display
│   └── __init__.py
│
├── educational/                 # Educational Modules
│   ├── ecg_tutor.py             # Interactive ECG tutor
│   └── __init__.py
│
├── telemedicine/                # Telemedicine Support
│   ├── patient_manager.py       # Patient database
│   ├── offline_storage.py       # Local sync
│   ├── report_generator.py      # PDF reports
│   └── sync_manager.py          # Cloud sync
│
├── ai_models/                   # Machine Learning Models
│   ├── arrhythmia_classifier.py # CNN arrhythmia detection
│   ├── risk_predictor.py        # LSTM risk prediction
│   └── explainability.py        # Model interpretation
│
├── reports/                     # Generated Reports
│   └── (PDF/HTML outputs)
│
├── data/                        # Data Directory
│   ├── raw/                     # Raw recordings
│   ├── processed/               # Processed signals
│   └── features/                # Extracted features
│
├── notebooks/                   # Jupyter Notebooks
│   ├── ecg_exploration.ipynb
│   └── ecg_visualizer.ipynb
│
├── research/                    # Research & Development
│   └── (experimental notebooks)
│
├── datasets/                    # Test Data
│   └── test_data/               # Sample signals
│
├── requirements.txt             # Python dependencies
├── main.py                      # CLI entry point
├── README.md                    # Project documentation
├── SETUP_GUIDE.md              # This file
└── PROJECT_COMPLETION_REPORT.md # Feature status
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Optional configuration
export BIOMEDICAL_MODE=production  # or development
export MITBIH_CACHE_DIR=./datasets
export LOG_LEVEL=INFO
```

### Configuration Files

Edit `src/utils/config.py`:

```python
AppConfig(
    project_name="Biomedical Signal Platform",
    default_fs=250,           # Default sampling rate (Hz)
    safe_mode=True,           # Enable safety checks
    language="es",            # Language (es/en)
    rural_mode=False,         # Optimize for rural networks
    low_bandwidth=False       # Reduce data transfer
)
```

---

## 📊 Data Sources

### 1. MIT-BIH Arrhythmia Database

Automatic download on first use:

```python
from signals.loaders import load_mitbih_record

# Load record 100
signal, fs, metadata = load_mitbih_record('100')
```

Available records: 100-234 (48 records, 30 minutes each)

### 2. EDF Format

```python
from signals.loaders import load_edf_file

signal, fs, metadata = load_edf_file('path/to/file.edf', channel=0)
```

### 3. CSV Files

```python
from signals.loaders import load_csv_signal

signal, fs, metadata = load_csv_signal(
    'data.csv',
    signal_column=1,
    fs=250  # Or estimate from time column
)
```

### 4. Wearable Data

```python
from signals.loaders import load_wearable_data

signal, fs, metadata = load_wearable_data(
    'fitbit_export.json',
    signal_type='heart_rate'
)
```

---

## 🎮 Feature Modules

### Real-Time ECG Analysis

```python
from clinical.ecg_analyzer import ECGAnalyzer
from visualization.medical.plotly_clinical import create_clinical_ecg_figure

analyzer = ECGAnalyzer(fs=250)
r_peaks = analyzer.detect_r_peaks(signal)
intervals = analyzer.measure_intervals(signal)
hrv = analyzer.compute_heart_rate_variability(r_peaks)

# Visualization
fig = create_clinical_ecg_figure(signal, fs=250, r_peaks=r_peaks)
```

### Multisensorial Analysis

```python
from dashboards.multisensor import BiosignalChannel, MultisensoralRecord

# Create channels
channels = [
    BiosignalChannel(name='ECG', signal=ecg, fs=250, unit='mV', signal_type='ecg'),
    BiosignalChannel(name='PPG', signal=ppg, fs=250, unit='AU', signal_type='ppg'),
    BiosignalChannel(name='SpO2', signal=spo2, fs=1, unit='%', signal_type='spo2'),
]

# Combine into record
record = MultisensoralRecord(channels, patient_id='P001')

# Analysis
indices = record.compute_physiological_indices()
scores = record.health_score()
anomalies = record.detect_physiological_inconsistencies()
```

### Educational Mode

```python
from educational.ecg_tutor import ECGTutor

tutor = ECGTutor()

# Create case
case = tutor.create_case(case_type='fibrilacion_auricular', complexity='Intermedio')

# Get explanations
explanations = tutor.explain_components(case.signal, case.fs)

# Quiz system
quiz = tutor.generate_quiz()
is_correct = tutor.grade_quiz(quiz['question'], selected_answer)
```

---

## 💡 Usage Examples

### Example 1: Load and Analyze MIT-BIH Record

```python
from signals.loaders import load_mitbih_record
from clinical.ecg_analyzer import ECGAnalyzer
from visualization.medical.plotly_clinical import create_clinical_ecg_figure

# Load
signal, fs, metadata = load_mitbih_record('100')

# Analyze
analyzer = ECGAnalyzer(fs=fs)
r_peaks = analyzer.detect_r_peaks(signal)
hr = analyzer.estimate_heart_rate(r_peaks)
intervals = analyzer.measure_intervals(signal)
arrhythmias = analyzer.detect_arrhythmias(signal)

# Display
fig = create_clinical_ecg_figure(signal, fs, r_peaks=r_peaks)
fig.show()

print(f"Heart Rate: {hr:.0f} bpm")
print(f"Findings: {arrhythmias}")
```

### Example 2: Multisensor Health Score

```python
from dashboards.multisensor import BiosignalChannel, MultisensoralRecord
import numpy as np

# Create demo signals
fs = 250
duration = 60
t = np.arange(duration * fs) / fs

ecg = np.sin(2 * np.pi * 1.2 * t) * 0.5
ppg = np.sin(2 * np.pi * 1.2 * t + 0.3) * 0.3
spo2 = 98 + np.random.normal(0, 0.5, len(t))
resp = np.sin(2 * np.pi * 0.3 * t) * 2
temp = 37 + np.random.normal(0, 0.1, len(t))

channels = [
    BiosignalChannel('ECG', ecg, fs, 'mV', 'ecg'),
    BiosignalChannel('PPG', ppg, fs, 'AU', 'ppg'),
    BiosignalChannel('SpO2', spo2, 1, '%', 'spo2'),
    BiosignalChannel('Respiration', resp, fs, 'V', 'respiration'),
    BiosignalChannel('Temperature', temp, 1, '°C', 'temperature'),
]

record = MultisensoralRecord(channels, patient_id='DEMO_001')
scores = record.health_score()

print(f"Overall Score: {scores['overall']:.0f}/100")
print(f"Cardiovascular: {scores['cardiovascular']:.0f}%")
print(f"Oxygenation: {scores['oxygenation']:.0f}%")
```

### Example 3: ECG Education

```python
from educational.ecg_tutor import ECGTutor

tutor = ECGTutor()

# Create a teaching case
case = tutor.create_case('ritmo_sinusal_normal', 'Básico')

# Get teaching material
print(f"Case: {tutor.case_title(case.case_type)}")
print(f"Complexity: {case.complexity}")

# Explanations
explanations = tutor.explain_components(case.signal, case.fs)
for component, text in explanations.items():
    print(f"{component}: {text}\n")

# Create learning quiz
quiz = tutor.generate_quiz()
print(f"Question: {quiz['question']}")
print(f"Options: {quiz['options']}")
```

---

## 🧪 Testing

### Unit Tests

```bash
pytest tests/
```

### Integration Tests

```bash
python -m pytest tests/integration/
```

### Run Demo

```bash
streamlit run app/main.py
# Navigate to "Multisensor" and click "Generate Demo Signals"
```

---

## 🚀 Deployment

### Streamlit Cloud

```bash
# Create .streamlit/secrets.toml with API keys
# Deploy from GitHub

streamlit deploy
```

### Docker

```bash
# Build image
docker build -t bsp:2.0 .

# Run container
docker run -p 8501:8501 bsp:2.0
```

### Standalone Executable

```bash
# Using PyInstaller
pyinstaller --onefile --windowed app/main.py
```

---

## 📋 Minimum Requirements

- **RAM:** 4GB (8GB recommended)
- **Storage:** 2GB (for datasets)
- **CPU:** Dual-core (multi-core preferred)
- **Network:** For MIT-BIH database download (first run)

---

## ❓ Troubleshooting

### Import Errors

```bash
# Ensure project root is in Python path
export PYTHONPATH=$PYTHONPATH:/path/to/Biomedical-Signal-Visualizer
```

### WFDB Download Issues

```bash
# Manual download
mkdir -p datasets
cd datasets
wget -r https://www.physionet.org/physiobank/database/mitdb/
```

### Missing Dependencies

```bash
# Install all optional packages
pip install wfdb mne pyedflib tensorflow fpdf2 plotly kaleido
```

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [PhysioNet MIT-BIH Database](https://physionet.org/content/mitdb/)
- [ECG Interpretation Guidelines](https://www.acc.org)
- [GitHub Repository](https://github.com)

---

## 📞 Support

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Email:** support@example.com
- **Documentation:** [Full Wiki](https://github.com/wiki)

---

Last Updated: 2024
Version: 2.0
Status: Production Ready
