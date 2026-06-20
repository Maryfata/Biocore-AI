"""
BIOCORE AI — UNIFIED ORCHESTRATION COORDINATOR

Sistema nervioso central integrado de BIOCORE AI.

Coordina el flujo completo:
Signal Input → Signal Intelligence → Multisensor Fusion → Digital Twin → AI Analysis → Output

Este módulo orquesta todos los componentes del sistema en un pipeline cohesivo
y proporciona una interfaz unificada para aplicaciones.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
import numpy as np

from .orchestrator import (
    BiomedicalOrchestrator,
    SignalType,
    SignalMetadata,
    AnalysisMode,
)
from .signal_intelligence import (
    ECGEngine,
    EEGEngine,
    EMGEngine,
    RespiratoryEngine,
    PPGEngine,
)
from .hrv_engine import HRVEngine
from .fusion_engine import MultisensorFusionEngine
from .digital_twin import DigitalTwinEngine
from .physiology_core import PhysiologyCoreEngine

logger = logging.getLogger("biocore.coordinator")


class PipelineStage(Enum):
    """Etapas del pipeline de procesamiento"""
    INPUT = "input"
    SIGNAL_PROCESSING = "signal_processing"
    FUSION = "fusion"
    DIGITAL_TWIN = "digital_twin"
    AI_ANALYSIS = "ai_analysis"
    OUTPUT = "output"


@dataclass
class PipelineEvent:
    """Evento en el pipeline"""
    stage: PipelineStage
    timestamp: datetime
    signal_type: Optional[SignalType] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'stage': self.stage.value,
            'timestamp': self.timestamp.isoformat(),
            'signal_type': self.signal_type.value if self.signal_type else None,
            'data': self.data,
            'error': self.error,
        }


@dataclass
class AnalysisResult:
    """Resultado completo del análisis integrado"""
    timestamp: datetime
    signal_type: SignalType
    individual_analysis: Dict[str, Any]  # Resultado del engine específico
    multisensor_state: Optional[Dict[str, Any]] = None
    digital_twin_state: Optional[Dict[str, Any]] = None
    ai_insights: Optional[Dict[str, Any]] = None
    alerts: List[str] = None
    recommendations: List[str] = None
    confidence: float = 1.0
    
    def __post_init__(self):
        if self.alerts is None:
            self.alerts = []
        if self.recommendations is None:
            self.recommendations = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'signal_type': self.signal_type.value,
            'individual_analysis': self.individual_analysis,
            'multisensor_state': self.multisensor_state,
            'digital_twin_state': self.digital_twin_state,
            'ai_insights': self.ai_insights,
            'alerts': self.alerts,
            'recommendations': self.recommendations,
            'confidence': self.confidence,
        }


class BiomedicalSignalPipeline:
    """
    Pipeline integrado de procesamiento de señales biomédicas.
    
    Orquesta el flujo completo desde entrada de señal hasta análisis de IA
    y salida de recomendaciones clínicas.
    """
    
    def __init__(self):
        """Inicializa el pipeline y todos sus componentes"""
        logger.info("Inicializando BIOCORE AI Signal Pipeline...")
        
        # Componentes principales
        self.orchestrator = BiomedicalOrchestrator()
        self.physiology_core = PhysiologyCoreEngine()
        
        # Signal Intelligence Engines
        self.ecg_engine = ECGEngine()
        self.eeg_engine = EEGEngine()
        self.emg_engine = EMGEngine()
        self.respiratory_engine = RespiratoryEngine()
        self.ppg_engine = PPGEngine()
        self.hrv_engine = HRVEngine()
        
        # Fusion & Digital Twin
        self.fusion_engine = MultisensorFusionEngine()
        self.digital_twin = DigitalTwinEngine()
        
        # Estado del pipeline
        self.current_results: Dict[SignalType, Any] = {}
        self.event_log: List[PipelineEvent] = []
        self.analysis_history: List[AnalysisResult] = []
        
        # Mapeo de engines a tipos de señal
        self.signal_engines = {
            SignalType.ECG: self.ecg_engine,
            SignalType.EEG: self.eeg_engine,
            SignalType.EMG: self.emg_engine,
            SignalType.RESPIRATION: self.respiratory_engine,
            SignalType.PPG: self.ppg_engine,
        }
        
        logger.info("Pipeline inicializado correctamente")
    
    # =====================================================================
    # PIPELINE EXECUTION
    # =====================================================================
    
    def process_signal(self, 
                      signal_type: SignalType,
                      signal_data: np.ndarray,
                      metadata: SignalMetadata,
                      analyze_mode: AnalysisMode = AnalysisMode.CLINICAL) -> AnalysisResult:
        """
        Procesa una señal a través de todo el pipeline.
        
        Pipeline:
        1. INPUT → Validar entrada
        2. SIGNAL PROCESSING → Motor específico de la señal
        3. FUSION → Fusión multisensor
        4. DIGITAL TWIN → Actualizar gemelo digital
        5. AI ANALYSIS → Análisis e insights
        6. OUTPUT → Generar recomendaciones
        """
        
        try:
            # STAGE 1: INPUT
            self._log_event(PipelineStage.INPUT, signal_type)
            
            if not self.orchestrator.validate_signal_quality(metadata):
                logger.warning(f"Señal {signal_type.value} con calidad baja")
            
            # STAGE 2: SIGNAL PROCESSING
            self._log_event(PipelineStage.SIGNAL_PROCESSING, signal_type)
            individual_analysis = self._process_signal_individual(signal_type, signal_data)
            
            if individual_analysis is None:
                raise ValueError(f"No se pudo procesar señal {signal_type.value}")
            
            # STAGE 3: FUSION
            self._log_event(PipelineStage.FUSION, signal_type)
            self.fusion_engine.add_result(signal_type.value, individual_analysis)
            fusion_state = self.fusion_engine.generate_multisystem_state()
            
            # STAGE 4: DIGITAL TWIN
            self._log_event(PipelineStage.DIGITAL_TWIN, signal_type)
            twin_state = self.digital_twin.update(
                timestamp=metadata.timestamp.timestamp(),
                state=self.physiology_core.update_state()
            )
            
            # STAGE 5: AI ANALYSIS
            self._log_event(PipelineStage.AI_ANALYSIS, signal_type)
            ai_insights = self._generate_ai_insights(fusion_state, twin_state)
            
            # STAGE 6: OUTPUT
            self._log_event(PipelineStage.OUTPUT, signal_type)
            
            # Crear resultado integrado
            result = AnalysisResult(
                timestamp=datetime.now(),
                signal_type=signal_type,
                individual_analysis=self._analysis_to_dict(individual_analysis),
                multisensor_state=self._fusion_state_to_dict(fusion_state),
                digital_twin_state=self._twin_state_to_dict(twin_state),
                ai_insights=ai_insights,
                confidence=metadata.quality,
            )
            
            # Generar alertas y recomendaciones
            result.alerts = fusion_state.alerts if fusion_state else []
            result.recommendations = fusion_state.recommendations if fusion_state else []
            
            # Guardar en historial
            self.current_results[signal_type] = individual_analysis
            self.analysis_history.append(result)
            
            logger.info(f"Señal {signal_type.value} procesada exitosamente")
            
            return result
            
        except Exception as e:
            logger.error(f"Error procesando señal {signal_type.value}: {e}")
            self._log_event(PipelineStage.INPUT, signal_type, error=str(e))
            raise
    
    def _process_signal_individual(self, signal_type: SignalType, 
                                   signal_data: np.ndarray) -> Optional[Any]:
        """Procesa la señal con el engine específico"""
        
        try:
            if signal_type == SignalType.ECG:
                r_peaks = self.ecg_engine.detect_r_peaks(signal_data)
                analysis = self.ecg_engine.analyze(signal_data)
                
                # También calcular HRV
                rr_intervals = self.ecg_engine.calculate_rr_intervals(r_peaks)
                if len(rr_intervals) > 20:
                    hrv_metrics = self.hrv_engine.analyze(rr_intervals)
                    return {
                        'ecg': analysis,
                        'hrv': hrv_metrics,
                        'r_peaks': r_peaks,
                    }
                return analysis
                
            elif signal_type == SignalType.EEG:
                analysis = self.eeg_engine.analyze(signal_data)
                return analysis
                
            elif signal_type == SignalType.EMG:
                analysis = self.emg_engine.analyze(signal_data)
                return analysis
                
            elif signal_type == SignalType.RESPIRATION:
                analysis = self.respiratory_engine.analyze(signal_data)
                return analysis
                
            elif signal_type == SignalType.PPG:
                analysis = self.ppg_engine.analyze(signal_data)
                return analysis
                
            else:
                logger.warning(f"Tipo de señal no soportado: {signal_type.value}")
                return None
                
        except Exception as e:
            logger.error(f"Error en procesamiento de {signal_type.value}: {e}")
            return None
    
    def _generate_ai_insights(self, fusion_state: Any, twin_state: Any) -> Dict[str, Any]:
        """Genera insights desde IA basados en estado integrado"""
        
        insights = {
            'summary': '',
            'key_findings': [],
            'risk_assessment': '',
            'recommendations': [],
        }
        
        if fusion_state:
            # Resumen de salud
            insights['summary'] = f"Salud General: {fusion_state.overall_health_index:.0f}%, "
            insights['summary'] += f"Estrés: {fusion_state.physiological_stress_index:.0f}%, "
            insights['summary'] += f"Recuperación: {fusion_state.recovery_capacity_index:.0f}%"
            
            # Hallazgos clave
            if fusion_state.overall_health_index > 75:
                insights['key_findings'].append("✅ Sistema fisiológico en buen estado")
            elif fusion_state.overall_health_index < 40:
                insights['key_findings'].append("⚠️ Índice de salud bajo - evaluación recomendada")
            
            if fusion_state.physiological_stress_index > 70:
                insights['key_findings'].append("⚠️ Estrés fisiológico elevado")
                insights['recommendations'].append("Implementar técnicas de relajación")
            
            # Evaluación de riesgo
            if fusion_state.physiological_stress_index > 80:
                insights['risk_assessment'] = "ALTO riesgo de descompensación"
            elif fusion_state.physiological_stress_index > 60:
                insights['risk_assessment'] = "MODERADO riesgo - monitoreo recomendado"
            else:
                insights['risk_assessment'] = "BAJO riesgo"
        
        if twin_state:
            insights['twin_state'] = {
                'alerts': list(twin_state.alerts.values()) if twin_state.alerts else [],
                'predictions': twin_state.predictions if twin_state.predictions else {},
            }
        
        return insights
    
    # =====================================================================
    # HELPER METHODS
    # =====================================================================
    
    def _analysis_to_dict(self, analysis: Any) -> Dict[str, Any]:
        """Convierte análisis individual a diccionario"""
        if hasattr(analysis, '__dict__'):
            return analysis.__dict__
        return {'data': str(analysis)}
    
    def _fusion_state_to_dict(self, state: Any) -> Dict[str, Any]:
        """Convierte estado de fusión a diccionario"""
        if not state:
            return {}
        
        result = {
            'timestamp': state.timestamp.isoformat() if hasattr(state, 'timestamp') else None,
            'physiological_stress_index': state.physiological_stress_index,
            'recovery_capacity_index': state.recovery_capacity_index,
            'resilience_index': state.resilience_index,
            'overall_health_index': state.overall_health_index,
            'anomalies': state.anomalies_detected,
        }
        return result
    
    def _twin_state_to_dict(self, state: Any) -> Dict[str, Any]:
        """Convierte estado del gemelo digital a diccionario"""
        if not state:
            return {}
        
        result = {
            'timestamp': state.timestamp,
            'alerts': state.alerts if state.alerts else {},
            'predictions': state.predictions if state.predictions else {},
        }
        return result
    
    def _log_event(self, stage: PipelineStage, signal_type: Optional[SignalType] = None,
                   error: Optional[str] = None) -> None:
        """Registra un evento en el log del pipeline"""
        event = PipelineEvent(
            stage=stage,
            timestamp=datetime.now(),
            signal_type=signal_type,
            error=error,
        )
        self.event_log.append(event)
    
    # =====================================================================
    # MONITORING & REPORTING
    # =====================================================================
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Obtiene estado actual del pipeline"""
        return {
            'timestamp': datetime.now().isoformat(),
            'processed_signals': len(self.current_results),
            'total_analyses': len(self.analysis_history),
            'event_log_size': len(self.event_log),
            'signal_types_processed': [st.value for st in self.current_results.keys()],
        }
    
    def get_latest_analysis(self) -> Optional[AnalysisResult]:
        """Obtiene el último análisis realizado"""
        if self.analysis_history:
            return self.analysis_history[-1]
        return None
    
    def get_comprehensive_report(self) -> str:
        """Genera reporte comprehensivo del estado actual"""
        report = f"""
        ════════════════════════════════════════════════════════════════════
                         BIOCORE AI COMPREHENSIVE REPORT
        ════════════════════════════════════════════════════════════════════
        
        Timestamp: {datetime.now().isoformat()}
        
        📊 PIPELINE STATUS:
        • Total analyses: {len(self.analysis_history)}
        • Signal types processed: {len(self.current_results)}
        
        🔍 LATEST ANALYSIS:
        """
        
        latest = self.get_latest_analysis()
        if latest:
            report += f"""
        • Signal Type: {latest.signal_type.value}
        • Confidence: {latest.confidence:.0%}
        • Alerts: {len(latest.alerts)}
        • Recommendations: {len(latest.recommendations)}
        """
        
        if latest.ai_insights:
            report += f"""
        
        💡 AI INSIGHTS:
        • {latest.ai_insights.get('summary', 'N/A')}
        • Risk Assessment: {latest.ai_insights.get('risk_assessment', 'N/A')}
        """
        
        report += "\n        ════════════════════════════════════════════════════════════════════\n"
        return report
    
    def reset(self) -> None:
        """Reinicia el pipeline"""
        logger.info("Reiniciando pipeline...")
        self.current_results.clear()
        self.event_log.clear()
        self.fusion_engine.clear_results()
        logger.info("Pipeline reiniciado")


# Instancia global del pipeline
pipeline = BiomedicalSignalPipeline()
