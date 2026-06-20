"""Signal processing endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import SignalReading, Patient
from api.models import SignalReadingCreate
from security.audit_log import audit_logger
from security.encryption import encryption
from app.utils import validate_signal
import numpy as np

router = APIRouter(prefix="/api/signals", tags=["signals"])


def predict_signal_async(db: Session, signal_id: str, signal_type: str):
    """Background task placeholder for predictions"""
    try:
        # Placeholder for future ML inference
        return True
    except Exception:
        return False


@router.post("/upload/{patient_id}", response_model=dict)
async def upload_signal(
    patient_id: str,
    reading: SignalReadingCreate,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
    current_user: str = "system"
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    signal_array = np.array(reading.raw_signal, dtype=float)
    is_valid, validation_message = validate_signal(signal_array)
    if not is_valid:
        raise HTTPException(status_code=422, detail=f"Signal invalid: {validation_message}")

    signal_reading = SignalReading(
        patient_id=patient_id,
        signal_type=reading.signal_type,
        raw_signal=encryption.encrypt(signal_array.tobytes()),
        signal_quality=float(np.clip(np.std(signal_array) / (np.max(np.abs(signal_array)) + 1e-9), 0.0, 1.0)),
        metadata_json=reading.metadata,
    )
    db.add(signal_reading)
    db.commit()

    await audit_logger.log_access(
        db, current_user, "SIGNAL_UPLOAD",
        patient_id=patient_id,
        resource=f"signal/{reading.signal_type}"
    )

    if background_tasks:
        background_tasks.add_task(
            predict_signal_async,
            db, signal_reading.id, reading.signal_type
        )

    return {
        "signal_id": signal_reading.id,
        "quality_score": signal_reading.signal_quality,
        "message": "Signal uploaded successfully"
    }


@router.get("/{signal_id}")
async def get_signal(signal_id: str, db: Session = Depends(get_db)):
    reading = db.query(SignalReading).filter(SignalReading.id == signal_id).first()
    if not reading:
        raise HTTPException(status_code=404, detail="Signal not found")

    return {
        "id": reading.id,
        "signal_type": reading.signal_type,
        "quality_score": reading.signal_quality,
        "created_at": reading.created_at,
    }
