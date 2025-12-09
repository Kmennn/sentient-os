
import io
from PIL import Image, ImageOps, ImageEnhance

def preprocess_image(image_bytes: bytes, max_width: int = 1200) -> bytes:
    """
    Applies preprocessing to improve OCR accuracy and performance.
    1. Resize if too large.
    2. Grayscale.
    3. Enhance Contrast.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # 1. Resize (Downsample for speed)
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
        # 2. Grayscale
        img = ImageOps.grayscale(img)
        
        # 3. Enhance Contrast (for OCR)
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Save to bytes
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        print(f"Image preprocessing failed: {e}")
        return image_bytes # Fallback to original
