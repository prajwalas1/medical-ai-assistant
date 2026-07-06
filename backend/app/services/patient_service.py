from sqlalchemy.orm import Session
from app.enums.gender import Gender
from app.models.patient import Patient

def find_patient_by_phone(
    db: Session,
    phone: str,
):
    return (
        db.query(Patient)
        .filter(Patient.phone == phone)
        .first()
    )

def create_patient(
    db: Session,
    name: str,
    phone: str,
    age: int,
    gender: Gender,
):
    patient = Patient(
        name=name,
        phone=phone,
        age=age,
        gender=gender,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient

def find_or_create_patient(
    db: Session,
    name: str,
    phone: str,
    age: int,
    gender: Gender,
):
    patient = find_patient_by_phone(
        db,
        phone,
    )

    if patient:
        return patient

    return create_patient(
        db=db,
        name=name,
        phone=phone,
        age=age,
        gender=gender,
    )