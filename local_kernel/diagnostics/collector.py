
import psutil
import time
import requests
import threading
import logging
import platform

logger = logging.getLogger(__name__)

class DiagnosticsCollector:
    def __init__(self, brain_url: str = "http://localhost:8000/v1/jarvis/diagnostics"):
        self.brain_url = brain_url
        self.interval = 2.0
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        logger.info("Diagnostics Collector started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info("Diagnostics Collector stopped.")

    def _loop(self):
        while self.running:
            try:
                stats = self._collect()
                self._send(stats)
            except Exception as e:
                logger.error(f"Error collecting/sending diagnostics: {e}")
            time.sleep(self.interval)

    def _collect(self):
        return {
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_percent": psutil.virtual_memory().percent,
            "os": platform.system(),
            "timestamp": time.time()
        }

    def _send(self, stats):
        try:
            # We can either post to an HTTP endpoint or use a separate WB.
            # Plan says "Create endpoint brain/jarvis/diagnostics.py", so HTTP POST is good.
            requests.post(self.brain_url, json=stats, timeout=1)
        except requests.exceptions.RequestException:
            # Brain might be down, ignore
            pass

collector = DiagnosticsCollector()
