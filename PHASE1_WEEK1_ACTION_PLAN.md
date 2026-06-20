# 🚨 BIOCORE AI OS - PLAN DE ACCIÓN INMEDIATO (FASE 1)
**Versión:** 1.0  
**Fecha:** 2026-06-05  
**Responsable:** Equipo Técnico BIOCORE  
**Estado:** INICIACIÓN DE IMPLEMENTACIÓN

---

## 📌 OBJETIVOS FASE 1 (Semanas 1-4)

### Meta Principal
Crear **fundación sólida, segura y escalable** para BIOCORE v2.0

### Objetivos Específicos
1. ✅ Migrar de Streamlit monolítico → FastAPI modular
2. ✅ Implementar Base de Datos con encriptación
3. ✅ Sistema de auditoría completo
4. ✅ Validación de señales
5. ✅ Autenticación & Autorización
6. ✅ Tests automatizados 80%+

### Salida Esperada
- API FastAPI totalmente funcional (12+ endpoints)
- PostgreSQL con datos encriptados
- Sistema de logs auditables DICOM-compatible
- Test suite completo
- Documentación OpenAPI/Swagger

---

## 📋 TAREAS DETALLADAS SEMANA 1

### Tarea 1.1: Crear Estructura FastAPI (40 horas)
**Responsable:** Backend Lead  
**Deadline:** Viernes EOD

**Subtareas:**
```
├── 1.1.1 Crear proyecto FastAPI base
├── 1.1.2 Setup uvicorn + hot reload
├── 1.1.3 Crear estructura de carpetas
│   ├── /api/routes
│   ├── /api/middleware
│   └── /api/models
├── 1.1.4 Pydantic schemas básicos
├── 1.1.5 CORS configuration
└── 1.1.6 Error handling middleware
```

**Testing:**
- ✓ FastAPI app starts successfully
- ✓ OpenAPI docs available at `/docs`
- ✓ CORS headers correct

**Code Template:**
```python
# app/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="BIOCORE AI OS v2.0",
    version="2.0.0",
    description="Advanced biomedical signal analysis platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

---

### Tarea 1.2: Setup PostgreSQL + SQLAlchemy (35 horas)
**Responsable:** Database Architect  
**Deadline:** Viernes EOD

**Subtareas:**
```
├── 1.2.1 Install PostgreSQL local
├── 1.2.2 Create database BIOCORE_V2
├── 1.2.3 SQLAlchemy Base models
├── 1.2.4 Users table (encrypted passwords)
├── 1.2.5 Patients table (with HIPAA fields)
├── 1.2.6 Signals table (raw signal data)
├── 1.2.7 Results table (analysis results)
├── 1.2.8 AuditLog table
├── 1.2.9 Alembic migrations setup
└── 1.2.10 Connection pooling (psycopg2)
```

**Database Schema Minimal:**
```sql
-- Users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'student',  -- student, clinician, admin
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Patients (HIPAA de-identified by default)
CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    patient_code VARCHAR(255) UNIQUE NOT NULL,  -- De-identified
    created_by INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB  -- Flexible for future fields
);

-- Signals (Raw biomedical data)
CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(id),
    signal_type VARCHAR(50) NOT NULL,  -- ECG, HRV, EEG, EMG, etc
    raw_data BYTEA NOT NULL,  -- Encrypted
    sample_rate INT NOT NULL,
    duration_seconds FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis Results
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    signal_id INT REFERENCES signals(id),
    analysis_type VARCHAR(50) NOT NULL,  -- arrhythmia, hrv, eeg_bands, etc
    result_json JSONB NOT NULL,  -- Results with confidence
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Log (Immutable)
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT
);
```

**Testing:**
- ✓ PostgreSQL connection works
- ✓ All tables created
- ✓ Can insert/query records
- ✓ Encryption/decryption works

---

### Tarea 1.3: Sistema de Auditoría (25 horas)
**Responsable:** Security Engineer  
**Deadline:** Viernes EOD

**Subtareas:**
```
├── 1.3.1 Create AuditLog model
├── 1.3.2 Logging middleware
├── 1.3.3 Timestamp + IP capture
├── 1.3.4 Action types enumeration
├── 1.3.5 DICOM audit format compatibility
├── 1.3.6 Log export to CSV
└── 1.3.7 Log retention policy (7 years)
```

**Implementation:**
```python
# security/audit_log.py
from datetime import datetime
from enum import Enum
from db.models import AuditLog

class AuditAction(str, Enum):
    SIGNAL_UPLOAD = "signal_upload"
    SIGNAL_ANALYZE = "signal_analyze"
    RESULT_VIEW = "result_view"
    RESULT_EXPORT = "result_export"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PATIENT_CREATE = "patient_create"

async def log_action(
    user_id: int,
    action: AuditAction,
    resource_type: str,
    resource_id: int,
    request = None
):
    """Log action to audit trail"""
    audit = AuditLog(
        user_id=user_id,
        action=action.value,
        resource_type=resource_type,
        resource_id=resource_id,
        timestamp=datetime.utcnow(),
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get('user-agent') if request else None
    )
    db.session.add(audit)
    db.session.commit()
    return audit
```

**Testing:**
- ✓ Actions logged correctly
- ✓ Timestamps accurate
- ✓ Can query audit trail
- ✓ Export to CSV works

---

### Tarea 1.4: Validación de Señales (35 horas)
**Responsable:** Signal Processing Lead  
**Deadline:** Viernes EOD

**Subtareas:**
```
├── 1.4.1 Signal quality scorer
├── 1.4.2 Baseline drift detector
├── 1.4.3 Noise level estimator
├── 1.4.4 Artifact detector (powerline, EMG, etc)
├── 1.4.5 Missing data detector
├── 1.4.6 Sample rate validation
└── 1.4.7 Quality report generator
```

**Implementation:**
```python
# core/signal_processing/validation.py
import numpy as np
from enum import Enum
from dataclasses import dataclass

class SignalQuality(str, Enum):
    EXCELLENT = "excellent"  # SNR > 40dB
    GOOD = "good"            # 30-40dB
    FAIR = "fair"            # 20-30dB
    POOR = "poor"            # <20dB

@dataclass
class SignalValidationReport:
    is_valid: bool
    quality_level: SignalQuality
    snr_db: float
    noise_std: float
    artifacts_detected: List[str]
    baseline_drift: float
    missing_samples: int
    warnings: List[str]
    recommendations: List[str]

def validate_ecg_signal(ecg_signal: np.ndarray, sample_rate: float) -> SignalValidationReport:
    """Comprehensive ECG signal validation"""
    # Implement:
    # 1. Sample rate check (250-1000 Hz typical)
    # 2. Signal bounds check (-10mV to +10mV typical)
    # 3. Baseline drift analysis
    # 4. Powerline artifact (50/60Hz)
    # 5. EMG noise estimation
    # 6. Missing data (NaN detection)
    # 7. Signal-to-noise ratio
    pass

def estimate_snr(signal: np.ndarray, noise: np.ndarray) -> float:
    """Estimate Signal-to-Noise Ratio in dB"""
    signal_power = np.mean(signal**2)
    noise_power = np.mean(noise**2)
    return 10 * np.log10(signal_power / noise_power)
```

**Testing:**
- ✓ Quality scorer works on clean signals
- ✓ Artifacts detected correctly
- ✓ SNR estimated accurately
- ✓ Report generation works

---

### Tarea 1.5: Implementar JWT + OAuth2 (40 horas)
**Responsable:** Security Engineer  
**Deadline:** Viernes EOD

**Subtareas:**
```
├── 1.5.1 JWT token generation
├── 1.5.2 Token expiration (15 min access, 7 day refresh)
├── 1.5.3 OAuth2 PasswordBearer
├── 1.5.4 Dependency injection for auth
├── 1.5.5 Role-based access control (RBAC)
├── 1.5.6 Password hashing (bcrypt)
├── 1.5.7 Token refresh endpoint
└── 1.5.8 Logout with token blacklist
```

**Implementation:**
```python
# api/middleware/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key-change-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)
    return user_id

@app.post("/token")
async def login(username: str, password: str):
    # Verify user & password
    # Generate token
    access_token = create_access_token(data={"sub": user_id})
    return {"access_token": access_token, "token_type": "bearer"}
```

**Testing:**
- ✓ Token generated successfully
- ✓ Token validation works
- ✓ Role-based access works
- ✓ Token expiration works

---

### Tarea 1.6: MediaPipe & Gestos (15 horas) ✅
**Responsable:** Frontend Lead  
**Deadline:** Lunes (DONE)

- ✅ Agregar mediapipe + opencv-python a requirements.txt
- ✅ Mejorar error messages en gesture_controller.py
- ✅ Test gesture detection

---

## 📊 MATRIZ DE RIESGOS FASE 1

### Riesgos Críticos

| ID | Riesgo | Probabilidad | Impacto | Mitigación | Propietario |
|----|--------|--------------|---------|-----------|------------|
| R1 | PostgreSQL setup fallido | Media | Alto | Documentación step-by-step + equipo dedicado | DB Arch |
| R2 | Seguridad JWT incompleta | Media | Crítico | Security audit + OWASP checklist | Security Eng |
| R3 | Performance API lenta | Baja | Alto | Load testing + indexing DB | Backend Lead |
| R4 | Pérdida de datos en migración | Baja | Crítico | Backup + rollback plan | DB Arch |
| R5 | Retrasos en integración | Media | Medio | Daily standups + CI/CD | PM |

### Mitigaciones Implementadas

- ✅ Git version control (todas las changes)
- ✅ Daily backups PostgreSQL
- ✅ Testing automatizados en cada cambio
- ✅ Code reviews (mínimo 2 personas)
- ✅ Staging environment antes de prod

---

## 📈 KPI SEMANA 1

### Técnico
- [ ] FastAPI app + 5+ endpoints funcionales
- [ ] PostgreSQL con datos encriptados
- [ ] Sistema de auditoría capturando logs
- [ ] Validación de señales < 500ms
- [ ] JWT tokens generando/validando
- [ ] Test coverage 80%+

### Calidad
- [ ] 0 critical issues
- [ ] Deployment automático via CI/CD
- [ ] Code review 100% de cambios

### Seguridad
- [ ] 0 vulnerabilidades OWASP Top 10
- [ ] HTTPS enforced
- [ ] Passwords hashed + salted
- [ ] API rate limiting (100 req/min)

---

## 📅 TIMELINE DETALLADO SEMANA 1

```
LUNES
├── 09:00 - Kick-off meeting
├── 10:00 - FastAPI structure creation (1.1)
├── 14:00 - PostgreSQL local install (1.2)
└── 17:00 - End-of-day: Basic API running ✓

MARTES
├── 09:00 - Database schema completion (1.2)
├── 11:00 - Audit log table creation (1.3)
├── 14:00 - Signal validation module (1.4)
└── 17:00 - Basic validation working ✓

MIÉRCOLES
├── 09:00 - JWT implementation start (1.5)
├── 11:00 - Token generation + validation
├── 14:00 - RBAC setup
└── 17:00 - Auth middleware working ✓

JUEVES
├── 09:00 - Integration testing all modules
├── 11:00 - Error handling + edge cases
├── 14:00 - Documentation Swagger/OpenAPI
└── 17:00 - All 5 modules integrated ✓

VIERNES
├── 09:00 - Final testing + bug fixes
├── 11:00 - Performance benchmarking
├── 14:00 - Security audit
├── 15:00 - Code review + merge to main
└── 17:00 - PHASE 1 WEEK 1 COMPLETE ✓
```

---

## 📚 RECURSOS NECESARIOS

### Herramientas
- FastAPI 0.104+
- PostgreSQL 15+
- SQLAlchemy 2.0+
- Pydantic 2.0+
- python-jose + cryptography
- pytest + pytest-cov

### Personal
- 1 Backend Lead (40h)
- 1 Database Architect (35h)
- 1 Security Engineer (65h)
- 1 Frontend Lead (15h)
- 1 QA Engineer (30h)

### Tiempo Total: 185 horas (~5.2 FTE-weeks)

---

## 🔄 REVIEW & VALIDATION

### Daily Standup (09:00 - 15 min)
- Progreso del día anterior
- Blockers
- Plan del día

### End-of-Day Sync (17:00 - 30 min)
- Demos de features completadas
- Issues encontrados
- Ajustes para mañana

### Friday Review (16:00 - 1 hora)
- Demo con stakeholders
- Retrospective
- Planning próxima semana

---

## 📞 CONTACTOS & ESCALACIÓN

**Backend Lead:** [Contact]  
**Database Architect:** [Contact]  
**Security Engineer:** [Contact]  
**PM/Scrum Master:** [Contact]  

**Escalación:**
- Blocker crítico: Escalate inmediatamente
- PM debe ser notificado en 30 min
- Daily report via Slack #biocore-v2

---

## ✅ CHECKLIST COMPLETITUD FASE 1 WEEK 1

- [ ] FastAPI app deployed locally
- [ ] PostgreSQL database running
- [ ] All tables created with data
- [ ] Audit logging working
- [ ] Signal validation module complete
- [ ] JWT + OAuth2 implemented
- [ ] 80%+ test coverage
- [ ] Documentation complete
- [ ] Security audit passed
- [ ] Ready for Week 2 start

---

**Preparado por:** Technical Lead, BIOCORE AI OS v2.0  
**Aprobado por:** Project Manager  
**Fecha:** 2026-06-05  
**Estado:** INICIACIÓN
