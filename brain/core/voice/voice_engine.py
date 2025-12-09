
import os
import json
import logging
from vosk import Model, KaldiRecognizer
import wave
import io

logger = logging.getLogger("voice_engine")

class VoiceEngine:
    def __init__(self, model_path="brain/models/vosk-model-small-en-us-0.15"):
        self.model = None
        self.model_path = model_path
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            logger.info(f"Loading Vosk model from {self.model_path}...")
            try:
                self.model = Model(self.model_path)
                logger.info("Vosk model loaded.")
            except Exception as e:
                logger.error(f"Failed to load Vosk model: {e}")
        else:
            logger.warning(f"Vosk model not found at {self.model_path}. Voice features disabled.")

    async def transcribe(self, audio_data: bytes) -> dict:
        """
        Transcribe WAV bytes.
        Returns: {"text": "...", "confidence": 1.0}
        """
        if not self.model:
            return {"text": "", "error": "Model not loaded"}

        # Vosk expects 16kHz mono PCM usually.
        # We assume the UI sends correct format or we might need headers.
        # If raw bytes, we need to know sample rate.
        # KaldiRecognizer(model, sample_rate)
        
        try:
             # Try to read as Wav to get params?
             # Or assume raw 16k mono?
             # Let's try to parse wav header if present
            with io.BytesIO(audio_data) as wav_file:
                with wave.open(wav_file, "rb") as wf:
                    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                        # Simplification: Accept it anyway for now or log warning
                        pass
                    
                    rec = KaldiRecognizer(self.model, wf.getframerate())
                    rec.AcceptWaveform(audio_data)
                    res = json.loads(rec.FinalResult())
                    return {"text": res.get("text", "")}
        except Exception as e:
            # Fallback: assume raw 16000?
            try:
                rec = KaldiRecognizer(self.model, 16000)
                rec.AcceptWaveform(audio_data)
                res = json.loads(rec.FinalResult())
                return {"text": res.get("text", "")}
            except Exception as e2:
                 logger.error(f"Transcription error: {e2}")
                 return {"text": "", "error": str(e2)}

voice_engine = VoiceEngine()
