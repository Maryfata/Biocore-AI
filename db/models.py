"""SQLAlchemy ORM Models for BIOCORE AI"""
from sqlalchemy import Column, String, DateTime, Float, LargeBinary, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    medical_id = Column(String(255), unique=True, index=True)
    name_encrypted = Column(LargeBinary, nullable=False)
    email_encrypted = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SignalReading(Base):
    __tablename__ = "signal_readings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String(36), index=True)
    signal_type = Column(String(50))
    raw_signal = Column(LargeBinary)
    signal_quality = Column(Float)
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    signal_id = Column(String(36), index=True)
    model_name = Column(String(100))
    prediction = Column(String(255))
    confidence = Column(Float)
    explanation_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36))
    action = Column(String(255))
    patient_id = Column(String(36), nullable=True, index=True)
    resource = Column(String(255))
    ip_address = Column(String(45))
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
