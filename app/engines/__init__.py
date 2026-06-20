"""BIOCORE AI Engine Layer - Complete Signal Processing & Analysis Framework

This module exports all signal intelligence engines and orchestration components.
Provides comprehensive biomedical signal analysis, multisensor fusion, and digital twin capabilities.
"""

# Core Orchestration
from .orchestrator import (
    BiomedicalOrchestrator,
    SignalRouter,
    FusionEngine,
    SessionManager,
    ModuleRegistry,
    SignalMetadata,
    AnalysisResult,
    SignalType,
    AnalysisMode,
    orchestrator,
)

# Pipeline Coordinator (Main Integration Point)
from .pipeline_coordinator import (
    BiomedicalSignalPipeline,
    PipelineEvent,
    PipelineStage,
    AnalysisResult as PipelineAnalysisResult,
    pipeline,
)

# Physiology Core & Digital Twin
from .digital_twin import DigitalTwinEngine, DigitalTwinState
from .physiology_core import PhysiologyCoreEngine, PhysiologySignal, PhysiologicalState

# Signal Intelligence Engines
from .signal_intelligence import (
    # ECG Engine
    ECGEngine,
    ECGAnalysis,
    CardiacRhythm,
    
    # EEG Engine
    EEGEngine,
    EEGAnalysis,
    
    # EMG Engine
    EMGEngine,
    EMGAnalysis,
    
    # Respiratory Engine
    RespiratoryEngine,
    RespiratoryAnalysis,
    
    # PPG/SpO2 Engine
    PPGEngine,
    PPGAnalysis,
)

# HRV Engine
from .hrv_engine import (
    HRVEngine,
    HRVMetrics,
    AutonomicState,
)

# Multisensor Fusion
from .fusion_engine import (
    FusionEngine as MultisensorFusionEngine,
    MultisensorFusionState,
    CouplingIndex,
    SystemInteraction,
)

__all__ = [
    # Orchestration
    'BiomedicalOrchestrator',
    'SignalRouter',
    'FusionEngine',
    'SessionManager',
    'ModuleRegistry',
    'SignalMetadata',
    'AnalysisResult',
    'SignalType',
    'AnalysisMode',
    'orchestrator',
    
    # Pipeline Coordinator
    'BiomedicalSignalPipeline',
    'PipelineEvent',
    'PipelineStage',
    'PipelineAnalysisResult',
    'pipeline',
    
    # Digital Twin & Physiology
    'DigitalTwinEngine',
    'DigitalTwinState',
    'PhysiologyCoreEngine',
    'PhysiologySignal',
    'PhysiologicalState',
    
    # Signal Intelligence
    'ECGEngine',
    'ECGAnalysis',
    'CardiacRhythm',
    'EEGEngine',
    'EEGAnalysis',
    'EMGEngine',
    'EMGAnalysis',
    'RespiratoryEngine',
    'RespiratoryAnalysis',
    'PPGEngine',
    'PPGAnalysis',
    
    # HRV
    'HRVEngine',
    'HRVMetrics',
    'AutonomicState',
    
    # Multisensor Fusion
    'MultisensorFusionEngine',
    'MultisensorFusionState',
    'CouplingIndex',
    'SystemInteraction',
]


