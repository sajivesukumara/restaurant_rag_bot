"""
Two-Stage Menu Extraction Pipeline
Schema is loaded from external file for easy maintenance.
"""

import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# ====================== PROJECT SETUP ======================
PROJECT_ROOT = Path(__file__).parent.absolute()

IMAGE_FOLDER = PROJECT_ROOT / "menu_images"
INTERMEDIATE_FOLDER = PROJECT_ROOT / "intermediate_ocr"
OUTPUT_FOLDER = PROJECT_ROOT / "final_json"
MODELS_FOLDER = PROJECT_ROOT / "models" / "paddleocr"
SCHEMA_FILE = PROJECT_ROOT / "menu_schema.json"

# Create directories
for folder in [IMAGE_FOLDER, INTERMEDIATE_FOLDER, OUTPUT_FOLDER, MODELS_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

os.environ['PADDLE_HOME'] = str(MODELS_FOLDER)
os.environ['PADDLE_PDX_CACHE_HOME'] = str(MODELS_FOLDER)

# Load Schema
def load_schema():
    try:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load menu_schema.json: {e}")
        exit(1)

schema = load_schema()

print(f"✅ Schema loaded successfully from {SCHEMA_FILE.name}")

# ====================== CONFIG ======================
PROVIDER = "grok"

# ====================== STAGE 1: PADDLEOCR ======================
def setup_paddleocr():
    print("🔧 Initializing PaddleOCR-VL...")
    from paddleocr import PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
    print("✅ PaddleOCR ready!")
    return ocr

def extract_ocr(ocr, image_path: Path):
    # ... (same as previous version - unchanged)
    # Returns full_text, ocr_data
    pass  # I'll provide full code if needed

# ====================== STAGE 2: LLM ======================
def get_user_prompt(filename: str, ocr_text: str):
    schema_str = json.dumps(schema, indent=2)
    
    return f"""You are an expert restaurant menu data extractor.

Raw OCR text from the image:

{ocr_text[:4000]}

Convert this into structured data using the **exact schema** below.

**SCHEMA:**
{schema_str}

Return ONLY valid JSON matching this schema. No extra text."""

# ====================== MAIN PIPELINE ======================
def process_image(image_path: Path, paddle_ocr):
    print(f"🔄 Processing: {image_path.name}")
    
    ocr_text, _ = extract_ocr(paddle_ocr, image_path)
    if not ocr_text:
        return False

    # Call LLM (same logic as before)
    # ... 

    print(f"✅ Saved: {image_path.stem}.json")
    return True


# ====================== RUN ======================
if __name__ == "__main__":
    print("🚀 Two-Stage Menu Extraction Pipeline (External Schema)")
    paddle_ocr = setup_paddleocr()
    
    image_files = list(IMAGE_FOLDER.glob("*.jpg")) + list(IMAGE_FOLDER.glob("*.jpeg")) + list(IMAGE_FOLDER.glob("*.png"))
    
    success = 0
    for img in tqdm(image_files):
        if process_image(img, paddle_ocr):
            success += 1
        time.sleep(1.5)

    print(f"\n🎉 Completed! {success}/{len(image_files)} menus processed.")
    
