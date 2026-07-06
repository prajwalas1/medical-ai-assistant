from app.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String , Enum
from app.enums.gender import Gender

class Patient(Base):
    __tablename__="patients"

    patient_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(15))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[Gender] = mapped_column(
    Enum(Gender)
)
    




