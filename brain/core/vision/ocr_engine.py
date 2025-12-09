
import pytesseract
from PIL import Image
import io
import logging

logger = logging.getLogger("ocr_engine")

class OCREngine:
    def __init__(self):
        # Explicit path might be needed if Tesseract is not in PATH
        # For now assume it is, or user set TESSDATA_PREFIX
        pass

    def extract_text(self, image_data: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            logger.error(f"OCR Failed: {e}")
            return ""

ocr_engine = OCREngine()
