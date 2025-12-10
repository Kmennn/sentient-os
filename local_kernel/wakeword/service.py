import os
import json
import pyaudio
import logging
from vosk import Model, KaldiRecognizer

logger = logging.getLogger(__name__)

class WakewordService:
    def __init__(self, model_path: str = "models/vosk-model-small-en-us-0.15"):
        self.model_path = model_path
        self.model = None
        self.rec = None
        self.is_listening = False
        
        # Initialize Audio
        self.p = pyaudio.PyAudio()
        self.stream = None

    def load_model(self):
        if not os.path.exists(self.model_path):
            logger.warning(f"Vosk model not found at {self.model_path}. Wakeword disabled.")
            return False
        try:
            self.model = Model(self.model_path)
            self.rec = KaldiRecognizer(self.model, 16000)
            logger.info("Vosk Wakeword Model loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            return False

    def start_listening(self, callback):
        if not self.model and not self.load_model():
            return

        self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        self.stream.start_stream()
        self.is_listening = True
        logger.info("Wakeword Listener Started...")

        try:
            while self.is_listening:
                data = self.stream.read(4000, exception_on_overflow=False)
                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    text = result.get("text", "")
                    if text:
                        logger.info(f"Heard: {text}")
                        callback(text)
        except Exception as e:
            logger.error(f"Error in Wakeword loop: {e}")
            self.stop()

    def stop(self):
        self.is_listening = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()

