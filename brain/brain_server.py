from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import google.generativeai as genai
from pydantic import BaseModel

# Load environment variables
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL", "gemini-2.0-flash")

# Configure Gemini
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

app = FastAPI(title="JARVIS Brain (Gemini)")

# Allow frontend (Flutter app) to call this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str

@app.get("/ping")
async def ping():
    return {"ok": True, "msg": "Brain (Gemini) here ✅"}

@app.get("/reply")
async def reply(text: str = Query(..., description="user text")):
    text = text.strip()
    if not text:
        return {"reply": "(empty)"}

    # If no API key is present, just echo
    if not GEMINI_KEY:
        return {"reply": f"(no GEMINI key) You said: {text}"}

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        # Create a chat session or just generate content
        response = model.generate_content(text)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"(error contacting Gemini) {e}"}

@app.post("/chat")
async def chat(msg: ChatMessage):
    return await reply(text=msg.message)
