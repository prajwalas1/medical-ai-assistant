from datetime import date, time

from sqlalchemy.orm import Session

from app.enums.appointment_status import AppointmentStatus
from app.models.appointment import Appointment
from app.schemas.appointment_request import AppointmentRequest

from app.services.patient_service import (
    find_or_create_patient,
    find_patient_by_phone,
)

from app.services.doctor_service import (
    find_doctor_by_specialization,
    get_next_available_slots,
)


def check_doctor_availability(
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


def get_patient_appointments(
    db: Session,
    phone: str,
):
    patient = find_patient_by_phone(
        db=db,
        phone=phone,
    )

    if patient is None:
        raise ValueError(
            "Patient not found."
        )

    appointments = (
        db.query(Appointment)
        .filter(
            Appointment.patient_id == patient.patient_id,
            Appointment.status == AppointmentStatus.BOOKED,
        )
        .all()
    )

    return appointments


def cancel_appointment(
    db: Session,
    appointment_id: int,
):
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.appointment_id == appointment_id,
        )
        .first()
    )

    if appointment is None:
        raise ValueError(
            "Appointment not found."
        )

    appointment.status = AppointmentStatus.CANCELLED

    db.commit()
    db.refresh(appointment)

    return appointment


def reschedule_appointment(
    db: Session,
    appointment_id: int,
    appointment_date: date,
    appointment_time: time,
):
    appointment = (
        db.query(Appointment)
        .filter(
            Appointment.appointment_id == appointment_id,
        )
        .first()
    )

    if appointment is None:
        raise ValueError(
            "Appointment not found."
        )

    available = check_doctor_availability(
        db=db,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
    )

    if not available:

        slots = get_next_available_slots(
            db=db,
            doctor_id=appointment.doctor_id,
            appointment_date=appointment_date,
        )

        raise ValueError(
            f"Doctor is unavailable.\n"
            f"Available slots: {', '.join(slots)}"
        )

    appointment.appointment_date = appointment_date
    appointment.appointment_time = appointment_time

    db.commit()
    db.refresh(appointment)

    return appointment


def book_appointment(
    db: Session,
    request: AppointmentRequest,
):
    patient = find_or_create_patient(
        db=db,
        name=request.name,
        phone=request.phone,
        age=request.age,
        gender=request.gender,
    )

    doctor = find_doctor_by_specialization(
        db=db,
        specialization=request.specialization,
    )

    if doctor is None:
        raise ValueError(
            f"No doctor available with specialization '{request.specialization.value}'."
        )

    available = check_doctor_availability(
        db=db,
        doctor_id=doctor.doctor_id,
        appointment_date=request.appointment_date,
        appointment_time=request.appointment_time,
    )

    if not available:

        slots = get_next_available_slots(
            db=db,
            doctor_id=doctor.doctor_id,
            appointment_date=request.appointment_date,
        )

        raise ValueError(
            f"Dr. {doctor.name} is not available at "
            f"{request.appointment_time.strftime('%I:%M %p')}.\n"
            f"Available slots: {', '.join(slots)}"
        )

    appointment = Appointment(
        patient_id=patient.patient_id,
        doctor_id=doctor.doctor_id,
        appointment_date=request.appointment_date,
        appointment_time=request.appointment_time,
        status=AppointmentStatus.BOOKED,
        reason=request.reason,
    )

    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment 