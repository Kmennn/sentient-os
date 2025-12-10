import asyncio
import websockets
import pyaudio
import logging
import json

logger = logging.getLogger(__name__)

class VoiceStreamer:
    def __init__(self, brain_url: str = "ws://localhost:8000/v1/voice/stream"):
        self.brain_url = brain_url
        self.is_streaming = False
        self.p = pyaudio.PyAudio()
        self.stream = None

    async def stream_audio(self):
        self.is_streaming = True
        logger.info(f"Connecting to Brain Voice Stream at {self.brain_url}...")
        
        try:
            async with websockets.connect(self.brain_url) as websocket:
                logger.info("Connected to Voice Stream.")
                
                self.stream = self.p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
                self.stream.start_stream()
                
                logger.info("Streaming audio...")
                while self.is_streaming:
                    try:
                        data = self.stream.read(4096, exception_on_overflow=False)
                        # Send binary
                        await websocket.send(data)
                        
                        # Ideally, we also listen for responses (transcripts) here
                        # But for simplicity, we might just fire and forget or have a separate listener task
                        # response = await asyncio.wait_for(websocket.recv(), timeout=0.1) 
                        # if response: logger.info(f"Brain: {response}")
                        
                    except Exception as e:
                        logger.error(f"Stream loop error: {e}")
                        break
        except Exception as e:
            logger.error(f"Failed to connect/stream: {e}")
        finally:
            self.stop()

    def stop(self):
        self.is_streaming = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
        logger.info("Voice Streamer Stopped.")

