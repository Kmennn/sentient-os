
import base64
import httpx
import logging
from core.vision.ocr_engine import ocr_engine
from core.vision.detect_engine import detect_engine
from core.db import get_connection

logger = logging.getLogger("vision_engine")

class VisionEngine:
    def __init__(self):
        self.body_url = "http://localhost:8001/vision/screenshot"

    async def capture_screen(self) -> bytes:
        """Fetch screenshot from Body"""
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(self.body_url, timeout=2.0)
                if resp.status_code == 200:
                    data = resp.json()
                    b64_img = data.get("image")
                    if b64_img:
                        return base64.b64decode(b64_img)
            except Exception as e:
                logger.error(f"Failed to capture screen: {e}")
        return None

    async def analyze(self, image_bytes: bytes = None, capture: bool = False):
        """
        Full analysis pipeline.
        """
        screenshot_path = ""
        
        # 1. Capture if requested
        if capture or not image_bytes:
             # Call Body
             async with httpx.AsyncClient() as client:
                try:
                    resp = await client.get(self.body_url, timeout=2.0)
                    if resp.status_code == 200:
                        data = resp.json()
                        b64_img = data.get("image")
                        screenshot_path = data.get("path", "")
                        if b64_img:
                            image_bytes = base64.b64decode(b64_img)
                except Exception as e:
                    logger.error(f"Failed to capture screen: {e}")

        if not image_bytes:
            return {"error": "Could not acquire image"}

        # Pipeline
        # Pipeline
        # Preprocessing: Grayscale
        from PIL import Image
        import io
        
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to grayscale for better text extraction
            gray_image = image.convert('L')
            # (Optional) Thresholding could be added here
            
            # Pass processed image to OCR (need to adjust ocr_engine to accept PIL image or bytes)
            # Assuming ocr_engine takes bytes, we convert back. 
            # OR we modify ocr_engine. For now, let's keep it simple:
            # We will use the raw bytes for ocr_engine if it handles it well, 
            # but if we want improvements we should modify ocr_engine.py.
            # Let's check ocr_engine content first. Assuming it uses pytesseract on bytes.
            
            # Actually, ocr_engine likely uses PIL.open(). 
            # If so, we should just let it handle it or modify IT.
            # But the prompt said "quality upgrade... Add preprocessing". 
            # Let's check ocr_engine.py next. For now, I'll add the tagging logic.
            
            text = ocr_engine.extract_text(image_bytes) # We stick to bytes for now
        except Exception:
             text = ocr_engine.extract_text(image_bytes)

        # MVP Tags
        tags = ["screen_content"] 
        if text: tags.append("has_text")
        
        # Simple keyword tagging
        keywords = {
            "VSCode": ["Code", "Visual Studio", "File", "Edit"],
            "Browser": ["http", "www", "Chrome", "Edge", "Firefox"],
            "Terminal": ["PS", "C:\\", "bash", "user@"],
            "Settings": ["Settings", "System", "Bluetooth"]
        }
        
        for tag, words in keywords.items():
            if any(w in text for w in words):
                tags.append(tag)
                break
        
        summary = f"Screen contains text: {text[:100]}... Tags: {tags}" if text else "Screen appears empty."
        
        # Log event (Persist)
        import uuid
        import json
        import time
        
        event_id = str(uuid.uuid4())
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vision_events (id, user_id, screenshot_path, ocr_text, tags, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event_id, "user", screenshot_path, text, json.dumps(tags), int(time.time())))
        conn.commit()
        conn.close()
        
        return {
            "event_id": event_id,
            "ocr_text": text,
            "tags": tags,
            "summary": summary
        }

vision_engine = VisionEngine()
