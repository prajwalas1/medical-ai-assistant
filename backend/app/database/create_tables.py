from app.database.base import Base
from app.database.session import engine
from app.models import Patient, Doctor, Appointment

Base.metadata.create_all(bind=engine)