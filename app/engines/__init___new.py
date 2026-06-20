"""BIOCORE AI engine entry points for scalable physiology and digital twin architecture."""

try:
    from .digital_twin import DigitalTwinEngine, DigitalTwinState
except ImportError:
    DigitalTwinEngine = None
    DigitalTwinState = None

try:
    from .physiology_core import PhysiologyCoreEngine, PhysiologySignal, PhysiologicalState
except ImportError:
    PhysiologyCoreEngine = None
    PhysiologySignal = None
    PhysiologicalState = None

try:
    from .digital_twin_multisystem import DigitalTwinMultisystem
except ImportError:
    DigitalTwinMultisystem = None

try:
    from .orchestrator import BiomedicalOrchestratr, SignalRouter, FusionEngine, SignalType, AnalysisMode
except ImportError:
    BiomedicalOrchestratr = None
    SignalRouter = None
    FusionEngine = None
    SignalType = None
    AnalysisMode = None

try:
    from .signal_intelligence import (
        ECGEngine, ECGAnalysis, CardiacRhythm,
        EEGEngine, EEGAnalysis,
        EMGEngine, EMGAnalysis,
        RespiratoryEngine, RespiratoryAnalysis,
        PPGEngine, PPGAnalysis,
    )
except ImportError:
    ECGEngine = None
    ECGAnalysis = None
    CardiacRhythm = None
    EEGEngine = None
    EEGAnalysis = None
    EMGEngine = None
    EMGAnalysis = None
    RespiratoryEngine = None
    RespiratoryAnalysis = None
    PPGEngine = None
    PPGAnalysis = None

__all__ = [
    # Digital Twin
    'DigitalTwinEngine',
    'DigitalTwinState',
    'DigitalTwinMultisystem',
    
    # Physiology Core
    'PhysiologyCoreEngine',
    'PhysiologySignal',
    'PhysiologicalState',
    
    # Orchestration Layer
    'BiomedicalOrchestratr',
    'SignalRouter',
    'FusionEngine',
    'SignalType',
    'AnalysisMode',
    
    # Signal Intelligence Engines
    'ECGEngine', 'ECGAnalysis', 'CardiacRhythm',
    'EEGEngine', 'EEGAnalysis',
    'EMGEngine', 'EMGAnalysis',
    'RespiratoryEngine', 'RespiratoryAnalysis',
    'PPGEngine', 'PPGAnalysis',
]
