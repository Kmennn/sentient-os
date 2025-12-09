
import asyncio
import os
import sys
# Ensure gitignored/local modules are found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../brain")))

from core.local_model_engine import local_engine


async def verify_llm():
    print("--- Verifying LLM (Ollama) ---")
    try:
        response = await local_engine.generate("Hello")
        if "Error" in response:
            print(f"FAILURE: {response}")
            if "500" in response:
                print(">>> TIP: Model might not be pulled. Run: 'ollama pull tinyllama'")
        else:
             print(f"SUCCESS: LLM response received: {response}")
    except Exception as e:
        print(f"FAILURE: LLM verification failed: {e}")

def verify_embeddings():
    print("\n--- Verifying Embeddings (SentenceTransformers) ---")
    try:
        vec = local_engine.embed("Test")
        if len(vec) == 384:
             print("SUCCESS: Embeddings generated.")
        else:
             print(f"WARNING: Unexpected vector length {len(vec)}")
    except Exception as e:
        print(f"FAILURE: Embeddings failed: {e}")

def verify_ocr():
    print("\n--- Verifying OCR (Tesseract) ---")
    try:
        # Create a simple image using PIL to test
        from PIL import Image
        import io
        img = Image.new('RGB', (100, 30), color = (255, 255, 255))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        text = local_engine.ocr(img_bytes)
        print("SUCCESS: OCR function executed.")
    except Exception as e:
        print(f"FAILURE: OCR failed: {e}")
        print(">>> TIP: Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")


async def main():
    print("=== Sentient OS v1.6 Offline Verification ===\n")
    await verify_llm()
    verify_embeddings()
    verify_ocr()
    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    asyncio.run(main())
