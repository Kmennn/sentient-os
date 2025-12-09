
# Stub for local wake word engine (Porcupine/Protov)
# Currently simulates detection.

class WakeWordEngine:
    def __init__(self):
        self.active = False
    
    def process(self, audio_chunk):
        # Placeholder for real detection
        return False

wake_word_engine = WakeWordEngine()
