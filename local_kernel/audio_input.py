import time
import requests
import base64
import threading

class AudioInputSimulator:
    def __init__(self):
        self._running = False
        self._thread = None
        self.brain_url = "http://127.0.0.1:8000/v1/audio"

    def start_streaming(self):
        if self._running: return
        self._running = True
        self._thread = threading.Thread(target=self._stream_loop)
        self._thread.start()

    def stop_streaming(self):
        self._running = False
        if self._thread:
            self._thread.join()

    def _stream_loop(self):
        print("Starting simulated audio stream...")
        while self._running:
            try:
                # Generate dummy 1KB chunk
                chunk = b'\x00' * 1024 
                response = requests.post(
                    self.brain_url, 
                    data=chunk,
                    headers={"Content-Type": "application/octet-stream"}
                )
                if response.status_code == 200:
                    print(".", end="", flush=True)
                else:
                    print("x", end="", flush=True)
            except Exception as e:
                print(f"Audio stream error: {e}")
            
            time.sleep(0.5) # 2Hz

audio_sim = AudioInputSimulator()

if __name__ == "__main__":
    audio_sim.start_streaming()
    time.sleep(5)
    audio_sim.stop_streaming()
