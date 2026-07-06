from datetime import date, time

from pydantic import BaseModel

from app.enums.gender import Gender
from app.enums.doctor_specialization import DoctorSpecialization


class AppointmentRequest(BaseModel):
    name: str
    phone: str
    age: int
    gender: Gender

    specialization: DoctorSpecialization

    appointment_date: date
    appointment_time: time

    reason: str