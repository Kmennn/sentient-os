import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Removed for Offline Mode
    
    # Local Model Configuration
    VERSION = "1.9.0"
    MODEL_MODE = os.getenv("MODEL_MODE", "local")
    MODEL_PATH = os.getenv("MODEL_PATH", "./models/main/")
    EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", "./models/embed/")
    
    # Ollama Configuration - Optimized for 16GB RAM
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "qwen2.5:3b")  # Primary: fast, low RAM
    FALLBACK_LLM_MODEL = os.getenv("FALLBACK_LLM_MODEL", "phi3:mini")  # Fallback: even smaller
    
    # Pre-warm settings
    PREWARM_MODEL = os.getenv("PREWARM_MODEL", "true").lower() == "true"
    
    # Legacy flag mapped to local mode for backward compatibility if needed, 
    # but strictly we are "local_llm" now.
    MOCK_LLM = os.getenv("MOCK_LLM", "false").lower() == "true"
    
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")

config = Config()
