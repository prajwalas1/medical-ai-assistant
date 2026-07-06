from datetime import date, time, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.models.appointment import Appointment

from app.enums.doctor_specialization import DoctorSpecialization
from app.enums.appointment_status import AppointmentStatus


def find_doctor_by_specialization(
    db: Session,
    specialization: DoctorSpecialization,
):
    return (
        db.query(Doctor)
        .filter(
            Doctor.specialization == specialization
        )
        .first()
    )


def is_doctor_available(
    db: Session,
    doctor_id: int,
    appointment_date: date,
    appointment_time: time,
):
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.appointment_time == appointment_time,
            Appointment.status == AppointmentStatus.BOOKED,
        )
        .first()
    )

    return appointment is None


def check_doctor_availability(
    db: Session,
    specialization: DoctorSpecialization,
    appointment_date: date,
    appointment_time: time,
):
    """
    Returns:
        (available, doctor)

    available -> bool
    doctor -> Doctor object
    """

    doctor = find_doctor_by_specialization(
        db=db,
        specialization=specialization,
    )

    if doctor is None:
        raise ValueError(
            f"No doctor available for specialization '{specialization.value}'."
        )

    available = is_doctor_available(
        db=db,
        doctor_id=doctor.doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
    )

    return available, doctor


def get_next_available_slots(
    db: Session,
    doctor_id: int,
    appointment_date: date,
    limit: int = 5,
):
    booked_slots = (
        db.query(Appointment.appointment_time)
        .filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date,
            Appointment.status == AppointmentStatus.BOOKED,
        )
        .all()
    )

    booked_slots = {
        slot[0]
        for slot in booked_slots
    }

    available_slots = []

    current = datetime.combine(
        appointment_date,
        time(9, 0),
    )

    end = datetime.combine(
        appointment_date,
        time(17, 0),
    )

    while current < end:

        slot = current.time()

        if slot not in booked_slots:
            available_slots.append(
                slot.strftime("%I:%M %p")
            )

        if len(available_slots) == limit:
            break

        current += timedelta(minutes=30)

    return available_slots


def get_available_slots_by_specialization(
    db: Session,
    specialization: DoctorSpecialization,
    appointment_date: date,
    limit: int = 5,
):
    """
    Returns the next available slots for the given specialization.
    """

    doctor = find_doctor_by_specialization(
        db=db,
        specialization=specialization,
    )

    if doctor is None:
        raise ValueError(
            f"No doctor available for specialization '{specialization.value}'."
        )

    return get_next_available_slots(
        db=db,
        doctor_id=doctor.doctor_id,
        appointment_date=appointment_date,
        limit=limit,
    )