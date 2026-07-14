from datetime import timedelta
import json
import uuid

from fastapi import APIRouter
from livekit import api
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class TokenRequest(BaseModel):
    identity: str | None = None
    room_name: str | None = None
    language: str = "en"  # "en" | "hi" | "kn"
    stt_provider: str = "sarvam"   # "sarvam" | "deepgram" | "elevenlabs"
    llm_provider: str = "sarvam"   # "sarvam" | "openai" | "gemini"


class TokenResponse(BaseModel):
    token: str
    url: str
    room_name: str
    identity: str


@router.post("/livekit/token", response_model=TokenResponse)
def create_token(request: TokenRequest):
    room_name = request.room_name or f"hospital-call-{uuid.uuid4().hex[:8]}"
    identity = request.identity or f"patient-{uuid.uuid4().hex[:6]}"

    token = (
        api.AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET,
        )
        .with_identity(identity)
        .with_name(identity)
        .with_metadata(json.dumps({"language": request.language,"stt_provider": request.stt_provider,"llm_provider": request.llm_provider,}))
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )
        )
        .with_ttl(timedelta(minutes=30))
        .to_jwt()
    )

    return TokenResponse(
        token=token,
        url=settings.LIVEKIT_URL,
        room_name=room_name,
        identity=identity,
    )  







