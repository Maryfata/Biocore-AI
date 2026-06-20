# PROJECT TITAN

## BIOCORE AI GLOBAL REBUILD PROMPT

### Propósito
Redefinir BIOCORE AI como la plataforma más avanzada de Inteligencia Biomédica del mundo, no como una colección de laboratorios independientes. El objetivo es construir una verdadera `Physiological Intelligence Platform` centrada en un `Multisystem Physiological Digital Twin`.

---

## 1. Auditoría rápida

### Estado actual
- La aplicación está organizada como páginas Streamlit independientes (`app/pages/*.py`).
- Existe una mezcla de módulos de análisis clásico de señales, visualización y utilidades.
- La navegación actual está fragmentada en hubs y vistas, pero la ejecución de páginas depende de `if __name__ == '__main__'` en varios archivos.
- Hay referencias tempranas a gemelos digitales, motores de descubrimiento y métricas fisiológicas, pero no a una capa de integración centralizada.

### Limitaciones identificadas
- `app/pages` usa un patrón de carga que no funciona bien en multipage Streamlit: muchas páginas no se renderizan al importarse.
- La arquitectura actual trata señales por dominio aislado (ECG, EEG, EMG, respiración) en lugar de una fusión fisiológica multisistema.
- No hay un `Physiology Core Engine` central ni un `Digital Twin Engine` claramente definido.
- La plataforma no tiene un roadmap técnico estructurado en fases de implementación para el sistema global.
- El sistema educativo sigue siendo en gran parte presentacional y no es un motor de misiones, residencias o tutores adaptativos.

---

## 2. Rediseño arquitectónico propuesto

### 2.1 Principios de diseño
- Centralizar todo en un `Physiological Digital Twin`.
- Tratar la fisiología como un organismo integrado, no como señales separadas.
- Priorizar educación active learning, investigación reproducible, simulación dinámica y apoyo clínico.
- Construir sobre motores modulares que puedan expandirse a un ecosistema global.

### 2.2 Motores centrales
- `Physiology Core Engine`
  - Fusiona ECG, EEG, EMG, PPG, SpO2, respiración, BP, temperatura y movimiento.
  - Genera indicadores propios como `Global Physiological State`, `Autonomic Balance`, `Recovery Capacity`.
- `Signal Intelligence Engine`
  - Normaliza datos, detecta artefactos y produce características multisensor.
- `Clinical Reasoning Engine`
  - Realiza diagnósticos diferenciales, riesgos y recomendaciones.
- `Education Engine`
  - Orquesta misiones, rutas de aprendizaje, tutores adaptativos y mapas de competencia.
- `Digital Twin Engine`
  - Mantiene el modelo vivo, predice dinámicas y simula intervenciones.
- `Simulation Engine`
  - Permite manipular variables y ver respuestas fisiológicas en tiempo real.
- `Research Engine`
  - Genera datasets reproducibles, experimentos y publicaciones.
- `Biomedical Foundation Models`
  - Soporta razonamiento, simulación, explicación y generación de contenido científico.

### 2.3 Arquitectura de alto nivel

- Frontend Streamlit
  - Hub de Learning Paths
  - Hub de Virtual Patients
  - Hub de Clinical Missions
  - Hub de Biomedical Simulator
  - Hub de AI Tutor
  - Hub de Research Academy
  - Hub de Skill Tree
  - Hub de Residency Mode
- Backend de motores
  - `app/engines/physiology_core.py`
  - `app/engines/digital_twin.py`
  - Módulos de integración futura en `src/` para modelos, telemedicina y federated learning

---

## 3. Roadmap de implementación

### Fase 0: Estabilización
- Corregir la ejecución de páginas multipágina de Streamlit.
- Normalizar la navegación y el renderizado de contenidos.
- Crear el esqueleto del `Physiology Core Engine` y `Digital Twin Engine`.

### Fase 1: Fundaciones multisistema
- Construir un pipeline de ingestión para ECG, EEG, EMG, respiración, SpO2, temperatura y BP.
- Desarrollar un `Signal Intelligence Engine` de preprocesamiento y calidad de señal.
- Exponer métricas de estado fisiológico central.

### Fase 2: Gemelo Digital y simulación
- Implementar el `Digital Twin Engine` que actualiza estado y predice riesgos.
- Crear la vista de `Digital Twin Education Mode` y `Digital Twin Simulation Mode`.
- Integrar una capa de visualización interactiva conectada al gemelo.

### Fase 3: Educación y tutoría adaptativa
- Transformar la Academia en misiones, casos clínicos y residencias.
- Capturar fortalezas/debilidades y adaptar contenido.
- Incluir un tutor IA permanente que explique, genere ejercicios y planifique rutas.

### Fase 4: Investigación y plataforma global
- Añadir `Dataset Builder`, `Experiment Builder`, `Publication Generator`.
- Preparar conectividad de telemedicina, rural health y wearables.
- Definir interoperabilidad con BFM, Knowledge Graphs y RL/edge AI.

---

## 4. Prioridades de mayor impacto

1. Hacer que todas las páginas se rendericen correctamente en Streamlit.
2. Establecer un núcleo fisiológico centralizado (`Physiology Core Engine`).
3. Crear el `Digital Twin Engine` que actúe como núcleo del ecosistema.
4. Reposicionar la Academia como misiones, residencias y gemelo digital educativo.
5. Añadir integración multisensorial real con interoperabilidad.

---

## 5. Bases ya construidas en esta entrega
- Se corrigió la ejecución de todas las páginas `app/pages/*.py` para multipage Streamlit.
- Se añadió un esqueleto modular en `app/engines/` que soporta:
  - `PhysiologyCoreEngine`
  - `DigitalTwinEngine`
- Se creó `PROJECT_TITAN.md` como documento de rediseño y roadmap.

---

## 6. Siguiente paso inmediato
- Conectar el `Digital Twin Engine` a una página de `Digital Twin Hub` real.
- Extender `Physiology Core Engine` con ingestión de señales reales y métricas de fusión.
- Redefinir los hubs de la plataforma hacia el modelo de `Learning Paths`, `Virtual Patients`, `Clinical Missions`, `BIomedical Simulator`, `AI Tutor`, `Research Academy`, `Skill Tree` y `Residency Mode`.
