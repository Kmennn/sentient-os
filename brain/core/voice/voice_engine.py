
import os
import json
import logging
import io

# Try importing vosk
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

# Try importing speech_recognition
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

logger = logging.getLogger("voice_engine")

class VoiceEngine:
    def __init__(self, model_path="brain/models/vosk-model-small-en-us-0.15"):
        self.mode = "none"
        self.vosk_model = None
        self.sr_recognizer = None
        
        # 1. Try Vosk
        if VOSK_AVAILABLE and os.path.exists(model_path):
            try:
                logger.info(f"Loading Vosk model from {model_path}...")
                self.vosk_model = Model(model_path)
                self.mode = "vosk"
                logger.info("Vosk engine active.")
            except Exception as e:
                logger.error(f"Vosk load failed: {e}")
        
        # 2. Fallback to SpeechRecognition (Google/Sphinx)
        if self.mode == "none" and SR_AVAILABLE:
            self.sr_recognizer = sr.Recognizer()
            self.mode = "sr"
            logger.info("SpeechRecognition engine active (Google/Sphinx).")
            
        if self.mode == "none":
            logger.warning("No voice engine available (Vosk model missing & SpeechRecognition not installed).")

    async def transcribe(self, audio_data: bytes) -> dict:
        """
        Transcribe WAV bytes.
        Returns: {"text": "...", "confidence": 1.0}
        """
        if self.mode == "none":
            return {"text": "", "error": "No engine"}

        # Vosk
        if self.mode == "vosk":
            try:
                rec = KaldiRecognizer(self.vosk_model, 16000)
                rec.AcceptWaveform(audio_data)
                res = json.loads(rec.FinalResult())
                return {"text": res.get("text", "")}
            except Exception as e:
                logger.error(f"Vosk error: {e}")
                return {"text": "", "error": str(e)}

        # SpeechRecognition
        if self.mode == "sr":
            try:
                # Convert bytes to AudioFile-like
                import wave
                with io.BytesIO(audio_data) as wav_io:
                    with sr.AudioFile(wav_io) as source:
                        audio = self.sr_recognizer.record(source)
                        # Recognize
                        text = self.sr_recognizer.recognize_google(audio)
                        return {"text": text}
            except sr.UnknownValueError:
                return {"text": ""}
            except Exception as e:
                logger.error(f"SR error: {e}")
                return {"text": "", "error": str(e)}

voice_engine = VoiceEngine()
