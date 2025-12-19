import logging
import threading

class VoiceOutputManager:
    def __init__(self, context_provider=None):
        self.logger = logging.getLogger(__name__)
        self.context_provider = context_provider # Access to Focus/Presence
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160) # Slightly faster
            self.engine.setProperty('volume', 1.0)
        except ImportError:
            self.logger.warning("pyttsx3 not found. Voice output will be logged only.")
        except Exception as e:
            self.logger.error(f"Failed to init TTS engine: {e}")

    def speak(self, text: str, force: bool = False):
        """
        Speak text if policy allows.
        force: Override focus/presence checks (e.g. Critical Emergency).
        """
        if not self._should_speak(force):
            self.logger.info(f"[VOICE SUPPRESSED] {text}")
            return

        self.logger.info(f"[VOICE] {text}")
        if self.engine:
            # Run in thread to avoid blocking the tick
            threading.Thread(target=self._run_speech, args=(text,), daemon=True).start()

    def _should_speak(self, force: bool) -> bool:
        if force:
            return True
        
        if not self.context_provider:
             return True # Default to allowed if no context
             
        # Check Focus
        # Assuming context_provider has access to current focus state
        # For minimal impl, we might need a direct reference or callback
        # If blocked -> return False
        
        return True

    def _run_speech(self, text):
        try:
            # Re-init engine in thread if needed (pyttsx3 is touchy with threads)
            # For robustness in this minimal phase, we try-catch
            # Ideally we use a queue and a dedicated worker thread
            
            # Simple approach: New engine instance per thread is safer on some OS
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            self.logger.error(f"TTS Error: {e}")
