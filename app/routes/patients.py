import logging
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Patient
from app.schemas import PatientCreate, PatientUpdate, PatientResponse

router = APIRouter()
logger = logging.getLogger("patient-registration")

def ok(data): return {"data": data, "error": None}

def serialize(p): return PatientResponse.model_validate(p).model_dump(mode="json")

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    existing = db.query(Patient).filter(Patient.phone_number == payload.phone_number, Patient.deleted_at.is_(None)).first()
    if existing:
        raise HTTPException(status_code=409, detail={"code":"DUPLICATE_PATIENT", "message":"A patient with this phone number already exists", "patient_id": existing.patient_id})
    patient = Patient(**payload.model_dump())
    db.add(patient); db.commit(); db.refresh(patient)
    logger.info("Patient registered successfully: patient_id=%s", patient.patient_id)
    return ok(serialize(patient))

@router.get("", response_model=dict)
def list_patients(last_name: str | None = None, phone_number: str | None = None, date_of_birth: date | None = None, include_deleted: bool = False, db: Session = Depends(get_db)):
    q = db.query(Patient)
    if not include_deleted: q = q.filter(Patient.deleted_at.is_(None))
    if last_name: q = q.filter(Patient.last_name.ilike(f"%{last_name}%"))
    if phone_number: q = q.filter(Patient.phone_number == phone_number)
    if date_of_birth: q = q.filter(Patient.date_of_birth == date_of_birth)
    return ok([serialize(p) for p in q.order_by(Patient.created_at.desc()).all()])

@router.get("/{patient_id}", response_model=dict)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.patient_id == patient_id, Patient.deleted_at.is_(None)).first()
    if not p: raise HTTPException(status_code=404, detail={"code":"NOT_FOUND", "message":"Patient not found"})
    return ok(serialize(p))

@router.put("/{patient_id}", response_model=dict)
def update_patient(patient_id: str, payload: PatientUpdate, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.patient_id == patient_id, Patient.deleted_at.is_(None)).first()
    if not p: raise HTTPException(status_code=404, detail={"code":"NOT_FOUND", "message":"Patient not found"})
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(p, key, value)
    p.updated_at = datetime.now(timezone.utc); db.commit(); db.refresh(p)
    logger.info("Patient updated: patient_id=%s", patient_id)
    return ok(serialize(p))

@router.delete("/{patient_id}", response_model=dict)
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    p = db.query(Patient).filter(Patient.patient_id == patient_id, Patient.deleted_at.is_(None)).first()
    if not p: raise HTTPException(status_code=404, detail={"code":"NOT_FOUND", "message":"Patient not found"})
    p.deleted_at = datetime.now(timezone.utc); db.commit()
    logger.info("Patient soft-deleted: patient_id=%s", patient_id)
    return ok({"patient_id": patient_id, "deleted": True})
