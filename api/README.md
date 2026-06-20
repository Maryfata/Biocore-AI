# BIOCORE AI API

Este directorio contiene el backend FastAPI para BIOCORE AI.

## Setup

1. Crear entorno virtual e instalar dependencias:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r ..\requirements.txt
   pip install fastapi uvicorn sqlalchemy pydantic-settings cryptography fpdf
   ```

2. Ejecutar la API:
   ```powershell
   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Abrir documentación automática en:
   ```
   http://127.0.0.1:8000/docs
   ```

## Endpoints

- `GET /api/health`
- `POST /api/patients`
- `GET /api/patients/{patient_id}`
- `POST /api/signals/upload/{patient_id}`
- `GET /api/signals/{signal_id}`

## Notes

- El backend usa SQLite por defecto para arrancar rápido.
- Los datos de señal se encriptan en la base de datos.
- La inferencia asíncrona se deja como placeholder para integrar modelos ML.
