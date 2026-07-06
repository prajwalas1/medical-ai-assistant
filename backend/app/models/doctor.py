from app.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String , Enum
from app.enums.doctor_specialization import DoctorSpecialization

class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    specialization: Mapped[DoctorSpecialization] = mapped_column(
    Enum(DoctorSpecialization)
)
    
