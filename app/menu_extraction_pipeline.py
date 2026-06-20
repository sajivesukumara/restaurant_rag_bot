"""
Two-Stage Menu Extraction Pipeline
- External schema (menu_schema.json)
- Auto generates requirements.txt
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
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

# Create directories
for folder in [IMAGE_FOLDER, INTERMEDIATE_FOLDER, OUTPUT_FOLDER, MODELS_FOLDER]:
    folder.mkdir(parents=True, exist_ok=True)

# Set PaddleOCR model directory
os.environ['PADDLE_HOME'] = str(MODELS_FOLDER)
os.environ['PADDLE_PDX_CACHE_HOME'] = str(MODELS_FOLDER)

# ====================== AUTO-GENERATE requirements.txt ======================
def generate_requirements():
    requirements = """# Menu Extraction Pipeline Requirements
paddleocr>=2.8.0
paddlepaddle>=2.6.0
tqdm>=4.66.0
python-dotenv>=1.0.0
openai>=1.0.0
Pillow>=10.0.0
"""
    with open(REQUIREMENTS_FILE, "w", encoding="utf-8") as f:
        f.write(requirements)
    print(f"✅ requirements.txt generated/updated")

generate_requirements()

# ====================== LOAD SCHEMA ======================
def load_schema():
    try:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema = json.load(f)
        print(f"✅ Schema loaded: {SCHEMA_FILE.name}")
        return schema
    except Exception as e:
        print(f"❌ Failed to load schema: {e}")
        exit(1)

schema = load_schema()

# ====================== CONFIG ======================
PROVIDER = "grok"

# ====================== STAGE 1: PADDLEOCR ======================
def setup_paddleocr():
    print("🔧 Initializing PaddleOCR-VL...")
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        print("✅ PaddleOCR ready!")
        return ocr
    except ImportError:
        print("❌ Missing dependencies. Run: pip install -r requirements.txt")
        exit(1)

def extract_ocr(ocr, image_path: Path):
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
                structured_lines.append({"text": text, "confidence": float(confidence)})
                full_text += text + "\n"

        ocr_data = {
            "filename": image_path.name,
            "full_text": full_text.strip(),
            "structured_lines": structured_lines
        }

        inter_path = INTERMEDIATE_FOLDER / f"{image_path.stem}_ocr.json"
        with open(inter_path, "w", encoding="utf-8") as f:
            json.dump(ocr_data, f, indent=2, ensure_ascii=False)

        return full_text.strip(), ocr_data
    except Exception as e:
        print(f"   OCR Error: {e}")
        return None, None


# ====================== STAGE 2: LLM ======================
def get_user_prompt(filename: str, ocr_text: str):
    schema_str = json.dumps(schema, indent=2)
    return f"""You are an expert restaurant menu data extractor.

Raw OCR text:

{ocr_text[:4000]}

Convert into structured JSON using this exact schema:

{schema_str}

Return ONLY valid JSON."""

def call_llm(filename: str, ocr_text: str):
    try:
        if PROVIDER == "grok":
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1")
            model_name = "grok-4.3"
        elif PROVIDER == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            model_name = "gpt-4o"
        else:
            raise ValueError("Unsupported provider")

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert restaurant menu parser."},
                {"role": "user", "content": get_user_prompt(filename, ocr_text)}
            ],
            temperature=0.0,
            max_tokens=4000
        )

        text = response.choices[0].message.content.strip()

        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].strip()

        return json.loads(text)

    except Exception as e:
        print(f"   LLM Error: {e}")
        return None


# ====================== MAIN ======================
def process_image(image_path: Path, paddle_ocr):
    print(f"🔄 Processing: {image_path.name}")

    ocr_text, _ = extract_ocr(paddle_ocr, image_path)
    if not ocr_text:
        return False

    final_data = call_llm(image_path.name, ocr_text)
    if not final_data:
        return False

    output_path = OUTPUT_FOLDER / f"{image_path.stem}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved: {output_path.name}")
    return True


# ====================== RUN ======================
if __name__ == "__main__":
    print("=" * 70)
    print("🚀 Two-Stage Menu Extraction Pipeline (External Schema)")
    print("=" * 70)

    paddle_ocr = setup_paddleocr()

    image_files = [f for ext in ["*.jpg", "*.jpeg", "*.png"] for f in IMAGE_FOLDER.glob(ext)]

    if not image_files:
        print(f"❌ No images found in {IMAGE_FOLDER}")
        exit()

    print(f"Found {len(image_files)} images.\n")

    success = 0
    for img_path in tqdm(image_files):
        if process_image(img_path, paddle_ocr):
            success += 1
        time.sleep(1.5)

    print("\n" + "=" * 70)
    print(f"🎉 Completed! {success}/{len(image_files)} menus processed successfully.")
    print(f"Final files saved in: {OUTPUT_FOLDER}")
    print("=" * 70)
