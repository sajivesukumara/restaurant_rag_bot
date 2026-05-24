import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import time

load_dotenv()

# ====================== CONFIGURATION ======================
STAGE1_MODEL = "PaddleOCR-VL"             # Stage 1: Local OCR VLM
PROVIDER = os.getenv("PROVIDER", "grok")  # Stage 2: Cloud LLM ("grok", "openai", "anthropic")

IMAGE_FOLDER = "menu_images"
INTERMEDIATE_FOLDER = "intermediate_ocr"
OUTPUT_FOLDER = "final_json"

os.makedirs(INTERMEDIATE_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Set custom cache directory
os.environ['PADDLE_PDX_CACHE_HOME'] = 'd:/models'
os.environ['PADDLE_HOME'] = 'd:/models'

# ====================== STAGE 1: LOCAL PADDLEOCR-VL ======================
def setup_paddleocr_vl():
    print("Setting up PaddleOCR-VL...")
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        print("✅ PaddleOCR-VL loaded successfully!")
        return ocr
    except ImportError:
        print("❌ PaddleOCR not installed. Run: pip install paddleocr paddlepaddle")
        exit(1)

def extract_with_paddleocr(ocr, image_path: Path):
    """Stage 1: Extract raw text + layout using PaddleOCR-VL"""
    try:
        result = ocr.ocr(str(image_path), cls=True)
        
        full_text = ""
        structured_lines = []
        
        for line in result:
            if line is None:
                continue
            for word_info in line:
                text = word_info[1][0]
                confidence = word_info[1][1]
                structured_lines.append({
                    "text": text,
                    "confidence": float(confidence)
                })
                full_text += text + "\n"
        
        output_data = {
            "filename": image_path.name,
            "full_text": full_text.strip(),
            "structured_lines": structured_lines,
            "total_lines": len(structured_lines)
        }
        
        # Save intermediate result
        inter_path = Path(INTERMEDIATE_FOLDER) / f"{image_path.stem}_ocr.json"
        with open(inter_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        return full_text, output_data
    
    except Exception as e:
        print(f"Error in PaddleOCR: {e}")
        return None, None


# ====================== STAGE 2: CLOUD LLM ======================
def get_user_prompt(filename: str, ocr_text: str):
    return f"""You are an expert menu data extractor.

Here is the raw OCR text extracted from the menu image:

{ocr_text[:3500]}

Convert this into a clean, structured JSON using the following schema.
Be accurate with prices, categories, and ingredients.

Return ONLY valid JSON (no extra text):

{{
  "restaurant": {{
    "id": "string",
    "name": "string",
    "address": "string or null",
    "cuisine_type": ["array of strings"],
    "source": "Menu Image",
    "source_file": "{filename}",
    "menu": [
      {{
        "id": "string",
        "original_name": "string",
        "canonical_name": "string (lowercase_with_underscores)",
        "name": "string",
        "category": "string",
        "normalized_category": "string",
        "sub_category": "string",
        "veg_nonveg": "Vegetarian | Non-Vegetarian | Eggetarian",
        "ingredients": ["array"],
        "normalized_ingredients": ["array"],
        "allergens": ["array"],
        "price": number,
        "currency": "string",
        "description": "string",
        "pairings": ["array"],
        "halal": boolean,
        "jain_available": boolean,
        "availability": {{
          "available": true,
          "seasonal": false,
          "meal_slots": ["Lunch", "Dinner"],
          "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        }},
        "confidence_score": 0.85
      }}
    ]
  }}
}}"""

# ====================== MAIN PIPELINE ======================
def process_image(image_path: Path, paddle_ocr):
    print(f"\n🔄 Processing: {image_path.name}")
    
    # Stage 1: Local OCR
    ocr_text, ocr_data = extract_with_paddleocr(paddle_ocr, image_path)
    if not ocr_text:
        print("❌ Stage 1 failed")
        return False
    
    # Stage 2: Cloud LLM Structuring
    try:
        # (Add your LLM client code here - Grok / OpenAI / Anthropic)
        # Example for Grok:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
        
        response = client.chat.completions.create(
            model="grok-4.3",
            messages=[
                {"role": "system", "content": "You are an expert restaurant menu parser."},
                {"role": "user", "content": get_user_prompt(image_path.name, ocr_text)}
            ],
            temperature=0.0,
            max_tokens=4000
        )
        
        json_text = response.choices[0].message.content.strip()
        
        # Clean JSON
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0].strip()
        
        final_data = json.loads(json_text)
        
        # Save final output
        final_path = Path(OUTPUT_FOLDER) / f"{image_path.stem}.json"
        with open(final_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Final JSON saved: {final_path.name}")
        return True
        
    except Exception as e:
        print(f"❌ Stage 2 failed: {e}")
        return False


# ====================== RUN PIPELINE ======================
if __name__ == "__main__":
    paddle_ocr = setup_paddleocr_vl()
    
    image_files = list(Path(IMAGE_FOLDER).glob("*.jpg")) + list(Path(IMAGE_FOLDER).glob("*.jpeg")) + list(Path(IMAGE_FOLDER).glob("*.png"))
    
    print(f"Found {len(image_files)} images. Starting two-stage pipeline...\n")
    
    success = 0
    for img_path in tqdm(image_files):
        if process_image(img_path, paddle_ocr):
            success += 1
        time.sleep(1)  # Be gentle on API
    
    print(f"\n🎉 Pipeline Completed! {success}/{len(image_files)} menus processed successfully.")
