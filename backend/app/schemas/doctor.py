from pydantic import BaseModel
from app.enums.doctor_specialization import DoctorSpecialization

class DoctorCreate(BaseModel):
    name: str
    specialization: DoctorSpecialization

class DoctorResponse(BaseModel):
    doctor_id : int
    name: str
    specialization: DoctorSpecialization

    model_config = {
        "from_attributes":True
    }  