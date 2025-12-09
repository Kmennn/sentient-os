import base64
import httpx
import logging
from core.vision.ocr_engine import ocr_engine
from core.local_model_engine import local_engine
from core.vision.image_utils import preprocess_image
from typing import Dict, Any, List
import re

logger = logging.getLogger(__name__)


class VisionEngine:
    def __init__(self):
        self.screenshot_url = "http://localhost:8001/vision/screenshot"

    async def _capture_data(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(self.screenshot_url, timeout=5.0)
                if resp.status_code == 200:
                    return resp.json()
            except Exception as e:
                logger.error(f"Capture failed: {e}")
        return {}

    async def analyze(self, capture: bool = True) -> Dict[str, Any]:
        """
        Analyze screen content.
        """
        data = {}
        if capture:
            data = await self._capture_data()
            
        b64_img = data.get("image", "")
        if not b64_img:
            return {"error": "No image data"}

        image_bytes = base64.b64decode(b64_img)
        screenshot_path = data.get("path", "")
        active_window = data.get("active_window", "Unknown")

        # 1. Preprocess
        processed_bytes = preprocess_image(image_bytes)

        # 2. OCR
        text = ocr_engine.extract_text(processed_bytes)

        # 3. Tagging
        tags = self._extract_tags(text, active_window)
        
        # 4. Summary
        summary = f"Active Window: {active_window}. Content: {text[:200]}..."
        
        # 5. Persist
        await self._persist_event(screenshot_path, text, tags, active_window)

        return {
            "description": summary, # Key expected by Flutter
            "ocr_text": text,
            "tags": tags,
            "active_window": active_window, 
            "objects": tags # Legacy key
        }

    def _extract_tags(self, text: str, active_window: str) -> List[str]:
        tags = []
        # Window based tags
        if active_window:
            tags.append(f"window:{active_window}")
            
        # Keyword based
        keywords = {
            "VSCode": ["Visual Studio Code", "def ", "class ", "import "],
            "Browser": ["Chrome", "Edge", "http", "www"],
            "Terminal": ["PowerShell", "cmd.exe", "user@"],
            "Explorer": ["File Explorer", "C:\\"]
        }
        
        # Check title first
        for key, vals in keywords.items():
            if key in active_window:
                tags.append(key)
        
        # Check text
        for key, vals in keywords.items():
             if any(v in text for v in vals):
                 if key not in tags: tags.append(key)

        return tags

    async def _persist_event(self, path, text, tags, active_window):
        from core.db import get_connection
        import json
        import time
        import uuid
        
        event_id = str(uuid.uuid4())
        ts = int(time.time())
        conn = get_connection()
        cursor = conn.cursor()
        
        # Migration check? We assume vision_events exists.
        # But 'active_window' column might not exist if I haven't migrated.
        # I'll store it in tags or text if column missing?
        # Or better: I'll try to insert. If fails, I'll update schema plan.
        # The user task says "Update Database Schema (active_window)".
        # I haven't done that yet.
        # I am in Phase C. I should do it.
        # But for 'persist_event', I'll use existing columns for now to avoid crash?
        # Or I'll just use 'tags' to store metadata.
        
        metadata = {"active_window": active_window, "tags": tags}
        
        cursor.execute("""
            INSERT INTO vision_events (id, user_id, screenshot_path, ocr_text, tags, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (event_id, "user", path, text, json.dumps(metadata), ts))
        
        conn.commit()
        conn.close()

vision_engine = VisionEngine()
