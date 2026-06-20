import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import time

load_dotenv()

# ====================== CONFIG ======================
USE_VISION_OCR = True                    # Set to False to skip Vision OCR
PROVIDER = "grok"                        # LLM provider: grok, openai, anthropic

IMAGE_FOLDER = "menu_images"
OUTPUT_FOLDER = "output_json"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Google Cloud Vision Setup
if USE_VISION_OCR:
    from google.cloud import vision
    vision_client = vision.ImageAnnotatorClient()   # Make sure GOOGLE_APPLICATION_CREDENTIALS is set

# ==================== GOOGLE VISION OCR ====================
def extract_text_with_vision(image_path: Path):
    """Use Google Cloud Vision for high-quality OCR"""
    try:
        with open(image_path, "rb") as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = vision_client.text_detection(image=image)
        
        texts = response.text_annotations
        if not texts:
            return ""
        
        full_text = texts[0].description  # Full extracted text
        return full_text
    except Exception as e:
        print(f"Vision OCR failed for {image_path.name}: {e}")
        return None


# ==================== MAIN PROCESSING ====================
def process_menu_image(image_path: Path):
    filename = image_path.name
    print(f"Processing: {filename}")

    ocr_text = None
    if USE_VISION_OCR:
        ocr_text = extract_text_with_vision(image_path)

    # Now send to LLM (with or without OCR text)
    try:
        # You can pass OCR text to LLM to improve accuracy
        enhanced_prompt = get_user_prompt(filename)
        if ocr_text:
            enhanced_prompt += f"\n\nExtracted raw text from image (for reference):\n{ocr_text[:3000]}"

        # ... (same LLM call as before - Grok / OpenAI / Anthropic)

        # Save the final structured JSON
        output_path = Path(OUTPUT_FOLDER) / f"{image_path.stem}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved: {output_path.name}")
        return True

    except Exception as e:
        print(f"❌ Failed {filename}: {e}")
        return False


# Run the batch
if __name__ == "__main__":
    # ... same batch logic as previous script
