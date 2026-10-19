# BIOCORE AI

**Un laboratorio digital de fisiología humana para enseñar medicina con IA, construido sobre una regla: nunca finge lo que no sabe.**

BIOCORE AI es una plataforma educativa de fisiología humana para estudiantes de medicina y ciencias de la salud. En lugar de enseñar con texto estático, enseña con un **gemelo digital reactivo**: un organismo virtual cuyo estado fisiológico se calcula con modelos reales, se altera con escenarios clínicos, y se explica con fundamento.

La tesis: aprender medicina no es leer una buena explicación, es intentar, equivocarse y ser corregido con fundamento. El estudiante no memoriza que la sepsis baja la presión — ve la presión desplomarse por el mecanismo de la vasoplejía, e intenta diagnosticarlo mientras sucede.

---

## Qué lo hace distinto

La mayoría de las plataformas educativas médicas *suenan* clínicas sin serlo: muestran números con apariencia de métrica que nadie calculó, etiquetas que parecen diagnósticos sin un algoritmo detrás. Para una herramienta que forma médicos, un dato falso que suena convincente es lo más peligroso que puede haber.

BIOCORE se construyó sobre la regla opuesta, que gobierna toda su arquitectura:

> **Cada dato declara su procedencia. Cuando el sistema no puede saber algo, lo dice — nunca rellena el hueco con algo plausible.**

Cada valor en la plataforma sabe de dónde viene y lo declara: **medido**, **simulado**, **referencia clínica citada**, o **calculado por modelo**. Los biomarcadores llevan la cita del estándar del que provienen. Cuando falta señal para un cálculo, el sistema devuelve "no disponible" con el motivo — nunca un número de relleno. Y cada módulo declara su nivel de validación: un lab validado contra un dataset canónico se presenta con más autoridad que un índice heurístico de ingeniería, y la interfaz lo hace visible.

Esa honestidad de procedencia no es un detalle estético. Es la diferencia entre enseñar medicina real y enseñar algo que suena a medicina — y es el diferenciador de confianza frente a plataformas que no la tienen.

---

## Arquitectura

**UPS (Unified Physiological State) — el estado fisiológico unificado.** La fuente única de verdad del paciente. Cada dato lleva su procedencia. Los dominios modelados incluyen cardiovascular, respiratorio, neurológico y muscular, con biomarcadores que los cruzan.

**Motor hemodinámico validado.** Calcula presión arterial y dinámica cardiovascular por fisiología real, basado en un modelo publicado (svZeroDSolver), con parámetros validados por un experto humano contra literatura. La sepsis colapsa a shock por mecanismo, no por ajuste — la prueba de honestidad del modelo.

**Los tres hubs:**
- **Digital Twin OS** — el organismo entero: órganos que reaccionan al UPS, acoplamientos entre sistemas, casos clínicos, línea de tiempo fisiológica.
- **Clinical Hub** — los laboratorios de señal: ECG, EEG, EMG, Respiratorio, HRV, Biomarcadores, y más — y las **🧮 Calculadoras Clínicas**.
- **Learning Hub** — casos clínicos ciegos y evaluación con feedback fundamentado.

**🧮 Calculadoras Clínicas.** Fórmulas y escalas publicadas, cada una con su cita y su lectura contra el corte que fija la referencia: QTc (Bazett, Fridericia, Framingham, Hodges), FC desde el papel del ECG, eje eléctrico con dial hexaxial, PAM / presión de pulso / índice de choque, gasto e índice cardiaco, IMC y superficie corporal (Mosteller, Du Bois), PAO₂ y gradiente A–a **corregidos por altitud** (Ciudad de México, Guadalajara, Toluca…), PaO₂/FiO₂ con los rangos de Berlín, NEWS2, qSOFA y Glasgow. Pueden importar la FC, FR y SpO₂ del gemelo digital (etiquetadas como simulación) y exportan un informe PDF/HTML.

**Funciona sin clave de IA.** Los quizzes y los casos clínicos ciegos se califican con la respuesta del banco/simulador (código, no modelo); la clave de Anthropic solo activa el feedback narrado.

**Procesamiento de señal real.** Detección de complejos QRS y bloqueos de rama validada contra el MIT-BIH Arrhythmia Database; análisis espectral de EEG con parametrización del componente aperiódico (FOOOF); métricas de variabilidad cardíaca bajo estándares de la Task Force ESC/NASPE, con gráfico de Poincaré (SD1/SD2) y carga de series RR reales desde archivo (Polar, Kubios, CSV propio); electromiografía con activación fisiológica real.

---

## Estado del proyecto

BIOCORE está en desarrollo activo. La base honesta está construida y verificada: el motor hemodinámico validado, los dominios del UPS con procedencia por descriptor, el procesamiento de señal real en múltiples laboratorios, y una suite de pruebas extensa que verifica tanto el cálculo como la ausencia de fachadas.

El desarrollo sigue una disciplina de honestidad estricta: cada capacidad se valida antes de exhibirse, cada biomarcador de vanguardia se prueba contra ground truth antes de declararse, y las ideas que no alcanzan el estándar se archivan con evidencia en lugar de construirse a medias.

---

## Instalación

Requiere Python 3.10+.

**Windows:** doble clic en `RUN_BIOCORE.bat` (o `.\run_local.ps1` en PowerShell). La primera vez crea un entorno virtual `.venv` e instala las dependencias (unos minutos); las siguientes veces arranca directo y solo reinstala si cambió `requirements.txt`. El navegador se abre solo en <http://localhost:8501> cuando la app está lista; para cerrarla, cierra la ventana negra.

**Manual (cualquier sistema):**

```bash
git clone <url-del-repositorio>
cd biocore
python -m venv .venv
# Windows: .venv\Scripts\activate   ·   macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run_biocore.py          # o: streamlit run app/main.py
```

`run_biocore.py` es el arranque recomendado en Windows: usa el event loop de selectores, que evita que el servidor deje de escuchar si una conexión se corta a medias. La app escucha solo en esta computadora (`127.0.0.1`); para abrirla desde otro dispositivo de tu red: `python run_biocore.py --server.address 0.0.0.0`.

La aplicación se abre en el navegador (<http://localhost:8501>). Los datos de señal se generan por escenario o se cargan desde archivos; ninguna clave de API es necesaria para el uso base.

**Narrador clínico IA (opcional):** copia `.env.example` a `.env` y escribe tu `ANTHROPIC_API_KEY`. La app lee `.env` al arrancar (una variable ya definida en el entorno tiene prioridad). Sin clave, los paneles del narrador lo declaran como "no configurado" en vez de simular texto.

**Desarrollo:** `pip install -r requirements-dev.txt` (pytest, linters, notebooks) y `pytest tests/ -q`.

---

## Licencia

Este proyecto se distribuye bajo una licencia de fuente disponible, no comercial. El código es visible para revisión, estudio y evaluación, pero su uso comercial requiere acuerdo con el titular. Ver [`LICENSE`](LICENSE) para los términos completos.

© 2026 Luis Nazariego Santome.

---

*BIOCORE AI — fisiología humana para enseñar medicina, sobre la regla de que nunca finge lo que no sabe.*
