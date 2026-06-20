"""
BIOCORE AI OMEGA — EJEMPLO COMPLETO DE USO

Demuestra cómo usar:
1. Signal Intelligence Layer (5 engines)
2. Multisensor Fusion Engine
3. Digital Twin Multisystem
4. Orchestration Layer

Este script genera datos sintéticos y los procesa completamente
a través de toda la arquitectura OMEGA.
"""

import numpy as np
from datetime import datetime
import json

# Importar engines
from app.engines.signal_intelligence import (
    ECGEngine, EEGEngine, EMGEngine, 
    RespiratoryEngine, PPGEngine
)
from app.engines.fusion_engine import FusionEngine
from app.engines.digital_twin_multisystem import DigitalTwinMultisystem
from app.engines.orchestrator import (
    BiomedicalOrchestratr, SignalType, AnalysisMode
)


def generate_demo_signals(duration: float = 10.0, sampling_rate: float = 250.0):
    """
    Genera señales biomédicas sintéticas para demostración
    """
    samples = int(duration * sampling_rate)
    t = np.linspace(0, duration, samples)
    
    # ECG: Señal simulada (aproximadamente sinusoidal + ruido)
    hr = 72  # Frecuencia cardíaca base (bpm)
    ecg_freq = hr / 60  # Hz
    ecg = np.sin(2 * np.pi * ecg_freq * t) + 0.1 * np.sin(2 * np.pi * 3 * ecg_freq * t)
    ecg += 0.05 * np.random.randn(samples)  # Ruido
    
    # EEG: Banda alfa (~10 Hz) con modulación
    eeg = 5 * np.sin(2 * np.pi * 10 * t) + 2 * np.sin(2 * np.pi * 5 * t)
    eeg += np.random.randn(samples)  # Ruido
    
    # EMG: Actividad muscular (bursts aleatorios)
    emg = np.random.randn(samples) * 0.5
    for i in range(5):
        start = int(i * samples / 5)
        end = int((i + 0.3) * samples / 5)
        emg[start:end] += 2 * np.sin(2 * np.pi * 50 * t[start:end])
    
    # Respiración: ~15 respiraciones por minuto
    respiration = 2 * np.sin(2 * np.pi * 0.25 * t) + 0.3 * np.random.randn(samples)
    
    # PPG: Similar a ECG pero con variabilidad
    ppg = np.sin(2 * np.pi * ecg_freq * t) + 0.15 * np.sin(2 * np.pi * 2 * ecg_freq * t)
    ppg += 0.1 * np.random.randn(samples)
    
    return {
        'ecg': ecg,
        'eeg': eeg,
        'emg': emg,
        'respiration': respiration,
        'ppg': ppg,
        'sampling_rate': sampling_rate,
        'duration': duration,
        'time_vector': t
    }


def demo_signal_intelligence():
    """
    DEMO 1: Signal Intelligence Layer
    Procesa cada señal individualmente
    """
    print("\n" + "="*70)
    print("DEMO 1: SIGNAL INTELLIGENCE LAYER")
    print("="*70)
    
    signals = generate_demo_signals(duration=10, sampling_rate=250)
    
    # ECG Engine
    print("\n🫀 ECG ENGINE:")
    ecg_engine = ECGEngine()
    ecg_analysis = ecg_engine.analyze(signals['ecg'])
    print(f"   • Heart Rate: {ecg_analysis.heart_rate:.1f} bpm")
    print(f"   • HRV: {ecg_analysis.hrv:.1f} ms")
    print(f"   • Rhythm: {ecg_analysis.rhythm.value}")
    print(f"   • Risk Score: {ecg_analysis.risk_score:.2f}")
    print(f"   • Interpretation: {ecg_analysis.interpretation}")
    
    # EEG Engine
    print("\n🧠 EEG ENGINE:")
    eeg_engine = EEGEngine()
    eeg_analysis = eeg_engine.analyze(signals['eeg'])
    print(f"   • Attention: {eeg_analysis.attention:.1f}%")
    print(f"   • Relaxation: {eeg_analysis.relaxation_level:.1f}%")
    print(f"   • Sleepiness: {eeg_analysis.sleepiness:.1f}%")
    print(f"   • Brain State: {eeg_analysis.brain_state}")
    print(f"   • Interpretation: {eeg_analysis.interpretation}")
    
    # EMG Engine
    print("\n💪 EMG ENGINE:")
    emg_engine = EMGEngine()
    emg_analysis = emg_engine.analyze(signals['emg'])
    print(f"   • RMS Amplitude: {emg_analysis.rms_amplitude:.2f} μV")
    print(f"   • Fatigue Index: {emg_analysis.fatigue_index:.1f}%")
    print(f"   • Activation Level: {emg_analysis.activation_level:.1f}%")
    print(f"   • Efficiency: {emg_analysis.efficiency:.1f}%")
    print(f"   • Interpretation: {emg_analysis.interpretation}")
    
    # Respiratory Engine
    print("\n💨 RESPIRATORY ENGINE:")
    resp_engine = RespiratoryEngine()
    resp_analysis = resp_engine.analyze(signals['respiration'], duration=10)
    print(f"   • Respiratory Rate: {resp_analysis.respiratory_rate:.1f} resp/min")
    print(f"   • Pattern: {resp_analysis.breathing_pattern}")
    print(f"   • Ventilation Quality: {resp_analysis.ventilation_quality:.1f}%")
    print(f"   • Apnea Risk: {resp_analysis.apnea_risk:.1f}%")
    print(f"   • Interpretation: {resp_analysis.interpretation}")
    
    # PPG Engine
    print("\n🫀 PPG ENGINE:")
    ppg_engine = PPGEngine()
    ppg_analysis = ppg_engine.analyze(signals['ppg'])
    print(f"   • SpO2: {ppg_analysis.spo2:.1f}%")
    print(f"   • Pulse Rate: {ppg_analysis.pulse_rate:.1f} bpm")
    print(f"   • Perfusion Index: {ppg_analysis.perfusion_index:.1f}%")
    print(f"   • Vascular Tone: {ppg_analysis.vascular_tone}")
    print(f"   • Interpretation: {ppg_analysis.interpretation}")
    
    return {
        'ecg': ecg_analysis,
        'eeg': eeg_analysis,
        'emg': emg_analysis,
        'respiration': resp_analysis,
        'ppg': ppg_analysis
    }


def demo_fusion_engine(analyses):
    """
    DEMO 2: Multisensor Fusion Engine
    Integra todos los análisis individuales
    """
    print("\n" + "="*70)
    print("DEMO 2: MULTISENSOR FUSION ENGINE")
    print("="*70)
    
    fusion = FusionEngine()
    
    # Añadir todos los resultados
    fusion.add_result('ECG', analyses['ecg'])
    fusion.add_result('EEG', analyses['eeg'])
    fusion.add_result('EMG', analyses['emg'])
    fusion.add_result('Respiratory', analyses['respiration'])
    fusion.add_result('PPG', analyses['ppg'])
    
    # Generar estado integrado
    state = fusion.generate_multisystem_state()
    
    # Mostrar acoplamientos
    print("\n🔗 ACOPLAMIENTO NEUROCARDIACO:")
    if state.neurocardiac_coupling:
        nc = state.neurocardiac_coupling
        print(f"   • Valor: {nc.value:.2f}")
        print(f"   • Interpretación: {nc.interpretation}")
        print(f"   • Riesgo: {nc.risk_level}")
    
    print("\n🔗 ACOPLAMIENTO CARDIORRESPIRATORIO:")
    if state.cardiorespiratory_coupling:
        cr = state.cardiorespiratory_coupling
        print(f"   • Valor: {cr.value:.2f}")
        print(f"   • Interpretación: {cr.interpretation}")
        print(f"   • Riesgo: {cr.risk_level}")
    
    print("\n🔗 ACOPLAMIENTO NEUROMUSCULAR:")
    if state.neuromuscular_coupling:
        nm = state.neuromuscular_coupling
        print(f"   • Valor: {nm.value:.2f}")
        print(f"   • Interpretación: {nm.interpretation}")
        print(f"   • Riesgo: {nm.risk_level}")
    
    # Índices integrados
    print("\n📊 ÍNDICES INTEGRADOS:")
    print(f"   • Salud General: {state.overall_health_index:.1f}%")
    print(f"   • Estrés Fisiológico: {state.physiological_stress_index:.1f}%")
    print(f"   • Capacidad Recuperación: {state.recovery_capacity_index:.1f}%")
    print(f"   • Resiliencia: {state.resilience_index:.1f}%")
    
    # Anomalías
    if state.anomalies_detected:
        print("\n⚠️  ANOMALÍAS DETECTADAS:")
        for anomaly in state.anomalies_detected:
            print(f"   {anomaly}")
    else:
        print("\n✅ No se detectaron anomalías")
    
    # Recomendaciones
    if state.recommendations:
        print("\n💡 RECOMENDACIONES:")
        for rec in state.recommendations:
            print(f"   {rec}")
    
    # Resumen completo
    print("\n📋 RESUMEN DE SALUD:")
    print(fusion.get_health_summary())
    
    return state


def demo_digital_twin(analyses):
    """
    DEMO 3: Digital Human Twin
    Simula 10 gemelos digitales interconectados
    """
    print("\n" + "="*70)
    print("DEMO 3: DIGITAL HUMAN TWIN (10 Physiological Twins)")
    print("="*70)
    
    twin = DigitalTwinMultisystem()
    
    # Actualizar desde sensores
    print("\n🔄 Actualizando gemelos desde datos de sensores...")
    twin.update_from_sensors(
        ecg_signal=np.random.randn(250),
        respiratory_signal=np.random.randn(100),
        spo2_signal=np.random.randn(100),
        eeg_signal=np.random.randn(250),
        emg_signals={'biceps': np.random.randn(1000)}
    )
    
    # Simular intervención
    print("\n💊 Simulando intervención: Oxígeno Suplementario...")
    twin.simulate_intervention('oxygen', intensity=0.7)
    
    print(f"\n   • SpO2 Proyectado: {twin.oxygenation_state.spo2:.1f}%")
    print(f"   • Estrés Cardiaco: {twin.cardiac_state.myocardial_stress:.1f}%")
    print(f"   • Cambio HR: {twin.cardiac_state.heart_rate - 72:.1f} bpm")
    
    # Predicciones
    print("\n🔮 PREDICCIONES FISIOLÓGICAS:")
    predictions = twin.predict_physiological_events()
    for prediction in predictions:
        print(f"   • {prediction}")
    
    # Generar reporte clínico
    print("\n📋 REPORTE CLÍNICO DEL GEMELO DIGITAL:")
    report = twin.generate_clinical_summary()
    print(report)
    
    return twin


def demo_orchestrator(signals):
    """
    DEMO 4: Orchestration Layer
    Procesa señales a través del pipeline completo
    """
    print("\n" + "="*70)
    print("DEMO 4: ORCHESTRATION LAYER (Complete Pipeline)")
    print("="*70)
    
    orchestrator = BiomedicalOrchestratr()
    
    # Iniciar sesión clínica
    orchestrator.session_manager.start_session(
        user_id="doctor001",
        patient_id="patient001",
        notes="Demostración de arquitectura OMEGA"
    )
    orchestrator.session_manager.set_mode(AnalysisMode.CLINICAL)
    
    print(f"\n✅ Sesión iniciada: {orchestrator.session_manager.current_user}")
    print(f"   • Modo: {orchestrator.session_manager.current_mode.value}")
    
    # Procesar señal ECG
    print("\n📊 Procesando señal ECG...")
    result = orchestrator.process_signal(
        signal_type=SignalType.ECG,
        signal_data=signals['ecg'],
        metadata={
            'sampling_rate': signals['sampling_rate'],
            'duration': signals['duration']
        }
    )
    
    if result:
        print(f"   ✅ Análisis completado")
        print(f"   • Timestamp: {result.timestamp}")
        print(f"   • Tipo: {result.signal_type.value}")
        print(f"   • Modo: {result.analysis_mode.value}")
    
    # Ver estado de módulos
    print("\n📦 ESTADO DE MÓDULOS:")
    registry = orchestrator.module_registry
    print(f"   • ECG Engine: {'✅' if registry.is_enabled('ecg') else '❌'}")
    print(f"   • EEG Engine: {'✅' if registry.is_enabled('eeg') else '❌'}")
    print(f"   • EMG Engine: {'✅' if registry.is_enabled('emg') else '❌'}")
    print(f"   • Respiratory Engine: {'✅' if registry.is_enabled('respiratory') else '❌'}")
    print(f"   • PPG Engine: {'✅' if registry.is_enabled('ppg') else '❌'}")
    
    return orchestrator


def main():
    """
    Ejecuta todas las demostraciones
    """
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  BIOCORE AI OMEGA — DEMOSTRACIÓN COMPLETA".center(68) + "║")
    print("║" + "  Arquitectura Integrada de Análisis Biomédico".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    # DEMO 1: Signal Intelligence
    analyses = demo_signal_intelligence()
    
    # DEMO 2: Fusion
    fusion_state = demo_fusion_engine(analyses)
    
    # DEMO 3: Digital Twin
    digital_twin = demo_digital_twin(analyses)
    
    # DEMO 4: Orchestration
    signals = generate_demo_signals()
    orchestrator = demo_orchestrator(signals)
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN FINAL")
    print("="*70)
    
    print("\n✅ CAPAS EJECUTADAS:")
    print("   1. ✅ Signal Intelligence Layer (5 engines)")
    print("   2. ✅ Multisensor Fusion Engine")
    print("   3. ✅ Digital Human Twin Engine")
    print("   4. ✅ Orchestration Layer")
    
    print("\n📊 DATOS GENERADOS:")
    print(f"   • Salud General: {fusion_state.overall_health_index:.1f}%")
    print(f"   • Estrés Fisiológico: {fusion_state.physiological_stress_index:.1f}%")
    print(f"   • Capacidad Recuperación: {fusion_state.recovery_capacity_index:.1f}%")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("   1. Integrar con AI Core Engine")
    print("   2. Implementar Education Engine")
    print("   3. Crear Research Engine")
    print("   4. Agregar database layer")
    
    print("\n✨ Demostración completada exitosamente\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error durante la demostración: {e}")
        import traceback
        traceback.print_exc()
