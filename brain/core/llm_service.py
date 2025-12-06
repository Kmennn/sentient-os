import google.generativeai as genai
from core.config import config

class LLMService:
    def __init__(self):
        if config.GEMINI_API_KEY:
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(config.MODEL_NAME)
        else:
            self.model = None

    async def generate_response(self, text: str, history: list = None, stream: bool = False) -> str:
        """
        Generates a response from the LLM.
        Args:
            text: User input.
            history: List of previous messages.
            stream: If True, returns a generator (not implemented yet for this v1.2 Interface).
        """
        # Mock Mode
        if config.MOCK_LLM:
            return f"Mock reply to: {text}"

        if not self.model:
            return f"(no GEMINI key) You said: {text}"
        
        try:
            # Construct chat session from history if provided
            chat_history = []
            if history:
                # Map standard role names to Gemini roles if needed (user/model)
                # Gemini expects 'user' and 'model' usually.
                for msg in history:
                    role = "user" if msg["role"] == "user" else "model"
                    chat_history.append({"role": role, "parts": [msg["content"]]})
            
            # Create a chat session
            chat = self.model.start_chat(history=chat_history)
            
            # Send the new message
            response = chat.send_message(text)
            return response.text
        except Exception as e:
            return f"(error contacting Gemini) {e}"

llm_service = LLMService()
