from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.database.connection import (
    connect_to_database,
    disconnect_database,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_database()
    yield
    await disconnect_database()


app = FastAPI(
    title="AI Medical Appointment Assistant",
    description="Voice-based medical appointment booking system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)