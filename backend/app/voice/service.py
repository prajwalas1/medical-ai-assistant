import tempfile
from pathlib import Path
import traceback

from sqlalchemy.orm import Session

from app.ai.conversation_manager import ConversationManager
from app.voice.stt import speech_to_text
from app.voice.tts import text_to_speech

conversation = ConversationManager()


def process_voice(
    db: Session,
    audio_file,
):
    """
    Voice Pipeline

    Audio
        ↓
    STT
        ↓
    ConversationManager
        ↓
    TTS
        ↓
    Return text + audio
    """

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav",
    ) as temp:

        # Save uploaded audio
        temp.write(audio_file.read())
        temp.flush()

        temp_path = Path(temp.name)

        print("\n========== SAVED AUDIO ==========")
        print("Path :", temp_path)
        print("Size :", temp_path.stat().st_size, "bytes")
        print("=================================\n")

    try:

        print("\n========== VOICE PIPELINE ==========")

        # -------------------------
        # STT
        # -------------------------
        print("1️⃣ Running STT...")

        user_message = speech_to_text(
            str(temp_path)
        )

        print("STT Result:", repr(user_message))

        # -------------------------
        # Conversation Manager
        # -------------------------
        print("\n2️⃣ Calling ConversationManager...")

        response = conversation.process_message(
            db=db,
            message=user_message,
        )

        print("Conversation Response:")
        print(response)

        # -------------------------
        # Assistant Message
        # -------------------------
        print("\n3️⃣ Extracting assistant message...")

        assistant_message = response["message"]

        print("Assistant Message:")
        print(repr(assistant_message))
        print("Length:", len(assistant_message))

        # -------------------------
        # TTS
        # -------------------------
        print("\n4️⃣ Running TTS...")

        assistant_audio = text_to_speech(
            assistant_message
        )

        print("TTS Success")
        print("Audio Size:", len(assistant_audio), "bytes")

        print("\n========== PIPELINE COMPLETE ==========\n")

        return {
            "user_message": user_message,
            "assistant_message": assistant_message,
            "assistant_audio": assistant_audio,
        }

    except Exception:

        print("\n========== PIPELINE ERROR ==========")
        traceback.print_exc()
        print("====================================\n")

        raise

    finally:

        # Comment this temporarily so we can inspect the file.
        # Uncomment it again after debugging.

        # temp_path.unlink(missing_ok=True)

        print("Temporary audio file kept at:")
        print(temp_path)