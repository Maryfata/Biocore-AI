# Biomedical Reasoning Engine - Guía Completa

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [Arquitectura](#arquitectura)
3. [Instalación](#instalación)
4. [Uso del Motor](#uso-del-motor)
5. [Integración con Streamlit](#integración-con-streamlit)
6. [Integración con Pipeline Existente](#integración-con-pipeline-existente)
7. [Ejemplos Prácticos](#ejemplos-prácticos)
8. [API Reference](#api-reference)

---

## Descripción General

El **Biomedical Reasoning Engine (BRE)** es un motor de razonamiento clínico que transforma métricas fisiológicas (HRV, ECG) en:

- **Hallazgos fisiológicos** con confianza
- **Hipótesis clínicas** basadas en patrones
- **Diagnósticos diferenciales** educativos
- **Estimación de riesgo** (0-100 escala)
- **Recomendaciones educativas** personalizadas
- **Clasificación del estado autonómico**

### Entrada

```python
HRVMetrics(
    bpm: float,           # Latidos por minuto
    sdnn: float,         # Desv. estándar de intervalos RR (segundos)
    rmssd: float,        # Raíz cuadrada de diferencias al cuadrado
    pnn50: float,        # % de diferencias RR > 50ms
    lf: float,           # Potencia banda baja frecuencia
    hf: float,           # Potencia banda alta frecuencia
    lf_hf: float,        # Relación LF/HF
    entropy: float,      # Complejidad del ritmo
    ai_score: Optional[float] = None  # Score de anomalía IA (0-1)
)
```

### Salida

```python
ReasoningOutput(
    findings: List[PhysiologicalFinding],
    hypotheses: List[ClinicalHypothesis],
    differential_diagnoses: List[DifferentialDiagnosis],
    risk_level: RiskLevel,  # BAJO, MODERADO, ALTO, CRÍTICO
    autonomic_state: AutonomicState,  # SIMPÁTICO, PARASIMPÁTICO, EQUILIBRIO, DISFUNCIÓN
    risk_score: float,  # 0-100
    main_narrative: str,
    clinical_impression: str,
    recommendations: List[EducationalRecommendation],
    warnings: List[str]
)
```

---

## Arquitectura

### Componentes Principales

#### 1. **PhysiologicalPatternDetector**
Detecta patrones fisiológicos reconocibles:
- Taquicardia (leve/moderada/severa)
- Bradicardia (leve/moderada/severa)
- Variabilidad alta/baja
- Dominancia simpática/parasimpática
- Entropía alta/baja

#### 2. **ClinicalHypothesisGenerator**
Genera hipótesis clínicas con:
- Probabilidad estimada (0-1)
- Métricas de apoyo
- Contraindicaciones
- Próximos pasos
- Notas educativas

#### 3. **DifferentialDiagnosisGenerator**
Genera diagnósticos diferenciales educativos con:
- Condición
- Características cardinales
- Hallazgos de apoyo
- Características distinguidoras
- Recomendaciones de investigación

#### 4. **RiskEstimator**
Estima riesgo global (0-100):
- Factor frecuencia cardíaca
- Factor variabilidad
- Factor entropía
- Factor balance autonómico
- Factor AI score
- Factor hallazgos adversos

#### 5. **AutonomicStateClassifier**
Clasifica estado del sistema nervioso autónomo:
- **SIMPÁTICO**: Activación del sistema simpático
- **PARASIMPÁTICO**: Activación del sistema parasimpático
- **EQUILIBRIO**: Balance autonómico
- **DISFUNCIÓN**: Función autonómica deteriorada

#### 6. **EducationalRecommendationGenerator**
Genera recomendaciones educativas:
- Categoría (lifestyle, monitoring, investigation, clinical_follow_up)
- Recomendación específica
- Razón fundamentada
- Nivel de urgencia (routine, soon, urgent)
- Nivel de evidencia (A, B, C)

#### 7. **BiomedicalReasoningEngine**
Orquestador principal que:
- Valida métricas
- Coordina detectores
- Integra hallazgos
- Genera narrativa clínica
- Produce advertencias

### Principios SOLID

- **S**: Cada clase tiene única responsabilidad
- **O**: Abierto a extensión (nuevos patrones, reglas)
- **L**: Sustitución de Liskov respetada
- **I**: Interfaces segregadas por responsabilidad
- **D**: Inversión de dependencias mediante abstracciones

---

## Instalación

### 1. Agregar a requirements.txt

```bash
# Las siguientes librerías son necesarias (ya presentes):
numpy>=1.23.0
scipy>=1.10.0
pandas>=1.5.0
plotly>=5.10.0
streamlit>=1.25.0
```

### 2. Verificar módulo en src/

```
src/
  reasoning_engine.py  ✓ (creado)
```

### 3. Verificar tests en tests/

```
tests/
  test_reasoning_engine.py  ✓ (creado)
```

---

## Uso del Motor

### Uso Básico

```python
from src.reasoning_engine import BiomedicalReasoningEngine, HRVMetrics

# Inicializar motor
engine = BiomedicalReasoningEngine()

# Crear métricas
metrics = HRVMetrics(
    bpm=112,
    sdnn=0.08,
    rmssd=0.02,
    pnn50=8,
    lf=3.5,
    hf=1.0,
    lf_hf=3.5,
    entropy=2.5,
    ai_score=0.65
)

# Ejecutar razonamiento
output = engine.reason(metrics)

# Acceder resultados
print(f"Riesgo: {output.risk_level.value}")
print(f"Puntuación: {output.risk_score:.1f}/100")
print(f"Estado autonómico: {output.autonomic_state.value}")
print(f"Impresión clínica: {output.clinical_impression}")
```

### Validación de Métricas

```python
metrics = HRVMetrics(...)

is_valid, msg = metrics.validate()
if not is_valid:
    print(f"Error: {msg}")
else:
    output = engine.reason(metrics)
```

### Acceso a Componentes Individuales

```python
from src.reasoning_engine import (
    PhysiologicalPatternDetector,
    ClinicalHypothesisGenerator,
    RiskEstimator,
)

# Detectar patrones
detector = PhysiologicalPatternDetector()
findings = detector.detect_all(metrics)

# Generar hipótesis
hyp_gen = ClinicalHypothesisGenerator()
hypotheses = hyp_gen.generate_hypotheses(findings, metrics)

# Estimar riesgo
risk_level, risk_score = RiskEstimator.estimate_risk(metrics, findings)
```

### Serialización

```python
# A diccionario
output_dict = output.to_dict()

# A JSON
output_json = output.to_json()

# Guardar a archivo
with open("reasoning_output.json", "w") as f:
    f.write(output_json)
```

---

## Integración con Streamlit

### Opción 1: App Completa Independiente

```bash
streamlit run app/reasoning_engine_streamlit.py
```

### Opción 2: Integración en Página Existente

```python
# En app/pages/0_🏠_Home.py (o cualquier página)
import streamlit as st
from app.reasoning_engine_streamlit import (
    BiomedicalReasoningStreamlit,
    create_reasoning_component
)

st.title("Mi Página")

# Componente integrado
result = create_reasoning_component("Análisis HRV")

if result:
    st.success("Análisis completado")
    st.write(result.risk_level)
```

### Opción 3: Componente Personalizado

```python
from app.reasoning_engine_streamlit import BiomedicalReasoningStreamlit
import streamlit as st

app = BiomedicalReasoningStreamlit()

# Panel de entrada (lado izquierdo)
metrics = app.input_metrics_panel()

if metrics:
    from src.reasoning_engine import BiomedicalReasoningEngine
    engine = BiomedicalReasoningEngine()
    output = engine.reason(metrics)
    
    # Mostrar componentes individuales
    app.display_risk_dashboard(output)
    app.display_clinical_impression(output)
    app.display_findings(output)
    app.display_hypotheses(output)
    app.display_differential_diagnoses(output)
    app.display_recommendations(output)
```

---

## Integración con Pipeline Existente

### Pipeline Actual

```
ECG → Filtrado → R Peaks → HRV → Machine Learning → Explainable AI → Reportes
```

### Pipeline Mejorado

```
ECG → Filtrado → R Peaks → HRV → Biomedical Reasoning Engine → IA → Reportes
```

### Integración Paso a Paso

#### 1. En el módulo que calcula HRV

```python
# En app/ecg_trainer.py o equivalente
from src.reasoning_engine import BiomedicalReasoningEngine, HRVMetrics

class ECGTrainer:
    def analyze_hrv(self, intervals_rr, ai_score=None):
        # Código existente de cálculo HRV
        bpm, sdnn, rmssd, pnn50, lf, hf, lf_hf = self.calculate_hrv_metrics(intervals_rr)
        entropy = self.calculate_entropy(intervals_rr)
        
        # NUEVO: Integración con Reasoning Engine
        metrics = HRVMetrics(
            bpm=bpm,
            sdnn=sdnn,
            rmssd=rmssd,
            pnn50=pnn50,
            lf=lf,
            hf=hf,
            lf_hf=lf_hf,
            entropy=entropy,
            ai_score=ai_score
        )
        
        engine = BiomedicalReasoningEngine()
        reasoning_output = engine.reason(metrics)
        
        return {
            'hrv_metrics': {
                'bpm': bpm,
                'sdnn': sdnn,
                'rmssd': rmssd,
                'pnn50': pnn50,
                'lf': lf,
                'hf': hf,
                'lf_hf': lf_hf,
                'entropy': entropy
            },
            'reasoning': reasoning_output  # NUEVO
        }
```

#### 2. En reportes

```python
# En app/reporting.py o equivalente
def generate_report(analysis_results):
    hrv_data = analysis_results['hrv_metrics']
    reasoning = analysis_results['reasoning']  # NUEVO
    
    report = f"""
    ## Análisis Cardiométrico
    
    ### Métricas HRV
    - BPM: {hrv_data['bpm']:.0f}
    - SDNN: {hrv_data['sdnn']:.4f}
    - RMSSD: {hrv_data['rmssd']:.4f}
    
    ### Razonamiento Clínico
    **Riesgo:** {reasoning.risk_level.value}
    **Puntuación:** {reasoning.risk_score:.1f}/100
    
    **Hallazgos:**
    {format_findings(reasoning.findings)}
    
    **Hipótesis Clínica:**
    {format_hypotheses(reasoning.hypotheses)}
    
    **Diagnósticos Diferenciales:**
    {format_differentials(reasoning.differential_diagnoses)}
    
    **Recomendaciones:**
    {format_recommendations(reasoning.recommendations)}
    """
    
    return report
```

#### 3. En dashboard

```python
# En app/dashboard.py o equivalente
import streamlit as st
from app.reasoning_engine_streamlit import BiomedicalReasoningStreamlit

def display_analysis_results(analysis_results):
    reasoning = analysis_results['reasoning']
    
    app = BiomedicalReasoningStreamlit()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Riesgo", reasoning.risk_level.value)
    with col2:
        st.metric("Score", f"{reasoning.risk_score:.1f}")
    with col3:
        st.metric("Estado Autonómico", reasoning.autonomic_state.value)
    
    app.display_findings(reasoning)
    app.display_hypotheses(reasoning)
    app.display_differential_diagnoses(reasoning)
```

---

## Ejemplos Prácticos

### Ejemplo 1: Estrés Agudo

```python
from src.reasoning_engine import BiomedicalReasoningEngine, HRVMetrics

metrics = HRVMetrics(
    bpm=112,       # Taquicardia
    sdnn=0.06,     # Variabilidad baja
    rmssd=0.02,    # Muy baja
    pnn50=6,       # Bajo
    lf=3.5,        # Elevado
    hf=0.8,        # Bajo
    lf_hf=4.375,   # Muy elevado
    entropy=2.1    # Baja complejidad
)

engine = BiomedicalReasoningEngine()
output = engine.reason(metrics)

# Output esperado:
# - Riesgo: MODERADO/ALTO
# - Hipótesis: Estrés agudo (alta probabilidad)
# - Autonómico: SIMPÁTICO
# - Recomendaciones: Respiración, meditación, monitoreo
```

### Ejemplo 2: Buena Salud

```python
metrics = HRVMetrics(
    bpm=68,        # Normal
    sdnn=0.16,     # Excelente
    rmssd=0.07,    # Alto
    pnn50=32,      # Alto
    lf=1.2,        # Normal
    hf=2.8,        # Alto
    lf_hf=0.43,    # Bajo (buen balance)
    entropy=4.1    # Alta complejidad
)

output = engine.reason(metrics)

# Output esperado:
# - Riesgo: BAJO
# - Hipótesis: Buena función cardiovascular (muy alto)
# - Autonómico: PARASIMPÁTICO/EQUILIBRIO
# - Recomendaciones: Mantener estilo de vida
```

### Ejemplo 3: Riesgo Alto

```python
metrics = HRVMetrics(
    bpm=125,       # Taquicardia
    sdnn=0.04,     # Muy baja
    rmssd=0.008,   # Crítica
    pnn50=2,       # Crítica
    lf=5.0,        # Muy elevado
    hf=0.2,        # Muy bajo
    lf_hf=25.0,    # Extremo
    entropy=0.9,   # Muy baja
    ai_score=0.85  # IA detecta anomalía
)

output = engine.reason(metrics)

# Output esperado:
# - Riesgo: CRÍTICO
# - Hipótesis: Disfunción autonómica (alta)
# - Autonómico: DISFUNCIÓN
# - Warnings: Múltiples
# - Recomendaciones: Evaluación clínica inmediata
```

### Ejemplo 4: Análisis Post-Ejercicio

```python
metrics = HRVMetrics(
    bpm=58,        # Bradicardia (recuperación)
    sdnn=0.14,     # Buena variabilidad
    rmssd=0.08,    # Excelente
    pnn50=28,      # Alto
    lf=1.0,        # Normal
    hf=3.0,        # Elevado
    lf_hf=0.33,    # Bajo (parasimpático)
    entropy=3.9    # Compleja
)

output = engine.reason(metrics)

# Output esperado:
# - Riesgo: BAJO
# - Hipótesis: Recuperación post-esfuerzo
# - Autonómico: PARASIMPÁTICO
# - Notas: Patrón esperado y saludable
```

---

## API Reference

### HRVMetrics

```python
@dataclass
class HRVMetrics:
    bpm: float
    sdnn: float
    rmssd: float
    pnn50: float
    lf: float
    hf: float
    lf_hf: float
    entropy: float
    ai_score: Optional[float] = None
    timestamp: Optional[str] = None
    
    def validate() -> Tuple[bool, str]
    def to_dict() -> Dict[str, Any]
```

### ReasoningOutput

```python
@dataclass
class ReasoningOutput:
    findings: List[PhysiologicalFinding]
    hypotheses: List[ClinicalHypothesis]
    differential_diagnoses: List[DifferentialDiagnosis]
    risk_level: RiskLevel
    autonomic_state: AutonomicState
    risk_score: float
    main_narrative: str
    clinical_impression: str
    recommendations: List[EducationalRecommendation]
    warnings: List[str]
    
    def to_dict() -> Dict[str, Any]
    def to_json() -> str
```

### BiomedicalReasoningEngine

```python
class BiomedicalReasoningEngine:
    def reason(metrics: HRVMetrics) -> ReasoningOutput
```

### RiskLevel Enum

```python
class RiskLevel(Enum):
    BAJO = "bajo"
    MODERADO = "moderado"
    ALTO = "alto"
    CRÍTICO = "crítico"
```

### AutonomicState Enum

```python
class AutonomicState(Enum):
    SIMPÁTICO = "simpático"
    PARASIMPÁTICO = "parasimpático"
    EQUILIBRIO = "equilibrio"
    DISFUNCIÓN = "disfunción"
```

---

## Testing

### Ejecutar Tests

```bash
# Todos los tests
python -m pytest tests/test_reasoning_engine.py -v

# Test específico
python -m pytest tests/test_reasoning_engine.py::TestHRVMetrics -v

# Con coverage
python -m pytest tests/test_reasoning_engine.py --cov=src.reasoning_engine
```

### Cobertura de Tests

- ✓ Validación de métricas (7 tests)
- ✓ Detectores de patrones (9 tests)
- ✓ Generador de hipótesis (2 tests)
- ✓ Estimador de riesgo (4 tests)
- ✓ Clasificador autonómico (4 tests)
- ✓ Motor principal (8 tests)
- **Total: 34 tests unitarios**

---

## Notas Importantes

⚠️ **DESCARGO DE RESPONSABILIDAD MÉDICA:**
- Este motor proporciona análisis educativo y no sustituye evaluación clínica
- NO realiza diagnósticos médicos
- Genera "patrones sugestivos de" para evaluación posterior
- Siempre requerir evaluación por profesional médico certificado

✅ **GARANTÍAS:**
- Modular y desacoplado (no modifica código existente)
- Sigue principios SOLID
- Compatible con pipeline actual
- Compatible con Streamlit
- 100% testeable
- Extensible para nuevos patrones/reglas

---

## Contacto y Soporte

Para preguntas sobre implementación, integración o extensión del motor, consultar documentación o crear issues.
