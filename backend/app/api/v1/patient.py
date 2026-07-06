from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.patient import PatientCreate ,PatientResponse
from app.models.patient import Patient

router = APIRouter()

@router.post("/patients",response_model=PatientResponse)
def create_patient(
    patient:PatientCreate,
    db: Session = Depends(get_db)
):
    new_patient = Patient(
        name = patient.name,
        phone=patient.phone,
        age=patient.age,
        gender=patient.gender,
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    return new_patient

@router.get("/patients", response_model=list[PatientResponse])
def get_patients(
    db: Session = Depends(get_db)
):
    patients = db.query(Patient).all()
    return patients
    
