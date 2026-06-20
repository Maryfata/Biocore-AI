# BIOCORE AI v2.0 - FASE 1: Starter Code
# FastAPI Backend Foundation with Security & Database

---

## api/config.py
```python
"""Configuration for BIOCORE AI v2.0"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://biocore:secure_password@localhost:5432/biocore_ai"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Encryption
    ENCRYPTION_KEY: str = os.getenv(
        "ENCRYPTION_KEY",
        "dev-key-32-bytes-here-change-prod"
    )
    
    # Features
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HIPAA_MODE: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## db/models.py
```python
"""SQLAlchemy ORM Models for BIOCORE AI"""
from sqlalchemy import Column, String, DateTime, Float, LargeBinary, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    medical_id = Column(String(255), unique=True, index=True)  # Encrypted
    name_encrypted = Column(LargeBinary, nullable=False)
    email_encrypted = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SignalReading(Base):
    __tablename__ = "signal_readings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), index=True)
    signal_type = Column(String(50))  # 'ecg', 'hrv', 'eeg', 'emg', 'ppg', etc
    raw_signal = Column(LargeBinary)  # Encrypted
    signal_quality = Column(Float)    # 0-1
    metadata_json = Column(JSON)      # {'device': 'ESP32', 'location': 'home', ...}
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    signal_id = Column(String(36), index=True)
    model_name = Column(String(100))
    prediction = Column(String(255))
    confidence = Column(Float)
    explanation_json = Column(JSON)   # SHAP values
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36))
    action = Column(String(255))
    patient_id = Column(String(36), nullable=True, index=True)
    resource = Column(String(255))
    ip_address = Column(String(45))
    status = Column(String(50))  # 'success', 'denied', 'error'
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
```

---

## security/encryption.py
```python
"""Encryption utilities for HIPAA compliance"""
from cryptography.fernet import Fernet
from api.config import settings
import hashlib

class MedicalEncryption:
    def __init__(self):
        # Use settings key, ensure 32 bytes
        key = settings.ENCRYPTION_KEY[:32].ljust(32)
        key = hashlib.sha256(key.encode()).digest()
        # Fernet requires base64-encoded key
        import base64
        key_b64 = base64.urlsafe_b64encode(key)
        self.cipher = Fernet(key_b64)
    
    def encrypt(self, plaintext: str) -> bytes:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(plaintext.encode())
    
    def decrypt(self, ciphertext: bytes) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(ciphertext).decode()

encryption = MedicalEncryption()
```

---

## security/audit_log.py
```python
"""Audit logging for HIPAA compliance"""
from sqlalchemy.orm import Session
from db.models import AuditLog
from api.config import settings
import logging

logger = logging.getLogger(__name__)

class AuditLogger:
    @staticmethod
    async def log_access(
        db: Session,
        user_id: str,
        action: str,
        patient_id: str = None,
        resource: str = None,
        ip_address: str = None,
        status: str = "success"
    ):
        """Log all access to patient data (HIPAA requirement)"""
        audit = AuditLog(
            user_id=user_id,
            action=action,
            patient_id=patient_id,
            resource=resource,
            ip_address=ip_address,
            status=status
        )
        db.add(audit)
        db.commit()
        
        logger.info(
            f"AUDIT: {user_id} {action} {patient_id} {status}",
            extra={'ip': ip_address}
        )

audit_logger = AuditLogger()
```

---

## api/models.py
```python
"""Pydantic models for API validation"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import uuid

class PatientCreate(BaseModel):
    medical_id: str = Field(..., min_length=5)
    name: str = Field(..., min_length=2)
    email: str = Field(..., regex="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$")

class SignalReadingBase(BaseModel):
    signal_type: str  # 'ecg', 'hrv', 'eeg', etc
    raw_signal: List[float]
    metadata: Optional[Dict] = {}

class SignalReadingCreate(SignalReadingBase):
    pass

class SignalReading(SignalReadingBase):
    id: str
    patient_id: str
    signal_quality: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    explanation: Dict = {}
    model_name: str

class HealthCheck(BaseModel):
    status: str
    version: str = "2.0.0-alpha"
    database: str = "ok"
    services: Dict[str, str] = {}
```

---

## api/routes/signals.py
```python
"""Signal processing endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import SignalReading, Patient
from api.models import SignalReadingCreate, PredictionResponse
from security.audit_log import audit_logger
from biocore.signal_processing.validation import SignalValidator
import numpy as np

router = APIRouter(prefix="/api/signals", tags=["signals"])

@router.post("/upload/{patient_id}", response_model=dict)
async def upload_signal(
    patient_id: str,
    reading: SignalReadingCreate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
    current_user: str = None
):
    """Upload biomedical signal"""
    
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Validate signal quality
    validator = SignalValidator()
    signal_array = np.array(reading.raw_signal)
    validation = validator.validate(
        signal_array,
        signal_type=reading.signal_type
    )
    
    if not validation['is_valid']:
        raise HTTPException(
            status_code=422,
            detail=f"Signal invalid: {validation['reason']}"
        )
    
    # Store signal (encrypted)
    from security.encryption import encryption
    signal_reading = SignalReading(
        patient_id=patient_id,
        signal_type=reading.signal_type,
        raw_signal=encryption.encrypt(str(signal_array)),
        signal_quality=validation['quality_score'],
        metadata_json=reading.metadata
    )
    db.add(signal_reading)
    db.commit()
    
    # Audit log
    await audit_logger.log_access(
        db, current_user, "SIGNAL_UPLOAD",
        patient_id=patient_id,
        resource=f"signal/{reading.signal_type}"
    )
    
    # Async prediction
    if background_tasks:
        background_tasks.add_task(
            predict_signal_async,
            db, signal_reading.id, reading.signal_type
        )
    
    return {
        "signal_id": signal_reading.id,
        "quality_score": validation['quality_score'],
        "message": "Signal uploaded successfully"
    }

async def predict_signal_async(db: Session, signal_id: str, signal_type: str):
    """Background task for predictions"""
    # Will implement in PHASE 3
    pass

@router.get("/{signal_id}")
async def get_signal(signal_id: str, db: Session = Depends(get_db)):
    """Retrieve signal metadata"""
    reading = db.query(SignalReading).filter(SignalReading.id == signal_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    return {
        "id": reading.id,
        "signal_type": reading.signal_type,
        "quality_score": reading.signal_quality,
        "created_at": reading.created_at
    }
```

---

## api/routes/health.py
```python
"""Health check endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from api.models import HealthCheck

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    """System health check"""
    try:
        # Test DB connection
        db.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return HealthCheck(
        status="healthy",
        database=db_status,
        services={
            "signal_processing": "ok",
            "ai_inference": "ok",
            "telemedicine": "ready"
        }
    )
```

---

## api/main.py
```python
"""FastAPI Application Entry Point"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from api.config import settings
from api.routes import signals, health, patients
from db.database import engine, get_db
from db.models import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BIOCORE AI OS v2.0",
    description="Clinical-grade biomedical signal analysis platform",
    version="2.0.0-alpha"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router)
app.include_router(signals.router)
app.include_router(patients.router)

@app.on_event("startup")
async def startup_event():
    print("BIOCORE AI v2.0 Starting...")
    print(f"Debug Mode: {settings.DEBUG}")
    print(f"HIPAA Mode: {settings.HIPAA_MODE}")

@app.on_event("shutdown")
async def shutdown_event():
    print("BIOCORE AI v2.0 Shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

---

## db/database.py
```python
"""Database connection management"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from api.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Test connection before use
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add event listeners for security
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable encryption and safety features"""
    if "sqlite" in str(engine.url):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=FULL")
        cursor.close()
```

---

## biocore/signal_processing/validation.py
```python
"""Signal quality validation"""
import numpy as np
from typing import Dict

class SignalValidator:
    def __init__(self):
        self.min_length = 100
        self.max_length = 1000000
    
    def validate(self, signal: np.ndarray, signal_type: str) -> Dict:
        """Validate signal quality"""
        issues = []
        
        # Check length
        if len(signal) < self.min_length:
            issues.append(f"Signal too short: {len(signal)} samples")
        if len(signal) > self.max_length:
            issues.append(f"Signal too long: {len(signal)} samples")
        
        # Check for NaN
        if np.isnan(signal).any():
            issues.append("Signal contains NaN values")
        
        # Check for infinite values
        if np.isinf(signal).any():
            issues.append("Signal contains infinite values")
        
        # Check variance (no signal = constant)
        if np.var(signal) < 1e-10:
            issues.append("Signal has zero variance (dead channel)")
        
        # Calculate quality score
        quality_score = self._calculate_quality(signal)
        
        return {
            "is_valid": len(issues) == 0,
            "quality_score": quality_score,
            "issues": issues,
            "reason": "; ".join(issues) if issues else "OK"
        }
    
    def _calculate_quality(self, signal: np.ndarray) -> float:
        """Quality score 0-1"""
        snr = self._estimate_snr(signal)
        
        # SNR-based quality (assuming good SNR > 20 dB)
        quality = min(snr / 20, 1.0)
        return float(quality)
    
    @staticmethod
    def _estimate_snr(signal: np.ndarray) -> float:
        """Estimate signal-to-noise ratio in dB"""
        # Detrended signal = noise estimate
        detrended = signal - np.mean(signal)
        noise = np.std(np.diff(detrended))
        signal_power = np.std(detrended)
        
        snr = signal_power / noise if noise > 0 else 0
        snr_db = 20 * np.log10(snr + 1e-10)
        return snr_db
```

---

## tests/test_api.py
```python
"""API Tests"""
import pytest
from fastapi.testclient import TestClient
from api.main import app
from db.models import Base
from db.database import SessionLocal, engine

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_patient_creation(client):
    response = client.post("/api/patients", json={
        "medical_id": "TEST001",
        "name": "John Doe",
        "email": "john@example.com"
    })
    assert response.status_code == 201
    assert response.json()["medical_id"] == "TEST001"

def test_signal_upload(client):
    # First create patient
    patient = client.post("/api/patients", json={
        "medical_id": "TEST002",
        "name": "Jane Doe",
        "email": "jane@example.com"
    }).json()
    
    # Then upload signal
    import numpy as np
    signal = np.sin(np.linspace(0, 10*np.pi, 1000)).tolist()
    
    response = client.post(
        f"/api/signals/upload/{patient['id']}",
        json={
            "signal_type": "ecg",
            "raw_signal": signal,
            "metadata": {"device": "test"}
        }
    )
    assert response.status_code == 200
    assert "signal_id" in response.json()
```

---

## .env.example
```
# Database
DATABASE_URL=postgresql://biocore:secure_password@localhost:5432/biocore_ai

# Security
SECRET_KEY=your-secret-key-change-in-production
ENCRYPTION_KEY=your-32-byte-encryption-key-here

# Debug
DEBUG=False

# Features
HIPAA_MODE=True
```

---

## docker-compose.yml
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: biocore
      POSTGRES_PASSWORD: secure_password
      POSTGRES_DB: biocore_ai
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U biocore"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://biocore:secure_password@postgres:5432/biocore_ai
      SECRET_KEY: dev-secret-key
      ENCRYPTION_KEY: dev-encryption-key-32-bytes
      DEBUG: "False"
    volumes:
      - ./:/app

  streamlit:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    depends_on:
      - api
    environment:
      API_URL: http://api:8000
    volumes:
      - ./ui:/app/ui

volumes:
  postgres_data:

networks:
  default:
    name: biocore-network
```

---

## requirements-v2.txt
```
# Core
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
alembic==1.13.0

# Security
cryptography==41.0.7
python-jose==3.3.0
PyJWT==2.8.1
passlib==1.7.4

# Signal Processing
numpy==1.24.3
scipy==1.11.4
scikit-learn==1.3.2

# ML & AI (Phase 3)
tensorflow==2.15.0
torch==2.1.1
xgboost==2.0.3
lightgbm==4.1.0
shap==0.43.0
lime==0.2.0

# UI
streamlit==1.35.0
plotly==5.17.0

# Hardware
pyserial==3.5

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1

# Utilities
python-multipart==0.0.6
```

---

## STARTUP GUIDE

### 1. Setup Environment
```bash
git clone https://github.com/your-org/biocore-ai-v2.git
cd biocore-ai-v2

# Create .env
cp .env.example .env
# Edit .env with your credentials

# Create venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-v2.txt
```

### 2. Start Database
```bash
# With Docker Compose
docker-compose up -d postgres redis

# Or local PostgreSQL
createuser biocore
createdb biocore_ai -O biocore
```

### 3. Initialize Database
```bash
python -c "from db.database import engine; from db.models import Base; Base.metadata.create_all(bind=engine)"
```

### 4. Start API
```bash
python api/main.py
# Or with uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test API
```bash
curl http://localhost:8000/health

# Response:
# {
#   "status": "healthy",
#   "version": "2.0.0-alpha",
#   "database": "ok"
# }
```

### 6. Run Tests
```bash
pytest tests/ -v --cov=api --cov=db
```

---

## API ENDPOINTS (Phase 1)

### Health
- `GET /health` - System status

### Patients
- `POST /api/patients` - Create patient
- `GET /api/patients/{id}` - Get patient
- `PUT /api/patients/{id}` - Update patient

### Signals
- `POST /api/signals/upload/{patient_id}` - Upload signal
- `GET /api/signals/{signal_id}` - Get signal metadata

### Audit
- `GET /api/audit/logs/{patient_id}` - Access logs (HIPAA)

---

*Phase 1 Starter Code - Ready for Implementation*
