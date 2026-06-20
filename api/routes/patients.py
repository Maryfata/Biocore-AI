"""Patient management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Patient
from api.models import PatientCreate
from security.encryption import encryption
from security.audit_log import audit_logger

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.post("", response_model=dict)
async def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    encrypted_name = encryption.encrypt(patient.name)
    encrypted_email = encryption.encrypt(patient.email)

    new_patient = Patient(
        medical_id=patient.medical_id,
        name_encrypted=encrypted_name,
        email_encrypted=encrypted_email,
    )
    db.add(new_patient)
    db.commit()
    await audit_logger.log_access(db, "system", "PATIENT_CREATE", patient_id=new_patient.id, resource="patient")
    return {
        "id": new_patient.id,
        "medical_id": new_patient.medical_id,
        "created_at": new_patient.created_at,
    }


@router.get("/{patient_id}", response_model=dict)
async def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {
        "id": patient.id,
        "medical_id": patient.medical_id,
        "created_at": patient.created_at,
    }
