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
        self._load_embedding_model_async()

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
            return "Error: Could not connect to local Ollama instance at 127.0.0.1:11434. Is it running?"
        except Exception as e:
            logger.error(f"Local generation error: {e}")
            return f"Error regenerating text locally: {e}"

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
