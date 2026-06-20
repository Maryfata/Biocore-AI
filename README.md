BIOCORE AI - Biomedical Signal Visualizer

A Complete Integrated Biomedical Intelligence Operating System.

BIOCORE AI combines classical ICU-grade telemetry (ECG, EMG, EEG, SpO2), hardware integration, machine learning classification, and a deterministic Clinical Decision Support System (CDSS) powered by explainable AI.

📑 Table of Contents

About BIOCORE AI

Ecosystem Features

System Architecture

Comprehensive Setup Guide

Advanced Details

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

Complex Pattern Recognition: Automatically detects syndromes like Cushing's Triad, Septic Shock, and Occult Hemorrhage.

Automated Triage Reports: Generates detailed, explainable clinical narratives.

🧠 3. Proprietary Biomarkers Lab

Neuro-Autonomic Fusion: Merges EEG (Alpha/Theta power) and EDA (Galvanic Skin Response) with HRV.

Scoring: Calculates systemic Stress Index, Cognitive Load, Recovery Index, and NeuroCardiac Coupling.

🦾 4. Hardware Integration

Live EMG/ECG Streaming: Connects via serial port to microcontrollers (ESP32/Arduino).

Hands-Free Control: Computer vision integration (MediaPipe) for sterile, gesture-based UI navigation.

🏗️ System Architecture

Biomedical-Signal-Visualizer/
├── main.py              # Main analysis pipeline orchestrator
├── requirements.txt     # Project dependencies
├── README.md            # This file
├── src/                 # Core biomedical intelligence modules
├── app/                 # Unified Streamlit Ecosystem
├── data/                # Sensor, patient, and MIT-BIH databases
└── models/              # Persisted AI models


🚀 Comprehensive Setup Guide

1. Virtual Environment Setup

Windows:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
python -m venv .venv
.\.venv\Scripts\activate


Mac/Linux:

python3 -m venv .venv
source .venv/bin/activate


2. Dependency Installation

pip install --upgrade pip
pip install -r requirements.txt


3. API Keys Configuration

For the AI Copilot and Tutor modules, create a .env file in the root directory and add:

ANTHROPIC_API_KEY=your_key_here


4. Running the Ecosystem

python -m streamlit run app/main.py


🔬 Advanced Details

Deterministic Expert System (CDSS)

Logic Gates evaluate: HR, SpO2, RR, BP, Temp, EtCO2, GCS, ICP, Lactate, Glucose, Potassium, Sodium, and Body Fat %.

Hardware Integration (ESP32 Example)

#include <Arduino.h>
const int adcPin = 34;

void setup() {
  Serial.begin(115200);
}

void loop() {
  unsigned long t = millis();
  int raw = analogRead(adcPin); 
  Serial.printf("%lu,%d\n", t, raw);
  delay(1);
}


🛡️ Limitations & Disclaimers

Educational & Clinical Support Only: This system is for educational purposes and clinical decision support.

NOT a definitive diagnostic tool: Final diagnosis must be made by qualified medical professionals.

📜 Acknowledgements & Open Source License

This project is fully Open Source and free to use. We acknowledge MIT and PhysioNet for providing the MIT-BIH Arrhythmia Database.
