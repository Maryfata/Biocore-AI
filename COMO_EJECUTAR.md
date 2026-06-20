# CÓMO EJECUTAR BIOCORE AI — GUÍA COMPLETA

## 🚀 INICIO RÁPIDO (3 pasos)

### 1. Abre el terminal
- **Windows:** `Win + R` → escribe `cmd` → Entrar
- **Mac:** Cmd + Espacio → escribe `terminal` → Entrar
- **Linux:** Ctrl + Alt + T

### 2. Navega a la carpeta
```bash
cd "ruta/a/Biomedical-Signal-Visualizer"
```

### 3. Ejecuta la app
```bash
streamlit run app/main.py
```

La app se abrirá automáticamente en tu navegador en `http://localhost:8501`

---

## 📋 OPCIONES DE EJECUCIÓN

### Opción A: App Principal (LA MÁS COMPLETA)
```bash
streamlit run app/main.py
```
✅ Todos los hubs y módulos  
✅ Navegación integrada  
✅ Gemelo digital interactivo  
✅ Tutor IA chatbot  

**Acceso:**
- Home → Learning Hub → Academia Inteligente
- Home → Digital Twin Hub → Digital Twin
- Home → AI Hub → JARVIS Tutor

---

### Opción B: Academia Clínica Inteligente (NUEVA - MÁS INTERACTIVA)
```bash
streamlit run app/pages/12_Academia_Inteligente.py
```
✅ Misiones clínicas  
✅ Pacientes virtuales  
✅ Gemelo digital interactivo  
✅ Tutor IA integrado  

**Tab disponibles:**
1. 🎯 **Misiones** — Resuelve casos clínicos
2. 👥 **Pacientes Virtuales** — Interactúa con pacientes
3. 🧬 **Gemelo Digital** — Manipula en tiempo real
4. 📖 **Tutor IA** — Chatbot educativo
5. 📊 **Progreso** — Tus estadísticas

---

### Opción C: Tutor IA Chatbot
```bash
streamlit run app/main.py
```
Luego ve a: **AI Hub** → **🤖 JARVIS Tutor**

**Preguntas que puedes hacer:**
- "¿Qué es el ECG?"
- "Explica los intervalos del ECG"
- "¿Cuándo sospechar infarto?"
- "¿Qué es la fibrilación auricular?"
- "Diferencia entre EPOC y asma"

---

### Opción D: ECG Monitor
```bash
streamlit run app/pages/1_ECG_Monitor.py
```

---

## 🖥️ USANDO WINDOWS (FÁCIL)

### Método 1: Hacer doble clic (MÁS FÁCIL)
1. Busca el archivo `RUN_BIOCORE.bat` en la carpeta
2. Haz doble clic
3. Selecciona una opción (1-5)
4. ¡Listo!

### Método 2: Terminal
```bash
cd C:\Users\[TuNombre]\Downloads\Biomedical-Signal-Visualizer
streamlit run app/main.py
```

---

## 🎮 QUÉ HACER CUANDO ABRE LA APP

### 1. Explora el Gemelo Digital
- Click en **Digital Twin Hub** (lado izquierdo)
- Click en **Digital Twin**
- Ajusta los sliders de HR, SpO2, Respiración
- Observa cómo cambian las gráficas en tiempo real
- Aplica intervenciones (O₂, intubación, etc.)

### 2. Prueba una Misión Clínica
- Ve a **Learning Hub** → **Academia Inteligente**
- Tab **🎯 Misiones**
- Selecciona "Diagnóstico de Dolor Torácico"
- Click en "▶️ Iniciar Misión"
- Interactúa con el paciente
- Envía tu diagnóstico

### 3. Usa el Tutor IA
- Ve a **AI Hub** → **JARVIS Tutor**
- Escribe preguntas en el chat
- Genera ejercicios interactivos
- Resuelve quiz

---

## ⚙️ CONFIGURACIÓN (SI ALGO NO FUNCIONA)

### Error: "ModuleNotFoundError"
```bash
pip install --upgrade streamlit numpy scipy pandas plotly
```

### Gestos, voz y JARVIS AI Copilot
Si quieres usar control por voz o gestos, instala:
```bash
pip install mediapipe opencv-python Pillow SpeechRecognition
```

Para el asistente JARVIS usa Anthropic y configura la variable de entorno:
```bash
pip install anthropic
```

En Windows PowerShell:
```powershell
$env:ANTHROPIC_API_KEY = "sk-your-key-here"
```

En Windows CMD:
```cmd
set ANTHROPIC_API_KEY=sk-your-key-here
```

Si prefieres usar secretos de Streamlit, agrega esta línea a `secrets.toml`:
```toml
anthropic_api_key = "sk-your-key-here"
```

### Error: "Port 8501 already in use"
```bash
streamlit run app/main.py --server.port 8502
```

### Limpiar caché
```bash
streamlit cache clear
```

### Reinstalar todas las dependencias
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 🎯 CARACTERÍSTICAS PRINCIPALES

### ✅ Gemelo Digital Funcional
- Manipula HR, SpO2, Respiración
- Simula intervenciones médicas
- Ve respuestas fisiológicas en vivo
- Indicadores: Global State, Autonomic Balance, Stress Index

### ✅ Misiones Clínicas Interactivas
- Casos reales de urgencias
- Pacientes con diferentes condiciones
- Resuelve diagnosticando y recomendando
- Gana XP y desbloquea habilidades

### ✅ Tutor IA Chatbot
- Responde preguntas sobre ECG, EEG, SpO2, HRV
- Genera ejercicios personalizados
- Explica conceptos en lenguaje clínico
- Resuelve dudas en tiempo real

### ✅ Análisis Multisensor
- ECG, Respiración, SpO2 simultaneamente
- Fusión de datos
- Indicadores fisiológicos propios

---

## 📱 NAVEGACIÓN RÁPIDA

**Sidebar izquierdo:**
1. Selecciona un HUB (Learning, Clinical, Research, etc.)
2. Selecciona un MÓDULO dentro del hub
3. El contenido aparece automáticamente

**Volver al Home:**
- Click en el logo o "Home" en el sidebar

**Cambiar de página:**
- Usa los selectores del sidebar
- O haz click directo en los botones

---

## 🔒 PRIMERA VEZ QUE EJECUTAS

1. Streamlit te pedirá correo (opcional, presiona Enter)
2. Se abrirá tu navegador automáticamente
3. Si no se abre, copia esta URL en el navegador:
   ```
   http://localhost:8501
   ```

---

## 💡 TIPS

### Guardar estado del gemelo digital
- Usa el botón "💾 Guardar estado"
- Puedes cargar luego desde session state

### Generar ejercicios
- Usa el botón "📝 Generar ejercicio"
- Resuelve y verifica al instante

### Exportar informes
- En la tab de investigación
- Click en "Exportar segmento"
- Se guardará como CSV

### Ver logs de error
- Mira la consola de terminal
- Te dirá qué falla específicamente

---

## 🆘 PROBLEMAS COMUNES

| Problema | Solución |
|----------|----------|
| Página en blanco | Recarga (F5), borra caché |
| Gráficos no se ven | Instala Plotly: `pip install plotly` |
| Lento | Reduce duración de señales (5-10 seg) |
| Se congela | Recarga la página |
| Tutor IA no responde | Ejecuta desde `app/main.py`, no desde página |

---

## 📞 SOPORTE

Si encuentras problemas:
1. Verifica los **QUICKSTART.md** y **PROJECT_TITAN.md**
2. Mira la consola (abajo del terminal)
3. Limpia caché: `streamlit cache clear`
4. Reinstala: `pip install -r requirements.txt`

---

## 🎉 AHORA ESTÁS LISTO

Ejecuta:
```bash
streamlit run app/main.py
```

**¡Y disfruta explorando BIOCORE AI!**
