import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import Base, engine
from app.routes import patients

logging.basicConfig(level=logging.INFO)
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Voice AI Patient Registration API", version="1.0.0", description="REST API for a voice-based patient registration assessment")
origins = [x.strip() for x in settings.CORS_ORIGINS.split(",")] if settings.CORS_ORIGINS else ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(patients.router, prefix="/patients", tags=["Patients"])
@app.get("/health")
def health(): return {"data":{"status":"healthy"},"error":None}
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")
