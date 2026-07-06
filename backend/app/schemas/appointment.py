from app.enums.appointment_status import AppointmentStatus
from datetime import date, time
from pydantic import BaseModel

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus
    reason: str

class AppointmentResponse(BaseModel):
    appointment_id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus
    reason: str

    model_config = {
        "from_attributes": True
    }

