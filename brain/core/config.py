import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    # GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Removed for Offline Mode
    
    # Local Model Configuration
    MODEL_MODE = os.getenv("MODEL_MODE", "local")
    MODEL_PATH = os.getenv("MODEL_PATH", "./models/main/")
    EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", "./models/embed/")
    
    # Ollama Configuration
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    LOCAL_LLM_MODEL = os.getenv("LOCAL_LLM_MODEL", "mistral") # Updated to match installed model
    
    # Legacy flag mapped to local mode for backward compatibility if needed, 
    # but strictly we are "local_llm" now.
    MOCK_LLM = os.getenv("MOCK_LLM", "false").lower() == "true"
    
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")

config = Config()
