
import logging
import json
from vosk import KaldiRecognizer
from .voice_engine import voice_engine

logger = logging.getLogger("continuous_voice")

class ContinuousVoiceSession:
    def __init__(self, sample_rate=16000):
        self.recognizer = None
        self.sample_rate = sample_rate
        if voice_engine.model:
             self.recognizer = KaldiRecognizer(voice_engine.model, sample_rate)
        else:
             logger.warning("Vosk model missing, continuous voice disabled.")

    def process_chunk(self, audio_data: bytes) -> dict:
        """
        Process a chunk of audio.
        Returns {"text": "...", "final": bool}
        """
        if not self.recognizer:
            return {"error": "No Model"}

        if self.recognizer.AcceptWaveform(audio_data):
            # Final result (speech segment ended)
            res = json.loads(self.recognizer.Result())
            text = res.get("text", "")
            return {"text": text, "final": True}
        else:
            # Partial
            res = json.loads(self.recognizer.PartialResult())
            partial = res.get("partial", "")
            return {"text": partial, "final": False}
    
    def final_result(self):
        if not self.recognizer: return ""
        res = json.loads(self.recognizer.FinalResult())
        return res.get("text", "")

class ContinuousEngine:
    def create_session(self):
        return ContinuousVoiceSession()

continuous_engine = ContinuousEngine()
