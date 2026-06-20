"""Core physiology engine for BIOCORE AI.

This module defines the scalable foundations for signal fusion, state estimation,
and proprietary physiological indicators.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

SUPPORTED_MODALITIES = [
    'ECG', 'EEG', 'EMG', 'PPG', 'SpO2', 'Respiration', 'Temperature', 'BloodPressure', 'Motion'
]


@dataclass
class PhysiologySignal:
    modality: str
    timestamp: float
    values: np.ndarray
    fs: float
    metadata: Dict[str, str] = field(default_factory=dict)

    def normalize(self) -> np.ndarray:
        values = np.asarray(self.values, dtype=float)
        if values.size == 0:
            return values
        mean = np.nanmean(values)
        std = np.nanstd(values)
        return (values - mean) / (std + 1e-8)


@dataclass
class PhysiologicalState:
    global_score: float = 0.0
    cardiovascular: float = 0.0
    neurological: float = 0.0
    respiratory: float = 0.0
    muscular: float = 0.0
    autonomic: float = 0.0
    stress: float = 0.0
    recovery: float = 0.0
    fatigue: float = 0.0
    sleep: float = 0.0
    performance: float = 0.0
    indicators: Dict[str, float] = field(default_factory=dict)


class PhysiologyCoreEngine:
    """Hybrid fusion engine for multisystem physiology and proprietary indicator generation."""

    def __init__(self):
        self.signals: List[PhysiologySignal] = []
        self.state = PhysiologicalState()

    def ingest_signal(self, signal: PhysiologySignal) -> None:
        if signal.modality not in SUPPORTED_MODALITIES:
            raise ValueError(f'Modalidad no soportada: {signal.modality}')
        self.signals.append(signal)

    def clear_signals(self) -> None:
        self.signals.clear()

    def get_signals_by_modality(self, modality: str) -> List[PhysiologySignal]:
        return [s for s in self.signals if s.modality == modality]

    def compute_core_metrics(self) -> Dict[str, float]:
        metrics: Dict[str, float] = {}
        if self.signals:
            metrics['signal_count'] = float(len(self.signals))
            metrics['modalities'] = float(len({s.modality for s in self.signals}))
        else:
            metrics['signal_count'] = 0.0
            metrics['modalities'] = 0.0
        return metrics

    def fuse_signals(self) -> Dict[str, float]:
        """Produce inter-system physiological fusion indicators."""
        fusion = {
            'NeuroCardiacCoupling': 0.0,
            'NeuroRespiratoryCoupling': 0.0,
            'AutonomicBalance': 0.0,
            'RecoveryCapacity': 0.0,
            'PhysiologicalStressIndex': 0.0,
        }
        if self.signals:
            fusion['NeuroCardiacCoupling'] = 50.0
            fusion['NeuroRespiratoryCoupling'] = 50.0
            fusion['AutonomicBalance'] = 50.0
            fusion['RecoveryCapacity'] = 50.0
            fusion['PhysiologicalStressIndex'] = 50.0
        return fusion

    def update_state(self) -> PhysiologicalState:
        metrics = self.compute_core_metrics()
        fusion = self.fuse_signals()
        self.state.global_score = float(np.clip(metrics['modalities'] * 10.0 + fusion['AutonomicBalance'] * 0.4, 0.0, 100.0))
        self.state.cardiovascular = float(fusion['NeuroCardiacCoupling'])
        self.state.neurological = float(fusion['NeuroRespiratoryCoupling'])
        self.state.autonomic = float(fusion['AutonomicBalance'])
        self.state.stress = float(fusion['PhysiologicalStressIndex'])
        self.state.recovery = float(fusion['RecoveryCapacity'])
        self.state.indicators = fusion
        return self.state

    def summarize_state(self) -> str:
        return (
            f"Global State={self.state.global_score:.1f}, "
            f"Cardio={self.state.cardiovascular:.1f}, "
            f"Neuro={self.state.neurological:.1f}, "
            f"Autonomic={self.state.autonomic:.1f}, "
            f"Stress={self.state.stress:.1f}"
        )
