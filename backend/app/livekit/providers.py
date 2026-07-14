from abc import ABC, abstractmethod
import logging

from livekit.agents import stt, llm, tts
from livekit.plugins import sarvam, deepgram, elevenlabs

from app.core.config import settings

logger = logging.getLogger("hospital-agent")


class STTProvider(ABC):
    @abstractmethod
    def build(self, bcp47: str) -> stt.STT: ...

class LLMProvider(ABC):
    @abstractmethod
    def build(self) -> llm.LLM: ...

class TTSProvider(ABC):
    @abstractmethod
    def build(self, bcp47: str) -> tts.TTS: ...


class SarvamSTTProvider(STTProvider):
    def build(self, bcp47: str) -> stt.STT:
        return sarvam.STT(language=bcp47, model="saarika:v2.5", api_key=settings.SARVAM_API_KEY)


class DeepgramSTTProvider(STTProvider):
    def build(self, bcp47: str) -> stt.STT:
        return deepgram.STT(model="nova-3", api_key=settings.DEEPGRAM_API_KEY)

class ElevenLabsSTTProvider(STTProvider):
    def build(self, bcp47: str) -> stt.STT:
        return elevenlabs.STT(api_key=settings.ELEVENLABS_API_KEY)


class SarvamLLMProvider(LLMProvider):
    def build(self) -> llm.LLM:
        return sarvam.LLM(
            model="sarvam-30b",
            api_key=settings.SARVAM_API_KEY,
            temperature=0,
        )

class SarvamTTSProvider(TTSProvider):
    def build(self, bcp47: str) -> tts.TTS:
        return sarvam.TTS(target_language_code=bcp47, model="bulbul:v3", speaker="shubh", api_key=settings.SARVAM_API_KEY)

class DeepgramTTSProvider(TTSProvider):
    def build(self, bcp47: str) -> tts.TTS:
        return deepgram.TTS(model="aura-2-asteria-en", api_key=settings.DEEPGRAM_API_KEY)

class ElevenLabsTTSProvider(TTSProvider):
    def build(self, bcp47: str) -> tts.TTS:
        # eleven_multilingual_v2 is required for non-English output; language
        # is ISO-639-1 (e.g. "en", "hi", "kn") — strip the region suffix from bcp47.
        lang_code = bcp47.split("-")[0]
        return elevenlabs.TTS(
            model="eleven_multilingual_v2",
            language=lang_code,
            api_key=settings.ELEVENLABS_API_KEY,
        )


STT_PROVIDERS: dict[str, STTProvider] = {
    "sarvam": SarvamSTTProvider(),
    "deepgram": DeepgramSTTProvider(),
    "elevenlabs": ElevenLabsSTTProvider(),
}

LLM_PROVIDERS: dict[str, LLMProvider] = {
    "sarvam": SarvamLLMProvider(),
}

TTS_PROVIDERS: dict[str, TTSProvider] = {
    "sarvam": SarvamTTSProvider(),
    "deepgram": DeepgramTTSProvider(),
    "elevenlabs": ElevenLabsTTSProvider(),
}


DEFAULT_STT = "sarvam"
DEFAULT_LLM = "sarvam"
DEFAULT_TTS = "sarvam"

# Per-provider language support, verified against each vendor's docs.
# "sarvam" is omitted from these maps since it's the universal fallback
# and supports all configured languages (en/hi/kn) for both STT and TTS.
#
# STT:
#   - Deepgram (Nova-3): en, hi. No Kannada in their supported language list.
#   - ElevenLabs (Scribe): en, hi, kn all rated "Excellent Accuracy".
# TTS:
#   - Deepgram (Aura-2): English only. No Hindi/Kannada voices exist yet.
#   - ElevenLabs (eleven_multilingual_v2): en, hi, kn all supported.
STT_SUPPORTED_LANGUAGES: dict[str, set[str]] = {
    "deepgram": {"en", "hi"},
    "elevenlabs": {"en", "hi", "kn"},
}

TTS_SUPPORTED_LANGUAGES: dict[str, set[str]] = {
    "deepgram": {"en"},
    "elevenlabs": {"en", "hi"},
}


def _lang_key(bcp47: str) -> str:
    """'en-IN' -> 'en'"""
    return bcp47.split("-")[0]


def resolve_stt_provider(provider: str, bcp47: str) -> str:
    """Returns the provider name that get_stt() will actually build,
    after applying language-gating fallback. Lets callers (like the vad
    logic in agent.py) know the real provider, not just the requested one."""
    supported = STT_SUPPORTED_LANGUAGES.get(provider)
    if supported is not None and _lang_key(bcp47) not in supported:
        logger.warning(
            f"STT provider '{provider}' doesn't support '{bcp47}' — falling back to {DEFAULT_STT}"
        )
        return DEFAULT_STT
    return provider if provider in STT_PROVIDERS else DEFAULT_STT


def resolve_tts_provider(provider: str, bcp47: str) -> str:
    """Same idea as resolve_stt_provider, but for TTS. Deepgram's TTS gating
    differs from its STT gating (English-only vs en/hi), so this is tracked
    separately rather than reusing the STT resolver."""
    supported = TTS_SUPPORTED_LANGUAGES.get(provider)
    if supported is not None and _lang_key(bcp47) not in supported:
        logger.warning(
            f"TTS provider '{provider}' doesn't support '{bcp47}' — falling back to {DEFAULT_TTS}"
        )
        return DEFAULT_TTS
    return provider if provider in TTS_PROVIDERS else DEFAULT_TTS


def get_stt(provider: str, bcp47: str) -> stt.STT:
    provider = resolve_stt_provider(provider, bcp47)
    chosen = STT_PROVIDERS[provider]
    try:
        return chosen.build(bcp47)
    except NotImplementedError as e:
        logger.warning(f"{e} — falling back to {DEFAULT_STT}")
        return STT_PROVIDERS[DEFAULT_STT].build(bcp47)


def get_llm(provider: str) -> llm.LLM:
    chosen = LLM_PROVIDERS.get(provider, LLM_PROVIDERS[DEFAULT_LLM])
    try:
        return chosen.build()
    except NotImplementedError as e:
        logger.warning(f"{e} — falling back to {DEFAULT_LLM}")
        return LLM_PROVIDERS[DEFAULT_LLM].build()


def get_tts(provider: str, bcp47: str) -> tts.TTS:
    provider = resolve_tts_provider(provider, bcp47)
    chosen = TTS_PROVIDERS[provider]
    try:
        return chosen.build(bcp47)
    except NotImplementedError as e:
        logger.warning(f"{e} — falling back to {DEFAULT_TTS}")
        return TTS_PROVIDERS[DEFAULT_TTS].build(bcp47)