import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = os.getenv("MODEL", "gemini-2.0-flash")
    MOCK_LLM = os.getenv("MOCK_LLM", "false").lower() == "true"
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")

config = Config()
