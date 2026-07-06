from pydantic import BaseModel
from app.enums.gender import Gender

class PatientCreate(BaseModel):
    name: str
    phone: str
    age: int
    gender: Gender



class PatientResponse(BaseModel):
    patient_id: int
    name: str
    phone: str
    age: int
    gender: Gender

    model_config = {
        "from_attributes":True
    }