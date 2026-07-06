import asyncio
import json
import logging

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    RoomInputOptions,
    RunContext,
    function_tool,
    inference,
)
from livekit.plugins import sarvam  
from app.core.config import settings
from app.database.session import SessionLocal
from app.utils.parser import parse_date, parse_time
from app.enums.doctor_specialization import DoctorSpecialization
from app.enums.gender import Gender
from app.services.patient_service import find_patient_by_phone
from app.services.appointment_service import (
    book_appointment as svc_book_appointment,
    cancel_appointment as svc_cancel_appointment,
    reschedule_appointment as svc_reschedule_appointment,
    get_patient_appointments as svc_get_patient_appointments,
)
from app.services.doctor_service import (
    check_doctor_availability,
    get_available_slots_by_specialization,
)
from app.schemas.appointment_request import AppointmentRequest
from datetime import datetime

load_dotenv()
logger = logging.getLogger("hospital-agent")

# ---------- Language config ----------
# BCP-47 codes Sarvam expects. Replace "kn" with whatever your third language is.
LANGUAGE_MAP = {
    "en": "en-IN",
    "hi": "hi-IN",
    "kn": "kn-IN",
}

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada",
}

SYSTEM_PROMPT_TEMPLATE = """
You are the AI voice receptionist for ABC Hospital.

Today's real date is {today_str}. Use this as the anchor for any date math.

You are polite, professional, warm, and concise. You are speaking on a live
phone call, so keep every response short — 1 to 2 sentences.

Speak and understand only in: {language_name}. Keep the entire conversation
in this language regardless of what happens.

CRITICAL TOOL-USE RULE:
You have real tools available to you through the platform's function-calling
mechanism. When you need information or need to perform an action, call the
tool directly using that mechanism — never write out a function name,
arguments, or tags like <function=...> as part of your spoken text. Your
spoken response must always be natural language only, never code or
pseudo-syntax. Never speak any text in the same turn that you call a tool —
call the tool completely silently, wait for its result, and only then speak
your response to the patient in your next turn.

CONVERSATION FLOW — ask for exactly ONE piece of information per turn, in
this order, and wait for the patient's answer before asking the next
question. Never ask for multiple details in a single question.

For booking an appointment:
1. Ask for their name.
2. Ask for their phone number.
3. As soon as you have the phone number, call lookup_patient with it.
   Say NOTHING else in that same turn — no "one moment", no filler text,
   just the tool call by itself. Respond only after the result comes back.
4. If lookup_patient finds an existing patient, use their stored name, age,
   and gender exactly as returned — do not ask for these again, and use
   the stored name (not whatever the patient said earlier) for the rest of
   the conversation and in your final confirmation. Skip straight to asking
   what health concern they have today.
   If it's a new patient, ask for age, then gender, one at a time, each as
   its own turn.
5. Ask what health concern or specialization they need.
6. Ask for their preferred date.
7. Ask for their preferred time.
8. Read back all collected details — using the stored name if this was an
   existing patient — in one summary and ask the patient to confirm before
   calling book_appointment.

For cancelling or rescheduling: ask for phone number first, call
lookup_patient with no other text in that turn, then once you have the
result, read out the matching appointment(s) and ask which one, one
question at a time. If the patient's new date or time sounds ambiguous or
garbled, ask them to repeat it before calling any tool with it.

STRICT RULES:
- Never state a doctor's availability, invent appointment IDs, or confirm a
  booking without first calling the matching tool and using its real
  result.
- If a tool reports the doctor is unavailable, offer the alternate slots
  the tool returned. Never invent alternate slots yourself.
- If a tool returns an error message, relay that honestly and ask how the
  patient would like to proceed. Do not guess or fill in missing backend
  data.
- Dates must be resolved to ISO format (YYYY-MM-DD) and times to 24-hour
  HH:MM before calling any tool — convert natural phrases like "tomorrow"
  or "2 PM" yourself before the tool call.
- Never compute or guess an actual calendar date yourself for words like
  "today" or "tomorrow" — pass those exact words through to the tool as
  the appointment_date argument unchanged (e.g. appointment_date="today"
  or appointment_date="tomorrow"). The backend resolves these correctly
  using the real system clock. Only convert to an ISO date yourself when
  the patient names a specific date or weekday that is not "today" or
  "tomorrow" — and when you do, use Today's real date above as your
  anchor, never a guess.  

Hospital facts (use these directly for general queries, do not guess):
- Hours: 9:00 AM to 8:00 PM, Monday through Saturday.
- Location: Bangalore.
- Emergency services: available 24 hours.
- Contact: +91-9876543210.
"""


def _run_db(fn, *args, **kwargs):
    """Run a sync SQLAlchemy service-layer call without blocking the event loop."""

    def _call():
        db = SessionLocal()
        try:
            return fn(db, *args, **kwargs)
        finally:
            db.close()

    return asyncio.to_thread(_call)


class HospitalAgent(Agent):
    def __init__(self, language_name: str):
        today_str = datetime.now().strftime("%A, %B %d, %Y")
        super().__init__(
            instructions=SYSTEM_PROMPT_TEMPLATE.format(
                language_name=language_name,
                today_str=today_str,
            )
        )

    @function_tool()
    async def lookup_patient(self, context: RunContext, phone: str) -> str:
        """Look up a patient's stored name, age, gender, and active appointments
        by phone number. Call this as soon as you have the phone number and
        BEFORE asking for age, gender, or which appointment to cancel/reschedule.
        Say nothing else in this turn — call this tool silently, with no
        spoken text alongside it. Respond to the patient only after you have
        the result, in your next turn.

        Args:
            phone: Patient's phone number.
        """
        try:
            def _lookup(db):
                patient = find_patient_by_phone(db, phone)
                appts = svc_get_patient_appointments(db, phone) if patient else []
                return patient, appts

            patient, appointments = await _run_db(_lookup)

            if patient is None:
                return (
                    "No existing patient record for that phone number. This is "
                    "a new patient — you still need their name, age, and gender."
                )

            lines = [
                f"Existing patient found. Name: {patient.name}. Age: {patient.age}. "
                f"Gender: {patient.gender.value}. Use this name and these details "
                f"directly — do not ask the patient for their name, age, or "
                f"gender again."
            ]

            if appointments:
                appt_lines = [
                    f"ID {a.appointment_id}: {a.appointment_date} at {a.appointment_time}"
                    for a in appointments
                ]
                lines.append("Active appointments: " + "; ".join(appt_lines))
            else:
                lines.append("No active appointments currently.")

            return "\n".join(lines)

        except Exception as e:
            logger.exception("lookup_patient failed")
            return f"I couldn't look that up: {e}. Could you confirm your phone number?"

    @function_tool()
    async def check_availability(
        self,
        context: RunContext,
        specialization: str,
        appointment_date: str,
        appointment_time: str,
    ) -> str:
        """Check whether a doctor of the given specialization is free at a date/time.

        Args:
            specialization: One of GENERAL_PHYSICIAN, CARDIOLOGIST, DERMATOLOGIST,
                NEUROLOGIST, ORTHOPEDIC, PEDIATRICIAN, GYNECOLOGIST, PSYCHIATRIST,
                ENT, OPHTHALMOLOGIST.
            appointment_date: ISO date, e.g. 2026-07-10.
            appointment_time: 24-hour time, e.g. 14:00.
        """
        try:
            spec = DoctorSpecialization(specialization)
            d = parse_date(appointment_date)
            t = parse_time(appointment_time)
            available, doctor = await _run_db(check_doctor_availability, spec, d, t)

            if available:
                return f" {doctor.name} is available on {d} at {t}."

            slots = await _run_db(get_available_slots_by_specialization, spec, d)
            if slots:
                return (
                    f" {doctor.name} is NOT available at {t} on {d}. "
                    f"Next available slots that day: {', '.join(slots)}."
                )
            return f" {doctor.name} has no available slots on {d}."

        except Exception as e:
            logger.exception("check_availability failed")
            return f"I couldn't check that: {e}. Could you repeat the date and time?"

    @function_tool()
    async def book_appointment(
        self,
        context: RunContext,
        name: str,
        phone: str,
        age: int,
        gender: str,
        specialization: str,
        appointment_date: str,
        appointment_time: str,
        reason: str,
    ) -> str:
        """Book a new appointment after all details are confirmed with the patient.

        Args:
            name: Patient's full name.
            phone: Patient's phone number.
            age: Patient's age in years.
            gender: One of MALE, FEMALE, OTHER.
            specialization: Doctor specialization (see check_availability for valid values).
            appointment_date: ISO date, e.g. 2026-07-10.
            appointment_time: 24-hour time, e.g. 14:00.
            reason: Brief health concern / reason for the visit.
        """
        try:
            request = AppointmentRequest(
                name=name,
                phone=phone,
                age=age,
                gender=Gender(gender),
                specialization=DoctorSpecialization(specialization),
                appointment_date=parse_date(appointment_date),
                appointment_time=parse_time(appointment_time),
                reason=reason,
            )
            appointment = await _run_db(svc_book_appointment, request)

            return (
                f"Booked. Appointment ID {appointment.appointment_id} for "
                f"{appointment.appointment_date} at {appointment.appointment_time}."
            )

        except Exception as e:
            logger.exception("book_appointment failed")
            return f"I couldn't complete that booking: {e}. Could you confirm the details again?"

    @function_tool()
    async def cancel_appointment(self, context: RunContext, appointment_id: int) -> str:
        """Cancel an appointment by its ID. Confirm the ID with the patient first
        by calling lookup_patient if you don't already have it.

        Args:
            appointment_id: The appointment ID to cancel.
        """
        try:
            appointment = await _run_db(svc_cancel_appointment, appointment_id)
            return f"Appointment {appointment.appointment_id} has been cancelled."

        except Exception as e:
            logger.exception("cancel_appointment failed")
            return f"I couldn't cancel that: {e}. Could you confirm the appointment ID?"

    @function_tool()
    async def reschedule_appointment(
        self,
        context: RunContext,
        appointment_id: int,
        new_date: str,
        new_time: str,
    ) -> str:
        """Reschedule an existing appointment to a new date/time.

        Args:
            appointment_id: The appointment ID to reschedule.
            new_date: ISO date, e.g. 2026-07-12.
            new_time: 24-hour time, e.g. 15:30.
        """
        try:
            d = parse_date(new_date)
            t = parse_time(new_time)
            appointment = await _run_db(svc_reschedule_appointment, appointment_id, d, t)

            return (
                f"Rescheduled. Appointment {appointment.appointment_id} is now on "
                f"{appointment.appointment_date} at {appointment.appointment_time}."
            )

        except Exception as e:
            logger.exception("reschedule_appointment failed")
            return f"I couldn't reschedule that: {e}. Could you confirm the exact date and time?"


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    participant = await ctx.wait_for_participant()

    # Language selection: frontend sets participant metadata as
    # e.g. '{"language": "hi"}' when minting the token / joining.
    lang_key = "en"
    try:
        if participant.metadata:
            meta = json.loads(participant.metadata)
            lang_key = meta.get("language", "en")
    except (json.JSONDecodeError, AttributeError):
        pass

    bcp47 = LANGUAGE_MAP.get(lang_key, "en-IN")
    language_name = LANGUAGE_NAMES.get(lang_key, "English")

    session = AgentSession(
        # vad omitted — AgentSession auto-provisions inference.VAD(model="silero")
        stt=sarvam.STT(language=bcp47, model="saarika:v2.5"),
        llm=sarvam.LLM(
            model="sarvam-105b",
            api_key=settings.SARVAM_API_KEY,
            temperature=0,
            
        ),
        tts=sarvam.TTS(target_language_code=bcp47, model="bulbul:v3", speaker="shubh"),
        turn_detection=inference.TurnDetector(),
    )

    await session.start(
        room=ctx.room,
        agent=HospitalAgent(language_name=language_name),
        room_input_options=RoomInputOptions(),
    )

    await session.generate_reply(
        instructions=(
            "Greet the patient warmly as ABC Hospital's receptionist and ask "
            "how you can help, in the configured language."
        )
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))