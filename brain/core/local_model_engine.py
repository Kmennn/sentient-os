import httpx
import json
import logging
from typing import Iterator, List, Optional
from PIL import Image
import pytesseract
from sentence_transformers import SentenceTransformer
from functools import lru_cache
import io
import hashlib

from core.config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LocalModelEngine:
    def __init__(self):
        self.ollama_url = config.OLLAMA_URL
        self.model_name = config.LOCAL_LLM_MODEL
        self.embedding_model = None
        
        # Lazy load embeddings to avoid startup delay
        # self._load_embedding_model_async() # Do NOT load on import, it blocks main thread.

    def _load_embedding_model_async(self):
        """
        Loads the embedding model. In a real async scenario, this might be offloaded.
        For now, we initialize it on first use or here if acceptable.
        """
        try:
            logger.info(f"Loading embedding model from {config.EMBEDDING_MODEL_PATH}...")
            # cache_folder ensures we store models locally as requested
            self.embedding_model = SentenceTransformer(
                'all-MiniLM-L6-v2', 
                cache_folder=config.EMBEDDING_MODEL_PATH
            )
            logger.info("Local embedding model loaded.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")

    async def generate(self, text: str) -> str:
        """
        Generates text using the local Ollama instance.
        """
        if config.MOCK_LLM:
             return f"Local Mock: {text}"

        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": text,
            "stream": False
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=60.0)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.ConnectError:
            logger.error("Ollama Connection Error. Using Fallbacks.")
            return self._fallback_generate(text)
        except Exception as e:
            logger.error(f"Local generation error: {e}. Using Fallbacks.")
            return self._fallback_generate(text)

    def _fallback_generate(self, text: str) -> str:
        """
        Deterministic fallback with varied responses.
        """
        t = text.lower()
        
        # Intent classification
        if "classify the user intent" in t:
             if "scroll" in t or "click" in t or "type" in t:
                 return "TASK"
             return "CHAT"
        
        # Task planning
        if ("json list" in t or "task planner" in t) and ("scroll" in t or "click" in t):
             return json.dumps([{"action": "SCROLL_DOWN", "params": {}}])
        
        # Varied contextual chat responses
        # Greetings
        if "hello" in t:
            return "Hello! I'm JARVIS, your AI assistant. How can I help you today?"
        if "hi" in t and len(t.split()) <= 2:
            return "Hi there! What can I do for you?"
        if "hey" in t:
            return "Hey! Ready to assist. What do you need?"
        
        # Status/system queries
        if "status" in t or "how are you" in t:
            return "System operational. Local model offline, using fallback mode. Core functions available."
        
        # Questions
        if t.startswith("what") or "what is" in t or "what are" in t:
            return "I'm running in fallback mode with limited knowledge. For detailed answers, please ensure Ollama is running with sufficient RAM."
        
        if t.startswith("how") or "how do" in t or "how can" in t:
            return "In fallback mode, I can help with basic tasks and system commands. What specific action would you like to perform?"
        
        if t.startswith("why") or "why is" in t:
            return "I'm currently using fallback responses because the local LLM (Mistral) requires more RAM than is available."
        
        # Help
        if "help" in t:
            return "I can assist with system tasks like opening apps, scrolling, clicking. Try commands like 'open chrome' or 'scroll down'."
        
        # Appreciation
        if "thank" in t or "thanks" in t:
            return "You're welcome! Let me know if you need anything else."
        
        # Default with context
        if len(t.split()) <= 3:
            return f"I heard: '{text}'. I'm in fallback mode - responses are limited. What would you like to do?"
        
        return f"I understand you said: '{text[:50]}...'. My local model is unavailable. I can help with basic commands and tasks. What do you need?"

    async def generate_stream(self, text: str) -> Iterator[str]:
        """
        Stream generation from Ollama.
        """
        if config.MOCK_LLM:
            yield f"Mock stream: {text}"
            return

        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": text,
            "stream": True
        }

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", url, json=payload, timeout=60.0) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"[Stream Error: {e}]"

    def embed(self, text: str) -> List[float]:
        """
        Generates embeddings locally using sentence-transformers.
        """
        if not self.embedding_model:
            # Try loading again if it wasn't loaded
            self._load_embedding_model_async()
            if not self.embedding_model:
                 return [0.0] * 384 # Fallback
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return [0.0] * 384


    def ocr(self, image_path_or_bytes) -> str:
        """
        Performs OCR on an image using local Tesseract.
        """
        try:
            # If path, read bytes
            if isinstance(image_path_or_bytes, str):
                with open(image_path_or_bytes, "rb") as f:
                    img_bytes = f.read()
            else:
                img_bytes = image_path_or_bytes

            return self._ocr_cached(img_bytes)
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""

    @lru_cache(maxsize=32)
    def _ocr_cached(self, img_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(img_bytes))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            return ""

local_engine = LocalModelEngine()
