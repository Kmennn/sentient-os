import logging
import platform
import time
from typing import Optional
from brain.context.signals.context_signal_model import ContextSignal, ContextSource

class AppContextProvider:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.os_type = platform.system()
        self._last_title = ""
        self._last_app = ""

    def get_context(self) -> Optional[ContextSignal]:
        if self.os_type == "Windows":
            return self._get_windows_context()
        # Add macOS/Linux support here
        return None

    def _get_windows_context(self) -> Optional[ContextSignal]:
        try:
            import ctypes
            from ctypes import wintypes
            
            user32 = ctypes.windll.user32
            h_wnd = user32.GetForegroundWindow()
            if not h_wnd:
                return None
                
            # Dictionary to store data
            data = {}

            # 1. Get Window Title
            length = user32.GetWindowTextLengthW(h_wnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(h_wnd, buf, length + 1)
            title = buf.value
            data["window_title"] = title
            
            # 2. Get App Name (Simplified: Title often contains app name, or empty)
            # Full process name via ctypes is verbose. 
            # We will use a placeholder or inferred from title for now if psutil missing.
            # Ideally: psutil.Process(pid).name()
            data["app_name"] = "Unknown" 
            
            # Optimization: Only emit if changed significantly? 
            # The scheduler might want periodic updates. We'll return signal always.
            
            if not title:
                return None

            return ContextSignal(
                source=ContextSource.APP_WINDOW,
                data=data
            )
            
        except ImportError:
            self.logger.warning("ctypes not available (Unlikely on Windows).")
        except Exception as e:
            self.logger.error(f"Error getting app context: {e}")
            
        return None
