from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate,DoctorResponse

router = APIRouter()

@router.post("/doctors",response_model=DoctorResponse)
def create_doctor(
    doctor: DoctorCreate,
    db: Session = Depends(get_db),
):
    new_doctor = Doctor(
        name=doctor.name,
        specialization=doctor.specialization,
    )

    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)

    return new_doctor
@router.get("/doctors",response_model=list[DoctorResponse])
def get_doctors(
    db: Session = Depends(get_db),
):
    doctors = db.query(Doctor).all()
    return doctors
