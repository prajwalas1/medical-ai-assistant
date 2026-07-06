from fastapi import APIRouter
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.patient import router as patient_router
from app.api.v1.doctor import router as doctor_router
from app.api.v1.appointment import router as appointment_router
from app.api.v1.livekit_token import router as livekit_token_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(patient_router)
api_router.include_router(doctor_router)
api_router.include_router(appointment_router)
api_router.include_router(livekit_token_router)