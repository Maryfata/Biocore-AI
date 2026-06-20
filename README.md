🧬 BIOCORE AI & Biomedical Signal Visualizer

A Complete Integrated Biomedical Intelligence Operating System

What started as a modular, research-ready ECG analysis and arrhythmia detection system has evolved into a comprehensive computational cardiology and critical care platform.

📑 Table of Contents

About BIOCORE AI

Ecosystem Features

System Architecture

Comprehensive Setup Guide

Advanced Details (ML, Hardware, Report)

Limitations & Disclaimers

Acknowledgements & Open Source License

🔬 About BIOCORE AI

BIOCORE AI combines classical ICU-grade telemetry (ECG, EMG, EEG, SpO2), hardware integration, machine learning classification, and a deterministic Clinical Decision Support System (CDSS) powered by explainable AI.

✨ Ecosystem Features

🫀 1. Computational Cardiology & ML

Signal Processing: ECG filtering, adaptive R-peak detection, and RR interval computation.

Feature Extraction: Temporal (SDNN, RMSSD), frequency-domain (LF/HF ratio), and nonlinear HRV features.

Machine Learning Classifier: Binary classification (Normal vs. Arrhythmia) trained on the MIT-BIH Arrhythmia Database.

🏥 2. Clinical Expert System (CDSS)

Multi-System Deterministic Engine: ICU-grade reasoning engine evaluating over 50 physiological logic gates.

Complex Pattern Recognition: Automatically detects syndromes like Cushing's Triad, Septic Shock, and Occult Hemorrhage by cross-referencing vitals and laboratory metrics.

Automated Triage Reports: Generates detailed, explainable clinical narratives without LLM hallucinations.

🧠 3. Proprietary Biomarkers Lab

Neuro-Autonomic Fusion: Merges EEG (Alpha/Theta power) and EDA (Galvanic Skin Response) with HRV.

Scoring: Calculates systemic Stress Index, Cognitive Load, Recovery Index, and NeuroCardiac Coupling.

🦾 4. Hardware Integration

Live EMG/ECG Streaming: Connects via serial port to microcontrollers (ESP32/Arduino) for real-time muscular and cardiac activation tracking.

Hands-Free Control: Computer vision integration (MediaPipe) for sterile, gesture-based UI navigation.

🏗️ System Architecture

Biomedical-Signal-Visualizer/
│
├── main.py                      # Main analysis pipeline orchestrator
├── requirements.txt             # Project dependencies
├── README.md                    # This file
│
├── src/                         # Core biomedical intelligence modules
│   ├── signal_processing.py     # ECG filtering, R-peak detection
│   ├── feature_extraction.py    # HRV and multisensor feature computation
│   ├── machine_learning.py      # ML Model training and prediction
│   └── interpretability.py      # Clinical reasoning for ML
│
├── app/                         # Unified Streamlit Ecosystem
│   ├── main.py                  # Streamlit UI Entrypoint (The Hubs)
│   ├── clinical_ai.py           # Deterministic ICU-grade CDSS Engine
│   ├── biomarkers.py            # Proprietary Neuro/Autonomic Biomarkers
│   └── ai_copilot.py            # LLM-powered Medical Tutor
│
├── data/                        # Sensor, patient, and MIT-BIH databases
└── models/                      # Persisted AI models


🚀 Comprehensive Setup Guide

This guide covers the environment setup for Windows, Mac, and Linux, including hardware troubleshooting.

1. Virtual Environment Setup

Windows:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
python -m venv .venv
.\.venv\Scripts\activate


Mac/Linux:

python3 -m venv .venv
source .venv/bin/activate


2. Dependency Installation

Install all core data science, visualization, and biomedical libraries:

python -m pip install --upgrade pip
pip install -r requirements.txt


3. API Keys Configuration (Optional)

For the AI Copilot and Tutor modules, create a .env file in the root directory and add:

ANTHROPIC_API_KEY=your_key_here


4. Running the Ecosystem

Launch the Streamlit web platform:

python -m streamlit run app/main.py


(The App will open at http://localhost:8501)

💡 Troubleshooting Memory Errors (OpenBLAS): If the app crashes on startup on Windows, close VS Code, open Windows Task Manager, kill all Python processes, and retry Step 4.

🔬 Advanced Details

Classical Machine Learning Pipeline (Arrhythmia Detection)

Dataset: MIT-BIH Arrhythmia Database via PhysioNet (wfdb).

Feature Extraction: Temporal (Mean RR, SDNN, RMSSD), Frequency (LF, HF, LF/HF), and Morphological constraints.

Model Architecture: Logistic Regression / Random Forest Classifier with Stratified K-Fold Cross Validation.

Metrics Achieved: Accuracy (~87%), High Recall (~89%) to minimize false negatives in a clinical context.

Deterministic Expert System (CDSS)

To circumvent hallucination risks in healthcare, a deterministic physiological engine (clinical_ai.py) was implemented.

Logic Gates: Over 50 hardcoded thresholds based on intensive care literature (ATLS, Surviving Sepsis).

Variables: HR, SpO2, RR, BP (Sys/Dia/MAP), Temp, EtCO2, GCS, ICP, Lactate, Glucose, Potassium, Sodium, Body Fat %.

Proprietary Biomarkers Engine

A mathematical fusion model that calculates non-standard indices:

Stress Index: Weighted function of LF/HF ratio, EDA Skin Conductance Responses, and inverted RMSSD.

Cognitive Load: Ratio of EEG Theta/Alpha power mapped against heart rate accelerations.

NeuroCardiac Coupling: Cross-coherence mapping between Alpha brainwaves and HRV (SDNN).

The platform supports live hardware streaming for modules like the EMG Muscle Lab. Ensure your microcontroller outputs data via Serial at 115200 baud. Ensure your OS grants permission to read the Serial Port (COM on Windows, /dev/ttyUSB or /dev/ttyACM on Linux/Mac).

Minimal ESP32 Sketch:

#include <Arduino.h>
const int adcPin = 34; // Example ADC Pin

void setup() {
  Serial.begin(115200);
  delay(1000);
}

void loop() {
  unsigned long t = millis();
  int raw = analogRead(adcPin); 
  Serial.printf("%lu,%d\n", t, raw);
  delay(1); // ~1000 Hz sample rate
}


Executive Summary

The BIOCORE AI project has successfully transitioned from an offline, script-based ECG analysis tool into a fully integrated, containerized web application suitable for real-time clinical monitoring, education, and physiological simulation.

Milestones Achieved

Core Signal Processing: Implemented adaptive bandpass filtering, robust R-peak detection, and frequency-domain HRV metrics using SciPy.

Machine Learning Integration: Trained a classification model on the MIT-BIH database with Explainable AI (XAI) text generation for clinical transparency.

Hardware & UI Ecosystem: Migrated to a multi-hub Streamlit architecture with pyserial streamers for live hardware data ingestion and hands-free UI control via MediaPipe.

Advanced Clinical Intelligence: Developed the Biomarkers Lab (Neuro/Autonomic fusion) and a Deterministic CDSS capable of outputting ICU-grade medical reports with personalized anthropometric calculations.

Future Roadmap

Cloud Database Integration: Migrate SQLite local states to Firebase/Supabase for cross-device patient tracking.

LLM RAG Integration: Connect the deterministic CDSS to a local open-source LLM (via Ollama) and a Vector Database containing clinical guidelines.

🛡️ Limitations & Disclaimers

⚠️ Educational & Clinical Support Only

This system is for educational purposes and clinical decision support.

NOT a definitive diagnostic tool - requires clinician interpretation.

Final diagnosis must be made by qualified medical professionals.

⚠️ Dataset Dependency

Model accuracy depends on training dataset composition.

Transfer learning to other populations may be needed.

📜 Acknowledgements & Open Source License

This project is fully Open Source and free to use. We would like to acknowledge MIT (Massachusetts Institute of Technology) and PhysioNet for providing the MIT-BIH Arrhythmia Database, which was strictly used as the foundational dataset for training and validating our machine learning models.

The entire system architecture, physiological engines, and biomedical integrations were built from scratch by our team.