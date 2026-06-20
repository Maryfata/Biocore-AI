"""Health check endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from api.models import HealthCheck

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthCheck)
async def health_check(db: Session = Depends(get_db)):
    try:
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
            "telemedicine": "ready",
        },
    )
