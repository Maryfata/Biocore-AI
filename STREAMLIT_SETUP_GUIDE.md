# GUÍA DE INSTALACIÓN Y EJECUCIÓN - INTERFACE STREAMLIT
## BIOCORE AI OS v3.0 - Plataforma Médica Integrada

---

## 📋 CONTENIDO

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación de Dependencias](#instalación-de-dependencias)
3. [Estructura de Carpetas](#estructura-de-carpetas)
4. [Ejecutar la Aplicación](#ejecutar-la-aplicación)
5. [Instrucciones de Uso](#instrucciones-de-uso)
6. [Funcionalidades Implementadas](#funcionalidades-implementadas)
7. [Solución de Problemas](#solución-de-problemas)
8. [Notas de Desarrollo](#notas-de-desarrollo)

---

## 🖥️ Requisitos del Sistema

### Mínimos
- **Python**: 3.8 o superior
- **RAM**: 4 GB
- **Espacio en disco**: 500 MB
- **Navegador**: Chrome, Firefox, Safari, Edge (versión reciente)

### Recomendados
- **Python**: 3.10+
- **RAM**: 8 GB
- **GPU**: Opcional (para cálculos más rápidos)

---

## 📦 Instalación de Dependencias

### Paso 1: Crear Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

### Paso 2: Instalar Dependencias

```bash
# Instalar desde requirements.txt
pip install streamlit plotly numpy scipy pandas

# O instalar manualmente:
pip install streamlit==1.28.0
pip install plotly==5.17.0
pip install numpy==1.24.3
pip install scipy==1.11.2
pip install pandas==2.0.3
```

### Paso 3: Verificar Instalación

```bash
# Verificar que Streamlit está instalado
streamlit --version

# Debe mostrar: Streamlit, version X.X.X
```

---

## 📂 Estructura de Carpetas

```
Biomedical-Signal-Visualizer/
│
├── app/
│   ├── __init__.py
│   ├── main.py                    (Archivo principal anterior)
│   ├── pages/
│   │   └── specialties.py         (NUEVO: Interface Unificada)
│   │
│   ├── components/                (NUEVA CARPETA)
│   │   ├── __init__.py
│   │   ├── cardiology_ui.py       (Componentes Cardiología)
│   │   ├── neurology_ui.py        (Componentes Neurología)
│   │   ├── musculoskeletal_ui.py  (Componentes Musculoesquelético)
│   │   ├── digital_twins_ui.py    (Simulaciones Digital Twin)
│   │   └── alerts_and_reports_ui.py (Alertas y Reportes)
│   │
│   ├── utils/                     (NUEVA CARPETA)
│   │   ├── __init__.py
│   │   └── data_generator.py      (Generador de datos de prueba)
│   │
│   └── (otros archivos existentes)
│
├── core/
│   ├── specialties/
│   │   ├── cardiology.py          (Cardiology module)
│   │   ├── neurology.py           (Neurology module)
│   │   └── musculoskeletal.py     (Musculoskeletal module)
│   │
│   ├── digital_twins/
│   │   └── digital_twins.py       (Digital Twins)
│   │
│   ├── ai/
│   │   └── automatic/
│   │       └── orchestrator.py    (IA Automática)
│   │
│   └── (otros módulos)
│
├── docs/
│   ├── especialidades/
│   │   ├── CARDIOLOGIA_EXPLICITO_PRINCIPIANTES.md
│   │   ├── NEUROLOGIA_EXPLICITO_PRINCIPIANTES.md
│   │   ├── PLATFORM_OVERVIEW_INTEGRATED.md
│   │   ├── QUICK_START_USER_MANUAL.md
│   │   ├── README.md
│   │   └── RESUMEN_EJECUTIVO_SESION.md
│   │
│   └── (otros documentos)
│
├── STREAMLIT_SETUP_GUIDE.md       (Este archivo)
├── requirements.txt
└── (otros archivos del proyecto)
```

---

## ▶️ Ejecutar la Aplicación

### Opción 1: Ejecutar Interface Unificada (RECOMENDADO)

```bash
# Desde la raíz del proyecto
streamlit run app/pages/specialties.py

# O con configuración personalizada
streamlit run app/pages/specialties.py --logger.level=debug
```

Esto abrirá automáticamente en tu navegador:
```
http://localhost:8501
```

### Opción 2: Ejecutar desde Terminal Específica

```bash
# Si estás en la carpeta app/
cd app
streamlit run pages/specialties.py

# Si estás en la carpeta raíz
streamlit run ./app/pages/specialties.py
```

### Opción 3: Configuración Avanzada

Crear archivo `.streamlit/config.toml`:

```toml
[browser]
gatherUsageStats = false

[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
port = 8501
headless = true
```

Luego ejecutar:
```bash
streamlit run app/pages/specialties.py
```

---

## 📖 Instrucciones de Uso

### Flujo Típico de Usuario

#### 1. **Seleccionar Especialidad (Sidebar)**
   - 🫀 Cardiología
   - 🧠 Neurología  
   - 💪 Musculoesquelético

#### 2. **Seleccionar Paciente (Sidebar)**
   - Elige de la lista de pacientes disponibles
   - Se cargarán los datos del paciente automáticamente

#### 3. **Tab: MEDICIÓN**
   - **Cardiología:**
     - Registrar ECG (Electrocardiograma)
     - Ingresar Presión Arterial
     - Medir Oximetría
     - Guardar medición
   
   - **Neurología:**
     - Registrar EEG (Electroencefalograma)
     - Seleccionar estadio de sueño
     - Evaluar calidad subjetiva
     - Guardar medición
   
   - **Musculoesquelético:**
     - Registrar EMG (Electromiografía)
     - Medir ROM (Rango de Movimiento)
     - Evaluar fuerza muscular
     - Guardar medición

#### 4. **Tab: ANÁLISIS IA**
   - Ver resultados automáticos del análisis
   - Gráficas por especialidad
   - Tabla resumen de hallazgos
   - Métricas clave

#### 5. **Tab: DIGITAL TWIN**
   - Ver simulación del órgano/sistema
   - Escenarios "¿Qué pasa si...?" interactivos
   - Comparar diferentes intervenciones
   - Proyecciones futuras

#### 6. **Tab: ALERTAS**
   - Ver alertas activas por severidad
   - Historial de 30 días
   - Clasificación por tipo

#### 7. **Tab: REPORTE**
   - Vista previa del reporte automático
   - Descargar como PDF
   - Enviar por email
   - Explicaciones SHAP (IA)

#### 8. **Tab: EDUCACIÓN**
   - Explicaciones para pacientes
   - Conceptos médicos simplificados
   - Preguntas frecuentes
   - Recomendaciones

#### 9. **Sección Inferior**
   - Historial de mediciones (tabla)
   - Gráficas de tendencia

### Ejemplo Concreto: Medir Corazón

1. **Sidebar:** Selecciona "🫀 Cardiología"
2. **Tab MEDICIÓN:**
   - Desliza "Duración ECG" a 10 segundos
   - Selecciona "Normal" en condición
   - Haz clic en "▶️ Registrar ECG"
   - Espera a que aparezca "✅ ECG registrado"
3. **Ingresa valores manuales:**
   - Presión Sistólica: 120 mmHg
   - Presión Diastólica: 80 mmHg
   - O2 Saturación: 98%
4. **Haz clic "✅ Guardar Medición Cardíaca"**
5. **Ve a Tab ANÁLISIS IA:**
   - Verás el ECG grafiado
   - Resultados de arritmia
   - Métricas vitales
   - Tabla resumen
6. **Ve a Tab DIGITAL TWIN:**
   - Simulación del corazón
   - Escenarios "¿Y si tomo medicamento?"
7. **Ve a Tab REPORTE:**
   - Reporte automático completo
   - Explicaciones IA
   - Descarga PDF

---

## ✨ Funcionalidades Implementadas

### Por Especialidad

#### 🫀 CARDIOLOGÍA

**Mediciones:**
- ECG de 10 segundos
- ECG 12 derivaciones
- Presión arterial
- Oximetría

**Análisis IA:**
- Detección de arritmias (FA, Bradicardia, Taquicardia)
- Análisis de frecuencia (FFT)
- HRV (Variabilidad del Ritmo Cardíaco)
- Clasificación de riesgo

**Gráficas:**
- Forma de onda ECG
- Análisis de frecuencia
- Métricas con gauges
- Tendencia de FC (30 días)
- Detección de arritmias (barras de confianza)
- Evaluación de riesgo

**Digital Twin:**
- Simulación de corazón
- Escenarios interactivos (medicamento, ejercicio, estrés)

**Alertas:**
- Por severidad (Crítico, Alto, Medio, Bajo)
- Historial de 30 días

**Reporte:**
- Reporte técnico automático
- Explicación SHAP de factores
- Predicciones 30 días
- Recomendaciones clínicas

---

#### 🧠 NEUROLOGÍA

**Mediciones:**
- EEG multi-canal
- Evaluación de sueño
- Dolor de cabeza subjetivo

**Análisis IA:**
- Extracción de bandas (Delta, Theta, Alpha, Beta, Gamma)
- Clasificación de estadio de sueño (AASM)
- Detección de epilepsia
- Análisis de conectividad

**Gráficas:**
- Señal EEG cruda
- Potencia por banda
- Clasificación de sueño
- Riesgo de crisis
- Mapa de calor de actividad
- Calidad de sueño (tendencia 30 días)

**Digital Twin:**
- Mapa 3D de actividad cerebral
- Escenarios interactivos (higiene del sueño, meditación)

**Alertas:**
- Riesgo de crisis epiléptica
- Problemas de sueño

**Reporte:**
- Hallazgos de sueño
- Recomendaciones de higiene del sueño
- Riesgo de patología

---

#### 💪 MUSCULOESQUELÉTICO

**Mediciones:**
- EMG bilateral
- Rango de movimiento (ROM)
- Evaluación de fuerza

**Análisis IA:**
- Análisis de fatiga (Median Frequency)
- Activación muscular
- Detección de patología (Miopatía vs Neuropatía)
- Análisis bilateral

**Gráficas:**
- EMG crudo + envolvente
- Progresión de fatiga
- Nivel de activación (gauge)
- Comparación bilateral
- Clasificación de patología
- Proyección de recuperación

**Digital Twin:**
- Simulación de contracción muscular
- Escenarios interactivos (fisioterapia, descanso)

**Reporte:**
- Evaluación de patología
- Plan de rehabilitación
- Tiempo de recuperación esperado

---

### Componentes Comunes

**Sistema de Alertas:**
- 4 niveles de severidad (🟢🟡🔴⚫)
- Historial interactivo
- Recomendaciones por alerta

**Generación de Reportes:**
- Reporte automático completo
- Explicabilidad SHAP
- Descarga PDF
- Envío por email
- Explicaciones para paciente

**Centro Educativo:**
- Explicaciones por especialidad
- 3 niveles de profundidad
- Conceptos médicos simplificados
- Preguntas frecuentes

---

## 🛠️ Solución de Problemas

### Problema: "ModuleNotFoundError: No module named 'streamlit'"

**Solución:**
```bash
pip install streamlit
# O reinstalar todas las dependencias
pip install -r requirements.txt
```

### Problema: Puerto 8501 ya está en uso

**Solución:**
```bash
# Usar puerto diferente
streamlit run app/pages/specialties.py --server.port=8502
```

### Problema: La interface se ve cortada o deformada

**Solución:**
1. Abre en navegador diferente
2. Limpia caché del navegador (Ctrl+Shift+Delete)
3. Redimensiona la ventana
4. Ejecuta con `--logger.level=info` para debug

### Problema: Los gráficos no aparecen

**Solución:**
```bash
# Reinstalar plotly
pip install --upgrade plotly
```

### Problema: "Permission denied" al crear archivos

**Solución:**
```bash
# En Linux/macOS, dar permisos
chmod 755 app/pages/specialties.py
```

### Problema: La aplicación es lenta

**Soluciones:**
1. Usa menos datos (reduce histórico de mediciones)
2. Aumenta RAM disponible
3. Cierra otras aplicaciones
4. Usa Python 3.10+ (más rápido)

---

## 🔧 Notas de Desarrollo

### Agregar Nueva Especialidad

1. Crear `app/components/new_specialty_ui.py`
2. Crear clase con métodos de gráficas
3. Importar en `app/pages/specialties.py`
4. Agregar Tab nueva en la sección de tabs
5. Agregar lógica de medición en Tab MEDICIÓN

### Agregar Nueva Gráfica a Especialidad Existente

1. Agregar método a clase especialidad en `components/`
2. Llamar en Tab ANÁLISIS IA o DIGITAL TWIN
3. Usar `st.plotly_chart()` para mostrar

### Personalizar Estilos

Editar CSS en la función `st.markdown()` al inicio:

```python
st.markdown("""
    <style>
        /* Agregar estilos CSS aquí */
    </style>
""", unsafe_allow_html=True)
```

### Conectar a Base de Datos Real

Reemplazar `DataGenerator` con queries a BD:

```python
# En lugar de:
patient_data = generate_sample_patient()

# Usar:
from app.database import get_patient_data
patient_data = get_patient_data(patient_id)
```

### Agregar Autenticación

Instalar `streamlit-authenticator`:

```bash
pip install streamlit-authenticator
```

Luego agregar al inicio de `specialties.py`:

```python
import streamlit_authenticator as stauth

# Código de autenticación aquí
```

---

## 📚 Recursos Adicionales

- **Documentación Streamlit:** https://docs.streamlit.io
- **Documentación Plotly:** https://plotly.com/python/
- **NumPy/SciPy:** https://numpy.org/, https://scipy.org/
- **Documentación BIOCORE:** `docs/especialidades/`

---

## 📞 Soporte

**Para problemas técnicos:**
- Email: biocore-support@hospital.com
- Teléfono: +1-555-BIOCORE-1

**Para reportar bugs:**
- Incluir:
  - Versión de Python
  - Versión de Streamlit
  - Sistema operativo
  - Pasos para reproducir
  - Screenshot del error

---

## 📝 Changelog

### v3.0.0 (2026-06-15)
- ✅ Interface unificada Streamlit
- ✅ 3 especialidades integradas
- ✅ Digital Twins con simulación
- ✅ Sistema de alertas
- ✅ Generación automática de reportes
- ✅ Centro educativo
- ✅ 6 tabs principales

---

**¡Listo! Tu plataforma médica integrada está funcionando.** 🎉

Para más información, consulta `docs/especialidades/QUICK_START_USER_MANUAL.md`
