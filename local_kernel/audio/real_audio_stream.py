
import logging
import time
import math
from typing import Dict, Any, Optional

try:
    import pyaudio
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    np = None

logger = logging.getLogger(__name__)

class RealAudioStream:
    def __init__(self):
        self.stream = None
        self.pa = None
        self.is_mock = not AUDIO_AVAILABLE
        
        if AUDIO_AVAILABLE:
            try:
                self.pa = pyaudio.PyAudio()
                # Attempt to open default input
                self.stream = self.pa.open(format=pyaudio.paInt16,
                                           channels=1,
                                           rate=16000,
                                           input=True,
                                           frames_per_buffer=1024)
            except Exception as e:
                logger.error(f"Audio init error: {e}")
                self.is_mock = True
        else:
            logger.info("Audio: pyaudio not installed. Using Mock mode.")

    def get_audio_level(self) -> float:
        """
        Return RMS amplitude (0.0 to 1.0 approx).
        """
        if self.is_mock:
            # Simulate silence mostly, with random spikes
            import random
            if random.random() > 0.95:
                return 0.8
            return 0.1
            
        try:
            data = self.stream.read(1024, exception_on_overflow=False)
            # Calculate RMS
            ints = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(ints**2))
            
            # Normalize reasonably (16-bit audio, max 32767)
            level = min(1.0, rms / 10000.0) 
            return level
        except Exception as e:
            logger.error(f"Audio read error: {e}")
            return 0.0

    def analyze_stream(self) -> Optional[Dict[str, Any]]:
        """
        Check for high noise or speech.
        """
        level = self.get_audio_level()
        
        if level > 0.7:
             return {"type": "audio", "label": "loud_noise", "level": level}
             
        # Simple threshold VAD
        if level > 0.3:
             return {"type": "audio", "label": "speech_detected", "level": level}
             
        return None

    def close(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.pa:
            self.pa.terminate()

real_audio = RealAudioStream()
