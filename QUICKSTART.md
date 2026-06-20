# BIOCORE AI — GUÍA RÁPIDA DE INICIO

## 1️⃣ Requisitos

### Python 3.9+
```bash
python --version
```

### Dependencias principales
- streamlit
- numpy
- scipy
- pandas
- plotly

### Instalación rápida
```bash
# Clonar o navegar al proyecto
cd Biomedical-Signal-Visualizer

# Crear entorno virtual (opcional pero recomendado)
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 2️⃣ EJECUTAR LA APLICACIÓN

### Opción A: Aplicación principal multipágina (RECOMENDADO)
```bash
streamlit run app/main.py
```
- Abre automáticamente en `http://localhost:8501`
- Acceso a todos los hubs y páginas
- Navegación integrada

### Opción B: Página específica de ECG
```bash
streamlit run app/pages/1_ECG_Monitor.py
```

### Opción C: Academia Clínica Inteligente (nueva)
```bash
streamlit run app/pages/12_Academia_Inteligente.py
```

### Opción D: Todas las páginas como multipage
```bash
streamlit run app/pages/0_🏠_Home.py
```

---

## 3️⃣ NAVEGACIÓN EN LA APP

### 🏠 Home
Página principal con descripción de hubs y acceso rápido a módulos.

### 📚 Learning Hub
- **🎓 Education:** Tutoriales interactivos
- **🏫 Academia Inteligente:** Misiones, pacientes virtuales, gemelos digitales
- **📚 Guides:** Documentación y referencias

### 🏥 Clinical Hub
- **📊 ECG Monitor:** Análisis de ECG en tiempo real
- **🔗 Multisensor:** Fusión de múltiples sensores
- **📋 ECG 12-Derivaciones:** Vista clínica completa
- **💨 Respiratory Lab:** Análisis respiratorio
- **🧠 EEG Neuro Lab:** Monitoreo neurológico
- **🦾 EMG Muscle Lab:** Análisis muscular

### 🤖 Research Hub
- **🤖 AI Analysis:** Interpretabilidad de modelos
- **👥 Patients:** Gestión de casos clínicos

### 🧬 Digital Twin Hub
- **🧬 Digital Twin:** Gemelo digital interactivo

---

## 4️⃣ CARACTERÍSTICAS PRINCIPALES

### 🧬 Gemelo Digital Interactivo
1. Selecciona un paciente virtual
2. Observa ECG, respiración y SpO₂ en vivo
3. Manipula parámetros:
   - Frecuencia cardíaca
   - SpO₂
   - Respiración
   - Intervenciones (O₂, intubación, etc.)
4. Ve cómo responde el organismo completo

### 🎯 Misiones Clínicas
1. Elige una misión (principiante, intermedio, avanzado)
2. Recibe un paciente virtual
3. Interpreta sus signos vitales y señales
4. Toma decisiones clínicas
5. Gana XP y desbloquea habilidades

### 🤖 Chatbot IA del Tutor
- Pregunta sobre ECG, EEG, SpO₂, HRV
- Obtén explicaciones personalizadas
- Resuelve ejercicios interactivos
- Recibe explicaciones fisiológicas

### 📊 Análisis Multisensorial
- Fusión de ECG, EEG, EMG, PPG, SpO2, respiración
- Indicadores propios: Global State, Autonomic Balance, etc.
- Visualización de interacciones fisiológicas

---

## 5️⃣ SOLUCIÓN DE PROBLEMAS

### ❌ Error: "ModuleNotFoundError"
```bash
# Reinstala las dependencias
pip install --upgrade -r requirements.txt
```

### ❌ Error: "No module named 'streamlit'"
```bash
pip install streamlit
```

### ❌ Puerto 8501 ya en uso
```bash
# Usa un puerto diferente
streamlit run app/main.py --server.port 8502
```

### ❌ La app no muestra contenido
1. Verifica que estés ejecutando desde `app/main.py` o `app/pages/0_🏠_Home.py`
2. Recarga la página (F5)
3. Borra caché: `streamlit cache clear`

### ❌ Los gráficos no aparecen
- Necesita Plotly: `pip install plotly`
- Fallback a Matplotlib si Plotly no funciona

---

## 6️⃣ ESTRUCTURA DEL PROYECTO

```
Biomedical-Signal-Visualizer/
├── app/
│   ├── main.py                    # Punto de entrada principal
│   ├── pages/                      # Páginas multipágina
│   │   ├── 0_🏠_Home.py
│   │   ├── 1_ECG_Monitor.py
│   │   ├── 12_Academia_Inteligente.py  # NEW - Academia mejorada
│   │   └── ...
│   ├── engines/                    # Motores centrales (PROJECT TITAN)
│   │   ├── physiology_core.py      # Fusión fisiológica
│   │   └── digital_twin.py         # Gemelo digital
│   ├── biomedical_tutor.py         # Chatbot IA (NEW)
│   └── utils.py                    # Utilidades
├── PROJECT_TITAN.md                # Diseño arquitectónico global
├── QUICKSTART.md                   # Este archivo
└── requirements.txt
```

---

## 7️⃣ PRIMEROS PASOS

### Paso 1: Ejecuta la app
```bash
streamlit run app/main.py
```

### Paso 2: Ve a Academia Inteligente
- Navegación → Learning Hub → Academia Inteligente
- O ejecuta directamente: `streamlit run app/pages/12_Academia_Inteligente.py`

### Paso 3: Prueba una misión
1. Tab "🎯 Misiones"
2. Selecciona "Diagnóstico de Dolor Torácico"
3. Haz clic "▶️ Iniciar Misión"
4. Interactúa con el gemelo digital
5. Envía tu diagnóstico

### Paso 4: Usa el Tutor IA
- Tab "📖 Tutor IA Biomédico"
- Pregunta: "¿Qué es el ECG?"
- Interactúa con ejercicios

### Paso 5: Explora el Gemelo Digital
- Navegación → Digital Twin Hub → Digital Twin
- Manipula parámetros y ve cambios en tiempo real

---

## 8️⃣ CONFIGURACIÓN AVANZADA

### Ejecutar en servidor remoto
```bash
streamlit run app/main.py --server.address 0.0.0.0 --server.port 8501
```

### Deshabilitar telemetría
```bash
streamlit run app/main.py --logger.level=error --client.showErrorDetails=false
```

### Usar archivo de configuración
Crea `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#0BC4DD"
backgroundColor = "#051019"
secondaryBackgroundColor = "#0f192a"
textColor = "#eef7ff"

[server]
port = 8501
headless = true
```

---

## 9️⃣ CARACTERÍSTICAS EN CONSTRUCCIÓN

- ✅ Gemelo digital interactivo
- ✅ Misiones clínicas
- ✅ Tutor IA chatbot
- ✅ Análisis multisensorial
- 🚧 Integración con hardware real (ESP32, wearables)
- 🚧 Modelos de IA más avanzados
- 🚧 Federación de learning para investigación
- 🚧 Telemedicina integrada

---

## 🔟 PRÓXIMOS PASOS

1. **Explora Academia Inteligente** → Completa 3 misiones
2. **Aprende con el Tutor** → Resuelve 5 ejercicios
3. **Manipula Gemelos Digitales** → Simula 3 intervenciones
4. **Configura tus sensores** → Integra hardware (opcional)

---

## ❓ SOPORTE

Para reportar bugs o sugerencias:
```bash
# Abre issues en GitHub o contacta al equipo
github.com/[tu-repo]/issues
```

---

**¡Bienvenido a BIOCORE AI!**
