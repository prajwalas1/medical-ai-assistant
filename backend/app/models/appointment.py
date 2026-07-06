from app.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Date, Time, ForeignKey,Integer, String , Enum
from datetime import date, time
from app.enums.appointment_status import AppointmentStatus

class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(
    ForeignKey("patients.patient_id")
    )
    doctor_id: Mapped[int] = mapped_column(
    ForeignKey("doctors.doctor_id")
    )
    appointment_date: Mapped[date] = mapped_column(Date)
    appointment_time: Mapped[time] = mapped_column(Time)
    status: Mapped[AppointmentStatus] = mapped_column(
    Enum(AppointmentStatus)
    )
    reason: Mapped[str] = mapped_column(String(255))

