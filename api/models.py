"""Pydantic models for API validation"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class PatientCreate(BaseModel):
    medical_id: str = Field(..., min_length=5)
    name: str = Field(..., min_length=2)
    email: str = Field(..., regex="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class SignalReadingBase(BaseModel):
    signal_type: str
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
