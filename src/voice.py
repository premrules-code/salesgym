import os
import re
from elevenlabs import ElevenLabs
from src.config import VOICE_DIR


class VoiceGenerator:
    def __init__(self, api_key: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb"):
        self.api_key = api_key
        self.voice_id = voice_id  # Default: George (professional male voice)
        self.client = ElevenLabs(api_key=api_key) if api_key and api_key != "fake-key" else None

    def _sanitize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

    def _build_audio_path(self, generation: int, call_id: str, turn: int) -> str:
        gen_dir = os.path.join(VOICE_DIR, f"gen_{generation}")
        os.makedirs(gen_dir, exist_ok=True)
        return os.path.join(gen_dir, f"{call_id}_turn_{turn}.mp3")

    async def generate_audio(self, text: str, generation: int, call_id: str, turn: int) -> str:
        """Convert text to speech and save as MP3. Returns file path."""
        if not self.client:
            return ""

        sanitized = self._sanitize_text(text)
        audio_path = self._build_audio_path(generation, call_id, turn)

        audio = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            text=sanitized,
            model_id="eleven_turbo_v2_5",
        )

        with open(audio_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)

        return audio_path
