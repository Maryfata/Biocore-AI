"""FastAPI Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.routes import signals, patients, health
from db.database import engine
from db.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="BIOCORE AI OS v2.0",
    description="Clinical-grade biomedical signal analysis platform",
    version="2.0.0-alpha",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        reload=settings.DEBUG,
    )
