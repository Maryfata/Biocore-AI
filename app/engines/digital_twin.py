"""Digital twin engine components for BIOCORE AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import numpy as np
from .physiology_core import PhysiologicalState


@dataclass
class DigitalTwinState:
    timestamp: float
    physiological_state: PhysiologicalState
    interventions: Dict[str, Any] = field(default_factory=dict)
    predictions: Dict[str, float] = field(default_factory=dict)
    alerts: Dict[str, str] = field(default_factory=dict)


class DigitalTwinEngine:
    """Living physiological twin engine for simulation, prediction, and explanation."""

    def __init__(self, physiology_engine: Optional[Any] = None):
        self.physiology_engine = physiology_engine
        self.current_state: Optional[DigitalTwinState] = None

    def initialize(self, timestamp: float, state: PhysiologicalState) -> DigitalTwinState:
        self.current_state = DigitalTwinState(timestamp=timestamp, physiological_state=state)
        return self.current_state

    def update(self, timestamp: float, state: PhysiologicalState) -> DigitalTwinState:
        if self.current_state is None:
            return self.initialize(timestamp, state)
        self.current_state.timestamp = timestamp
        self.current_state.physiological_state = state
        self.current_state.predictions = self._compute_predictions(state)
        self.current_state.alerts = self._generate_alerts(state)
        return self.current_state

    def _compute_predictions(self, state: PhysiologicalState) -> Dict[str, float]:
        return {
            'decompensation_risk': float(max(0.0, 100.0 - state.global_score)),
            'fatigue_risk': float(max(0.0, state.stress - 50.0)),
            'recovery_window': float(np.clip(state.recovery * 0.8, 0.0, 100.0)) if hasattr(state, 'recovery') else 0.0,
        }

    def _generate_alerts(self, state: PhysiologicalState) -> Dict[str, str]:
        alerts = {}
        if state.global_score < 30.0:
            alerts['global'] = 'Estado fisiológico comprometido: activar intervención inmediata.'
        if state.stress > 70.0:
            alerts['stress'] = 'Estrés fisiológico elevado. Evaluar causa subyacente.'
        return alerts

    def simulate_intervention(self, intervention: Dict[str, Any]) -> DigitalTwinState:
        if self.current_state is None:
            raise RuntimeError('Digital twin no ha sido inicializado.')
        self.current_state.interventions.update(intervention)
        self.current_state.physiological_state.global_score = float(np.clip(self.current_state.physiological_state.global_score + 5.0, 0.0, 100.0))
        self.current_state.alerts = self._generate_alerts(self.current_state.physiological_state)
        return self.current_state

    def explain(self) -> str:
        if self.current_state is None:
            return 'Digital twin no inicializado.'
        return (
            'El gemelo digital integra los estados cardiovascular, neurológico, respiratorio y autonómico. '
            f'Global score={self.current_state.physiological_state.global_score:.1f}. '
            'Predice riesgos y ofrece alertas en función de la dinámica fisiológica.'
        )
